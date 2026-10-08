select supplier_id, supplier_name, sum(order_amount) as committed_cost,
       sum(invoiced_amount) as actual_cost, count(*) as purchase_order_count
from {{ ref('stg_purchases') }}
group by 1, 2
