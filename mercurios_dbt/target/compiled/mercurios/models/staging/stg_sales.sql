with source as (
    select * from MERCURIOS_DATA.RAW.sales
),

renamed as (
    select
        sale_id,
        article_id,
        tenant_id,
        quantity as sold_quantity,
        price as unit_price,
        updated_at,
        
        -- Add calculated fields
        (quantity * price) as total_sale_amount,
        
        -- Add date dimensions
        date(updated_at) as sale_date,
        extract(year from updated_at) as sale_year,
        extract(month from updated_at) as sale_month,
        extract(day from updated_at) as sale_day,
        extract(dayofweek from updated_at) as sale_day_of_week,
        
        -- Add metadata fields
        current_timestamp() as dbt_updated_at,
        '268bbaba-a93a-4be3-aee9-ecf58e6b9848' as dbt_updated_by,
        'stg_sales' as dbt_model
    from source
)

select * from renamed