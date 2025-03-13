"""
Database models for the Mercurios.ai ETL pipeline.
"""
# Import models from models.py instead of individual modules
from etl.models.models import (
    Article, Customer, Order, Sale, Inventory, 
    Supplier, Branch, Category, Voucher, Invoice, 
    Payment, ETLMetadata
)

# Import data warehouse models
from etl.models.data_warehouse import (
    DimDate, DimProduct, DimLocation, DimCustomer, DimSupplier,
    FactSales, FactInventory, FactOrders,
    FactSalesDaily as SalesDailyAggregation, 
    FactSalesWeekly as SalesWeeklyAggregation, 
    FactSalesMonthly as SalesMonthlyAggregation
)

__all__ = [
    'Article',
    'Customer',
    'Order',
    'Sale',
    'Inventory',
    'Supplier',
    'Branch',
    'Category',
    'Voucher',
    'Invoice',
    'Payment',
    'ETLMetadata',
    'DimDate',
    'DimProduct',
    'DimLocation',
    'DimCustomer',
    'DimSupplier',
    'FactSales',
    'FactInventory',
    'FactOrders',
    'SalesDailyAggregation',
    'SalesWeeklyAggregation',
    'SalesMonthlyAggregation',
]