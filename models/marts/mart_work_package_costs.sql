with budget as (
    select work_package_id, sum(budget_amount) as budget_cost
    from {{ ref('stg_boq') }} group by 1
), purchases as (
    select work_package_id, sum(order_amount) as committed_cost, sum(invoiced_amount) as actual_cost
    from {{ ref('stg_purchases') }} group by 1
), valuation as (
    select work_package_id, sum(certified_amount) as certified_amount
    from {{ ref('stg_valuations') }} group by 1
), variation as (
    select work_package_id, sum(case when status = 'approved' then amount else 0 end) as approved_variations
    from {{ ref('stg_variations') }} group by 1
)
select wp.project_id, wp.work_package_id, wp.work_package_name,
       coalesce(b.budget_cost, 0) as budget_cost,
       coalesce(p.actual_cost, 0) as actual_cost,
       coalesce(p.committed_cost, 0) as committed_cost,
       coalesce(v.certified_amount, 0) as certified_amount,
       coalesce(x.approved_variations, 0) as approved_variations,
       coalesce(b.budget_cost, 0) + coalesce(x.approved_variations, 0) as revised_budget,
       coalesce(b.budget_cost, 0) - coalesce(p.actual_cost, 0) as remaining_budget,
       coalesce(p.actual_cost, 0) - coalesce(b.budget_cost, 0) as cost_variance,
       case when coalesce(b.budget_cost, 0) = 0 then null
            else coalesce(x.approved_variations, 0) / b.budget_cost end as variation_pct
from {{ ref('stg_work_packages') }} wp
left join budget b using (work_package_id)
left join purchases p using (work_package_id)
left join valuation v using (work_package_id)
left join variation x using (work_package_id)
