with source as (
    select * from {{ source('prohandel', 'inventory') }}
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
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from source
)

select * from renamed
