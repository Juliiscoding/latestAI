select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select warehouse_id
from "MERCURIOS_DATA"."RAW"."inventory"
where warehouse_id is null



      
    ) dbt_internal_test