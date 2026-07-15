with staging 
as (
    select * from {{ ref('stg_superstore_orders') }}
)

select
    region,
    sum(sales) as total_sales,
    sum(profit) as total_profit,
    round((sum(profit) / sum(sales)) * 100, 2) as profit_margin_pct,
    round(avg(discount) * 100, 2) as avg_discount_pct
from staging
group by region
order by total_profit desc
