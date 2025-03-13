with sales_history as (
    select
        article_number,
        date_trunc('day', sale_date) as sale_date,
        sum(quantity) as quantity_sold
    from {{ ref('stg_prohandel__sales') }}
    where sale_date >= dateadd('day', -365, current_date)
    group by article_number, date_trunc('day', sale_date)
),

-- Calculate daily average over the last 30, 90, and 365 days
sales_averages as (
    select
        article_number,
        
        -- Last 30 days
        sum(case when sale_date >= dateadd('day', -30, current_date) then quantity_sold else 0 end) as quantity_30d,
        sum(case when sale_date >= dateadd('day', -30, current_date) then 1 else 0 end) as days_with_sales_30d,
        
        -- Last 90 days
        sum(case when sale_date >= dateadd('day', -90, current_date) then quantity_sold else 0 end) as quantity_90d,
        sum(case when sale_date >= dateadd('day', -90, current_date) then 1 else 0 end) as days_with_sales_90d,
        
        -- Last 365 days
        sum(quantity_sold) as quantity_365d,
        count(distinct sale_date) as days_with_sales_365d
    from sales_history
    group by article_number
),

-- Calculate daily, weekly, and monthly averages
sales_rates as (
    select
        article_number,
        
        -- Daily averages
        quantity_30d / greatest(days_with_sales_30d, 1) as daily_avg_30d,
        quantity_90d / greatest(days_with_sales_90d, 1) as daily_avg_90d,
        quantity_365d / greatest(days_with_sales_365d, 1) as daily_avg_365d,
        
        -- Weekly averages (multiply daily by 7)
        (quantity_30d / greatest(days_with_sales_30d, 1)) * 7 as weekly_avg_30d,
        (quantity_90d / greatest(days_with_sales_90d, 1)) * 7 as weekly_avg_90d,
        (quantity_365d / greatest(days_with_sales_365d, 1)) * 7 as weekly_avg_365d,
        
        -- Monthly averages (multiply daily by 30)
        (quantity_30d / greatest(days_with_sales_30d, 1)) * 30 as monthly_avg_30d,
        (quantity_90d / greatest(days_with_sales_90d, 1)) * 30 as monthly_avg_90d,
        (quantity_365d / greatest(days_with_sales_365d, 1)) * 30 as monthly_avg_365d,
        
        -- Sales frequency (percentage of days with sales)
        days_with_sales_30d / 30.0 as sales_frequency_30d,
        days_with_sales_90d / 90.0 as sales_frequency_90d,
        days_with_sales_365d / 365.0 as sales_frequency_365d
    from sales_averages
),

-- Get current inventory levels
current_inventory as (
    select
        article_number,
        sum(quantity) as current_quantity
    from {{ ref('stg_prohandel__inventory') }}
    group by article_number
)

-- Final forecast model
select
    s.article_number,
    a.article_name,
    a.price_tier,
    
    -- Current inventory
    coalesce(i.current_quantity, 0) as current_quantity,
    
    -- Sales rates
    s.daily_avg_30d,
    s.daily_avg_90d,
    s.daily_avg_365d,
    s.weekly_avg_30d,
    s.weekly_avg_90d,
    s.weekly_avg_365d,
    s.monthly_avg_30d,
    s.monthly_avg_90d,
    s.monthly_avg_365d,
    
    -- Sales frequency
    s.sales_frequency_30d,
    s.sales_frequency_90d,
    s.sales_frequency_365d,
    
    -- Weighted forecast (more weight to recent data)
    (s.daily_avg_30d * 0.5) + (s.daily_avg_90d * 0.3) + (s.daily_avg_365d * 0.2) as daily_forecast,
    (s.weekly_avg_30d * 0.5) + (s.weekly_avg_90d * 0.3) + (s.weekly_avg_365d * 0.2) as weekly_forecast,
    (s.monthly_avg_30d * 0.5) + (s.monthly_avg_90d * 0.3) + (s.monthly_avg_365d * 0.2) as monthly_forecast,
    
    -- Days of supply based on forecast
    case
        when (s.daily_avg_30d * 0.5) + (s.daily_avg_90d * 0.3) + (s.daily_avg_365d * 0.2) > 0
        then coalesce(i.current_quantity, 0) / ((s.daily_avg_30d * 0.5) + (s.daily_avg_90d * 0.3) + (s.daily_avg_365d * 0.2))
        else null
    end as forecast_days_of_supply,
    
    -- Recommended reorder point (7-day lead time, 1.5 safety factor)
    ceiling(((s.daily_avg_30d * 0.5) + (s.daily_avg_90d * 0.3) + (s.daily_avg_365d * 0.2)) * 7 * 1.5) as reorder_point,
    
    -- Recommended order quantity (30-day supply)
    ceiling(((s.daily_avg_30d * 0.5) + (s.daily_avg_90d * 0.3) + (s.daily_avg_365d * 0.2)) * 30) as recommended_order_qty,
    
    -- Stockout risk
    case
        when coalesce(i.current_quantity, 0) <= 0 then 'current_stockout'
        when coalesce(i.current_quantity, 0) <= ceiling(((s.daily_avg_30d * 0.5) + (s.daily_avg_90d * 0.3) + (s.daily_avg_365d * 0.2)) * 7) then 'high_risk'
        when coalesce(i.current_quantity, 0) <= ceiling(((s.daily_avg_30d * 0.5) + (s.daily_avg_90d * 0.3) + (s.daily_avg_365d * 0.2)) * 14) then 'medium_risk'
        when coalesce(i.current_quantity, 0) <= ceiling(((s.daily_avg_30d * 0.5) + (s.daily_avg_90d * 0.3) + (s.daily_avg_365d * 0.2)) * 30) then 'low_risk'
        else 'no_risk'
    end as stockout_risk
from sales_rates s
left join {{ ref('stg_prohandel__articles') }} a on s.article_number = a.article_number
left join current_inventory i on s.article_number = i.article_number
