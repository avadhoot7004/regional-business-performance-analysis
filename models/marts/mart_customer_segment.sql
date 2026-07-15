with staging 
as (
    select * from {{ ref('stg_superstore_orders') }}
)

select
    customer_segment,
    sum(sales) as total_sales,
    sum(profit) as total_profit,
    round((sum(profit) / sum(sales)) * 100, 2) as profit_margin_pct,
    count(distinct order_id) as order_count,
    count(distinct customer_id) as customer_count,
    round(sum(sales) / count(distinct order_id), 2) as average_order_value
from staging
group by customer_segment
order by total_sales desc
