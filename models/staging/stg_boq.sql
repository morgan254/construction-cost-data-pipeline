select cast(boq_line_id as varchar) as boq_line_id,
       cast(work_package_id as varchar) as work_package_id,
       trim(description) as description, trim(unit) as unit,
       cast(quantity as double) as quantity,
       cast(unit_rate as decimal(18,2)) as unit_rate,
       cast(budget_amount as decimal(18,2)) as budget_amount
from {{ source('raw', 'boq') }}
