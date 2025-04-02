{{ config(
    materialized= 'table', 
    alias= 'ny_anthem_ppo'
) }}

select
    primary_key
    , plan_name
    , plan_id
    , plan_id_type
    , description
    , location
    , count(*) over (PARTITION BY primary_key) cnt_records_per_json_block
    , count(*) over (PARTITION BY primary_key, location) cnt_location
from {{ ref('all_plans_and_locations_exploded_raw') }} t
where plan_name ilike '%anthem%' 
    and plan_name ilike '%ppo%'  
    and location like '%NY\_%' ESCAPE '\' 
order by location desc
