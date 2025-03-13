with product_insights as (
    select *
    from {{ ref('fct_product_insights') }}
),

customer_insights as (
    select *
    from {{ ref('fct_customer_insights') }}
),

inventory_data as (
    select *
    from {{ ref('stg_inventory') }}
),

sales_history as (
    select
        article_id,
        sale_date,
        sum(quantity) as daily_quantity_sold,
        count(distinct order_id) as daily_orders,
        count(distinct customer_id) as daily_customers
    from {{ ref('stg_sales') }}
    group by 1, 2
),

-- Calculate historical sales velocity
sales_velocity as (
    select
        article_id,
        avg(daily_quantity_sold) as avg_daily_sales,
        percentile_cont(0.5) within group (order by daily_quantity_sold) as median_daily_sales,
        percentile_cont(0.9) within group (order by daily_quantity_sold) as p90_daily_sales,
        stddev(daily_quantity_sold) as stddev_daily_sales,
        count(distinct sale_date) as days_with_sales,
        min(sale_date) as first_sale_date,
        max(sale_date) as last_sale_date
    from sales_history
    group by 1
),

-- Get GA4 online product interest data
online_interest as (
    select
        article_id,
        article_number,
        page_views,
        online_users,
        engagement_rate,
        online_conversion_rate,
        online_quantity_sold,
        online_revenue
    from product_insights
),

-- Calculate regional customer distribution
regional_distribution as (
    select
        region,
        country,
        count(distinct customer_id) as customer_count,
        sum(total_order_amount) as region_total_sales,
        avg(avg_order_value) as region_avg_order_value
    from customer_insights
    group by 1, 2
),

