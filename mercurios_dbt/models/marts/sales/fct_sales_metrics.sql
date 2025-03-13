with sales_analysis as (
    select * from {{ ref('int_sales_analysis') }}
),

-- Create a comprehensive fact table for sales metrics
final as (
    select
        tenant_id,
        article_id,
        article_name,
        category,
        price_tier,
        
        -- Sales metrics
        number_of_sales,
        total_quantity_sold,
        total_revenue,
        total_profit,
        average_unit_price,
        
        -- Time metrics
        first_sale_date,
        last_sale_date,
        sales_period_days,
        
        -- Velocity metrics
        daily_sales_rate,
        monthly_sales_frequency,
        sales_velocity_category,
        
        -- Add time-based metrics
        datediff('day', last_sale_date, current_date()) as days_since_last_sale,
        
        -- Add sales trend indicators
        case
            when days_since_last_sale <= 30 then 'Active'
            when days_since_last_sale <= 90 then 'Slowing'
            else 'Inactive'
        end as sales_activity_status,
        
        -- Add profitability indicators
        case
            when total_profit <= 0 then 'Unprofitable'
            when total_profit / total_revenue < 0.1 then 'Low Margin'
            when total_profit / total_revenue < 0.3 then 'Medium Margin'
            else 'High Margin'
        end as profitability_category,
        
        -- Metadata
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from sales_analysis
)

select * from final
