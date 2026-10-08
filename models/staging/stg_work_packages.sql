select cast(work_package_id as varchar) as work_package_id,
       cast(project_id as varchar) as project_id,
       trim(work_package_name) as work_package_name
from {{ source('raw', 'work_packages') }}
