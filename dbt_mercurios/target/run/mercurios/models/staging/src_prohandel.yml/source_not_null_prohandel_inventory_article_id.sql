select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select article_id
from "MERCURIOS_DATA"."RAW"."inventory"
where article_id is null



      
    ) dbt_internal_test