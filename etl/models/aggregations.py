"""
Database models for aggregated data in the Mercurios.ai ETL pipeline.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SalesDailyAggregation(Base):
    """Daily sales aggregation model."""
    __tablename__ = 'sales_daily_aggregation'
    
    id = Column(Integer, primary_key=True)
    date = Column(String, nullable=False, index=True)
    article_id = Column(String, nullable=False, index=True)
    location_id = Column(String, nullable=False, index=True)
    total_quantity = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<SalesDailyAggregation(date='{self.date}', article_id='{self.article_id}', location_id='{self.location_id}')>"


class SalesWeeklyAggregation(Base):
    """Weekly sales aggregation model."""
    __tablename__ = 'sales_weekly_aggregation'
    
    id = Column(Integer, primary_key=True)
    week_start_date = Column(String, nullable=False, index=True)
    article_id = Column(String, nullable=False, index=True)
    location_id = Column(String, nullable=False, index=True)
    total_quantity = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    daily_average_quantity = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<SalesWeeklyAggregation(week_start_date='{self.week_start_date}', article_id='{self.article_id}', location_id='{self.location_id}')>"


class SalesMonthlyAggregation(Base):
    """Monthly sales aggregation model."""
    __tablename__ = 'sales_monthly_aggregation'
    
    id = Column(Integer, primary_key=True)
    month = Column(String, nullable=False, index=True)
    article_id = Column(String, nullable=False, index=True)
    location_id = Column(String, nullable=False, index=True)
    total_quantity = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    daily_average_quantity = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<SalesMonthlyAggregation(month='{self.month}', article_id='{self.article_id}', location_id='{self.location_id}')>"


class InventoryHistory(Base):
    """Inventory history model."""
    __tablename__ = 'inventory_history'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(String, nullable=False, index=True)
    branch_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    days_of_supply = Column(Float, nullable=True)
    reorder_point = Column(Integer, nullable=True)
    safety_stock = Column(Integer, nullable=True)
    stock_status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<InventoryHistory(article_id='{self.article_id}', branch_id='{self.branch_id}', timestamp='{self.timestamp}')>"


class CustomerPurchasePattern(Base):
    """Customer purchase pattern model."""
    __tablename__ = 'customer_purchase_pattern'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, nullable=False, index=True, unique=True)
    preferred_categories = Column(JSON, nullable=True)
    preferred_products = Column(JSON, nullable=True)
    purchase_time_distribution = Column(JSON, nullable=True)
    purchase_day_distribution = Column(JSON, nullable=True)
    purchase_month_distribution = Column(JSON, nullable=True)
    basket_analysis = Column(JSON, nullable=True)
    average_basket_size = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<CustomerPurchasePattern(customer_id='{self.customer_id}')>"


class ArticleFeatures(Base):
    """Article features model for transformed article data."""
    __tablename__ = 'article_features'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(String, nullable=False, index=True, unique=True)
    normalized_article_id = Column(String, nullable=False, index=True)
    inventory_turnover_rate = Column(Float, nullable=True)
    seasonal_indices = Column(JSON, nullable=True)
    lead_time_days = Column(Float, nullable=True)
    product_category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<ArticleFeatures(article_id='{self.article_id}')>"


class SupplierMetrics(Base):
    """Supplier metrics model."""
    __tablename__ = 'supplier_metrics'
    
    id = Column(Integer, primary_key=True)
    supplier_id = Column(String, nullable=False, index=True, unique=True)
    order_frequency = Column(JSON, nullable=True)  # orders per day/week/month
    average_order_size = Column(JSON, nullable=True)  # items, amount, unique products
    average_lead_time = Column(Float, nullable=True)  # days
    on_time_delivery_rate = Column(Float, nullable=True)  # percentage
    order_volume_trend = Column(JSON, nullable=True)  # monthly volumes and trend
    reliability_score = Column(Float, nullable=True)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<SupplierMetrics(supplier_id='{self.supplier_id}')>"
