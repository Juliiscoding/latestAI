with source as (
    select * from MERCURIOS_DATA.RAW.articles
),

renamed as (
    select
        article_id,
        tenant_id,
        name as article_name,
        description,
        price as retail_price,
        cost as wholesale_cost,
        category,
        supplier_id,
        created_at,
        updated_at,
        
        -- Add calculated fields
        (retail_price - wholesale_cost) as gross_profit,
        case 
            when wholesale_cost = 0 then null
            else (retail_price - wholesale_cost) / wholesale_cost 
        end as margin_percent,
        
        -- Add price tier categorization
        case
            when retail_price < 10 then 'Budget'
            when retail_price < 50 then 'Standard'
            when retail_price < 200 then 'Premium'
            else 'Luxury'
        end as price_tier,
        
        -- Add metadata fields
        current_timestamp() as dbt_updated_at,
        '268bbaba-a93a-4be3-aee9-ecf58e6b9848' as dbt_updated_by,
        'stg_articles' as dbt_model
    from source
)

select * from renamed