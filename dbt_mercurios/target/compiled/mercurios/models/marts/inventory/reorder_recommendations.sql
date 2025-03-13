

with inventory_status as (
    select * from "dbt_mercurios_dev"."main_marts_inventory"."inventory_status"
),

-- Get historical sales velocity
sales_velocity as (
    select
        s.article_id,
        -- Calculate average daily sales for different time periods
        sum(s.quantity) / 30.0 as daily_sales_30d,
        sum(s.quantity) / 90.0 as daily_sales_90d,
        -- Calculate standard deviation of daily sales for safety stock
        stddev(daily_qty) as daily_sales_stddev
    from (
        select
            article_id,
            sale_date,
            sum(quantity) as daily_qty
        from "dbt_mercurios_dev"."main_staging"."stg_prohandel__sales"
        where sale_date >= dateadd('day', -90, current_date())
        group by article_id, sale_date
    ) s
    group by s.article_id
),

-- Calculate reorder points and quantities
reorder_calc as (
    select
        i.inventory_id,
        i.article_id,
        i.warehouse_id,
        i.article_number,
        i.description,
        i.category,
        i.subcategory,
        i.brand,
        i.supplier,
        i.quantity as current_quantity,
        i.stock_level,
        i.stockout_risk,
        i.purchase_price,
        i.retail_price,
        i.inventory_value,
        i.abc_class,
        i.tenant_id,
        
        -- Sales metrics
        i.quantity_sold_30d,
        i.quantity_sold_90d,
        coalesce(sv.daily_sales_30d, 0) as daily_sales_30d,
        coalesce(sv.daily_sales_90d, 0) as daily_sales_90d,
        coalesce(sv.daily_sales_stddev, 0) as daily_sales_stddev,
        
        -- Use lead_time_days from article if available
        coalesce(i.lead_time_days, 
            case
                when i.abc_class = 'A' then 7  -- Priority items get faster shipping
                when i.abc_class = 'B' then 10
                when i.abc_class = 'C' then 14
                else 14
            end
        ) as lead_time_days,
        
        -- Service level factor (z-score) based on ABC classification
        case
            when i.abc_class = 'A' then 2.33  -- 99% service level
            when i.abc_class = 'B' then 1.65  -- 95% service level
            when i.abc_class = 'C' then 1.28  -- 90% service level
            else 1.28
        end as service_level_factor,
        
        -- Calculate reorder point components
        coalesce(sv.daily_sales_90d, 0) * 
            coalesce(i.lead_time_days, 
                case
                    when i.abc_class = 'A' then 7
                    when i.abc_class = 'B' then 10
                    when i.abc_class = 'C' then 14
                    else 14
                end
            ) as lead_time_demand,
            
        coalesce(sv.daily_sales_stddev, 0) * 
            case
                when i.abc_class = 'A' then 2.33
                when i.abc_class = 'B' then 1.65
                when i.abc_class = 'C' then 1.28
                else 1.28
            end * sqrt(
                coalesce(i.lead_time_days, 
                    case
                        when i.abc_class = 'A' then 7
                        when i.abc_class = 'B' then 10
                        when i.abc_class = 'C' then 14
                        else 14
                    end
                )
            ) as safety_stock,
        
        -- Economic Order Quantity (EOQ) calculation
        -- Assuming ordering cost of $20 per order and holding cost of 25% of item value per year
        case
            when coalesce(sv.daily_sales_90d, 0) > 0 and i.purchase_price > 0 then
                sqrt(
                    (2 * 20 * coalesce(sv.daily_sales_90d, 0) * 365) / 
                    (0.25 * i.purchase_price)
                )
            else null
        end as economic_order_quantity
        
    from inventory_status i
    left join sales_velocity sv on i.article_id = sv.article_id
),

-- Generate final recommendations
reorder_recommendations as (
    select
        inventory_id,
        article_id,
        warehouse_id,
        article_number,
        description,
        category,
        subcategory,
        brand,
        supplier,
        current_quantity,
        stock_level,
        stockout_risk,
        purchase_price,
        retail_price,
        inventory_value,
        abc_class,
        tenant_id,
        
        -- Sales metrics
        quantity_sold_30d,
        quantity_sold_90d,
        daily_sales_30d,
        daily_sales_90d,
        
        -- Reorder calculations
        lead_time_days,
        round(lead_time_demand, 2) as lead_time_demand,
        round(safety_stock, 2) as safety_stock,
        
        -- Calculate reorder point
        round(lead_time_demand + safety_stock, 0) as reorder_point,
        
        -- Calculate if reorder is needed
        case
            when current_quantity <= (lead_time_demand + safety_stock) then true
            else false
        end as needs_reorder,
        
        -- Calculate reorder quantity
        case
            when current_quantity <= (lead_time_demand + safety_stock) then
                case
                    -- Use EOQ if available and reasonable
                    when economic_order_quantity is not null and 
                         economic_order_quantity >= (lead_time_demand + safety_stock - current_quantity) then
                        ceil(greatest(economic_order_quantity, 1))
                    -- Otherwise use lead time demand plus safety stock minus current quantity
                    else
                        ceil(greatest(lead_time_demand + safety_stock - current_quantity, 1))
                end
            else 0
        end as recommended_order_quantity,
        
        -- Calculate order cost
        case
            when current_quantity <= (lead_time_demand + safety_stock) then
                case
                    when economic_order_quantity is not null and 
                         economic_order_quantity >= (lead_time_demand + safety_stock - current_quantity) then
                        ceil(greatest(economic_order_quantity, 1)) * purchase_price
                    else
                        ceil(greatest(lead_time_demand + safety_stock - current_quantity, 1)) * purchase_price
                end
            else 0
        end as order_cost,
        
        -- Calculate days until stockout
        case
            when daily_sales_90d > 0 then
                round(current_quantity / daily_sales_90d, 0)
            else
                999  -- Arbitrary large number for items with no sales
        end as days_until_stockout,
        
        -- Calculate priority
        case
            when current_quantity <= 0 then 1  -- Already out of stock
            when current_quantity <= safety_stock then 2  -- Below safety stock
            when current_quantity <= (lead_time_demand + safety_stock) then 3  -- Below reorder point
            else 4  -- Above reorder point
        end as priority,
        
        -- Calculate priority label
        case
            when current_quantity <= 0 then 'Critical - Out of Stock'
            when current_quantity <= safety_stock then 'High - Below Safety Stock'
            when current_quantity <= (lead_time_demand + safety_stock) then 'Medium - Below Reorder Point'
            else 'Low - Stock Adequate'
        end as priority_label,
        
        -- Add timestamp
        current_timestamp() as generated_at
        
    from reorder_calc
)

select * from reorder_recommendations
order by priority, abc_class, order_cost desc