with source as (
    select * from {{ source('prohandel', 'sale') }}
),

renamed as (
    select
        sale_id,
        order_number,
        article_number,
        quantity,
        amount,
        sale_date,
        customer_number,
        
        -- Add calculated fields
        amount / nullif(quantity, 0) as unit_price,
        
        -- Add time-based categorization
        case
            when extract(hour from sale_date) >= 9 and extract(hour from sale_date) < 12 then 'morning'
            when extract(hour from sale_date) >= 12 and extract(hour from sale_date) < 17 then 'afternoon'
            when extract(hour from sale_date) >= 17 and extract(hour from sale_date) < 20 then 'evening'
            else 'night'
        end as day_part,
        
        extract(dow from sale_date) as day_of_week,
        extract(month from sale_date) as month,
        extract(year from sale_date) as year
    from source
)

select * from renamed
