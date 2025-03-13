
  
  create view "dbt_mercurios_dev"."main_staging"."stg_prohandel__articles__dbt_tmp" as (
    with source as (
    select * from "MERCURIOS_DATA"."RAW"."article"
),

renamed as (
    select
        article_id,
        article_number,
        description,
        category,
        subcategory,
        brand,
        supplier,
        purchase_price,
        retail_price,
        min_stock_level,
        max_stock_level,
        reorder_point,
        lead_time_days,
        is_active,
        
        -- Calculate profit margin
        (retail_price - purchase_price) as profit_margin,
        case 
            when (purchase_price > 0) then ((retail_price - purchase_price) / purchase_price) * 100 
            else null 
        end as profit_margin_percent,
        
        -- Add price tier categorization
        case
            when retail_price < 10 then 'Budget'
            when retail_price >= 10 and retail_price < 50 then 'Standard'
            when retail_price >= 50 and retail_price < 100 then 'Premium'
            when retail_price >= 100 then 'Luxury'
            else 'Uncategorized'
        end as price_tier,
        
        created_at,
        updated_at,
        tenant_id,
        
        -- Fivetran metadata
        _fivetran_synced,
        
        -- Add data quality flags
        case when description is null or description = '' then true else false end as is_missing_description,
        case when purchase_price is null or purchase_price = 0 then true else false end as is_missing_purchase_price,
        case when retail_price is null or retail_price = 0 then true else false end as is_missing_retail_price
    from source
)

select * from renamed
  );
