with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

-- Calculate order metrics per customer
customer_orders as (
    select
        customer_id,
        tenant_id,
        count(*) as number_of_orders,
        sum(total_amount) as total_spent,
        avg(total_amount) as average_order_value,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        datediff('day', min(order_date), max(order_date)) as customer_lifespan_days
    from orders
    group by 1, 2
),

-- Join customers with order metrics
final as (
    select
        c.customer_id,
        c.tenant_id,
        c.first_name,
        c.last_name,
        c.full_name,
        c.email,
        c.phone,
        c.full_address,
        c.city,
        c.country,
        c.customer_age_days,
        
        -- Order metrics
        coalesce(o.number_of_orders, 0) as number_of_orders,
        coalesce(o.total_spent, 0) as total_spent,
        o.average_order_value,
        o.first_order_date,
        o.last_order_date,
        o.customer_lifespan_days,
        
        -- Calculate days since last order
        datediff('day', o.last_order_date, current_date()) as days_since_last_order,
        
        -- Customer segmentation by recency
        case
            when o.last_order_date is null then 'Never Ordered'
            when datediff('day', o.last_order_date, current_date()) <= 30 then 'Active'
            when datediff('day', o.last_order_date, current_date()) <= 90 then 'Recent'
            when datediff('day', o.last_order_date, current_date()) <= 180 then 'Lapsed'
            else 'Inactive'
        end as recency_segment,
        
        -- Customer segmentation by frequency
        case
            when o.number_of_orders is null then 'Never Ordered'
            when o.number_of_orders = 1 then 'One-time Customer'
            when o.number_of_orders < 5 then 'Occasional Customer'
            when o.number_of_orders < 10 then 'Regular Customer'
            else 'Loyal Customer'
        end as frequency_segment,
        
        -- Customer segmentation by monetary value
        case
            when o.total_spent is null then 'No Spend'
            when o.total_spent < 100 then 'Low Spend'
            when o.total_spent < 500 then 'Medium Spend'
            when o.total_spent < 1000 then 'High Spend'
            else 'VIP'
        end as monetary_segment,
        
        -- RFM combined segment
        case
            when o.last_order_date is null then 'Never Ordered'
            when datediff('day', o.last_order_date, current_date()) <= 30 
                and o.number_of_orders >= 5 
                and o.total_spent >= 500 then 'Champions'
            when datediff('day', o.last_order_date, current_date()) <= 30 
                and o.number_of_orders >= 2 then 'Loyal Customers'
            when datediff('day', o.last_order_date, current_date()) <= 90 
                and o.number_of_orders = 1 then 'Promising'
            when datediff('day', o.last_order_date, current_date()) > 90 
                and o.number_of_orders >= 5 then 'At Risk'
            when datediff('day', o.last_order_date, current_date()) > 180 
                and o.number_of_orders >= 2 then 'Needs Attention'
            when datediff('day', o.last_order_date, current_date()) <= 30 
                and o.number_of_orders = 1 then 'New Customers'
            else 'Others'
        end as rfm_segment,
        
        -- Metadata
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from customers c
    left join customer_orders o on c.customer_id = o.customer_id and c.tenant_id = o.tenant_id
)

select * from final
