with inventory as (
    select * from {{ ref('stg_prohandel__inventory') }}
),

articles as (
    select * from {{ ref('stg_prohandel__articles') }}
),

sales_last_30_days as (
    select
        article_id,
        sum(quantity) as quantity_sold_30d,
        count(distinct sale_id) as num_orders_30d
    from {{ ref('stg_prohandel__sales') }}
    where sale_date >= dateadd('day', -30, current_date())
    group by article_id
),

sales_last_90_days as (
    select
        article_id,
        sum(quantity) as quantity_sold_90d,
        count(distinct sale_id) as num_orders_90d
    from {{ ref('stg_prohandel__sales') }}
    where sale_date >= dateadd('day', -90, current_date())
    group by article_id
),

inventory_with_metrics as (
    select
        -- Inventory fields
        i.inventory_id,
        i.article_id,
        i.warehouse_id,
        i.quantity,
        i.stock_level,
        i.needs_reorder,
        i.location,
        i.last_count_date,
        i.is_available,
        i.tenant_id,
        
        -- Article fields
        a.article_number,
        a.description,
        a.category,
        a.subcategory,
        a.brand,
        a.supplier,
        a.purchase_price,
        a.retail_price,
        a.min_stock_level,
        a.max_stock_level,
        a.reorder_point,
        a.lead_time_days,
        a.profit_margin,
        a.profit_margin_percent,
        a.price_tier,
        
        -- Sales metrics
        coalesce(s30.quantity_sold_30d, 0) as quantity_sold_30d,
        coalesce(s30.num_orders_30d, 0) as num_orders_30d,
        coalesce(s90.quantity_sold_90d, 0) as quantity_sold_90d,
        coalesce(s90.num_orders_90d, 0) as num_orders_90d,
        
        -- Calculate days of supply
        case
            when coalesce(s30.quantity_sold_30d, 0) > 0 then 
                (i.quantity / (s30.quantity_sold_30d / 30.0))
            else null
        end as days_of_supply_30d,
        
        case
            when coalesce(s90.quantity_sold_90d, 0) > 0 then 
                (i.quantity / (s90.quantity_sold_90d / 90.0))
            else null
        end as days_of_supply_90d,
        
        -- Calculate stock turnover rate (annualized)
        case
            when i.quantity > 0 and coalesce(s30.quantity_sold_30d, 0) > 0 then 
                (s30.quantity_sold_30d * (365.0 / 30.0)) / i.quantity
            else null
        end as turnover_rate_30d,
        
        case
            when i.quantity > 0 and coalesce(s90.quantity_sold_90d, 0) > 0 then 
                (s90.quantity_sold_90d * (365.0 / 90.0)) / i.quantity
            else null
        end as turnover_rate_90d,
        
        -- Calculate inventory value
        i.quantity * a.purchase_price as inventory_value,
        i.quantity * a.retail_price as potential_revenue,
        
        -- Calculate excess inventory flag
        case
            when coalesce(s90.quantity_sold_90d, 0) = 0 and i.quantity > 10 then true
            when coalesce(s90.quantity_sold_90d, 0) > 0 and 
                 (i.quantity / (s90.quantity_sold_90d / 90.0)) > 180 then true
            else false
        end as is_excess_inventory,
        
        -- Calculate slow-moving inventory flag
        case
            when coalesce(s90.quantity_sold_90d, 0) = 0 and i.quantity > 0 then true
            when coalesce(s90.quantity_sold_90d, 0) > 0 and 
                 (s90.quantity_sold_90d * (365.0 / 90.0)) / i.quantity < 1 then true
            else false
        end as is_slow_moving,
        
        -- Calculate stockout risk flag
        case
            when i.quantity = 0 then 'Stockout'
            when coalesce(s30.quantity_sold_30d, 0) > 0 and 
                 (i.quantity / (s30.quantity_sold_30d / 30.0)) < 7 then 'Critical'
            when coalesce(s30.quantity_sold_30d, 0) > 0 and 
                 (i.quantity / (s30.quantity_sold_30d / 30.0)) < 14 then 'Warning'
            else 'Normal'
        end as stockout_risk,
        
        -- Fivetran metadata
        i._fivetran_synced
    from inventory i
    left join articles a on i.article_id = a.article_id
    left join sales_last_30_days s30 on i.article_id = s30.article_id
    left join sales_last_90_days s90 on i.article_id = s90.article_id
)

select * from inventory_with_metrics
