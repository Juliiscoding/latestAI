select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select article_number
from "MERCURIOS_DATA"."RAW"."article"
where article_number is null



      
    ) dbt_internal_test