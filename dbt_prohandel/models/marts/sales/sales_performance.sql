with sales as (
    select * from {{ ref('stg_prohandel__sales') }}
),

articles as (
    select * from {{ ref('stg_prohandel__articles') }}
),

sales_with_margins as (
    select
        s.*,
        a.article_name,
        a.cost_price,
        a.price_tier,
        a.margin_percentage,
        
        -- Calculate margin amount
        s.amount - (s.quantity * a.cost_price) as margin_amount
    from sales s
    left join articles a on s.article_number = a.article_number
),

-- Daily aggregation
daily_sales as (
    select
        date_trunc('day', sale_date) as sale_day,
        count(distinct sale_id) as num_transactions,
        count(distinct article_number) as num_unique_articles,
        sum(quantity) as total_quantity,
        sum(amount) as total_amount,
        sum(margin_amount) as total_margin,
        avg(margin_percentage) as avg_margin_percentage
    from sales_with_margins
    group by date_trunc('day', sale_date)
),

-- Weekly aggregation
weekly_sales as (
    select
        date_trunc('week', sale_date) as sale_week,
        count(distinct sale_id) as num_transactions,
        count(distinct article_number) as num_unique_articles,
        sum(quantity) as total_quantity,
        sum(amount) as total_amount,
        sum(margin_amount) as total_margin,
        avg(margin_percentage) as avg_margin_percentage
    from sales_with_margins
    group by date_trunc('week', sale_date)
),

-- Monthly aggregation
monthly_sales as (
    select
        date_trunc('month', sale_date) as sale_month,
        count(distinct sale_id) as num_transactions,
        count(distinct article_number) as num_unique_articles,
        sum(quantity) as total_quantity,
        sum(amount) as total_amount,
        sum(margin_amount) as total_margin,
        avg(margin_percentage) as avg_margin_percentage
    from sales_with_margins
    group by date_trunc('month', sale_date)
)

-- Final model combining all time periods
select
    'daily' as time_period,
    sale_day as period_date,
    num_transactions,
    num_unique_articles,
    total_quantity,
    total_amount,
    total_margin,
    avg_margin_percentage,
    total_amount / nullif(num_transactions, 0) as avg_transaction_value,
    total_quantity / nullif(num_transactions, 0) as avg_items_per_transaction
from daily_sales

union all

select
    'weekly' as time_period,
    sale_week as period_date,
    num_transactions,
    num_unique_articles,
    total_quantity,
    total_amount,
    total_margin,
    avg_margin_percentage,
    total_amount / nullif(num_transactions, 0) as avg_transaction_value,
    total_quantity / nullif(num_transactions, 0) as avg_items_per_transaction
from weekly_sales

union all

select
    'monthly' as time_period,
    sale_month as period_date,
    num_transactions,
    num_unique_articles,
    total_quantity,
    total_amount,
    total_margin,
    avg_margin_percentage,
    total_amount / nullif(num_transactions, 0) as avg_transaction_value,
    total_quantity / nullif(num_transactions, 0) as avg_items_per_transaction
from monthly_sales
