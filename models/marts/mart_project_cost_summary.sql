with costs as (
    select project_id, sum(budget_cost) as budget_cost, sum(actual_cost) as actual_cost,
           sum(committed_cost) as committed_cost, sum(certified_amount) as certified_amount,
           sum(approved_variations) as approved_variations, sum(revised_budget) as revised_budget
    from {{ ref('mart_work_package_costs') }} group by 1
), project_payments as (
    select wp.project_id, sum(p.paid_amount) as paid_amount
    from {{ ref('stg_payments') }} p
    join {{ ref('stg_valuations') }} v using (valuation_id)
    join {{ ref('stg_work_packages') }} wp using (work_package_id)
    group by 1
)
select c.project_id, pr.project_name, pr.location, pr.area_m2,
       c.budget_cost, c.actual_cost, c.committed_cost, c.certified_amount,
       coalesce(p.paid_amount, 0) as paid_amount,
       c.budget_cost - c.actual_cost as remaining_budget,
       c.actual_cost - c.budget_cost as cost_variance,
       c.approved_variations,
       case when c.budget_cost = 0 then null else c.approved_variations / c.budget_cost end as variation_pct,
       case when pr.area_m2 = 0 then null else c.actual_cost / pr.area_m2 end as actual_cost_per_m2,
       c.revised_budget
from costs c join {{ ref('stg_projects') }} pr using (project_id)
left join project_payments p using (project_id)
