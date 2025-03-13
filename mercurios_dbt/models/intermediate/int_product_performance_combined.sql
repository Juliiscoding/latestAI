with prohandel_articles as (
    select *
    from {{ ref('stg_articles') }}
),

prohandel_inventory as (
    select *
    from {{ ref('stg_inventory') }}
),

prohandel_sales as (
    select *
    from {{ ref('stg_sales') }}
),

ga4_product_performance as (
    select *
    from {{ ref('stg_ga4_product_performance') }}
),

-- Aggregate sales data by article
article_sales as (
    select
        article_id,
        sum(quantity) as total_quantity_sold,
        sum(total_price) as total_sales_amount,
        count(distinct order_id) as order_count,
        count(distinct customer_id) as customer_count,
        min(sale_date) as first_sale_date,
        max(sale_date) as last_sale_date
    from prohandel_sales
    group by 1
),

-- Aggregate inventory data by article
article_inventory as (
    select
        article_id,
        sum(quantity) as total_inventory,
        avg(quantity) as avg_inventory,
        count(distinct warehouse_id) as warehouse_count,
        min(last_updated) as earliest_inventory_date,
        max(last_updated) as latest_inventory_date
    from prohandel_inventory
    group by 1
),

-- Join all data sources
combined as (
    select
        -- Article information
        a.article_id,
        a.article_name,
        a.article_number,
        a.article_description,
        a.brand,
        a.category,
        a.subcategory,
        a.price,
        a.cost,
        a.margin,
        a.margin_percentage,
        a.price_tier,
        
        -- Inventory information
        i.total_inventory,
        i.avg_inventory,
        i.warehouse_count,
        
        -- Sales information
        s.total_quantity_sold,
        s.total_sales_amount,
        s.order_count,
        s.customer_count,
        s.first_sale_date,
        s.last_sale_date,
        
        -- Calculate offline metrics
        case 
            when i.total_inventory > 0 and s.total_quantity_sold > 0 
            then s.total_quantity_sold / i.total_inventory 
            else 0 
        end as inventory_turnover_ratio,
        
        case 
            when s.total_quantity_sold > 0 
            then datediff('day', s.first_sale_date, s.last_sale_date) / s.total_quantity_sold 
            else 0 
        end as days_per_unit_sold,
        
        -- GA4 online metrics
        g.item_revenue as online_revenue,
        g.transactions as online_transactions,
        g.quantity as online_quantity_sold,
        g.page_views,
        g.active_users as online_users,
        g.engagement_rate,
        g.conversion_rate as online_conversion_rate,
        g.daily_sales_rate as online_daily_sales_rate,
        g.revenue_category as online_revenue_category,
        g.volume_category as online_volume_category,
        
        -- Combined metrics
        coalesce(s.total_sales_amount, 0) + coalesce(g.total_revenue, 0) as combined_revenue,
        coalesce(s.total_quantity_sold, 0) + coalesce(g.total_quantity, 0) as combined_quantity,
        
        -- Product performance categorization
        case
            when (coalesce(s.total_sales_amount, 0) > 1000 or coalesce(g.total_revenue, 0) > 1000) then 'High Value'
            when (coalesce(s.total_sales_amount, 0) > 500 or coalesce(g.total_revenue, 0) > 500) then 'Medium Value'
            when (coalesce(s.total_sales_amount, 0) > 100 or coalesce(g.total_revenue, 0) > 100) then 'Low Value'
            else 'Very Low Value'
        end as combined_value_category,
        
        case
            when (coalesce(s.total_quantity_sold, 0) > 50 or coalesce(g.total_quantity, 0) > 50) then 'High Volume'
            when (coalesce(s.total_quantity_sold, 0) > 20 or coalesce(g.total_quantity, 0) > 20) then 'Medium Volume'
            when (coalesce(s.total_quantity_sold, 0) > 5 or coalesce(g.total_quantity, 0) > 5) then 'Low Volume'
            else 'Very Low Volume'
        end as combined_volume_category,
        
        -- Channel preference
        case
            when coalesce(s.total_sales_amount, 0) > coalesce(g.total_revenue, 0) * 2 then 'Strongly Offline'
            when coalesce(s.total_sales_amount, 0) > coalesce(g.total_revenue, 0) then 'Moderately Offline'
            when coalesce(g.total_revenue, 0) > coalesce(s.total_sales_amount, 0) * 2 then 'Strongly Online'
            when coalesce(g.total_revenue, 0) > coalesce(s.total_sales_amount, 0) then 'Moderately Online'
            else 'Balanced'
        end as channel_preference,
        
        -- Add metadata fields
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from prohandel_articles a
    left join article_inventory i
        on a.article_id = i.article_id
    left join article_sales s
        on a.article_id = s.article_id
    left join ga4_product_performance g
        on a.article_number = g.item_id
        or a.article_name = g.item_name
)

select * from combined
