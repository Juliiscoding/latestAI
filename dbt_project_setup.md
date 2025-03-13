# Setting Up dbt for Mercurios.ai

This guide outlines how to set up dbt (data build tool) for transforming raw data in Snowflake into analytics-ready tables.

## Project Structure

```
mercurios_dbt/
├── dbt_project.yml          # Project configuration
├── models/                  # All your SQL models
│   ├── staging/             # Initial cleaning of source data
│   │   ├── stg_prohandel/   # ProHandel specific staging models
│   │   │   ├── stg_prohandel__articles.sql
│   │   │   ├── stg_prohandel__customers.sql
│   │   │   ├── stg_prohandel__orders.sql
│   │   │   └── stg_prohandel__sales.sql
│   │   ├── stg_ga4/         # Google Analytics 4 staging models
│   │   │   ├── stg_ga4__events.sql
│   │   │   ├── stg_ga4__pages.sql
│   │   │   └── stg_ga4__conversions.sql
│   │   └── stg_klaviyo/     # Klaviyo staging models
│   │       ├── stg_klaviyo__persons.sql
│   │       ├── stg_klaviyo__events.sql
│   │       └── stg_klaviyo__campaigns.sql
│   ├── intermediate/        # Business logic layer
│   │   ├── int_inventory/   # Inventory-related models
│   │   │   ├── int_inventory__current_stock.sql
│   │   │   └── int_inventory__stock_movements.sql
│   │   ├── int_sales/       # Sales-related models
│   │   │   ├── int_sales__daily.sql
│   │   │   └── int_sales__product.sql
│   │   └── int_customers/   # Customer-related models
│   │       ├── int_customers__profiles.sql
│   │       └── int_customers__segments.sql
│   └── marts/              # Business-specific output models
│       ├── inventory/       # Inventory analytics
│       │   ├── inventory_status.sql
│       │   └── reorder_recommendations.sql
│       ├── sales/           # Sales analytics
│       │   ├── sales_performance.sql
│       │   └── product_performance.sql
│       └── customers/       # Customer analytics
│           ├── customer_segments.sql
│           └── customer_lifetime_value.sql
├── macros/                 # Reusable SQL snippets
│   ├── generate_schema_name.sql
│   └── tenant_isolation.sql
├── seeds/                  # CSV files for reference data
│   └── product_categories.csv
└── tests/                  # Data quality tests
    ├── assert_positive_values.sql
    └── assert_unique_key.sql
```

## Initial Setup

1. Install dbt:
```bash
pip install dbt-snowflake
```

2. Initialize a new dbt project:
```bash
dbt init mercurios_dbt
cd mercurios_dbt
```

3. Configure Snowflake connection in `~/.dbt/profiles.yml`:
```yaml
mercurios_dbt:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: VRXDFZX-ZZ95717
      user: JULIUSRECHENBACH
      password: "{{ env_var('DBT_SNOWFLAKE_PASSWORD') }}"
      role: MERCURIOS_FIVETRAN_SERVICE
      database: MERCURIOS_DATA
      warehouse: COMPUTE_WH
      schema: dbt_dev
      threads: 4
      client_session_keep_alive: False
```

4. Test the connection:
```bash
dbt debug
```

## Multi-tenant Considerations

For multi-tenant data isolation, implement a macro that adds tenant filtering:

```sql
-- macros/tenant_isolation.sql
{% macro tenant_filter() %}
    tenant_id = '{{ var("tenant_id") }}'
{% endmacro %}
```

Then use it in your models:

```sql
-- models/staging/stg_prohandel/stg_prohandel__articles.sql
SELECT 
    id,
    name,
    price,
    category
FROM 
    {{ source('raw', 'articles') }}
WHERE 
    {{ tenant_filter() }}
```

## Example Model: Inventory Status

```sql
-- models/marts/inventory/inventory_status.sql
WITH current_stock AS (
    SELECT * FROM {{ ref('int_inventory__current_stock') }}
),

sales_velocity AS (
    SELECT 
        product_id,
        AVG(quantity) as avg_daily_sales
    FROM {{ ref('int_sales__daily') }}
    WHERE date >= DATEADD(day, -30, CURRENT_DATE())
    GROUP BY product_id
)

SELECT
    cs.product_id,
    cs.product_name,
    cs.current_stock,
    cs.reorder_point,
    sv.avg_daily_sales,
    CASE 
        WHEN cs.current_stock <= 0 THEN 'Out of stock'
        WHEN cs.current_stock <= cs.reorder_point THEN 'Reorder'
        WHEN cs.current_stock <= cs.reorder_point * 2 THEN 'Low stock'
        ELSE 'In stock'
    END as stock_status,
    CASE
        WHEN sv.avg_daily_sales > 0 THEN FLOOR(cs.current_stock / sv.avg_daily_sales)
        ELSE 999
    END as days_of_inventory
FROM current_stock cs
LEFT JOIN sales_velocity sv ON cs.product_id = sv.product_id
```

## Running dbt

1. Build all models:
```bash
dbt run
```

2. Run tests:
```bash
dbt test
```

3. Generate documentation:
```bash
dbt docs generate
dbt docs serve
```

## CI/CD Integration

Set up a GitHub Actions workflow to run dbt on push:

```yaml
# .github/workflows/dbt.yml
name: dbt

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  dbt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install dbt-snowflake
      - name: Run dbt
        env:
          DBT_SNOWFLAKE_PASSWORD: ${{ secrets.DBT_SNOWFLAKE_PASSWORD }}
        run: |
          dbt debug
          dbt compile
          dbt test
```
