with prohandel_customers as (
    select *
    from {{ ref('stg_customers') }}
),

prohandel_orders as (
    select *
    from {{ ref('stg_orders') }}
),

prohandel_sales as (
    select *
    from {{ ref('stg_sales') }}
),

ga4_user_acquisition as (
    select *
    from {{ ref('stg_ga4_user_acquisition') }}
),

-- Aggregate order data by customer
customer_orders as (
    select
        customer_id,
        count(distinct order_id) as order_count,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        sum(total_amount) as total_order_amount,
        avg(total_amount) as avg_order_value
    from prohandel_orders
    group by 1
),

-- Aggregate sales data by customer
customer_sales as (
    select
        customer_id,
        count(distinct article_id) as unique_articles_purchased,
        sum(quantity) as total_quantity_purchased,
        sum(total_price) as total_sales_amount
    from prohandel_sales
    group by 1
),

-- Extract customer location data for joining with GA4 demographic data
customer_locations as (
    select
        customer_id,
        city,
        region,
        country,
        postal_code
    from prohandel_customers
),

-- Join all data sources
combined as (
    select
        -- Customer information
        c.customer_id,
        c.customer_name,
        c.email,
        c.phone,
        c.address,
        c.city,
        c.region,
        c.country,
        c.postal_code,
        c.customer_type,
        c.customer_since,
        c.customer_age,
        
        -- Order information
        o.order_count,
        o.first_order_date,
        o.last_order_date,
        o.total_order_amount,
        o.avg_order_value,
        
        -- Sales information
        s.unique_articles_purchased,
        s.total_quantity_purchased,
        s.total_sales_amount,
        
        -- Calculate offline metrics
        case 
            when o.order_count > 0 
            then datediff('day', o.first_order_date, o.last_order_date) / o.order_count 
            else 0 
        end as days_between_orders,
        
        case 
            when datediff('day', o.last_order_date, current_date()) <= 90 then 'Active'
            when datediff('day', o.last_order_date, current_date()) <= 180 then 'At Risk'
            when datediff('day', o.last_order_date, current_date()) <= 365 then 'Lapsed'
            else 'Inactive'
        end as customer_status,
        
        -- GA4 metrics (aggregated at region/city level)
        g.active_users as regional_online_users,
        g.new_users as regional_new_users,
        g.total_revenue as regional_online_revenue,
        g.transactions as regional_online_transactions,
        g.conversions as regional_online_conversions,
        g.acquisition_channel as predominant_acquisition_channel,
        g.user_value_segment as online_user_value_segment,
        
        -- Combined metrics and segments
        case
            when o.total_order_amount > 1000 then 'High Value'
            when o.total_order_amount > 500 then 'Medium Value'
            when o.total_order_amount > 100 then 'Low Value'
            else 'Very Low Value'
        end as offline_value_segment,
        
        case
            when o.order_count > 10 then 'High Frequency'
            when o.order_count > 5 then 'Medium Frequency'
            when o.order_count > 1 then 'Low Frequency'
            else 'One-time'
        end as purchase_frequency_segment,
        
        -- RFM segmentation (Recency, Frequency, Monetary)
        case
            when datediff('day', o.last_order_date, current_date()) <= 30 then 5
            when datediff('day', o.last_order_date, current_date()) <= 90 then 4
            when datediff('day', o.last_order_date, current_date()) <= 180 then 3
            when datediff('day', o.last_order_date, current_date()) <= 365 then 2
            else 1
        end as recency_score,
        
        case
            when o.order_count > 20 then 5
            when o.order_count > 10 then 4
            when o.order_count > 5 then 3
            when o.order_count > 1 then 2
            else 1
        end as frequency_score,
        
        case
            when o.total_order_amount > 2000 then 5
            when o.total_order_amount > 1000 then 4
            when o.total_order_amount > 500 then 3
            when o.total_order_amount > 100 then 2
            else 1
        end as monetary_score,
        
        -- Add metadata fields
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from prohandel_customers c
    left join customer_orders o
        on c.customer_id = o.customer_id
    left join customer_sales s
        on c.customer_id = s.customer_id
    left join ga4_user_acquisition g
        on c.city = g.city
        and c.region = g.region
        and c.country = g.country
)

select 
    *,
    -- Calculate combined RFM score and segment
    (recency_score + frequency_score + monetary_score) as rfm_score,
    case
        when (recency_score + frequency_score + monetary_score) >= 13 then 'Champions'
        when (recency_score + frequency_score + monetary_score) >= 10 then 'Loyal Customers'
        when (recency_score + frequency_score + monetary_score) >= 7 then 'Potential Loyalists'
        when (recency_score + frequency_score + monetary_score) >= 5 then 'At Risk Customers'
        when (recency_score + frequency_score + monetary_score) >= 3 then 'Hibernating'
        else 'Lost'
    end as rfm_segment
from combined
