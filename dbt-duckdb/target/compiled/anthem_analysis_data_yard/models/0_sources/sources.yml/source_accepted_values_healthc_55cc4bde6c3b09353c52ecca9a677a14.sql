
    
    

with all_values as (

    select
        plan_market_type as value_field,
        count(*) as n_records

    from "anthem_data"."main"."reporting_plans"
    group by plan_market_type

)

select *
from all_values
where value_field not in (
    'group','individual'
)