-- Calculate inventory forecast
inventory_forecast as (
    select
        -- Product identifiers
        p.article_id,
        p.article_name,
        p.article_number,
        p.brand,
        p.category,
        p.subcategory,
        
        -- Current inventory status
        p.total_inventory,
        p.inventory_status,
        p.months_of_inventory,
        
        -- Historical sales metrics
        v.avg_daily_sales,
        v.median_daily_sales,
        v.p90_daily_sales,
        v.stddev_daily_sales,
        v.days_with_sales,
        
        -- Online interest metrics
        o.page_views,
        o.online_users,
        o.engagement_rate,
        o.online_conversion_rate,
        
        -- Combined sales channel metrics
        p.total_quantity_sold as offline_quantity_sold,
        o.online_quantity_sold,
        p.combined_quantity as total_quantity_sold,
        p.channel_preference,
        p.sales_channel_distribution,
        
        -- Calculate forecast parameters
        case
            -- Adjust forecast based on online interest trends
            when o.page_views > 100 and o.online_conversion_rate > 0.03 and v.avg_daily_sales > 0
            then v.avg_daily_sales * 1.2  -- Increase forecast for high online interest
            
            when o.page_views > 50 and o.online_conversion_rate > 0.02 and v.avg_daily_sales > 0
            then v.avg_daily_sales * 1.1  -- Slight increase for moderate online interest
            
            when o.page_views < 10 and v.avg_daily_sales > 0
            then v.avg_daily_sales * 0.9  -- Decrease forecast for low online interest
            
            when v.avg_daily_sales > 0
            then v.avg_daily_sales  -- Use historical average as baseline
            
            -- For new products with no sales history but online interest
            when v.avg_daily_sales = 0 and o.page_views > 20
            then 0.5  -- Conservative estimate for new products with interest
            
            else 0.1  -- Minimal forecast for products with no history or interest
        end as adjusted_daily_sales_forecast,
        
        -- Calculate safety stock based on sales variability and lead time
        -- Assuming 7 days lead time for replenishment
        case
            when v.stddev_daily_sales > 0
            then v.stddev_daily_sales * sqrt(7) * 1.65  -- 95% service level
            else 
                case
                    when v.avg_daily_sales > 1 then v.avg_daily_sales * 0.5 * sqrt(7)
                    else 1
                end
        end as safety_stock,
        
        -- Calculate reorder point
        case
            when v.avg_daily_sales > 0
            then (v.avg_daily_sales * 7) + (v.stddev_daily_sales * sqrt(7) * 1.65)
            else 
                case
                    when o.page_views > 20 then 5
                    else 2
                end
        end as reorder_point,
        
        -- Calculate optimal order quantity (Economic Order Quantity simplified)
        case
            when v.avg_daily_sales > 0
            then sqrt(2 * 365 * v.avg_daily_sales * 10 / (0.2 * p.total_sales_amount / p.total_quantity_sold))
            else 
                case
                    when o.page_views > 20 then 10
                    else 5
                end
        end as economic_order_quantity,
        
        -- Forecast for next 30/60/90 days
        case
            when v.avg_daily_sales > 0 or o.page_views > 0
            then 
                case
                    -- Adjust forecast based on online interest trends
                    when o.page_views > 100 and o.online_conversion_rate > 0.03 and v.avg_daily_sales > 0
                    then v.avg_daily_sales * 1.2 * 30  -- Increase forecast for high online interest
                    
                    when o.page_views > 50 and o.online_conversion_rate > 0.02 and v.avg_daily_sales > 0
                    then v.avg_daily_sales * 1.1 * 30  -- Slight increase for moderate online interest
                    
                    when o.page_views < 10 and v.avg_daily_sales > 0
                    then v.avg_daily_sales * 0.9 * 30  -- Decrease forecast for low online interest
                    
                    when v.avg_daily_sales > 0
                    then v.avg_daily_sales * 30  -- Use historical average as baseline
                    
                    -- For new products with no sales history but online interest
                    when v.avg_daily_sales = 0 and o.page_views > 20
                    then 0.5 * 30  -- Conservative estimate for new products with interest
                    
                    else 0.1 * 30  -- Minimal forecast for products with no history or interest
                end
            else 0
        end as forecast_30_days,
        
        case
            when v.avg_daily_sales > 0 or o.page_views > 0
            then 
                case
                    -- Adjust forecast based on online interest trends
                    when o.page_views > 100 and o.online_conversion_rate > 0.03 and v.avg_daily_sales > 0
                    then v.avg_daily_sales * 1.2 * 60  -- Increase forecast for high online interest
                    
                    when o.page_views > 50 and o.online_conversion_rate > 0.02 and v.avg_daily_sales > 0
                    then v.avg_daily_sales * 1.1 * 60  -- Slight increase for moderate online interest
                    
                    when o.page_views < 10 and v.avg_daily_sales > 0
                    then v.avg_daily_sales * 0.9 * 60  -- Decrease forecast for low online interest
                    
                    when v.avg_daily_sales > 0
                    then v.avg_daily_sales * 60  -- Use historical average as baseline
                    
                    -- For new products with no sales history but online interest
                    when v.avg_daily_sales = 0 and o.page_views > 20
                    then 0.5 * 60  -- Conservative estimate for new products with interest
                    
                    else 0.1 * 60  -- Minimal forecast for products with no history or interest
                end
            else 0
        end as forecast_60_days,
        
        case
            when v.avg_daily_sales > 0 or o.page_views > 0
            then 
                case
                    -- Adjust forecast based on online interest trends
                    when o.page_views > 100 and o.online_conversion_rate > 0.03 and v.avg_daily_sales > 0
                    then v.avg_daily_sales * 1.2 * 90  -- Increase forecast for high online interest
                    
                    when o.page_views > 50 and o.online_conversion_rate > 0.02 and v.avg_daily_sales > 0
                    then v.avg_daily_sales * 1.1 * 90  -- Slight increase for moderate online interest
                    
                    when o.page_views < 10 and v.avg_daily_sales > 0
                    then v.avg_daily_sales * 0.9 * 90  -- Decrease forecast for low online interest
                    
                    when v.avg_daily_sales > 0
                    then v.avg_daily_sales * 90  -- Use historical average as baseline
                    
                    -- For new products with no sales history but online interest
                    when v.avg_daily_sales = 0 and o.page_views > 20
                    then 0.5 * 90  -- Conservative estimate for new products with interest
                    
                    else 0.1 * 90  -- Minimal forecast for products with no history or interest
                end
            else 0
        end as forecast_90_days,
        
        -- Inventory action recommendation
        case
            when p.total_inventory <= 0 and (v.avg_daily_sales > 0 or o.page_views > 20)
            then 'Restock Immediately'
            
            when p.total_inventory < 
                case
                    when v.avg_daily_sales > 0
                    then (v.avg_daily_sales * 7) + (v.stddev_daily_sales * sqrt(7) * 1.65)
                    else 
                        case
                            when o.page_views > 20 then 5
                            else 2
                        end
                end
            then 'Restock Soon'
            
            when p.total_inventory > 
                case
                    when v.avg_daily_sales > 0
                    then v.avg_daily_sales * 90 * 1.5
                    else 10
                end
            then 'Overstocked'
            
            when p.inventory_status = 'Healthy Stock'
            then 'Maintain'
            
            else 'Monitor'
        end as inventory_action,
        
        -- Confidence level in forecast
        case
            when v.days_with_sales > 60 and v.stddev_daily_sales / nullif(v.avg_daily_sales, 0) < 0.5
            then 'High'
            
            when v.days_with_sales > 30 or (o.page_views > 50 and o.online_conversion_rate > 0)
            then 'Medium'
            
            when v.days_with_sales > 0 or o.page_views > 0
            then 'Low'
            
            else 'Very Low'
        end as forecast_confidence,
        
        -- Add metadata fields
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from product_insights p
    left join sales_velocity v
        on p.article_id = v.article_id
    left join online_interest o
        on p.article_id = o.article_id
)

select * from inventory_forecast
