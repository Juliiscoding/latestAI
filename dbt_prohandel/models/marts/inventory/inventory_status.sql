with inventory_metrics as (
    select * from {{ ref('int_inventory_with_metrics') }}
)

select
    warehouse_id,
    article_number,
    article_name,
    quantity,
    min_stock_level,
    max_stock_level,
    stock_status,
    days_of_supply,
    days_of_supply_category,
    annual_turnover_rate,
    quantity_sold_30d,
    abc_class,
    price_tier,
    inventory_value,
    
    -- Calculate reorder point based on sales velocity and lead time
    -- Assuming 7-day lead time and 1.5 safety stock factor
    greatest(
        min_stock_level,
        ceiling((quantity_sold_30d / 30.0) * 7 * 1.5)
    ) as recommended_reorder_point,
    
    -- Calculate reorder quantity
    greatest(
        ceiling((quantity_sold_30d / 30.0) * 30), -- 30-day supply
        max_stock_level - quantity
    ) as recommended_reorder_quantity,
    
    -- Flag items that need reordering
    case
        when quantity <= min_stock_level then true
        when days_of_supply <= 14 then true
        else false
    end as needs_reorder,
    
    -- Flag slow-moving inventory
    case
        when annual_turnover_rate < 1 and quantity > min_stock_level then true
        else false
    end as slow_moving,
    
    -- Flag excess inventory
    case
        when days_of_supply > 180 and quantity > max_stock_level then true
        else false
    end as excess_inventory,
    
    last_updated
from inventory_metrics
