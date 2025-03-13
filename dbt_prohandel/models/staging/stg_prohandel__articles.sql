with source as (
    select * from {{ source('prohandel', 'article') }}
),

renamed as (
    select
        article_number,
        name as article_name,
        description,
        price,
        cost_price,
        category,
        subcategory,
        brand,
        supplier,
        status,
        created_at,
        last_modified,
        
        -- Add calculated fields
        price - cost_price as gross_margin,
        (price - cost_price) / nullif(price, 0) * 100 as margin_percentage,
        
        -- Add price tier categorization
        case
            when price < 10 then 'budget'
            when price >= 10 and price < 50 then 'standard'
            when price >= 50 and price < 200 then 'premium'
            else 'luxury'
        end as price_tier
    from source
)

select * from renamed
