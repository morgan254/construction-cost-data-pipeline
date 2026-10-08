select cast(variation_id as varchar) as variation_id,
       cast(work_package_id as varchar) as work_package_id,
       trim(description) as description, lower(trim(status)) as status,
       cast(raised_date as date) as raised_date,
       cast(amount as decimal(18,2)) as amount
from {{ source('raw', 'variations') }}
