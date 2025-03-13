

with sales_history as (
    select
        s.article_id,
        a.article_number,
        a.description,
        a.category,
        a.subcategory,
        a.brand,
        a.supplier,
        a.price_tier,
        s.sale_date,
        sum(s.quantity) as quantity_sold,
        count(distinct s.sale_id) as number_of_sales,
        sum(s.revenue) as revenue
    from "dbt_mercurios_dev"."main_staging"."stg_prohandel__sales" s
    join "dbt_mercurios_dev"."main_staging"."stg_prohandel__articles" a on s.article_id = a.article_id
    where s.sale_date >= dateadd('day', -365, current_date())
    group by 
        s.article_id,
        a.article_number,
        a.description,
        a.category,
        a.subcategory,
        a.brand,
        a.supplier,
        a.price_tier,
        s.sale_date
),

-- Calculate daily, weekly, and monthly aggregates
daily_sales as (
    select
        article_id,
        article_number,
        description,
        category,
        subcategory,
        brand,
        supplier,
        price_tier,
        sale_date,
        quantity_sold,
        number_of_sales,
        revenue,
        -- Extract date parts for seasonality analysis
        dayofweek(sale_date) as day_of_week,
        dayofmonth(sale_date) as day_of_month,
        month(sale_date) as month,
        quarter(sale_date) as quarter
    from sales_history
),

weekly_sales as (
    select
        article_id,
        article_number,
        description,
        category,
        subcategory,
        brand,
        supplier,
        price_tier,
        date_trunc('week', sale_date) as week_start_date,
        sum(quantity_sold) as weekly_quantity_sold,
        sum(number_of_sales) as weekly_number_of_sales,
        sum(revenue) as weekly_revenue,
        avg(quantity_sold) as avg_daily_quantity_sold,
        week(sale_date) as week_of_year
    from daily_sales
    group by 
        article_id,
        article_number,
        description,
        category,
        subcategory,
        brand,
        supplier,
        price_tier,
        week_start_date,
        week_of_year
),

monthly_sales as (
    select
        article_id,
        article_number,
        description,
        category,
        subcategory,
        brand,
        supplier,
        price_tier,
        date_trunc('month', sale_date) as month_start_date,
        sum(quantity_sold) as monthly_quantity_sold,
        sum(number_of_sales) as monthly_number_of_sales,
        sum(revenue) as monthly_revenue,
        avg(quantity_sold) as avg_daily_quantity_sold,
        month(sale_date) as month_of_year
    from daily_sales
    group by 
        article_id,
        article_number,
        description,
        category,
        subcategory,
        brand,
        supplier,
        price_tier,
        month_start_date,
        month_of_year
),

-- Calculate moving averages and trends
moving_averages as (
    select
        article_id,
        sale_date,
        quantity_sold,
        
        -- Calculate 7-day moving average
        avg(quantity_sold) over (
            partition by article_id 
            order by sale_date 
            rows between 6 preceding and current row
        ) as ma_7_day,
        
        -- Calculate 30-day moving average
        avg(quantity_sold) over (
            partition by article_id 
            order by sale_date 
            rows between 29 preceding and current row
        ) as ma_30_day,
        
        -- Calculate 90-day moving average
        avg(quantity_sold) over (
            partition by article_id 
            order by sale_date 
            rows between 89 preceding and current row
        ) as ma_90_day
    from daily_sales
),

-- Calculate seasonality factors
seasonality as (
    select
        article_id,
        day_of_week,
        avg(quantity_sold) as avg_qty_by_day_of_week,
        
        -- Calculate day of week seasonality factor
        avg(quantity_sold) / nullif(
            avg(avg(quantity_sold)) over (partition by article_id),
            0
        ) as day_of_week_factor
    from daily_sales
    group by article_id, day_of_week
),

monthly_seasonality as (
    select
        article_id,
        month_of_year,
        avg(monthly_quantity_sold) as avg_qty_by_month,
        
        -- Calculate month seasonality factor
        avg(monthly_quantity_sold) / nullif(
            avg(avg(monthly_quantity_sold)) over (partition by article_id),
            0
        ) as month_factor
    from monthly_sales
    group by article_id, month_of_year
),

