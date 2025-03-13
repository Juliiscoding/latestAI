

with inventory_metrics as (
    select * from "dbt_mercurios_dev"."main_intermediate"."int_inventory_with_metrics"
),

inventory_status as (
    select
        -- Primary keys and identifiers
        inventory_id,
        article_id,
        warehouse_id,
        article_number,
        
        -- Article details
        description,
        category,
        subcategory,
        brand,
        supplier,
        price_tier,
        
        -- Inventory metrics
        quantity,
        stock_level,
        needs_reorder,
        days_of_supply_30d,
        days_of_supply_90d,
        turnover_rate_30d,
        turnover_rate_90d,
        stockout_risk,
        
        -- Sales metrics
        quantity_sold_30d,
        quantity_sold_90d,
        num_orders_30d,
        num_orders_90d,
        
        -- Financial metrics
        purchase_price,
        retail_price,
        profit_margin,
        profit_margin_percent,
        inventory_value,
        potential_revenue,
        
        -- Flags
        is_excess_inventory,
        is_slow_moving,
        
        -- Calculated fields
        case
            when stockout_risk = 'Stockout' then 1
            when stockout_risk = 'Critical' then 2
            when stockout_risk = 'Warning' then 3
            else 4
        end as stockout_risk_priority,
        
        case
            when is_excess_inventory then inventory_value else 0
        end as excess_inventory_value,
        
        case
            when is_slow_moving then inventory_value else 0
        end as slow_moving_value,
        
        -- Reorder quantity recommendation
        case
            -- If no sales, recommend minimum stock
            when quantity_sold_90d = 0 then 
                greatest(5 - quantity, 0)
            -- If sales exist, calculate based on days of supply target
            when days_of_supply_90d is not null then
                greatest(
                    ceil((quantity_sold_90d / 90.0) * 30) - quantity, -- 30 days supply
                    0
                )
            else 0
        end as recommended_reorder_quantity,
        
        -- ABC Analysis (based on sales volume and value)
        case
            when quantity_sold_90d > 0 and 
                 quantity_sold_90d * retail_price >= 
                 percentile_cont(0.8) within group (order by nullif(quantity_sold_90d * retail_price, 0)) 
                 over (partition by warehouse_id) then 'A'
            when quantity_sold_90d > 0 and 
                 quantity_sold_90d * retail_price >= 
                 percentile_cont(0.5) within group (order by nullif(quantity_sold_90d * retail_price, 0)) 
                 over (partition by warehouse_id) then 'B'
            when quantity_sold_90d > 0 then 'C'
            else 'D' -- No sales
        end as abc_class,
        
        -- Last update timestamp
        _fivetran_synced as last_updated,
        
        -- Add tenant_id
        tenant_id
    from inventory_metrics
)

select * from inventory_status