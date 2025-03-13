with inventory as (
    select * from {{ ref('stg_inventory') }}
),

articles as (
    select * from {{ ref('stg_articles') }}
),

sales as (
    select * from {{ ref('stg_sales') }}
),

-- Calculate sales metrics per article
sales_metrics as (
    select
        article_id,
        tenant_id,
        sum(sold_quantity) as total_quantity_sold,
        sum(total_sale_amount) as total_revenue,
        avg(unit_price) as average_selling_price,
        count(distinct sale_id) as number_of_sales,
        max(sale_date) as last_sale_date,
        datediff('day', max(sale_date), current_date()) as days_since_last_sale
    from sales
    group by 1, 2
),

-- Join inventory with articles and sales metrics
final as (
    select
        i.article_id,
        i.tenant_id,
        i.warehouse_id,
        i.stock_quantity,
        i.stock_status,
        i.updated_at as inventory_updated_at,
        
        -- Article information
        a.article_name,
        a.description,
        a.retail_price,
        a.wholesale_cost,
        a.category,
        a.supplier_id,
        a.gross_profit,
        a.margin_percent,
        a.price_tier,
        
        -- Sales metrics
        coalesce(s.total_quantity_sold, 0) as total_quantity_sold,
        coalesce(s.total_revenue, 0) as total_revenue,
        s.average_selling_price,
        coalesce(s.number_of_sales, 0) as number_of_sales,
        s.last_sale_date,
        s.days_since_last_sale,
        
        -- Inventory metrics
        case
            when s.total_quantity_sold is null then 'No Sales'
            when s.days_since_last_sale > 90 then 'Slow Moving'
            when s.days_since_last_sale > 30 then 'Medium Moving'
            else 'Fast Moving'
        end as inventory_velocity,
        
        -- Inventory value
        i.stock_quantity * a.wholesale_cost as inventory_cost_value,
        i.stock_quantity * a.retail_price as inventory_retail_value,
        
        -- Metadata
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from inventory i
    left join articles a on i.article_id = a.article_id and i.tenant_id = a.tenant_id
    left join sales_metrics s on i.article_id = s.article_id and i.tenant_id = s.tenant_id
)

select * from final
