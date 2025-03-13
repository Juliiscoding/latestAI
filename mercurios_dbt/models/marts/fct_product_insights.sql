with product_performance as (
    select *
    from {{ ref('int_product_performance_combined') }}
),

-- Calculate product performance metrics and insights
product_insights as (
    select
        -- Product identifiers
        article_id,
        article_name,
        article_number,
        brand,
        category,
        subcategory,
        price_tier,
        
        -- Inventory metrics
        total_inventory,
        avg_inventory,
        warehouse_count,
        
        -- Sales metrics
        total_quantity_sold,
        total_sales_amount,
        order_count,
        customer_count,
        
        -- Online metrics
        online_revenue,
        online_transactions,
        online_quantity_sold,
        page_views,
        online_users,
        engagement_rate,
        online_conversion_rate,
        
        -- Combined metrics
        combined_revenue,
        combined_quantity,
        combined_value_category,
        combined_volume_category,
        channel_preference,
        
        -- Inventory turnover metrics
        inventory_turnover_ratio,
        days_per_unit_sold,
        
        -- Calculate additional insights
        case
            when total_inventory > 0 and total_quantity_sold > 0 
            then total_inventory / (total_quantity_sold / nullif(datediff('day', first_sale_date, greatest(last_sale_date, current_date())), 0) * 30)
            else 0
        end as months_of_inventory,
        
        case
            when total_inventory = 0 and total_quantity_sold > 0 then 'Out of Stock'
            when total_inventory < (total_quantity_sold / nullif(datediff('day', first_sale_date, greatest(last_sale_date, current_date())), 0) * 30) then 'Low Stock'
            when total_inventory > (total_quantity_sold / nullif(datediff('day', first_sale_date, greatest(last_sale_date, current_date())), 0) * 90) then 'Overstocked'
            else 'Healthy Stock'
        end as inventory_status,
        
        -- Online vs offline insights
        case
            when page_views > 0 and online_transactions = 0 then 'High Bounce Rate'
            when page_views > 0 and online_conversion_rate < 0.01 then 'Low Conversion'
            when page_views > 0 and online_conversion_rate > 0.05 then 'High Conversion'
            else 'Average Conversion'
        end as online_performance,
        
        case
            when total_quantity_sold > 0 and online_quantity_sold = 0 then 'Offline Only'
            when total_quantity_sold = 0 and online_quantity_sold > 0 then 'Online Only'
            when total_quantity_sold > online_quantity_sold * 3 then 'Primarily Offline'
            when online_quantity_sold > total_quantity_sold * 3 then 'Primarily Online'
            else 'Omnichannel'
        end as sales_channel_distribution,
        
        -- Opportunity assessment
        case
            when inventory_turnover_ratio > 3 and total_inventory < 10 then 'Restock Needed'
            when inventory_turnover_ratio < 0.5 and total_inventory > 20 then 'Consider Discount'
            when page_views > 100 and online_conversion_rate < 0.01 then 'Improve Online Conversion'
            when online_quantity_sold = 0 and page_views > 50 then 'Online Sales Opportunity'
            when total_quantity_sold = 0 and total_inventory > 10 then 'Evaluate Product Viability'
            when combined_value_category = 'High Value' and combined_volume_category = 'High Volume' then 'Star Product'
            else 'Monitor Performance'
        end as action_recommendation,
        
        -- Seasonality indicator (if data spans multiple months)
        case
            when datediff('month', first_sale_date, greatest(last_sale_date, current_date())) > 3 
            then 'Analyze for Seasonality'
            else 'Insufficient Data for Seasonality'
        end as seasonality_indicator,
        
        -- Add metadata fields
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from product_performance
)

select * from product_insights
