
    
    

select
    inventory_id as unique_field,
    count(*) as n_records

from "MERCURIOS_DATA"."RAW"."inventory"
where inventory_id is not null
group by inventory_id
having count(*) > 1


