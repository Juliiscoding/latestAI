with customer_behavior as (
    select *
    from {{ ref('int_customer_behavior_combined') }}
),

-- Calculate customer insights and segmentation
customer_insights as (
    select
        -- Customer identifiers
        customer_id,
        customer_name,
        email,
        city,
        region,
        country,
        customer_type,
        customer_since,
        customer_age,
        
        -- Order metrics
        order_count,
        first_order_date,
        last_order_date,
        total_order_amount,
        avg_order_value,
        
        -- Purchase metrics
        unique_articles_purchased,
        total_quantity_purchased,
        total_sales_amount,
        
        -- Calculated metrics
        days_between_orders,
        customer_status,
        
        -- Online regional metrics
        regional_online_users,
        regional_new_users,
        regional_online_revenue,
        regional_online_transactions,
        predominant_acquisition_channel,
        
        -- Segmentation
        offline_value_segment,
        purchase_frequency_segment,
        rfm_score,
        rfm_segment,
        
        -- Calculate additional insights
        datediff('day', customer_since, current_date()) as customer_tenure_days,
        
        case
            when customer_status = 'Active' and rfm_segment in ('Champions', 'Loyal Customers') then 'Retain'
            when customer_status = 'Active' and rfm_segment = 'Potential Loyalists' then 'Nurture'
            when customer_status = 'At Risk' then 'Reactivate'
            when customer_status in ('Lapsed', 'Inactive') then 'Win Back'
            else 'Monitor'
        end as customer_strategy,
        
        -- Purchase behavior insights
        case
            when unique_articles_purchased > 10 then 'Diverse Buyer'
            when unique_articles_purchased > 5 then 'Moderate Variety'
            when unique_articles_purchased > 1 then 'Limited Variety'
            else 'Single Product'
        end as purchase_variety,
        
        case
            when avg_order_value > 500 then 'High Basket'
            when avg_order_value > 200 then 'Medium Basket'
            when avg_order_value > 50 then 'Low Basket'
            else 'Micro Basket'
        end as basket_size_segment,
        
        -- Engagement potential based on regional online behavior
        case
            when regional_online_users > 0 and regional_online_transactions > 0 
            then regional_online_transactions / regional_online_users
            else 0
        end as regional_conversion_rate,
        
        case
            when predominant_acquisition_channel = 'Organic Search' then 'SEO Opportunity'
            when predominant_acquisition_channel = 'Paid Search' then 'SEM Opportunity'
            when predominant_acquisition_channel = 'Social Media' then 'Social Opportunity'
            when predominant_acquisition_channel = 'Email Marketing' then 'Email Opportunity'
            else 'General Marketing'
        end as marketing_channel_opportunity,
        
        -- Omnichannel potential
        case
            when customer_status = 'Active' and regional_online_users > 0 and regional_online_transactions = 0 
            then 'High Online Potential'
            when customer_status in ('At Risk', 'Lapsed') and regional_online_transactions > 0 
            then 'Online Reactivation Potential'
            when customer_status = 'Active' and regional_online_transactions > 0 
            then 'Omnichannel Engaged'
            else 'Standard Approach'
        end as omnichannel_potential,
        
        -- Lifetime value prediction
        case
            when rfm_segment in ('Champions', 'Loyal Customers') 
            then total_order_amount * 2
            when rfm_segment = 'Potential Loyalists' 
            then total_order_amount * 1.5
            when rfm_segment = 'At Risk Customers' 
            then total_order_amount * 1.2
            else total_order_amount
        end as predicted_lifetime_value,
        
        -- Add metadata fields
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from customer_behavior
)

select * from customer_insights
