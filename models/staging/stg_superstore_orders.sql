with source as (
    select * from {{ source('superstore_raw', 'orders') }}
),

staged as (
    select
        -- surrogate primary key for the row transaction
        md5(cast(row_id as varchar)) as row_key,
        cast(row_id as int) as row_id,

        -- order attributes
        cast(order_id as varchar) as order_id,
        try_to_date(order_date, 'MM/DD/YYYY') as order_date,
        try_to_date(ship_date, 'MM/DD/YYYY') as ship_date,
        cast(ship_mode as varchar) as ship_mode,

        -- customer attributes & surrogate key
        md5(cast(coalesce(customer_id, '') as varchar)) as customer_key,
        cast(customer_id as varchar) as customer_id,
        cast(customer_name as varchar) as customer_name,
        cast(segment as varchar) as customer_segment,

        -- geographic attributes & surrogate key:combined location key
        md5(concat(
            coalesce(country, ''), '-',
            coalesce(region, ''), '-',
            coalesce(state, ''), '-',
            coalesce(city, ''), '-',
            coalesce(lpad(cast(postal_code as varchar), 5, '0'), '')
        )) as location_key,
        cast(country as varchar) as country,
        cast(region as varchar) as region,
        cast(state as varchar) as state,
        cast(city as varchar) as city,
        lpad(cast(postal_code as varchar), 5, '0') as postal_code,

        -- product attributes & surrogate key
        md5(cast(coalesce(product_id, '') as varchar)) as product_key,
        cast(product_id as varchar) as product_id,
        cast(category as varchar) as category,
        cast(sub_category as varchar) as sub_category,
        cast(product_name as varchar) as product_name,

        -- financial metrics
        cast(sales as decimal(16, 2)) as sales,
        cast(quantity as int) as quantity,
        cast(discount as decimal(4, 2)) as discount,
        cast(profit as decimal(16, 2)) as profit

    from source
)

select * from staged
