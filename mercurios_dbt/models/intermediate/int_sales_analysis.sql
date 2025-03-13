with sales as (
    select * from {{ ref('stg_sales') }}
),

articles as (
    select * from {{ ref('stg_articles') }}
),

-- Join sales with article information
sales_with_articles as (
    select
        s.sale_id,
        s.article_id,
        s.tenant_id,
        s.sold_quantity,
        s.unit_price,
        s.total_sale_amount,
        s.sale_date,
        s.sale_year,
        s.sale_month,
        s.sale_day,
        s.sale_day_of_week,
        s.updated_at,
        
        -- Article information
        a.article_name,
        a.category,
        a.retail_price,
        a.wholesale_cost,
        a.gross_profit,
        a.margin_percent,
        a.price_tier,
        
        -- Calculate profit for this sale
        s.sold_quantity * a.gross_profit as total_profit,
        
        -- Metadata
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from sales s
    left join articles a on s.article_id = a.article_id and s.tenant_id = a.tenant_id
),

-- Calculate daily aggregations
daily_sales as (
    select
        tenant_id,
        sale_date,
        count(distinct sale_id) as number_of_sales,
        count(distinct article_id) as number_of_unique_articles,
        sum(sold_quantity) as total_quantity_sold,
        sum(total_sale_amount) as total_revenue,
        sum(total_profit) as total_profit,
        avg(unit_price) as average_unit_price
    from sales_with_articles
    group by 1, 2
),

-- Calculate article aggregations
article_sales as (
    select
        tenant_id,
        article_id,
        article_name,
        category,
        price_tier,
        count(distinct sale_id) as number_of_sales,
        sum(sold_quantity) as total_quantity_sold,
        sum(total_sale_amount) as total_revenue,
        sum(total_profit) as total_profit,
        avg(unit_price) as average_unit_price,
        min(sale_date) as first_sale_date,
        max(sale_date) as last_sale_date,
        datediff('day', min(sale_date), max(sale_date)) as sales_period_days
    from sales_with_articles
    group by 1, 2, 3, 4, 5
),

-- Calculate sales velocity and frequency
article_velocity as (
    select
        *,
        case
            when sales_period_days = 0 then total_quantity_sold
            else total_quantity_sold / sales_period_days
        end as daily_sales_rate,
        
        case
            when sales_period_days = 0 then 0
            else number_of_sales / sales_period_days * 30
        end as monthly_sales_frequency,
        
        case
            when daily_sales_rate <= 0.1 then 'Very Slow'
            when daily_sales_rate <= 0.5 then 'Slow'
            when daily_sales_rate <= 2 then 'Medium'
            when daily_sales_rate <= 5 then 'Fast'
            else 'Very Fast'
        end as sales_velocity_category
    from article_sales
)

select * from article_velocity
