select cast(valuation_id as varchar) as valuation_id,
       cast(work_package_id as varchar) as work_package_id,
       cast(valuation_number as integer) as valuation_number,
       cast(certification_date as date) as certification_date,
       cast(certified_amount as decimal(18,2)) as certified_amount
from {{ source('raw', 'valuations') }}
