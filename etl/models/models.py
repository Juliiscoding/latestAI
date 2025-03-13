"""
Database models for the Mercurios.ai ETL pipeline.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from etl.utils.database import Base

class BaseModel(Base):
    """Base model with common fields."""
    __abstract__ = True
    
    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    raw_data = Column(JSON)  # Store the raw JSON data for reference

class Article(BaseModel):
    """Model for articles/products."""
    __tablename__ = "articles"
    
    number = Column(Float)
    name = Column(String(255))
    description = Column(Text)
    purchase_price = Column(Float)
    sale_price = Column(Float)
    is_active = Column(Boolean, default=True)
    manufacturer_number = Column(Integer)
    supplier_article_number = Column(String(255))
    first_purchase_date = Column(DateTime)
    last_purchase_date = Column(DateTime)
    last_change = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    inventory_items = relationship("Inventory", back_populates="article")
    sales = relationship("Sale", back_populates="article")
    order_positions = relationship("OrderPosition", back_populates="article")

class Customer(BaseModel):
    """Model for customers."""
    __tablename__ = "customers"
    
    number = Column(Integer)
    name1 = Column(String(255))
    name2 = Column(String(255))
    name3 = Column(String(255))
    search_term = Column(String(255))
    revenue = Column(Float)
    bonus_value = Column(Float)
    loyalty_points = Column(Integer)
    last_change = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    sales = relationship("Sale", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")
    customer_cards = relationship("CustomerCard", back_populates="customer")

class Order(BaseModel):
    """Model for orders."""
    __tablename__ = "orders"
    
    number = Column(Integer)
    source = Column(Integer)
    created = Column(DateTime)
    supplier_number = Column(Integer)
    supplier_order_id = Column(String(255))
    merchant_number = Column(Integer)
    info = Column(Text)
    overall_discount = Column(Float)
    status = Column(Integer)
    type = Column(Integer)
    last_change = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    positions = relationship("OrderPosition", back_populates="order")
    supplier = relationship("Supplier", back_populates="orders")

class OrderPosition(BaseModel):
    """Model for order positions/items."""
    __tablename__ = "order_positions"
    
    order_id = Column(String(36), ForeignKey("orders.id"))
    article_id = Column(String(36), ForeignKey("articles.id"))
    number = Column(Integer)
    article_number = Column(Float)
    branch_number = Column(Integer)
    quantity = Column(Integer)
    price = Column(Float)
    discount = Column(Float)
    expected_arrival = Column(DateTime)
    
    # Relationships
    order = relationship("Order", back_populates="positions")
    article = relationship("Article", back_populates="order_positions")

class Sale(BaseModel):
    """Model for sales."""
    __tablename__ = "sales"
    
    article_id = Column(String(36), ForeignKey("articles.id"))
    customer_id = Column(String(36), ForeignKey("customers.id"))
    branch_id = Column(String(36), ForeignKey("branches.id"))
    article_number = Column(Float)
    branch_number = Column(Integer)
    customer_number = Column(Integer)
    receipt_number = Column(Integer)
    date = Column(DateTime)
    purchase_price = Column(Float)
    discount = Column(Float)
    deduction = Column(Float)
    staff_discount = Column(Float)
    quantity = Column(Integer)
    last_change = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    article = relationship("Article", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    branch = relationship("Branch", back_populates="sales")

class Inventory(BaseModel):
    """Model for inventory items."""
    __tablename__ = "inventory"
    
    article_id = Column(String(36), ForeignKey("articles.id"))
    branch_id = Column(String(36), ForeignKey("branches.id"))
    branch_number = Column(Integer)
    supplier_number = Column(Integer)
    shop_number = Column(Integer)
    category_number = Column(Integer)
    active = Column(Boolean)
    date = Column(DateTime)
    stocktaking_date = Column(DateTime)
    type = Column(Integer)
    quantity = Column(Integer)
    last_change = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    article = relationship("Article", back_populates="inventory_items")
    branch = relationship("Branch", back_populates="inventory_items")

class CustomerCard(BaseModel):
    """Model for customer cards."""
    __tablename__ = "customer_cards"
    
    customer_id = Column(String(36), ForeignKey("customers.id"))
    customer_number = Column(Integer)
    card_number = Column(String(255))
    issue_date = Column(DateTime)
    expiry_date = Column(DateTime)
    status = Column(Integer)
    last_change = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="customer_cards")

class Supplier(BaseModel):
    """Model for suppliers."""
    __tablename__ = "suppliers"
    
    number = Column(Integer)
    name1 = Column(String(255))
    name2 = Column(String(255))
    name3 = Column(String(255))
    search_term = Column(String(255))
    currency_number = Column(String(10))
    country_number = Column(String(10))
    is_active = Column(Boolean)
    is_edi = Column(Boolean)
    last_change = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    orders = relationship("Order", back_populates="supplier")

class Branch(BaseModel):
    """Model for branches."""
    __tablename__ = "branches"
    
    number = Column(Integer)
    name1 = Column(String(255))
    name2 = Column(String(255))
    name3 = Column(String(255))
    search_term = Column(String(255))
    is_active = Column(Boolean)
    is_webshop = Column(Boolean)
    stocktaking_date = Column(DateTime)
    last_change = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    sales = relationship("Sale", back_populates="branch")
    inventory_items = relationship("Inventory", back_populates="branch")

class Category(BaseModel):
    """Model for categories."""
    __tablename__ = "categories"
    
    number = Column(Integer)
    name = Column(String(255))
    search_term = Column(String(255))
    department_number = Column(Integer)
    main_department_number = Column(Integer)
    main_category_number = Column(Integer)
    general_category_number = Column(Integer)
    tax_number = Column(Integer)
    is_service_category = Column(Boolean)
    last_change = Column(DateTime)
    is_deleted = Column(Boolean, default=False)

class Voucher(BaseModel):
    """Model for vouchers."""
    __tablename__ = "vouchers"
    
    number = Column(Integer)
    internet_code = Column(String(255))
    receipt_number = Column(Integer)
    date = Column(DateTime)
    status = Column(Integer)
    voucher_redemption_date = Column(DateTime)
    type = Column(Integer)
    branch_number = Column(Integer)
    valid_until = Column(DateTime)
    valid_from = Column(DateTime)
    value = Column(Float)
    amount_redeemed = Column(Float)
    customer_number = Column(Integer)
    currency_number = Column(String(10))
    last_change = Column(DateTime)
    is_deleted = Column(Boolean, default=False)

class Invoice(BaseModel):
    """Model for invoices."""
    __tablename__ = "invoices"
    
    number = Column(Integer)
    branch_number = Column(Integer)
    customer_id = Column(String(36), ForeignKey("customers.id"))
    customer_number = Column(Integer)
    currency_number = Column(String(10))
    receipt_number = Column(Integer)
    receipt_position = Column(Integer)
    date = Column(DateTime)
    payment_due_date = Column(DateTime)
    staff_number = Column(Integer)
    cash_register_number = Column(Integer)
    status = Column(Integer)
    amount = Column(Float)
    amount_cleared = Column(Float)
    payment_condition_number = Column(Integer)
    last_change = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")

class Payment(BaseModel):
    """Model for payments."""
    __tablename__ = "payments"
    
    number = Column(Integer)
    receipt_number = Column(Integer)
    receipt_position = Column(Integer)
    date = Column(DateTime)
    cash_register_number = Column(Integer)
    staff_number = Column(Integer)
    status = Column(Integer)
    amount = Column(Float)
    branch_number = Column(Integer)
    customer_id = Column(String(36), ForeignKey("customers.id"))
    customer_number = Column(Integer)
    currency_number = Column(String(10))
    invoice_date = Column(DateTime)
    invoice_id = Column(String(36), ForeignKey("invoices.id"))
    last_change = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")

class ETLMetadata(Base):
    """Model for ETL metadata."""
    __tablename__ = "etl_metadata"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_name = Column(String(255), index=True)
    last_extraction_time = Column(DateTime)
    last_record_timestamp = Column(DateTime)
    record_count = Column(Integer)
    status = Column(String(50))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "entity_name": self.entity_name,
            "last_extraction_time": self.last_extraction_time,
            "last_record_timestamp": self.last_record_timestamp,
            "record_count": self.record_count,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
