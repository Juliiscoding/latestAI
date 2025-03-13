with inventory as (
    select * from {{ ref('stg_prohandel__inventory') }}
),

articles as (
    select * from {{ ref('stg_prohandel__articles') }}
),

sales_last_30_days as (
    select
        article_number,
        sum(quantity) as quantity_sold_30d,
        count(distinct sale_id) as num_sales_30d
    from {{ ref('stg_prohandel__sales') }}
    where sale_date >= dateadd('day', -30, current_date)
    group by article_number
),

inventory_with_sales as (
    select
        i.*,
        a.article_name,
        a.price,
        a.cost_price,
        a.margin_percentage,
        a.price_tier,
        coalesce(s.quantity_sold_30d, 0) as quantity_sold_30d,
        coalesce(s.num_sales_30d, 0) as num_sales_30d,
        
        -- Calculate inventory value
        i.quantity * a.cost_price as inventory_value,
        
        -- Calculate days of supply
        case
            when coalesce(s.quantity_sold_30d, 0) > 0 
            then i.quantity / (s.quantity_sold_30d / 30.0)
            else null
        end as days_of_supply,
        
        -- Calculate turnover rate (annualized)
        case
            when i.quantity > 0 and coalesce(s.quantity_sold_30d, 0) > 0
            then (s.quantity_sold_30d / 30.0) * 365 / i.quantity
            else 0
        end as annual_turnover_rate
    from inventory i
    left join articles a on i.article_number = a.article_number
    left join sales_last_30_days s on i.article_number = s.article_number
)

select
    *,
    -- Classify inventory based on days of supply
    case
        when days_of_supply is null then 'no_sales'
        when days_of_supply <= 7 then 'critical_low'
        when days_of_supply > 7 and days_of_supply <= 30 then 'low'
        when days_of_supply > 30 and days_of_supply <= 90 then 'adequate'
        when days_of_supply > 90 and days_of_supply <= 180 then 'high'
        else 'excess'
    end as days_of_supply_category,
    
    -- ABC classification based on inventory value
    case
        when inventory_value > 1000 then 'A'
        when inventory_value > 100 and inventory_value <= 1000 then 'B'
        else 'C'
    end as abc_class
from inventory_with_sales
