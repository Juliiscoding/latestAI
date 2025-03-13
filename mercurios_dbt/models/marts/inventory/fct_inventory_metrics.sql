with inventory_with_sales as (
    select * from {{ ref('int_inventory_with_sales') }}
),

sales_analysis as (
    select * from {{ ref('int_sales_analysis') }}
),

-- Join inventory with sales analysis to get sales velocity
inventory_with_velocity as (
    select
        i.*,
        s.daily_sales_rate,
        s.monthly_sales_frequency,
        s.sales_velocity_category,
        
        -- Calculate days of supply based on sales rate
        case
            when s.daily_sales_rate is null or s.daily_sales_rate = 0 then null
            else i.stock_quantity / s.daily_sales_rate
        end as days_of_supply,
        
        -- Calculate reorder point based on sales velocity and lead time
        -- Assuming 14 days lead time and 7 days safety stock
        case
            when s.daily_sales_rate is null or s.daily_sales_rate = 0 then 5 -- Default for new items
            else ceiling(s.daily_sales_rate * (14 + 7))
        end as recommended_reorder_point,
        
        -- Calculate recommended order quantity (EOQ simplified)
        -- Assuming 4 weeks of supply or minimum 10 units
        case
            when s.daily_sales_rate is null or s.daily_sales_rate = 0 then 10 -- Default for new items
            else greatest(10, ceiling(s.daily_sales_rate * 28))
        end as recommended_order_quantity,
        
        -- Determine if reorder is needed
        case
            when i.stock_quantity <= 
                case
                    when s.daily_sales_rate is null or s.daily_sales_rate = 0 then 5
                    else ceiling(s.daily_sales_rate * (14 + 7))
                end
            then true
            else false
        end as needs_reorder,
        
        -- Determine stock status based on days of supply
        case
            when s.daily_sales_rate is null or s.daily_sales_rate = 0 then 'Unknown'
            when i.stock_quantity / s.daily_sales_rate <= 7 then 'Critical'
            when i.stock_quantity / s.daily_sales_rate <= 14 then 'Low'
            when i.stock_quantity / s.daily_sales_rate <= 30 then 'Medium'
            when i.stock_quantity / s.daily_sales_rate <= 60 then 'Good'
            else 'Excess'
        end as supply_status
        
    from inventory_with_sales i
    left join sales_analysis s 
        on i.article_id = s.article_id 
        and i.tenant_id = s.tenant_id
)

select * from inventory_with_velocity
