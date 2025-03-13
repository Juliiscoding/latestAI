
  create or replace   view MERCURIOS_DATA.RAW_staging.stg_inventory
  
   as (
    with source as (
    select * from MERCURIOS_DATA.RAW.inventory
),

renamed as (
    select
        article_id,
        tenant_id,
        warehouse_id,
        quantity as stock_quantity,
        updated_at,
        
        -- Add calculated fields for inventory status
        case
            when stock_quantity <= 0 then 'Out of Stock'
            when stock_quantity < 5 then 'Low Stock'
            when stock_quantity < 20 then 'Medium Stock'
            else 'Well Stocked'
        end as stock_status,
        
        -- Add metadata fields
        current_timestamp() as dbt_updated_at,
        '268bbaba-a93a-4be3-aee9-ecf58e6b9848' as dbt_updated_by,
        'stg_inventory' as dbt_model
    from source
)

select * from renamed
  );

