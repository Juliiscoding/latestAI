
  create or replace   view MERCURIOS_DATA.RAW_staging.stg_orders
  
   as (
    with source as (
    select * from MERCURIOS_DATA.RAW.orders
),

renamed as (
    select
        order_id,
        tenant_id,
        customer_id,
        order_date,
        status,
        total_amount,
        shipping_address,
        shipping_city,
        shipping_postal_code,
        shipping_country,
        created_at,
        updated_at,
        
        -- Add calculated fields
        datediff('day', order_date, current_date()) as days_since_order,
        
        -- Add full shipping address
        concat_ws(', ', 
            shipping_address,
            shipping_city,
            shipping_postal_code,
            shipping_country
        ) as full_shipping_address,
        
        -- Add order status categorization
        case
            when status = 'completed' then 'Completed'
            when status = 'shipped' then 'In Transit'
            when status = 'processing' then 'Processing'
            when status = 'pending' then 'Pending'
            when status = 'cancelled' then 'Cancelled'
            else 'Other'
        end as order_status_category,
        
        -- Add metadata fields
        current_timestamp() as dbt_updated_at,
        '268bbaba-a93a-4be3-aee9-ecf58e6b9848' as dbt_updated_by,
        'stg_orders' as dbt_model
    from source
)

select * from renamed
  );

