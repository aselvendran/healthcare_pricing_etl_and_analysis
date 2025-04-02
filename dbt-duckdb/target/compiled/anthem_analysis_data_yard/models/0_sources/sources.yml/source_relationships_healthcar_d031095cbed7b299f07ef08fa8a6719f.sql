
    
    

with child as (
    select primary_key as from_field
    from "anthem_data"."main"."in_network_files"
    where primary_key is not null
),

parent as (
    select primary_key as to_field
    from "anthem_data"."main"."reporting_plans"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


