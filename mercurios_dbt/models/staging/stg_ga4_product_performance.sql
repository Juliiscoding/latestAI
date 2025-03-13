{{ config(
    materialized='view',
    pre_hook=[
        "grant usage on schema {{ source('google_analytics_4', 'ECOMMERCE_PURCHASES_ITEM_ID_REPORT').database }}.{{ source('google_analytics_4', 'ECOMMERCE_PURCHASES_ITEM_ID_REPORT').schema }} to role MERCURIOS_FIVETRAN_USER",
        "grant select on {{ source('google_analytics_4', 'ECOMMERCE_PURCHASES_ITEM_ID_REPORT') }} to role MERCURIOS_FIVETRAN_USER",
        "grant select on {{ source('google_analytics_4', 'PAGES_PATH_REPORT') }} to role MERCURIOS_FIVETRAN_USER"
    ]
) }}

with ecommerce_item_id as (
    select 
        date_date,
        property_id,
        item_id,
        item_name,
        item_brand,
        item_category,
        item_category2,
        item_category3,
        item_category4,
        item_category5,
        price,
        quantity,
        item_revenue,
        purchase_revenue,
        purchase_revenue_in_usd,
        refund_value,
        refund_value_in_usd,
        shipping_value,
        shipping_value_in_usd,
        tax_value,
        tax_value_in_usd,
        unique_items,
        transactions
    from {{ source('google_analytics_4', 'ECOMMERCE_PURCHASES_ITEM_ID_REPORT') }}
),

ecommerce_item_name as (
    select 
        date_date,
        property_id,
        item_name,
        sum(quantity) as total_quantity,
        sum(item_revenue) as total_revenue,
        sum(transactions) as total_transactions,
        count(distinct date_date) as days_with_sales
    from {{ source('google_analytics_4', 'ECOMMERCE_PURCHASES_ITEM_NAME_REPORT') }}
    group by 1, 2, 3
),

page_views as (
    select 
        date_date,
        property_id,
        page_path,
        page_title,
        screen_class,
        screen_name,
        entrances,
        engaged_sessions,
        engagement_rate,
        engagement_time_msec,
        page_views,
        screen_views,
        active_users
    from {{ source('google_analytics_4', 'PAGES_PATH_REPORT') }}
),

combined as (
    select 
        e.date_date,
        e.property_id,
        e.item_id,
        e.item_name,
        e.item_brand,
        e.item_category,
        e.price,
        e.quantity,
        e.item_revenue,
        e.transactions,
        n.total_quantity,
        n.total_revenue,
        n.total_transactions,
        n.days_with_sales,
        
        -- Join with page views (assuming product pages follow a pattern like /product/[item_id])
        -- This is an example and might need adjustment based on your actual URL structure
        p.page_views,
        p.active_users,
        p.engagement_rate,
        
        -- Calculate metrics
        case 
            when n.days_with_sales > 0 then n.total_quantity / n.days_with_sales 
            else 0 
        end as daily_sales_rate,
        
        case 
            when p.page_views > 0 then (n.total_transactions * 100.0) / p.page_views 
            else 0 
        end as conversion_rate,
        
        -- Add product performance categorization
        case
            when n.total_revenue > 1000 then 'High Value'
            when n.total_revenue > 500 then 'Medium Value'
            when n.total_revenue > 100 then 'Low Value'
            else 'Very Low Value'
        end as revenue_category,
        
        case
            when n.total_quantity > 50 then 'High Volume'
            when n.total_quantity > 20 then 'Medium Volume'
            when n.total_quantity > 5 then 'Low Volume'
            else 'Very Low Volume'
        end as volume_category,
        
        -- Add metadata fields
        current_timestamp() as dbt_updated_at,
        '{{ invocation_id }}' as dbt_updated_by,
        '{{ this.name }}' as dbt_model
    from ecommerce_item_id e
    left join ecommerce_item_name n
        on e.date_date = n.date_date
        and e.property_id = n.property_id
        and e.item_name = n.item_name
    left join page_views p
        on e.date_date = p.date_date
        and e.property_id = p.property_id
        and p.page_path like '%/product/' || e.item_id || '%'
)

select * from combined
