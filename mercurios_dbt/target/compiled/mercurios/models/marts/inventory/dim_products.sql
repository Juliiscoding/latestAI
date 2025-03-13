with articles as (
    select * from MERCURIOS_DATA.RAW_staging.stg_articles
),

-- Create a comprehensive dimension table for products
final as (
    select
        article_id,
        tenant_id,
        article_name,
        description,
        category,
        supplier_id,
        retail_price,
        wholesale_cost,
        gross_profit,
        margin_percent,
        price_tier,
        created_at,
        updated_at,
        
        -- Add product age
        datediff('day', created_at, current_date()) as product_age_days,
        
        -- Add product status based on age
        case
            when datediff('day', created_at, current_date()) <= 30 then 'New'
            when datediff('day', created_at, current_date()) <= 180 then 'Recent'
            else 'Established'
        end as product_age_category,
        
        -- Metadata
        current_timestamp() as dbt_updated_at,
        '268bbaba-a93a-4be3-aee9-ecf58e6b9848' as dbt_updated_by,
        'dim_products' as dbt_model
    from articles
)

select * from final