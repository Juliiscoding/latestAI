"""
Data warehouse schema for the Mercurios.ai ETL pipeline.
Implements a star schema optimized for inventory analytics.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    ForeignKey, Table, MetaData, Index, Boolean,
    Text, JSON, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = MetaData()

# Dimension Tables

class DimDate(Base):
    """Date dimension table."""
    __tablename__ = 'dim_date'
    
    date_id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)
    day = Column(Integer, nullable=False)
    day_name = Column(String(10), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    day_of_year = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    week_of_year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    month_name = Column(String(10), nullable=False)
    quarter = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    is_weekend = Column(Boolean, nullable=False)
    is_holiday = Column(Boolean, nullable=False)
    season = Column(String(10), nullable=True)
    fiscal_year = Column(Integer, nullable=True)
    fiscal_quarter = Column(Integer, nullable=True)
    
    # Create indexes for common query patterns
    __table_args__ = (
        Index('idx_dim_date_year_month', year, month),
        Index('idx_dim_date_year_quarter', year, quarter),
    )
    
    def __repr__(self):
        return f"<DimDate(date='{self.date}', year={self.year}, month={self.month})>"


class DimProduct(Base):
    """Product dimension table."""
    __tablename__ = 'dim_product'
    
    product_id = Column(Integer, primary_key=True)
    article_id = Column(String(50), nullable=False, unique=True, index=True)
    normalized_article_id = Column(String(50), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    product_description = Column(Text, nullable=True)
    category_id = Column(String(50), nullable=True, index=True)
    category_name = Column(String(100), nullable=True)
    subcategory_id = Column(String(50), nullable=True)
    subcategory_name = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    supplier_id = Column(String(50), nullable=True, index=True)
    unit_cost = Column(Float, nullable=True)
    unit_price = Column(Float, nullable=True)
    unit_of_measure = Column(String(20), nullable=True)
    package_size = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    dimensions = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Product features and metrics
    inventory_turnover_rate = Column(Float, nullable=True)
    seasonal_indices = Column(JSON, nullable=True)
    lead_time_days = Column(Float, nullable=True)
    
    # Create indexes for common query patterns
    __table_args__ = (
        Index('idx_dim_product_category_supplier', category_id, supplier_id),
    )
    
    def __repr__(self):
        return f"<DimProduct(article_id='{self.article_id}', product_name='{self.product_name}')>"


class DimLocation(Base):
    """Location dimension table."""
    __tablename__ = 'dim_location'
    
    location_id = Column(Integer, primary_key=True)
    branch_id = Column(String(50), nullable=False, unique=True, index=True)
    location_name = Column(String(100), nullable=False)
    location_type = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(50), nullable=True)
    region = Column(String(50), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    size_sqm = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<DimLocation(branch_id='{self.branch_id}', location_name='{self.location_name}')>"


class DimCustomer(Base):
    """Customer dimension table."""
    __tablename__ = 'dim_customer'
    
    customer_id = Column(Integer, primary_key=True)
    customer_code = Column(String(50), nullable=False, unique=True, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_type = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Customer metrics
    lifetime_value = Column(Float, nullable=True)
    purchase_frequency = Column(Float, nullable=True)
    average_order_value = Column(Float, nullable=True)
    recency_days = Column(Integer, nullable=True)
    customer_segment = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<DimCustomer(customer_code='{self.customer_code}', customer_name='{self.customer_name}')>"


class DimSupplier(Base):
    """Supplier dimension table."""
    __tablename__ = 'dim_supplier'
    
    supplier_id = Column(Integer, primary_key=True)
    supplier_code = Column(String(50), nullable=False, unique=True, index=True)
    supplier_name = Column(String(255), nullable=False)
    contact_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Supplier metrics
    average_lead_time = Column(Float, nullable=True)
    on_time_delivery_rate = Column(Float, nullable=True)
    reliability_score = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<DimSupplier(supplier_code='{self.supplier_code}', supplier_name='{self.supplier_name}')>"


# Fact Tables

class FactSales(Base):
    """Sales fact table."""
    __tablename__ = 'fact_sales'
    
    sale_id = Column(Integer, primary_key=True)
    date_id = Column(Integer, ForeignKey('dim_date.date_id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('dim_product.product_id'), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey('dim_location.location_id'), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('dim_customer.customer_id'), nullable=False, index=True)
    
    # Measures
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_amount = Column(Float, nullable=True, default=0.0)
    net_amount = Column(Float, nullable=False)
    gross_amount = Column(Float, nullable=False)
    cost_amount = Column(Float, nullable=True)
    profit_amount = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    
    # Additional attributes
    invoice_number = Column(String(50), nullable=True)
    transaction_id = Column(String(50), nullable=True)
    
    # Relationships
    date = relationship("DimDate")
    product = relationship("DimProduct")
    location = relationship("DimLocation")
    customer = relationship("DimCustomer")
    
    # Create indexes for common query patterns
    __table_args__ = (
        Index('idx_fact_sales_date_product', date_id, product_id),
        Index('idx_fact_sales_date_location', date_id, location_id),
        Index('idx_fact_sales_date_customer', date_id, customer_id),
    )
    
    def __repr__(self):
        return f"<FactSales(sale_id={self.sale_id}, quantity={self.quantity}, net_amount={self.net_amount})>"


class FactInventory(Base):
    """Inventory fact table."""
    __tablename__ = 'fact_inventory'
    
    inventory_id = Column(Integer, primary_key=True)
    date_id = Column(Integer, ForeignKey('dim_date.date_id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('dim_product.product_id'), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey('dim_location.location_id'), nullable=False, index=True)
    
    # Measures
    quantity_on_hand = Column(Integer, nullable=False)
    quantity_reserved = Column(Integer, nullable=True, default=0)
    quantity_available = Column(Integer, nullable=True)
    quantity_on_order = Column(Integer, nullable=True, default=0)
    quantity_in_transit = Column(Integer, nullable=True, default=0)
    days_of_supply = Column(Float, nullable=True)
    reorder_point = Column(Integer, nullable=True)
    safety_stock = Column(Integer, nullable=True)
    stock_status = Column(String(20), nullable=True)  # In Stock, Low Stock, Out of Stock
    
    # Additional attributes
    unit_cost = Column(Float, nullable=True)
    total_value = Column(Float, nullable=True)
    
    # Relationships
    date = relationship("DimDate")
    product = relationship("DimProduct")
    location = relationship("DimLocation")
    
    # Create indexes for common query patterns
    __table_args__ = (
        Index('idx_fact_inventory_date_product', date_id, product_id),
        Index('idx_fact_inventory_date_location', date_id, location_id),
        Index('idx_fact_inventory_product_location', product_id, location_id),
        UniqueConstraint('date_id', 'product_id', 'location_id', name='uq_fact_inventory_date_product_location'),
    )
    
    def __repr__(self):
        return f"<FactInventory(inventory_id={self.inventory_id}, quantity_on_hand={self.quantity_on_hand})>"


class FactOrders(Base):
    """Orders fact table."""
    __tablename__ = 'fact_orders'
    
    order_id = Column(Integer, primary_key=True)
    date_id = Column(Integer, ForeignKey('dim_date.date_id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('dim_product.product_id'), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey('dim_location.location_id'), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey('dim_supplier.supplier_id'), nullable=False, index=True)
    
    # Measures
    quantity_ordered = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    
    # Additional attributes
    order_number = Column(String(50), nullable=True)
    expected_delivery_date_id = Column(Integer, ForeignKey('dim_date.date_id'), nullable=True)
    actual_delivery_date_id = Column(Integer, ForeignKey('dim_date.date_id'), nullable=True)
    order_status = Column(String(20), nullable=True)  # Ordered, In Transit, Delivered, Cancelled
    
    # Relationships
    date = relationship("DimDate", foreign_keys=[date_id])
    product = relationship("DimProduct")
    location = relationship("DimLocation")
    supplier = relationship("DimSupplier")
    expected_delivery_date = relationship("DimDate", foreign_keys=[expected_delivery_date_id])
    actual_delivery_date = relationship("DimDate", foreign_keys=[actual_delivery_date_id])
    
    # Create indexes for common query patterns
    __table_args__ = (
        Index('idx_fact_orders_date_product', date_id, product_id),
        Index('idx_fact_orders_date_supplier', date_id, supplier_id),
        Index('idx_fact_orders_product_supplier', product_id, supplier_id),
    )
    
    def __repr__(self):
        return f"<FactOrders(order_id={self.order_id}, quantity_ordered={self.quantity_ordered})>"


# Aggregated Fact Tables (for performance optimization)

class FactSalesDaily(Base):
    """Daily sales aggregation fact table."""
    __tablename__ = 'fact_sales_daily'
    
    id = Column(Integer, primary_key=True)
    date_id = Column(Integer, ForeignKey('dim_date.date_id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('dim_product.product_id'), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey('dim_location.location_id'), nullable=False, index=True)
    
    # Measures
    total_quantity = Column(Integer, nullable=False)
    total_net_amount = Column(Float, nullable=False)
    total_gross_amount = Column(Float, nullable=False)
    average_unit_price = Column(Float, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    
    # Relationships
    date = relationship("DimDate")
    product = relationship("DimProduct")
    location = relationship("DimLocation")
    
    # Create indexes and constraints
    __table_args__ = (
        UniqueConstraint('date_id', 'product_id', 'location_id', name='uq_fact_sales_daily_date_product_location'),
    )
    
    def __repr__(self):
        return f"<FactSalesDaily(date_id={self.date_id}, product_id={self.product_id}, total_quantity={self.total_quantity})>"


class FactSalesWeekly(Base):
    """Weekly sales aggregation fact table."""
    __tablename__ = 'fact_sales_weekly'
    
    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey('dim_product.product_id'), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey('dim_location.location_id'), nullable=False, index=True)
    
    # Measures
    total_quantity = Column(Integer, nullable=False)
    total_net_amount = Column(Float, nullable=False)
    total_gross_amount = Column(Float, nullable=False)
    average_unit_price = Column(Float, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    daily_average_quantity = Column(Float, nullable=False)
    
    # Relationships
    product = relationship("DimProduct")
    location = relationship("DimLocation")
    
    # Create indexes and constraints
    __table_args__ = (
        Index('idx_fact_sales_weekly_year_week', year, week),
        UniqueConstraint('year', 'week', 'product_id', 'location_id', name='uq_fact_sales_weekly_year_week_product_location'),
    )
    
    def __repr__(self):
        return f"<FactSalesWeekly(year={self.year}, week={self.week}, product_id={self.product_id})>"


class FactSalesMonthly(Base):
    """Monthly sales aggregation fact table."""
    __tablename__ = 'fact_sales_monthly'
    
    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey('dim_product.product_id'), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey('dim_location.location_id'), nullable=False, index=True)
    
    # Measures
    total_quantity = Column(Integer, nullable=False)
    total_net_amount = Column(Float, nullable=False)
    total_gross_amount = Column(Float, nullable=False)
    average_unit_price = Column(Float, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    daily_average_quantity = Column(Float, nullable=False)
    
    # Relationships
    product = relationship("DimProduct")
    location = relationship("DimLocation")
    
    # Create indexes and constraints
    __table_args__ = (
        Index('idx_fact_sales_monthly_year_month', year, month),
        UniqueConstraint('year', 'month', 'product_id', 'location_id', name='uq_fact_sales_monthly_year_month_product_location'),
    )
    
    def __repr__(self):
        return f"<FactSalesMonthly(year={self.year}, month={self.month}, product_id={self.product_id})>"
