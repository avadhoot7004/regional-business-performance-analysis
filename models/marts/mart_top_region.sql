with regional_metrics 
as (
    select
        region,
        sum(sales) as total_sales,
        sum(profit) as total_profit,
        round((sum(profit) / sum(sales)) * 100, 2) as profit_margin_pct
    from {{ ref('stg_superstore_orders') }}
    group by region
)

select
    region,
    total_sales,
    total_profit,
    profit_margin_pct,
    dense_rank() over (order by total_sales desc) as sales_rank,
    dense_rank() over (order by total_profit desc) as profit_rank
from regional_metrics
order by sales_rank
