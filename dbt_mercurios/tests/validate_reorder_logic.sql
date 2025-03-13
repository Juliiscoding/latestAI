-- Custom test to validate reorder recommendation logic
-- This test checks that high-priority reorder recommendations have appropriate values

WITH validation AS (
    SELECT
        tenant_id,
        article_id,
        article_name,
        current_stock,
        reorder_point,
        safety_stock,
        reorder_priority,
        days_until_stockout,
        -- Flag records that violate business logic
        CASE
            -- High priority items should have current stock below reorder point
            WHEN reorder_priority = 'High' AND current_stock > reorder_point THEN 1
            
            -- High priority items should have days_until_stockout <= 14
            WHEN reorder_priority = 'High' AND days_until_stockout > 14 THEN 1
            
            -- Items with current_stock < safety_stock should be high priority
            WHEN current_stock < safety_stock AND reorder_priority != 'High' THEN 1
            
            -- No issues found
            ELSE 0
        END AS has_logic_error
    FROM {{ ref('reorder_recommendations') }}
)

-- Return records that fail the test
SELECT
    tenant_id,
    article_id,
    article_name,
    current_stock,
    reorder_point,
    safety_stock,
    reorder_priority,
    days_until_stockout,
    CASE
        WHEN reorder_priority = 'High' AND current_stock > reorder_point 
            THEN 'High priority but stock above reorder point'
        WHEN reorder_priority = 'High' AND days_until_stockout > 14 
            THEN 'High priority but days until stockout > 14'
        WHEN current_stock < safety_stock AND reorder_priority != 'High' 
            THEN 'Stock below safety stock but not high priority'
        ELSE 'Unknown error'
    END AS error_description
FROM validation
WHERE has_logic_error = 1
