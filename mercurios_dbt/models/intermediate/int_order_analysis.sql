with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

-- Join orders with customer information
final as (
    select
        o.order_id,
        o.tenant_id,
        o.customer_id,
        o.order_date,
        o.status,
        o.total_amount,
        o.full_shipping_address,
        o.order_status_category,
        o.days_since_order,
        
        -- Customer information
        c.full_name as customer_name,
        c.email as customer_email,
        c.phone as customer_phone,
        c.full_address as customer_address,
        c.customer_age_days,
        
        -- Order metrics
        case
            when o.days_since_order <= 30 then 'Recent'
            when o.days_since_order <= 90 then 'Medium'
            else 'Old'
        end as order_age_category,
        
        -- Order value categorization
        case
            when o.total_amount < 50 then 'Low Value'
            when o.total_amount < 200 then 'Medium Value'
            when o.total_amount < 500 then 'High Value'
            else 'Very High Value'
        end as order_value_category,
        
        -- Metadata
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from orders o
    left join customers c on o.customer_id = c.customer_id and o.tenant_id = c.tenant_id
)

select * from final
