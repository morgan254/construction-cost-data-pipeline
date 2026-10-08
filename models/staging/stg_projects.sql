select cast(project_id as varchar) as project_id,
       trim(project_name) as project_name, trim(location) as location,
       cast(area_m2 as double) as area_m2,
       cast(start_date as date) as start_date,
       cast(planned_end_date as date) as planned_end_date
from {{ source('raw', 'projects') }}
