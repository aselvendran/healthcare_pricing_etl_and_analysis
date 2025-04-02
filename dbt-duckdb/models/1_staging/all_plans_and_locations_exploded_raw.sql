{{ config(
    materialized= 'table', 
    alias= 'all_plans_and_locations_exploded_raw'
) }}

select
    primary_key
    , plan_name
    , plan_id
    , plan_id_type
    , description
    , location
from {{ source('healthcare_pricing', 'reporting_plans') }}
    inner join {{ source('healthcare_pricing', 'in_network_files') }} using(primary_key)
