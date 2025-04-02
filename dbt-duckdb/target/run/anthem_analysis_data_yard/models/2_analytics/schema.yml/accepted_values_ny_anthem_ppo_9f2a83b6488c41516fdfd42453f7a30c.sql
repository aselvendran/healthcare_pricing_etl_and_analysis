select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with all_values as (

    select
        description as value_field,
        count(*) as n_records

    from "anthem_data"."main_analytics"."ny_anthem_ppo"
    group by description

)

select *
from all_values
where value_field not in (
    'In-Network Negotiated Rates Files'
)



      
    ) dbt_internal_test