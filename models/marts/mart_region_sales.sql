with staging 
as (
    select * from {{ ref('stg_superstore_orders') }}
),

total_sales 
as (
    select sum(sales) as company_total_sales
    from staging
),

region_aggregates 
as (
    select
        region,
        sum(sales) as total_sales,
        count(distinct order_id) as order_count,
        count(distinct customer_id) as customer_count
    from staging
    group by region
)

select
    r.region,
    r.total_sales,
    r.order_count,
    r.customer_count,
    round((r.total_sales / t.company_total_sales) * 100, 2) as sales_contribution_pct
from region_aggregates r
cross join total_sales t
order by total_sales desc
