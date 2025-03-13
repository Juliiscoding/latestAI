with source as (
    select * from {{ source('prohandel', 'customers') }}
),

renamed as (
    select
        customer_id,
        tenant_id,
        first_name,
        last_name,
        email,
        phone,
        address,
        city,
        postal_code,
        country,
        created_at,
        updated_at,
        
        -- Add calculated fields
        concat(first_name, ' ', last_name) as full_name,
        
        -- Add full address
        concat_ws(', ', 
            address,
            city,
            postal_code,
            country
        ) as full_address,
        
        -- Calculate customer age (days since creation)
        datediff('day', created_at, current_date()) as customer_age_days,
        
        -- Add metadata fields
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from source
)

select * from renamed
