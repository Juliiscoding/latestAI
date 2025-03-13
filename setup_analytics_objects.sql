-- Create the ANALYTICS schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS MERCURIOS_DATA.ANALYTICS;

-- Create the INVENTORY_STATUS table
CREATE OR REPLACE TABLE MERCURIOS_DATA.ANALYTICS.INVENTORY_STATUS (
    product_id VARCHAR(50),
    product_name VARCHAR(255),
    current_stock NUMBER,
    reorder_point NUMBER,
    avg_daily_sales NUMBER(10,2),
    stock_status VARCHAR(50),
    days_of_inventory NUMBER(10,2),
    last_updated TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert sample data
INSERT INTO MERCURIOS_DATA.ANALYTICS.INVENTORY_STATUS 
(product_id, product_name, current_stock, reorder_point, avg_daily_sales, stock_status, days_of_inventory)
VALUES
('P001', 'Premium Coffee Beans', 250, 100, 25.0, 'ADEQUATE', 10.0),
('P002', 'Organic Tea Assortment', 50, 75, 15.0, 'LOW', 3.3),
('P003', 'Artisanal Chocolate', 500, 150, 20.0, 'EXCESS', 25.0),
('P004', 'Specialty Honey', 120, 50, 8.0, 'ADEQUATE', 15.0),
('P005', 'Specialty Coffee Filters', 75, 100, 12.0, 'LOW', 6.25);

-- Create the REORDER_RECOMMENDATIONS table
CREATE OR REPLACE TABLE MERCURIOS_DATA.ANALYTICS.REORDER_RECOMMENDATIONS (
    product_id VARCHAR(50),
    product_name VARCHAR(255),
    current_stock NUMBER,
    recommended_order_quantity NUMBER,
    priority VARCHAR(10),
    last_updated TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert sample data
INSERT INTO MERCURIOS_DATA.ANALYTICS.REORDER_RECOMMENDATIONS
(product_id, product_name, current_stock, recommended_order_quantity, priority)
VALUES
('P002', 'Organic Tea Assortment', 50, 100, 'High'),
('P005', 'Specialty Coffee Filters', 75, 150, 'Medium'),
('P008', 'Ceramic Mugs', 120, 80, 'Low');

-- Create a stored procedure for setting tenant context
-- This is a placeholder and would be implemented based on your multi-tenancy approach
CREATE OR REPLACE PROCEDURE MERCURIOS_DATA.PUBLIC.SET_TENANT_CONTEXT(TENANT_ID VARCHAR)
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
AS
$$
    // In a real implementation, this would set session variables or apply filters
    // For now, it just returns success
    return "Tenant context set to: " + TENANT_ID;
$$;

-- Grant permissions
GRANT USAGE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE PUBLIC;
GRANT USAGE ON PROCEDURE MERCURIOS_DATA.PUBLIC.SET_TENANT_CONTEXT(VARCHAR) TO ROLE PUBLIC;
