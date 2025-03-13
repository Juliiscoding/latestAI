
    
    

select
    article_id as unique_field,
    count(*) as n_records

from "MERCURIOS_DATA"."RAW"."article"
where article_id is not null
group by article_id
having count(*) > 1


