select v.variation_id, wp.project_id, v.work_package_id, wp.work_package_name,
       v.description, v.status, v.raised_date, v.amount,
       case when v.status = 'approved' then v.amount else 0 end as approved_amount
from {{ ref('stg_variations') }} v
join {{ ref('stg_work_packages') }} wp using (work_package_id)
