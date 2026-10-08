with paid as (
    select valuation_id, sum(paid_amount) as paid_amount, max(payment_date) as last_payment_date
    from {{ ref('stg_payments') }} group by 1
)
select v.valuation_id, wp.project_id, v.work_package_id, wp.work_package_name,
       v.valuation_number, v.certification_date, v.certified_amount,
       coalesce(p.paid_amount, 0) as paid_amount,
       v.certified_amount - coalesce(p.paid_amount, 0) as outstanding_amount,
       p.last_payment_date,
       case when p.last_payment_date is null then null
            else date_diff('day', v.certification_date, p.last_payment_date) end as payment_lag_days
from {{ ref('stg_valuations') }} v
join {{ ref('stg_work_packages') }} wp using (work_package_id)
left join paid p using (valuation_id)
