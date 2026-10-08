select cast(purchase_id as varchar) as purchase_id,
       cast(work_package_id as varchar) as work_package_id,
       cast(supplier_id as varchar) as supplier_id,
       trim(supplier_name) as supplier_name,
       cast(order_date as date) as order_date,
       cast(order_amount as decimal(18,2)) as order_amount,
       cast(invoiced_amount as decimal(18,2)) as invoiced_amount,
       lower(trim(status)) as status
from {{ source('raw', 'purchases') }}
