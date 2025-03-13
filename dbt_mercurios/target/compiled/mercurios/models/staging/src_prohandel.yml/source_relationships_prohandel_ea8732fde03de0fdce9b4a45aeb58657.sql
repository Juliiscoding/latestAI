
    
    

with child as (
    select article_id as from_field
    from "MERCURIOS_DATA"."RAW"."sale"
    where article_id is not null
),

parent as (
    select article_id as to_field
    from "MERCURIOS_DATA"."RAW"."article"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


