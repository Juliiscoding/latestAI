-- Create sample data tables for testing dbt models
USE ROLE MERCURIOS_DEVELOPER;
USE DATABASE MERCURIOS_DATA;
USE WAREHOUSE MERCURIOS_DEV_WH;
USE SCHEMA RAW;

-- Create article table
CREATE OR REPLACE TABLE article (
    article_id VARCHAR(36) PRIMARY KEY,
    article_number VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    supplier VARCHAR(100),
    purchase_price FLOAT,
    retail_price FLOAT,
    min_stock_level INT,
    max_stock_level INT,
    reorder_point INT,
    lead_time_days INT,
    is_active BOOLEAN,
    created_at TIMESTAMP_NTZ,
    updated_at TIMESTAMP_NTZ,
    tenant_id VARCHAR(36),
    _fivetran_synced TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create inventory table
CREATE OR REPLACE TABLE inventory (
    inventory_id VARCHAR(36) PRIMARY KEY,
    article_id VARCHAR(36) NOT NULL,
    warehouse_id VARCHAR(36) NOT NULL,
    quantity INT NOT NULL,
    location VARCHAR(50),
    last_count_date DATE,
    is_available BOOLEAN,
    tenant_id VARCHAR(36),
    _fivetran_synced TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);

-- Create sale table
CREATE OR REPLACE TABLE sale (
    sale_id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL,
    article_id VARCHAR(36) NOT NULL,
    quantity INT NOT NULL,
    price FLOAT NOT NULL,
    discount FLOAT,
    sale_date DATE NOT NULL,
    shop_id VARCHAR(36),
    tenant_id VARCHAR(36),
    _fivetran_synced TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);

-- Create order table (using "orders" instead of "order" since order is a reserved keyword)
CREATE OR REPLACE TABLE orders (
    order_id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(20),
    total_amount FLOAT,
    payment_method VARCHAR(50),
    tenant_id VARCHAR(36),
    _fivetran_synced TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create customer table
CREATE OR REPLACE TABLE customer (
    customer_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    tenant_id VARCHAR(36),
    _fivetran_synced TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create shop table
CREATE OR REPLACE TABLE shop (
    shop_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    tenant_id VARCHAR(36),
    _fivetran_synced TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create daily_sales_agg table
CREATE OR REPLACE TABLE daily_sales_agg (
    agg_date DATE PRIMARY KEY,
    total_sales FLOAT NOT NULL,
    total_quantity INT NOT NULL,
    order_count INT,
    average_order_value FLOAT,
    tenant_id VARCHAR(36),
    _fivetran_synced TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create article_sales_agg table
CREATE OR REPLACE TABLE article_sales_agg (
    article_id VARCHAR(36) PRIMARY KEY,
    total_sales FLOAT NOT NULL,
    total_quantity INT NOT NULL,
    last_sale_date DATE,
    tenant_id VARCHAR(36),
    _fivetran_synced TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);

-- Create warehouse_inventory_agg table
CREATE OR REPLACE TABLE warehouse_inventory_agg (
    warehouse_id VARCHAR(36) PRIMARY KEY,
    total_articles INT NOT NULL,
    total_quantity INT NOT NULL,
    last_update_date DATE,
    tenant_id VARCHAR(36),
    _fivetran_synced TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert sample data into article table
INSERT INTO article (
    article_id, article_number, description, category, subcategory, 
    brand, supplier, purchase_price, retail_price, min_stock_level,
    max_stock_level, reorder_point, lead_time_days, is_active, 
    created_at, updated_at, tenant_id
)
VALUES
    ('a1', 'ART-001', 'T-Shirt Blue L', 'Clothing', 'T-Shirts', 'FashionBrand', 'ClothingSupplier', 10.50, 24.99, 5, 50, 10, 7, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 'mercurios'),
    ('a2', 'ART-002', 'T-Shirt Red M', 'Clothing', 'T-Shirts', 'FashionBrand', 'ClothingSupplier', 10.50, 24.99, 5, 50, 10, 7, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 'mercurios'),
    ('a3', 'ART-003', 'Jeans Blue 32/32', 'Clothing', 'Jeans', 'DenimCo', 'ClothingSupplier', 25.00, 59.99, 3, 30, 5, 10, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 'mercurios'),
    ('a4', 'ART-004', 'Sneakers White 42', 'Footwear', 'Sneakers', 'ShoeBrand', 'FootwearSupplier', 35.00, 89.99, 2, 20, 4, 14, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 'mercurios'),
    ('a5', 'ART-005', 'Backpack Black', 'Accessories', 'Bags', 'BagCo', 'AccessorySupplier', 20.00, 49.99, 3, 25, 5, 10, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 'mercurios');

-- Insert sample data into inventory table
INSERT INTO inventory (
    inventory_id, article_id, warehouse_id, quantity, 
    location, last_count_date, is_available, tenant_id
)
VALUES
    ('i1', 'a1', 'w1', 25, 'A1-B2-C3', CURRENT_DATE(), TRUE, 'mercurios'),
    ('i2', 'a2', 'w1', 15, 'A1-B2-C4', CURRENT_DATE(), TRUE, 'mercurios'),
    ('i3', 'a3', 'w1', 8, 'A2-B1-C1', CURRENT_DATE(), TRUE, 'mercurios'),
    ('i4', 'a4', 'w1', 12, 'A3-B2-C2', CURRENT_DATE(), TRUE, 'mercurios'),
    ('i5', 'a5', 'w1', 6, 'A4-B3-C1', CURRENT_DATE(), TRUE, 'mercurios'),
    ('i6', 'a1', 'w2', 15, 'D1-E2-F3', CURRENT_DATE(), TRUE, 'mercurios'),
    ('i7', 'a2', 'w2', 10, 'D1-E2-F4', CURRENT_DATE(), TRUE, 'mercurios'),
    ('i8', 'a3', 'w2', 5, 'D2-E1-F1', CURRENT_DATE(), TRUE, 'mercurios');

-- Insert sample data into sale table
INSERT INTO sale (
    sale_id, order_id, article_id, quantity, 
    price, discount, sale_date, shop_id, tenant_id
)
VALUES
    ('s1', 'o1', 'a1', 2, 24.99, 0, DATEADD(day, -1, CURRENT_DATE()), 'sh1', 'mercurios'),
    ('s2', 'o1', 'a3', 1, 59.99, 5.00, DATEADD(day, -1, CURRENT_DATE()), 'sh1', 'mercurios'),
    ('s3', 'o2', 'a2', 1, 24.99, 0, DATEADD(day, -2, CURRENT_DATE()), 'sh1', 'mercurios'),
    ('s4', 'o3', 'a4', 1, 89.99, 10.00, DATEADD(day, -3, CURRENT_DATE()), 'sh2', 'mercurios'),
    ('s5', 'o4', 'a5', 1, 49.99, 0, DATEADD(day, -3, CURRENT_DATE()), 'sh2', 'mercurios'),
    ('s6', 'o5', 'a1', 1, 24.99, 0, DATEADD(day, -5, CURRENT_DATE()), 'sh1', 'mercurios'),
    ('s7', 'o6', 'a2', 2, 24.99, 2.50, DATEADD(day, -7, CURRENT_DATE()), 'sh2', 'mercurios'),
    ('s8', 'o7', 'a3', 1, 59.99, 0, DATEADD(day, -10, CURRENT_DATE()), 'sh1', 'mercurios'),
    ('s9', 'o8', 'a1', 3, 24.99, 5.00, DATEADD(day, -15, CURRENT_DATE()), 'sh2', 'mercurios'),
    ('s10', 'o9', 'a4', 1, 89.99, 0, DATEADD(day, -20, CURRENT_DATE()), 'sh1', 'mercurios');

-- Insert sample data into orders table
INSERT INTO orders (
    order_id, customer_id, order_date, status, 
    total_amount, payment_method, tenant_id
)
VALUES
    ('o1', 'c1', DATEADD(day, -1, CURRENT_DATE()), 'Completed', 109.97, 'Credit Card', 'mercurios'),
    ('o2', 'c2', DATEADD(day, -2, CURRENT_DATE()), 'Completed', 24.99, 'PayPal', 'mercurios'),
    ('o3', 'c3', DATEADD(day, -3, CURRENT_DATE()), 'Completed', 79.99, 'Credit Card', 'mercurios'),
    ('o4', 'c1', DATEADD(day, -3, CURRENT_DATE()), 'Completed', 49.99, 'Credit Card', 'mercurios'),
    ('o5', 'c4', DATEADD(day, -5, CURRENT_DATE()), 'Completed', 24.99, 'Cash', 'mercurios'),
    ('o6', 'c2', DATEADD(day, -7, CURRENT_DATE()), 'Completed', 47.48, 'PayPal', 'mercurios'),
    ('o7', 'c5', DATEADD(day, -10, CURRENT_DATE()), 'Completed', 59.99, 'Credit Card', 'mercurios'),
    ('o8', 'c3', DATEADD(day, -15, CURRENT_DATE()), 'Completed', 69.97, 'Credit Card', 'mercurios'),
    ('o9', 'c1', DATEADD(day, -20, CURRENT_DATE()), 'Completed', 89.99, 'Credit Card', 'mercurios');

-- Insert sample data into customer table
INSERT INTO customer (
    customer_id, name, email, phone, 
    address, city, postal_code, country, tenant_id
)
VALUES
    ('c1', 'John Doe', 'john.doe@example.com', '+1234567890', '123 Main St', 'New York', '10001', 'USA', 'mercurios'),
    ('c2', 'Jane Smith', 'jane.smith@example.com', '+1987654321', '456 Oak Ave', 'Los Angeles', '90001', 'USA', 'mercurios'),
    ('c3', 'Robert Johnson', 'robert.j@example.com', '+1122334455', '789 Pine Rd', 'Chicago', '60007', 'USA', 'mercurios'),
    ('c4', 'Sarah Williams', 'sarah.w@example.com', '+1555666777', '321 Elm Blvd', 'Miami', '33101', 'USA', 'mercurios'),
    ('c5', 'Michael Brown', 'michael.b@example.com', '+1999888777', '654 Cedar Ln', 'Seattle', '98101', 'USA', 'mercurios');

-- Insert sample data into shop table
INSERT INTO shop (
    shop_id, name, address, city, 
    postal_code, country, tenant_id
)
VALUES
    ('sh1', 'Downtown Store', '100 Retail Ave', 'New York', '10001', 'USA', 'mercurios'),
    ('sh2', 'Mall Outlet', '200 Shopping Ctr', 'Los Angeles', '90001', 'USA', 'mercurios');

-- Insert sample data into daily_sales_agg table
INSERT INTO daily_sales_agg (
    agg_date, total_sales, total_quantity, 
    order_count, average_order_value, tenant_id
)
VALUES
    (DATEADD(day, -1, CURRENT_DATE()), 109.97, 3, 1, 109.97, 'mercurios'),
    (DATEADD(day, -2, CURRENT_DATE()), 24.99, 1, 1, 24.99, 'mercurios'),
    (DATEADD(day, -3, CURRENT_DATE()), 129.98, 2, 2, 64.99, 'mercurios'),
    (DATEADD(day, -5, CURRENT_DATE()), 24.99, 1, 1, 24.99, 'mercurios'),
    (DATEADD(day, -7, CURRENT_DATE()), 47.48, 2, 1, 47.48, 'mercurios'),
    (DATEADD(day, -10, CURRENT_DATE()), 59.99, 1, 1, 59.99, 'mercurios'),
    (DATEADD(day, -15, CURRENT_DATE()), 69.97, 3, 1, 69.97, 'mercurios'),
    (DATEADD(day, -20, CURRENT_DATE()), 89.99, 1, 1, 89.99, 'mercurios');

-- Insert sample data into article_sales_agg table
INSERT INTO article_sales_agg (
    article_id, total_sales, total_quantity, 
    last_sale_date, tenant_id
)
VALUES
    ('a1', 124.95, 6, DATEADD(day, -1, CURRENT_DATE()), 'mercurios'),
    ('a2', 47.48, 3, DATEADD(day, -7, CURRENT_DATE()), 'mercurios'),
    ('a3', 114.98, 2, DATEADD(day, -10, CURRENT_DATE()), 'mercurios'),
    ('a4', 169.98, 2, DATEADD(day, -20, CURRENT_DATE()), 'mercurios'),
    ('a5', 49.99, 1, DATEADD(day, -3, CURRENT_DATE()), 'mercurios');

-- Insert sample data into warehouse_inventory_agg table
INSERT INTO warehouse_inventory_agg (
    warehouse_id, total_articles, total_quantity, 
    last_update_date, tenant_id
)
VALUES
    ('w1', 5, 66, CURRENT_DATE(), 'mercurios'),
    ('w2', 3, 30, CURRENT_DATE(), 'mercurios');