-- Calculate recent sales statistics for forecasting
recent_stats as (
    select
        article_id,
        
        -- Last 30 days
        sum(case when sale_date >= dateadd('day', -30, current_date()) then quantity_sold else 0 end) as qty_last_30d,
        avg(case when sale_date >= dateadd('day', -30, current_date()) then quantity_sold else null end) as avg_daily_qty_last_30d,
        
        -- Last 90 days
        sum(case when sale_date >= dateadd('day', -90, current_date()) then quantity_sold else 0 end) as qty_last_90d,
        avg(case when sale_date >= dateadd('day', -90, current_date()) then quantity_sold else null end) as avg_daily_qty_last_90d,
        
        -- Last 365 days
        sum(quantity_sold) as qty_last_365d,
        avg(quantity_sold) as avg_daily_qty_last_365d,
        
        -- Calculate trend (comparing last 30 days to previous 30 days)
        sum(case when sale_date >= dateadd('day', -30, current_date()) then quantity_sold else 0 end) /
        nullif(sum(case when sale_date >= dateadd('day', -60, current_date()) and 
                        sale_date < dateadd('day', -30, current_date()) then quantity_sold else 0 end), 0) - 1 as trend_factor
    from daily_sales
    group by article_id
),

-- Generate forecast dates (simplified without dbt_utils for now)
forecast_dates as (
    select dateadd('day', seq4(), current_date()) as date_day
    from table(generator(rowcount => 90))
),

-- Create the final forecast
demand_forecast as (
    select
        a.article_id,
        a.article_number,
        a.description,
        a.category,
        a.subcategory,
        a.brand,
        a.supplier,
        a.price_tier,
        d.date_day as forecast_date,
        
        -- Extract date parts for applying seasonality
        dayofweek(d.date_day) as day_of_week,
        month(d.date_day) as month_of_year,
        
        -- Base forecast using recent average
        rs.avg_daily_qty_last_90d as base_forecast,
        
        -- Apply trend factor (capped to prevent extreme values)
        case
            when rs.trend_factor > 0.5 then 1.5
            when rs.trend_factor < -0.5 then 0.5
            else 1 + coalesce(rs.trend_factor, 0)
        end as applied_trend_factor,
        
        -- Apply day of week seasonality
        coalesce(s.day_of_week_factor, 1) as day_of_week_factor,
        
        -- Apply monthly seasonality
        coalesce(ms.month_factor, 1) as month_factor,
        
        -- Calculate final forecast
        round(
            rs.avg_daily_qty_last_90d * 
            case
                when rs.trend_factor > 0.5 then 1.5
                when rs.trend_factor < -0.5 then 0.5
                else 1 + coalesce(rs.trend_factor, 0)
            end *
            coalesce(s.day_of_week_factor, 1) *
            coalesce(ms.month_factor, 1),
            2
        ) as forecasted_daily_demand,
        
        -- Add cumulative forecast
        sum(
            round(
                rs.avg_daily_qty_last_90d * 
                case
                    when rs.trend_factor > 0.5 then 1.5
                    when rs.trend_factor < -0.5 then 0.5
                    else 1 + coalesce(rs.trend_factor, 0)
                end *
                coalesce(s.day_of_week_factor, 1) *
                coalesce(ms.month_factor, 1),
                2
            )
        ) over (
            partition by a.article_id 
            order by d.date_day 
            rows between unbounded preceding and current row
        ) as cumulative_forecasted_demand,
        
        -- Historical sales statistics
        rs.avg_daily_qty_last_30d,
        rs.avg_daily_qty_last_90d,
        rs.avg_daily_qty_last_365d,
        rs.qty_last_30d,
        rs.qty_last_90d,
        rs.qty_last_365d,
        
        -- Add confidence level based on data quality
        case
            when rs.qty_last_365d > 100 and rs.avg_daily_qty_last_30d > 0 then 'High'
            when rs.qty_last_90d > 30 and rs.avg_daily_qty_last_30d > 0 then 'Medium'
            when rs.qty_last_30d > 0 then 'Low'
            else 'Very Low'
        end as forecast_confidence,
        
        -- Generate forecast timestamp
        current_timestamp() as generated_at,
        
        -- Add tenant_id
        a.tenant_id
        
    from "dbt_mercurios_dev"."main_staging"."stg_prohandel__articles" a
    cross join forecast_dates d
    left join recent_stats rs on a.article_id = rs.article_id
    left join seasonality s on a.article_id = s.article_id and dayofweek(d.date_day) = s.day_of_week
    left join monthly_seasonality ms on a.article_id = ms.article_id and month(d.date_day) = ms.month_of_year
    where rs.avg_daily_qty_last_90d > 0  -- Only forecast for items with recent sales
)

select * from demand_forecast