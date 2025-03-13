select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select quantity
from "MERCURIOS_DATA"."RAW"."inventory"
where quantity is null



      
    ) dbt_internal_test