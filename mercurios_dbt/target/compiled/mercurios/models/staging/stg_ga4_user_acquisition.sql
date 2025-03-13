with user_source_medium as (
    select 
        date_date,
        property_id,
        first_user_source,
        first_user_medium,
        first_user_campaign,
        first_user_google_ads_ad_network_type,
        first_user_google_ads_ad_group_name,
        active_users,
        new_users,
        engaged_sessions,
        engagement_rate,
        engagement_time_msec,
        total_revenue,
        total_revenue_per_user,
        transactions,
        transactions_per_user,
        conversions,
        conversions_per_user,
        ecommerce_purchases,
        ecommerce_purchases_per_user
    from MERCURIOS_DATA.GOOGLE_ANALYTICS_4.USER_ACQUISITION_FIRST_USER_SOURCE_MEDIUM_REPORT
),

user_campaign as (
    select 
        date_date,
        property_id,
        first_user_campaign,
        sum(active_users) as total_active_users,
        sum(new_users) as total_new_users,
        sum(engaged_sessions) as total_engaged_sessions,
        sum(total_revenue) as total_campaign_revenue,
        sum(transactions) as total_campaign_transactions,
        sum(conversions) as total_campaign_conversions,
        sum(ecommerce_purchases) as total_campaign_purchases
    from MERCURIOS_DATA.GOOGLE_ANALYTICS_4.USER_ACQUISITION_FIRST_USER_CAMPAIGN_REPORT
    group by 1, 2, 3
),

demographic_data as (
    select 
        date_date,
        property_id,
        country,
        region,
        city,
        sum(active_users) as total_users_by_location,
        sum(new_users) as new_users_by_location,
        sum(total_revenue) as total_revenue_by_location,
        sum(transactions) as transactions_by_location
    from MERCURIOS_DATA.GOOGLE_ANALYTICS_4.DEMOGRAPHIC_CITY_REPORT
    group by 1, 2, 3, 4, 5
),

combined as (
    select 
        u.date_date,
        u.property_id,
        u.first_user_source,
        u.first_user_medium,
        u.first_user_campaign,
        u.active_users,
        u.new_users,
        u.engaged_sessions,
        u.engagement_rate,
        u.total_revenue,
        u.transactions,
        u.conversions,
        u.ecommerce_purchases,
        
        -- Join with campaign data
        c.total_active_users as campaign_active_users,
        c.total_new_users as campaign_new_users,
        c.total_campaign_revenue,
        c.total_campaign_transactions,
        
        -- Calculate user value metrics
        case 
            when u.active_users > 0 then u.total_revenue / u.active_users 
            else 0 
        end as revenue_per_user,
        
        case 
            when u.active_users > 0 then u.transactions / u.active_users 
            else 0 
        end as transactions_per_user,
        
        case 
            when u.active_users > 0 then u.conversions / u.active_users 
            else 0 
        end as conversions_per_user,
        
        -- Add user acquisition categorization
        case
            when u.first_user_source = 'google' and u.first_user_medium = 'organic' then 'Organic Search'
            when u.first_user_source = 'google' and u.first_user_medium = 'cpc' then 'Paid Search'
            when u.first_user_medium = 'email' then 'Email Marketing'
            when u.first_user_medium = 'social' then 'Social Media'
            when u.first_user_medium = 'referral' then 'Referral'
            when u.first_user_medium = 'direct' then 'Direct'
            else 'Other'
        end as acquisition_channel,
        
        -- Add user value categorization
        case
            when u.total_revenue > 500 then 'High Value'
            when u.total_revenue > 100 then 'Medium Value'
            when u.total_revenue > 0 then 'Low Value'
            else 'No Purchase'
        end as user_value_segment,
        
        -- Add metadata fields
        current_timestamp() as dbt_updated_at,
        'b1e47044-e608-4bc9-85bd-9d85edb5d40b' as dbt_updated_by,
        'stg_ga4_user_acquisition' as dbt_model
    from user_source_medium u
    left join user_campaign c
        on u.date_date = c.date_date
        and u.property_id = c.property_id
        and u.first_user_campaign = c.first_user_campaign
)

select * from combined