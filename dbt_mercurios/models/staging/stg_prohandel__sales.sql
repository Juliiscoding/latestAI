with source as (
    select * from {{ source('prohandel', 'sale') }}
),

renamed as (
    select
        sale_id,
        order_id,
        article_id,
        quantity,
        price,
        discount,
        
        -- Calculate net price and revenue
        (price - coalesce(discount, 0)) as net_price,
        (price - coalesce(discount, 0)) * quantity as revenue,
        
        -- Add sale type categorization
        case
            when discount is null or discount = 0 then 'Regular'
            when discount > 0 and discount < (price * 0.1) then 'Small Discount'
            when discount >= (price * 0.1) and discount < (price * 0.3) then 'Medium Discount'
            when discount >= (price * 0.3) then 'Large Discount'
            else 'Unknown'
        end as sale_type,
        
        sale_date,
        shop_id,
        tenant_id,
        
        -- Fivetran metadata
        _fivetran_synced,
        
        -- Add data quality flags
        case when quantity <= 0 then true else false end as is_invalid_quantity,
        case when price <= 0 then true else false end as is_invalid_price,
        case when discount > price then true else false end as is_discount_greater_than_price
    from source
)

select * from renamed
