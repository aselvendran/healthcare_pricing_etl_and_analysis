
  
    
    

    create  table
      "anthem_data"."main_staging"."all_plans_and_locations_exploded_raw__dbt_tmp"
  
    as (
      

select
    primary_key
    , plan_name
    , plan_id
    , plan_id_type
    , description
    , location
from "anthem_data"."main"."reporting_plans"
    inner join "anthem_data"."main"."in_network_files" using(primary_key)
    );
  
  