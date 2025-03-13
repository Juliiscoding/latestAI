
  
  create view "dbt_mercurios_dev"."main_staging"."stg_prohandel__inventory__dbt_tmp" as (
    with source as (
    select * from "MERCURIOS_DATA"."RAW"."inventory"
),

renamed as (
    select
        inventory_id,
        article_id,
        warehouse_id,
        quantity,
        
        -- Add stock level categorization
        case
            when quantity <= 0 then 'Out of Stock'
            when quantity <= 5 then 'Low Stock'
            when quantity <= 20 then 'Medium Stock'
            when quantity > 20 then 'High Stock'
            else 'Unknown'
        end as stock_level,
        
        -- Add reorder flag
        case
            when quantity <= 5 then true
            else false
        end as needs_reorder,
        
        location,
        last_count_date,
        is_available,
        tenant_id,
        
        -- Fivetran metadata
        _fivetran_synced,
        
        -- Add data quality flags
        case when quantity < 0 then true else false end as is_negative_quantity
    from source
)

select * from renamed
  );
