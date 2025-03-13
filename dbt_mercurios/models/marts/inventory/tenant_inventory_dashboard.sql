{{
  config(
    materialized = 'table',
    cluster_by = ['tenant_id', 'warehouse_id']
  )
}}

with inventory_status as (
    select 
        *,
        -- Extract tenant_id from the data based on your multi-tenant architecture
        -- This assumes tenant_id is stored in the inventory records
        -- If not available directly, it could be joined from another table
        tenant_id
    from {{ ref('inventory_status') }}
),

reorder_recommendations as (
    select * from {{ ref('reorder_recommendations') }}
),

-- Aggregate metrics by tenant and warehouse
tenant_warehouse_metrics as (
    select
        tenant_id,
        warehouse_id,
        count(distinct article_id) as total_articles,
        sum(quantity) as total_quantity,
        sum(inventory_value) as total_inventory_value,
        sum(potential_revenue) as total_potential_revenue,
        
        -- Stock level counts
        count(case when stock_level = 'Out of Stock' then 1 end) as out_of_stock_count,
        count(case when stock_level = 'Low Stock' then 1 end) as low_stock_count,
        count(case when stock_level = 'Medium Stock' then 1 end) as medium_stock_count,
        count(case when stock_level = 'High Stock' then 1 end) as high_stock_count,
        
        -- Risk level counts
        count(case when stockout_risk = 'Stockout' then 1 end) as stockout_count,
        count(case when stockout_risk = 'Critical' then 1 end) as critical_risk_count,
        count(case when stockout_risk = 'Warning' then 1 end) as warning_risk_count,
        count(case when stockout_risk = 'Normal' then 1 end) as normal_risk_count,
        
        -- Inventory health metrics
        sum(case when is_excess_inventory then inventory_value else 0 end) as excess_inventory_value,
        sum(case when is_slow_moving then inventory_value else 0 end) as slow_moving_value,
        
        -- Reorder metrics
        sum(case when r.needs_reorder then 1 else 0 end) as reorder_needed_count,
        sum(r.recommended_order_quantity) as total_recommended_order_quantity,
        sum(r.order_cost) as total_order_cost,
        
        -- ABC analysis counts
        count(case when abc_class = 'A' then 1 end) as class_a_count,
        count(case when abc_class = 'B' then 1 end) as class_b_count,
        count(case when abc_class = 'C' then 1 end) as class_c_count,
        count(case when abc_class = 'D' then 1 end) as class_d_count,
        
        -- Calculate percentages
        (count(case when stock_level = 'Out of Stock' then 1 end) * 100.0 / 
            nullif(count(distinct article_id), 0)) as out_of_stock_percent,
        (count(case when stock_level = 'Low Stock' then 1 end) * 100.0 / 
            nullif(count(distinct article_id), 0)) as low_stock_percent,
        (sum(case when is_excess_inventory then inventory_value else 0 end) * 100.0 / 
            nullif(sum(inventory_value), 0)) as excess_inventory_percent,
        (sum(case when is_slow_moving then inventory_value else 0 end) * 100.0 / 
            nullif(sum(inventory_value), 0)) as slow_moving_percent
    from inventory_status i
    left join reorder_recommendations r on i.inventory_id = r.inventory_id
    group by tenant_id, warehouse_id
),

-- Aggregate metrics by tenant, warehouse, and category
tenant_category_metrics as (
    select
        tenant_id,
        warehouse_id,
        category,
        count(distinct article_id) as total_articles,
        sum(quantity) as total_quantity,
        sum(inventory_value) as total_inventory_value,
        sum(potential_revenue) as total_potential_revenue,
        
        -- Stock level counts
        count(case when stock_level = 'Out of Stock' then 1 end) as out_of_stock_count,
        count(case when stock_level = 'Low Stock' then 1 end) as low_stock_count,
        
        -- Risk level counts
        count(case when stockout_risk = 'Stockout' or stockout_risk = 'Critical' then 1 end) as high_risk_count,
        
        -- Inventory health metrics
        sum(case when is_excess_inventory then inventory_value else 0 end) as excess_inventory_value,
        sum(case when is_slow_moving then inventory_value else 0 end) as slow_moving_value,
        
        -- Reorder metrics
        sum(case when r.needs_reorder then 1 else 0 end) as reorder_needed_count,
        sum(r.recommended_order_quantity) as total_recommended_order_quantity,
        sum(r.order_cost) as total_order_cost,
        
        -- ABC analysis counts
        count(case when abc_class = 'A' then 1 end) as class_a_count,
        count(case when abc_class = 'B' then 1 end) as class_b_count,
        count(case when abc_class = 'C' then 1 end) as class_c_count,
        count(case when abc_class = 'D' then 1 end) as class_d_count
    from inventory_status i
    left join reorder_recommendations r on i.inventory_id = r.inventory_id
    group by tenant_id, warehouse_id, category
),

-- Combine all metrics with tenant isolation
tenant_inventory_dashboard as (
    select
        'warehouse' as level_type,
        tenant_id,
        warehouse_id,
        null as category,
        total_articles,
        total_quantity,
        total_inventory_value,
        total_potential_revenue,
        out_of_stock_count,
        low_stock_count,
        medium_stock_count,
        high_stock_count,
        stockout_count,
        critical_risk_count,
        warning_risk_count,
        normal_risk_count,
        excess_inventory_value,
        slow_moving_value,
        reorder_needed_count,
        total_recommended_order_quantity,
        total_order_cost,
        class_a_count,
        class_b_count,
        class_c_count,
        class_d_count,
        out_of_stock_percent,
        low_stock_percent,
        excess_inventory_percent,
        slow_moving_percent,
        current_timestamp() as generated_at
    from tenant_warehouse_metrics
    
    union all
    
    select
        'category' as level_type,
        tenant_id,
        warehouse_id,
        category,
        total_articles,
        total_quantity,
        total_inventory_value,
        total_potential_revenue,
        out_of_stock_count,
        low_stock_count,
        null as medium_stock_count,
        null as high_stock_count,
        null as stockout_count,
        null as critical_risk_count,
        null as warning_risk_count,
        null as normal_risk_count,
        excess_inventory_value,
        slow_moving_value,
        reorder_needed_count,
        total_recommended_order_quantity,
        total_order_cost,
        class_a_count,
        class_b_count,
        class_c_count,
        class_d_count,
        (out_of_stock_count * 100.0 / nullif(total_articles, 0)) as out_of_stock_percent,
        (low_stock_count * 100.0 / nullif(total_articles, 0)) as low_stock_percent,
        (excess_inventory_value * 100.0 / nullif(total_inventory_value, 0)) as excess_inventory_percent,
        (slow_moving_value * 100.0 / nullif(total_inventory_value, 0)) as slow_moving_percent,
        current_timestamp() as generated_at
    from tenant_category_metrics
)

select * from tenant_inventory_dashboard
