select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select primary_key
from "anthem_data"."main_analytics"."ny_anthem_ppo"
where primary_key is null



      
    ) dbt_internal_test