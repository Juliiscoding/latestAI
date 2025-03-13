with inventory_metrics as (
    select * from {{ ref('fct_inventory_metrics') }}
),

sales_metrics as (
    select * from {{ ref('fct_sales_metrics') }}
),

-- Create a forecast model for inventory management
final as (
    select
        i.article_id,
        i.tenant_id,
        i.warehouse_id,
        i.article_name,
        i.category,
        i.stock_quantity,
        i.stock_status,
        i.retail_price,
        i.wholesale_cost,
        i.inventory_cost_value,
        i.inventory_retail_value,
        
        -- Sales velocity metrics
        i.total_quantity_sold,
        i.total_revenue,
        i.daily_sales_rate,
        i.days_of_supply,
        i.inventory_velocity,
        
        -- Reorder metrics
        i.recommended_reorder_point,
        i.recommended_order_quantity,
        i.needs_reorder,
        i.supply_status,
        
        -- Forecast next 30 days
        ceiling(i.daily_sales_rate * 30) as forecasted_30_day_demand,
        
        -- Forecast next 60 days
        ceiling(i.daily_sales_rate * 60) as forecasted_60_day_demand,
        
        -- Forecast next 90 days
        ceiling(i.daily_sales_rate * 90) as forecasted_90_day_demand,
        
        -- Calculate inventory coverage
        case
            when i.daily_sales_rate = 0 or i.daily_sales_rate is null then 'Infinite'
            when i.stock_quantity / i.daily_sales_rate > 90 then '> 90 days'
            when i.stock_quantity / i.daily_sales_rate > 60 then '61-90 days'
            when i.stock_quantity / i.daily_sales_rate > 30 then '31-60 days'
            when i.stock_quantity / i.daily_sales_rate > 14 then '15-30 days'
            when i.stock_quantity / i.daily_sales_rate > 7 then '8-14 days'
            else '< 7 days'
        end as inventory_coverage,
        
        -- Stockout risk
        case
            when i.daily_sales_rate = 0 or i.daily_sales_rate is null then 'Unknown'
            when i.stock_quantity / i.daily_sales_rate < 7 then 'High Risk'
            when i.stock_quantity / i.daily_sales_rate < 14 then 'Medium Risk'
            when i.stock_quantity / i.daily_sales_rate < 30 then 'Low Risk'
            else 'Very Low Risk'
        end as stockout_risk,
        
        -- Excess inventory risk
        case
            when i.daily_sales_rate = 0 or i.daily_sales_rate is null then 'Unknown'
            when i.stock_quantity / i.daily_sales_rate > 180 then 'High Risk'
            when i.stock_quantity / i.daily_sales_rate > 90 then 'Medium Risk'
            when i.stock_quantity / i.daily_sales_rate > 60 then 'Low Risk'
            else 'Optimal'
        end as excess_inventory_risk,
        
        -- Calculate optimal order quantity
        case
            when i.daily_sales_rate = 0 or i.daily_sales_rate is null then 10 -- Default for items with no sales history
            when i.stock_quantity <= i.recommended_reorder_point then 
                greatest(10, ceiling(i.daily_sales_rate * 30)) -- 30 days of supply
            else 0 -- No order needed
        end as optimal_order_quantity,
        
        -- Calculate optimal reorder date
        case
            when i.daily_sales_rate = 0 or i.daily_sales_rate is null then 'Unknown'
            when i.stock_quantity <= i.recommended_reorder_point then 'Order Now'
            else dateadd('day', 
                     floor((i.stock_quantity - i.recommended_reorder_point) / i.daily_sales_rate), 
                     current_date())::string
        end as optimal_reorder_date,
        
        -- Metadata
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from inventory_metrics i
    left join sales_metrics s on i.article_id = s.article_id and i.tenant_id = s.tenant_id
)

select * from final
