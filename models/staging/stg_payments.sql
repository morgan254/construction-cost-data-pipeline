select cast(payment_id as varchar) as payment_id,
       cast(valuation_id as varchar) as valuation_id,
       cast(payment_date as date) as payment_date,
       cast(paid_amount as decimal(18,2)) as paid_amount
from {{ source('raw', 'payments') }}
