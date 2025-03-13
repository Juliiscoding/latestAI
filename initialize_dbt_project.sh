#!/bin/bash
# Script to initialize a dbt project for Mercurios.ai

echo "Initializing dbt project for Mercurios.ai..."

# Check if dbt is installed
if ! command -v dbt &> /dev/null; then
    echo "dbt is not installed. Installing dbt-snowflake..."
    pip install dbt-snowflake
fi

# Create project directory
mkdir -p ~/mercurios_dbt
cd ~/mercurios_dbt

# Initialize dbt project
echo "Creating dbt project..."
dbt init mercurios

# Move into the project directory
cd mercurios

# Create profiles.yml template
mkdir -p ~/.dbt
cat > ~/.dbt/profiles.yml << EOF
mercurios:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: VRXDFZX-ZZ95717
      user: JULIUSRECHENBACH
      password: "{{ env_var('DBT_PASSWORD') }}"
      role: MERCURIOS_FIVETRAN_SERVICE
      database: MERCURIOS_DATA
      warehouse: COMPUTE_WH
      schema: dbt_dev
      threads: 4
      client_session_keep_alive: False
EOF

echo "Created profiles.yml template at ~/.dbt/profiles.yml"

# Create project structure
mkdir -p models/staging/stg_prohandel
mkdir -p models/staging/stg_ga4
mkdir -p models/staging/stg_klaviyo
mkdir -p models/intermediate/int_inventory
mkdir -p models/intermediate/int_sales
mkdir -p models/intermediate/int_customers
mkdir -p models/marts/inventory
mkdir -p models/marts/sales
mkdir -p models/marts/customers
mkdir -p macros
mkdir -p tests
mkdir -p seeds

# Create example models
cat > models/staging/stg_prohandel/stg_prohandel__articles.sql << EOF
SELECT 
    id as article_id,
    name as article_name,
    price,
    category,
    created_at,
    updated_at
FROM 
    {{ source('raw', 'articles') }}
EOF

cat > models/staging/stg_ga4/stg_ga4__events.sql << EOF
SELECT 
    event_date,
    event_name,
    event_params,
    user_id,
    device
FROM 
    {{ source('google_analytics_4', 'events_report') }}
EOF

cat > models/intermediate/int_inventory/int_inventory__current_stock.sql << EOF
WITH current_stock AS (
    SELECT 
        article_id,
        article_name,
        SUM(quantity) as current_stock
    FROM 
        {{ ref('stg_prohandel__inventory') }}
    GROUP BY 
        article_id,
        article_name
)

SELECT 
    cs.article_id,
    cs.article_name,
    cs.current_stock,
    a.price,
    a.category
FROM 
    current_stock cs
LEFT JOIN 
    {{ ref('stg_prohandel__articles') }} a
ON 
    cs.article_id = a.article_id
EOF

cat > models/marts/inventory/inventory_status.sql << EOF
WITH current_stock AS (
    SELECT * FROM {{ ref('int_inventory__current_stock') }}
),

sales_velocity AS (
    SELECT 
        article_id,
        AVG(quantity) as avg_daily_sales
    FROM {{ ref('int_sales__daily') }}
    WHERE date >= DATEADD(day, -30, CURRENT_DATE())
    GROUP BY article_id
)

SELECT
    cs.article_id,
    cs.article_name,
    cs.current_stock,
    cs.price,
    cs.category,
    sv.avg_daily_sales,
    CASE 
        WHEN cs.current_stock <= 0 THEN 'Out of stock'
        WHEN cs.current_stock <= 10 THEN 'Low stock'
        ELSE 'In stock'
    END as stock_status,
    CASE
        WHEN sv.avg_daily_sales > 0 THEN FLOOR(cs.current_stock / sv.avg_daily_sales)
        ELSE 999
    END as days_of_inventory
FROM current_stock cs
LEFT JOIN sales_velocity sv ON cs.article_id = sv.article_id
EOF

# Create sources.yml
cat > models/staging/sources.yml << EOF
version: 2

sources:
  - name: raw
    database: MERCURIOS_DATA
    schema: RAW
    tables:
      - name: articles
      - name: customers
      - name: orders
      - name: sales
      - name: inventory

  - name: google_analytics_4
    database: MERCURIOS_DATA
    schema: GOOGLE_ANALYTICS_4
    tables:
      - name: events_report
      - name: event_params_report
      - name: audiences_report

  - name: klaviyo
    database: MERCURIOS_DATA
    schema: KLAVIYO
    tables:
      - name: klaviyo__persons
      - name: klaviyo__events
      - name: klaviyo__campaigns
EOF

# Create dbt_project.yml
cat > dbt_project.yml << EOF
name: 'mercurios'
version: '1.0.0'
config-version: 2

profile: 'mercurios'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  mercurios:
    staging:
      +materialized: view
      stg_prohandel:
        +schema: staging
      stg_ga4:
        +schema: staging
      stg_klaviyo:
        +schema: staging
    intermediate:
      +materialized: table
      +schema: intermediate
    marts:
      +materialized: table
      +schema: analytics
EOF

echo "dbt project initialized at ~/mercurios_dbt/mercurios"
echo "To test the connection, run: cd ~/mercurios_dbt/mercurios && DBT_PASSWORD=your_password dbt debug"
echo "To run the models, run: cd ~/mercurios_dbt/mercurios && DBT_PASSWORD=your_password dbt run"
