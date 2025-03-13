with source as (
    select * from {{ source('prohandel', 'inventory') }}
),

renamed as (
    select
        inventory_id,
        article_number,
        warehouse_id,
        quantity,
        min_stock_level,
        max_stock_level,
        last_updated,
        
        -- Add stock level categorization
        case
            when quantity <= 0 then 'out_of_stock'
            when quantity > 0 and quantity <= min_stock_level then 'low_stock'
            when quantity > min_stock_level and quantity <= (min_stock_level + (max_stock_level - min_stock_level) * 0.5) then 'medium_stock'
            when quantity > (min_stock_level + (max_stock_level - min_stock_level) * 0.5) and quantity <= max_stock_level then 'high_stock'
            else 'excess_stock'
        end as stock_status
    from source
)

select * from renamed
