"""
Data Mart module for the Mercurios.ai ETL pipeline.
Handles creation and management of specialized data marts for inventory analytics.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

from sqlalchemy import create_engine, text, Table, MetaData
from sqlalchemy.orm import Session

from etl.utils.logger import logger
from etl.models.data_warehouse import (
    Base, DimDate, DimProduct, DimLocation, DimCustomer, DimSupplier,
    FactSales, FactInventory, FactOrders,
    FactSalesDaily, FactSalesWeekly, FactSalesMonthly
)

class DataMartManager:
    """
    Manages the creation and refresh of data marts for inventory analytics.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the data mart manager.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.engine = db_session.get_bind()
        self.metadata = MetaData(bind=self.engine)
    
    def create_data_warehouse_schema(self):
        """
        Create the data warehouse schema tables.
        """
        logger.info("Creating data warehouse schema...")
        Base.metadata.create_all(self.engine)
        logger.info("Data warehouse schema created successfully.")
    
    def populate_date_dimension(self, start_year: int = 2020, end_year: int = 2030):
        """
        Populate the date dimension table with dates.
        
        Args:
            start_year: Start year for date generation
            end_year: End year for date generation
        """
        logger.info(f"Populating date dimension from {start_year} to {end_year}...")
        
        from datetime import date, timedelta
        import calendar
        
        # Check if date dimension already has data
        date_count = self.db_session.query(DimDate).count()
        if date_count > 0:
            logger.info(f"Date dimension already has {date_count} records. Skipping population.")
            return
        
        # Generate dates
        start_date = date(start_year, 1, 1)
        end_date = date(end_year, 12, 31)
        
        current_date = start_date
        date_records = []
        
        while current_date <= end_date:
            # Create date record
            day_of_week = current_date.weekday()  # 0-6 (Monday is 0)
            is_weekend = day_of_week >= 5  # 5 = Saturday, 6 = Sunday
            
            # Determine season (Northern Hemisphere)
            month = current_date.month
            if 3 <= month <= 5:
                season = "Spring"
            elif 6 <= month <= 8:
                season = "Summer"
            elif 9 <= month <= 11:
                season = "Fall"
            else:
                season = "Winter"
            
            # Create date dimension record
            date_record = DimDate(
                date=current_date,
                day=current_date.day,
                day_name=current_date.strftime("%A"),
                day_of_week=day_of_week + 1,  # 1-7 (Monday is 1)
                day_of_year=current_date.timetuple().tm_yday,
                week=current_date.isocalendar()[1],
                week_of_year=current_date.isocalendar()[1],
                month=current_date.month,
                month_name=current_date.strftime("%B"),
                quarter=((current_date.month - 1) // 3) + 1,
                year=current_date.year,
                is_weekend=is_weekend,
                is_holiday=False,  # Would need a holiday calendar to determine
                season=season,
                fiscal_year=current_date.year if current_date.month >= 7 else current_date.year - 1,
                fiscal_quarter=((current_date.month - 7) % 12 // 3) + 1
            )
            
            date_records.append(date_record)
            
            # Move to next day
            current_date += timedelta(days=1)
            
            # Batch insert every 1000 records
            if len(date_records) >= 1000:
                self.db_session.bulk_save_objects(date_records)
                self.db_session.commit()
                date_records = []
        
        # Insert any remaining records
        if date_records:
            self.db_session.bulk_save_objects(date_records)
            self.db_session.commit()
        
        logger.info(f"Date dimension populated with dates from {start_year} to {end_year}.")
    
    def create_inventory_analytics_mart(self):
        """
        Create a specialized data mart for inventory analytics.
        This creates materialized views for common inventory queries.
        """
        logger.info("Creating inventory analytics data mart...")
        
        # Create materialized view for inventory levels by product and location
        self._create_materialized_view(
            view_name="mv_inventory_levels",
            query="""
            SELECT 
                dp.product_id,
                dp.article_id,
                dp.product_name,
                dp.category_name,
                dl.location_id,
                dl.branch_id,
                dl.location_name,
                dd.date,
                dd.year,
                dd.month,
                dd.month_name,
                fi.quantity_on_hand,
                fi.quantity_available,
                fi.days_of_supply,
                fi.reorder_point,
                fi.safety_stock,
                fi.stock_status
            FROM 
                fact_inventory fi
            JOIN 
                dim_product dp ON fi.product_id = dp.product_id
            JOIN 
                dim_location dl ON fi.location_id = dl.location_id
            JOIN 
                dim_date dd ON fi.date_id = dd.date_id
            """
        )
        
        # Create materialized view for inventory turnover by product
        self._create_materialized_view(
            view_name="mv_inventory_turnover",
            query="""
            WITH product_sales AS (
                SELECT 
                    fs.product_id,
                    dd.year,
                    dd.month,
                    SUM(fs.quantity) as total_sales_qty
                FROM 
                    fact_sales fs
                JOIN 
                    dim_date dd ON fs.date_id = dd.date_id
                GROUP BY 
                    fs.product_id, dd.year, dd.month
            ),
            product_inventory AS (
                SELECT 
                    fi.product_id,
                    dd.year,
                    dd.month,
                    AVG(fi.quantity_on_hand) as avg_inventory_qty
                FROM 
                    fact_inventory fi
                JOIN 
                    dim_date dd ON fi.date_id = dd.date_id
                GROUP BY 
                    fi.product_id, dd.year, dd.month
            )
            SELECT 
                dp.product_id,
                dp.article_id,
                dp.product_name,
                dp.category_name,
                ps.year,
                ps.month,
                ps.total_sales_qty,
                pi.avg_inventory_qty,
                CASE 
                    WHEN pi.avg_inventory_qty > 0 THEN ps.total_sales_qty / pi.avg_inventory_qty 
                    ELSE 0 
                END as turnover_rate
            FROM 
                product_sales ps
            JOIN 
                product_inventory pi ON ps.product_id = pi.product_id 
                AND ps.year = pi.year AND ps.month = pi.month
            JOIN 
                dim_product dp ON ps.product_id = dp.product_id
            """
        )
        
        # Create materialized view for stock-out risk
        self._create_materialized_view(
            view_name="mv_stock_out_risk",
            query="""
            WITH sales_velocity AS (
                SELECT 
                    fs.product_id,
                    dl.location_id,
                    SUM(fs.quantity) / 30.0 as daily_sales_rate
                FROM 
                    fact_sales fs
                JOIN 
                    dim_location dl ON fs.location_id = dl.location_id
                JOIN 
                    dim_date dd ON fs.date_id = dd.date_id
                WHERE 
                    dd.date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY 
                    fs.product_id, dl.location_id
            )
            SELECT 
                dp.product_id,
                dp.article_id,
                dp.product_name,
                dl.location_id,
                dl.branch_id,
                dl.location_name,
                fi.quantity_on_hand,
                sv.daily_sales_rate,
                CASE 
                    WHEN sv.daily_sales_rate > 0 THEN fi.quantity_on_hand / sv.daily_sales_rate 
                    ELSE 999 
                END as days_until_stockout,
                CASE 
                    WHEN sv.daily_sales_rate > 0 AND fi.quantity_on_hand / sv.daily_sales_rate < 7 THEN 'High'
                    WHEN sv.daily_sales_rate > 0 AND fi.quantity_on_hand / sv.daily_sales_rate < 14 THEN 'Medium'
                    ELSE 'Low'
                END as stock_out_risk
            FROM 
                fact_inventory fi
            JOIN 
                dim_product dp ON fi.product_id = dp.product_id
            JOIN 
                dim_location dl ON fi.location_id = dl.location_id
            JOIN 
                sales_velocity sv ON fi.product_id = sv.product_id AND fi.location_id = sv.location_id
            JOIN 
                dim_date dd ON fi.date_id = dd.date_id
            WHERE 
                dd.date = (SELECT MAX(date) FROM dim_date WHERE date <= CURRENT_DATE)
            """
        )
        
        logger.info("Inventory analytics data mart created successfully.")
    
    def create_supplier_analytics_mart(self):
        """
        Create a specialized data mart for supplier analytics.
        This creates materialized views for supplier performance metrics.
        """
        logger.info("Creating supplier analytics data mart...")
        
        # Create materialized view for supplier performance
        self._create_materialized_view(
            view_name="mv_supplier_performance",
            query="""
            WITH order_metrics AS (
                SELECT 
                    fo.supplier_id,
                    COUNT(DISTINCT fo.order_id) as total_orders,
                    SUM(fo.quantity_ordered) as total_quantity,
                    SUM(fo.total_cost) as total_cost,
                    AVG(
                        EXTRACT(EPOCH FROM dd_actual.date - dd_expected.date) / 86400.0
                    ) as avg_delivery_delay_days,
                    SUM(
                        CASE WHEN dd_actual.date <= dd_expected.date THEN 1 ELSE 0 END
                    )::FLOAT / COUNT(*) as on_time_delivery_rate
                FROM 
                    fact_orders fo
                JOIN 
                    dim_date dd_order ON fo.date_id = dd_order.date_id
                JOIN 
                    dim_date dd_expected ON fo.expected_delivery_date_id = dd_expected.date_id
                LEFT JOIN 
                    dim_date dd_actual ON fo.actual_delivery_date_id = dd_actual.date_id
                WHERE 
                    dd_order.date >= CURRENT_DATE - INTERVAL '365 days'
                GROUP BY 
                    fo.supplier_id
            )
            SELECT 
                ds.supplier_id,
                ds.supplier_code,
                ds.supplier_name,
                om.total_orders,
                om.total_quantity,
                om.total_cost,
                om.avg_delivery_delay_days,
                om.on_time_delivery_rate,
                ds.average_lead_time,
                ds.reliability_score,
                CASE 
                    WHEN om.on_time_delivery_rate >= 0.95 AND ds.reliability_score >= 0.8 THEN 'Excellent'
                    WHEN om.on_time_delivery_rate >= 0.85 AND ds.reliability_score >= 0.7 THEN 'Good'
                    WHEN om.on_time_delivery_rate >= 0.75 AND ds.reliability_score >= 0.6 THEN 'Average'
                    ELSE 'Poor'
                END as performance_category
            FROM 
                dim_supplier ds
            LEFT JOIN 
                order_metrics om ON ds.supplier_id = om.supplier_id
            """
        )
        
        logger.info("Supplier analytics data mart created successfully.")
    
    def create_sales_analytics_mart(self):
        """
        Create a specialized data mart for sales analytics.
        This creates materialized views for sales performance metrics.
        """
        logger.info("Creating sales analytics data mart...")
        
        # Create materialized view for product sales trends
        self._create_materialized_view(
            view_name="mv_product_sales_trends",
            query="""
            SELECT 
                dp.product_id,
                dp.article_id,
                dp.product_name,
                dp.category_name,
                dd.year,
                dd.month,
                dd.month_name,
                SUM(fs.quantity) as total_quantity,
                SUM(fs.net_amount) as total_net_amount,
                COUNT(DISTINCT fs.sale_id) as transaction_count,
                SUM(fs.quantity) / COUNT(DISTINCT fs.sale_id) as avg_quantity_per_transaction
            FROM 
                fact_sales fs
            JOIN 
                dim_product dp ON fs.product_id = dp.product_id
            JOIN 
                dim_date dd ON fs.date_id = dd.date_id
            WHERE 
                dd.date >= CURRENT_DATE - INTERVAL '24 months'
            GROUP BY 
                dp.product_id, dp.article_id, dp.product_name, dp.category_name,
                dd.year, dd.month, dd.month_name
            ORDER BY 
                dp.product_id, dd.year, dd.month
            """
        )
        
        # Create materialized view for customer purchase patterns
        self._create_materialized_view(
            view_name="mv_customer_purchase_patterns",
            query="""
            SELECT 
                dc.customer_id,
                dc.customer_code,
                dc.customer_name,
                COUNT(DISTINCT fs.sale_id) as total_transactions,
                SUM(fs.quantity) as total_quantity,
                SUM(fs.net_amount) as total_spent,
                AVG(fs.net_amount) as avg_transaction_value,
                COUNT(DISTINCT dp.category_id) as unique_categories_purchased,
                COUNT(DISTINCT fs.product_id) as unique_products_purchased,
                MAX(dd.date) as last_purchase_date,
                MIN(dd.date) as first_purchase_date
            FROM 
                fact_sales fs
            JOIN 
                dim_customer dc ON fs.customer_id = dc.customer_id
            JOIN 
                dim_product dp ON fs.product_id = dp.product_id
            JOIN 
                dim_date dd ON fs.date_id = dd.date_id
            WHERE 
                dd.date >= CURRENT_DATE - INTERVAL '365 days'
            GROUP BY 
                dc.customer_id, dc.customer_code, dc.customer_name
            """
        )
        
        logger.info("Sales analytics data mart created successfully.")
    
    def refresh_all_data_marts(self):
        """
        Refresh all materialized views in the data marts.
        """
        logger.info("Refreshing all data marts...")
        
        # Get list of all materialized views
        result = self.engine.execute(text("""
            SELECT matviewname FROM pg_matviews
        """))
        
        materialized_views = [row[0] for row in result]
        
        # Refresh each materialized view
        for view_name in materialized_views:
            self._refresh_materialized_view(view_name)
        
        logger.info(f"Refreshed {len(materialized_views)} materialized views.")
    
    def _create_materialized_view(self, view_name: str, query: str):
        """
        Create a materialized view.
        
        Args:
            view_name: Name of the materialized view
            query: SQL query for the materialized view
        """
        try:
            # Check if materialized view already exists
            check_query = text(f"""
                SELECT 1 FROM pg_matviews WHERE matviewname = '{view_name}'
            """)
            result = self.engine.execute(check_query)
            
            if result.scalar():
                logger.info(f"Materialized view {view_name} already exists. Dropping and recreating...")
                drop_query = text(f"DROP MATERIALIZED VIEW IF EXISTS {view_name}")
                self.engine.execute(drop_query)
            
            # Create materialized view
            create_query = text(f"""
                CREATE MATERIALIZED VIEW {view_name} AS
                {query}
                WITH DATA
            """)
            
            self.engine.execute(create_query)
            
            # Create index on materialized view
            index_query = text(f"""
                CREATE INDEX idx_{view_name} ON {view_name} (product_id)
            """)
            
            try:
                self.engine.execute(index_query)
            except Exception as e:
                logger.warning(f"Could not create index on {view_name}: {e}")
            
            logger.info(f"Created materialized view {view_name}")
        except Exception as e:
            logger.error(f"Error creating materialized view {view_name}: {e}")
            raise
    
    def _refresh_materialized_view(self, view_name: str):
        """
        Refresh a materialized view.
        
        Args:
            view_name: Name of the materialized view to refresh
        """
        try:
            refresh_query = text(f"""
                REFRESH MATERIALIZED VIEW {view_name}
            """)
            
            self.engine.execute(refresh_query)
            logger.info(f"Refreshed materialized view {view_name}")
        except Exception as e:
            logger.error(f"Error refreshing materialized view {view_name}: {e}")
            raise
