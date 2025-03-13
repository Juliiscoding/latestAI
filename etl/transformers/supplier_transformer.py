"""
Supplier transformer for the Mercurios.ai ETL pipeline.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from etl.transformers.base_transformer import BaseTransformer
from etl.utils.logger import logger

class SupplierTransformer(BaseTransformer):
    """
    Transformer for supplier data.
    Handles normalization, feature engineering, and aggregation for suppliers.
    """
    
    def __init__(self, orders_data: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize the supplier transformer.
        
        Args:
            orders_data: Optional orders data for feature engineering
        """
        super().__init__()
        self.orders_data = orders_data or []
        self.orders_by_supplier = self._group_orders_by_supplier()
        self.supplier_metrics = {}
        self.order_frequency_by_supplier = {}
        self.order_volume_by_supplier = {}
        self.lead_times_by_supplier = {}
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform supplier data.
        
        Args:
            data: Supplier data to transform
            
        Returns:
            Transformed supplier data
        """
        # Create a copy to avoid modifying the original
        transformed = data.copy()
        
        # Normalize timestamps
        for ts_field in ['created_at', 'updated_at', 'last_order_date']:
            if ts_field in transformed:
                transformed[ts_field] = self.standardize_timestamp(transformed.get(ts_field), ts_field)
        
        # Add supplier metrics
        supplier_id = transformed.get('supplier_id')
        if supplier_id:
            # Calculate order frequency
            transformed['order_frequency'] = self._calculate_order_frequency(supplier_id)
            
            # Calculate average order size
            transformed['average_order_size'] = self._calculate_average_order_size(supplier_id)
            
            # Calculate lead time
            transformed['average_lead_time'] = self._calculate_average_lead_time(supplier_id)
            
            # Calculate on-time delivery rate
            transformed['on_time_delivery_rate'] = self._calculate_on_time_delivery_rate(supplier_id)
            
            # Calculate order volume trends
            transformed['order_volume_trend'] = self._calculate_order_volume_trend(supplier_id)
            
            # Calculate supplier reliability score
            transformed['reliability_score'] = self._calculate_reliability_score(transformed)
            
            # Store supplier metrics
            self._store_supplier_metrics(supplier_id, transformed)
        
        return transformed
    
    def transform_batch(self, data_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a batch of supplier data and generate metrics.
        
        Args:
            data_batch: Batch of supplier data to transform
            
        Returns:
            Batch of transformed supplier data
        """
        # Reset metrics
        self.supplier_metrics = {}
        
        # Transform individual records
        transformed_batch = super().transform_batch(data_batch)
        
        # Generate supplier metrics
        self._generate_supplier_metrics()
        
        return transformed_batch
    
    def _group_orders_by_supplier(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group orders data by supplier ID.
        
        Returns:
            Dictionary of orders data grouped by supplier ID
        """
        result = {}
        for order in self.orders_data:
            supplier_id = order.get('supplier_id')
            if supplier_id:
                if supplier_id not in result:
                    result[supplier_id] = []
                result[supplier_id].append(order)
        return result
    
    def _calculate_order_frequency(self, supplier_id: str) -> Dict[str, Any]:
        """
        Calculate order frequency for a supplier (orders per month, week, day).
        
        Args:
            supplier_id: Supplier ID
            
        Returns:
            Dictionary with order frequency metrics
        """
        # Get orders for this supplier
        orders = self.orders_by_supplier.get(supplier_id, [])
        if not orders:
            return {
                "orders_per_month": 0.0,
                "orders_per_week": 0.0,
                "orders_per_day": 0.0,
                "days_between_orders": 0.0
            }
        
        # Get order dates
        order_dates = []
        for order in orders:
            order_date = order.get('order_date')
            if not order_date:
                continue
            
            if isinstance(order_date, str):
                try:
                    order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            order_dates.append(order_date)
        
        if not order_dates:
            return {
                "orders_per_month": 0.0,
                "orders_per_week": 0.0,
                "orders_per_day": 0.0,
                "days_between_orders": 0.0
            }
        
        # Sort order dates
        order_dates.sort()
        
        # Calculate date range
        min_date = min(order_dates)
        max_date = max(order_dates)
        date_range_days = (max_date - min_date).days
        
        if date_range_days == 0:
            date_range_days = 1  # Avoid division by zero
        
        # Calculate frequencies
        orders_per_day = len(order_dates) / date_range_days
        orders_per_week = orders_per_day * 7
        orders_per_month = orders_per_day * 30
        
        # Calculate average days between orders
        if len(order_dates) <= 1:
            days_between_orders = 0.0
        else:
            days_between = []
            for i in range(1, len(order_dates)):
                days = (order_dates[i] - order_dates[i-1]).days
                days_between.append(days)
            days_between_orders = sum(days_between) / len(days_between)
        
        return {
            "orders_per_month": orders_per_month,
            "orders_per_week": orders_per_week,
            "orders_per_day": orders_per_day,
            "days_between_orders": days_between_orders
        }
    
    def _calculate_average_order_size(self, supplier_id: str) -> Dict[str, Any]:
        """
        Calculate average order size for a supplier.
        
        Args:
            supplier_id: Supplier ID
            
        Returns:
            Dictionary with average order size metrics
        """
        # Get orders for this supplier
        orders = self.orders_by_supplier.get(supplier_id, [])
        if not orders:
            return {
                "average_items": 0.0,
                "average_amount": 0.0,
                "average_unique_products": 0.0
            }
        
        # Calculate metrics
        total_items = sum(order.get('total_items', 0) for order in orders)
        total_amount = sum(order.get('total_amount', 0) for order in orders)
        
        # Calculate unique products per order
        unique_products_per_order = []
        for order in orders:
            order_items = order.get('order_items', [])
            unique_products = set(item.get('article_id') for item in order_items if item.get('article_id'))
            unique_products_per_order.append(len(unique_products))
        
        average_unique_products = sum(unique_products_per_order) / len(orders) if unique_products_per_order else 0
        
        return {
            "average_items": total_items / len(orders),
            "average_amount": total_amount / len(orders),
            "average_unique_products": average_unique_products
        }
    
    def _calculate_average_lead_time(self, supplier_id: str) -> float:
        """
        Calculate average lead time for a supplier (days between order and delivery).
        
        Args:
            supplier_id: Supplier ID
            
        Returns:
            Average lead time in days
        """
        # Get orders for this supplier
        orders = self.orders_by_supplier.get(supplier_id, [])
        if not orders:
            return 0.0
        
        # Calculate lead times
        lead_times = []
        for order in orders:
            order_date = order.get('order_date')
            delivery_date = order.get('delivery_date')
            
            if not order_date or not delivery_date:
                continue
            
            # Convert to datetime if needed
            if isinstance(order_date, str):
                try:
                    order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            if isinstance(delivery_date, str):
                try:
                    delivery_date = datetime.fromisoformat(delivery_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            # Calculate lead time
            lead_time = (delivery_date - order_date).days
            if lead_time >= 0:  # Ignore negative lead times (data errors)
                lead_times.append(lead_time)
        
        if not lead_times:
            return 0.0
        
        return sum(lead_times) / len(lead_times)
    
    def _calculate_on_time_delivery_rate(self, supplier_id: str) -> float:
        """
        Calculate on-time delivery rate for a supplier.
        
        Args:
            supplier_id: Supplier ID
            
        Returns:
            On-time delivery rate (0.0 to 1.0)
        """
        # Get orders for this supplier
        orders = self.orders_by_supplier.get(supplier_id, [])
        if not orders:
            return 0.0
        
        # Count on-time deliveries
        on_time_count = 0
        total_count = 0
        
        for order in orders:
            expected_delivery_date = order.get('expected_delivery_date')
            actual_delivery_date = order.get('delivery_date')
            
            if not expected_delivery_date or not actual_delivery_date:
                continue
            
            # Convert to datetime if needed
            if isinstance(expected_delivery_date, str):
                try:
                    expected_delivery_date = datetime.fromisoformat(expected_delivery_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            if isinstance(actual_delivery_date, str):
                try:
                    actual_delivery_date = datetime.fromisoformat(actual_delivery_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            # Check if delivery was on time
            total_count += 1
            if actual_delivery_date <= expected_delivery_date:
                on_time_count += 1
        
        if total_count == 0:
            return 0.0
        
        return on_time_count / total_count
    
    def _calculate_order_volume_trend(self, supplier_id: str) -> Dict[str, Any]:
        """
        Calculate order volume trend for a supplier.
        
        Args:
            supplier_id: Supplier ID
            
        Returns:
            Dictionary with order volume trend metrics
        """
        # Get orders for this supplier
        orders = self.orders_by_supplier.get(supplier_id, [])
        if not orders:
            return {
                "monthly_volumes": {},
                "trend_coefficient": 0.0
            }
        
        # Group orders by month
        monthly_volumes = defaultdict(float)
        
        for order in orders:
            order_date = order.get('order_date')
            if not order_date:
                continue
            
            # Convert to datetime if needed
            if isinstance(order_date, str):
                try:
                    order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            # Get month key
            month_key = order_date.strftime('%Y-%m')
            
            # Add order amount
            monthly_volumes[month_key] += order.get('total_amount', 0)
        
        if not monthly_volumes:
            return {
                "monthly_volumes": {},
                "trend_coefficient": 0.0
            }
        
        # Sort months
        sorted_months = sorted(monthly_volumes.keys())
        
        # Calculate trend (simple linear regression)
        x = list(range(len(sorted_months)))
        y = [monthly_volumes[month] for month in sorted_months]
        
        if len(x) <= 1:
            trend_coefficient = 0.0
        else:
            # Calculate means
            x_mean = sum(x) / len(x)
            y_mean = sum(y) / len(y)
            
            # Calculate slope
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(len(x)))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(len(x)))
            
            if denominator == 0:
                trend_coefficient = 0.0
            else:
                trend_coefficient = numerator / denominator
        
        return {
            "monthly_volumes": dict(monthly_volumes),
            "trend_coefficient": trend_coefficient
        }
    
    def _calculate_reliability_score(self, supplier_data: Dict[str, Any]) -> float:
        """
        Calculate reliability score for a supplier based on various metrics.
        
        Args:
            supplier_data: Supplier data
            
        Returns:
            Reliability score (0.0 to 1.0)
        """
        # Get metrics
        on_time_rate = supplier_data.get('on_time_delivery_rate', 0.0)
        lead_time = supplier_data.get('average_lead_time', 0.0)
        
        # Normalize lead time (lower is better)
        # Assume 30 days is the maximum acceptable lead time
        normalized_lead_time = max(0, 1 - (lead_time / 30))
        
        # Calculate reliability score (weighted average)
        weights = {
            'on_time_rate': 0.7,
            'lead_time': 0.3
        }
        
        reliability_score = (
            weights['on_time_rate'] * on_time_rate +
            weights['lead_time'] * normalized_lead_time
        )
        
        return min(1.0, max(0.0, reliability_score))
    
    def _store_supplier_metrics(self, supplier_id: str, supplier_data: Dict[str, Any]):
        """
        Store metrics for a supplier.
        
        Args:
            supplier_id: Supplier ID
            supplier_data: Supplier data
        """
        self.supplier_metrics[supplier_id] = {
            'order_frequency': supplier_data.get('order_frequency', {}),
            'average_order_size': supplier_data.get('average_order_size', {}),
            'average_lead_time': supplier_data.get('average_lead_time', 0.0),
            'on_time_delivery_rate': supplier_data.get('on_time_delivery_rate', 0.0),
            'order_volume_trend': supplier_data.get('order_volume_trend', {}),
            'reliability_score': supplier_data.get('reliability_score', 0.0)
        }
    
    def _generate_supplier_metrics(self):
        """Generate supplier metrics."""
        if not self.supplier_metrics:
            logger.warning("No supplier metrics available")
            return
        
        logger.info(f"Generating supplier metrics for {len(self.supplier_metrics)} suppliers")
        
        # Generate order frequency by supplier
        self.order_frequency_by_supplier = {
            supplier_id: metrics.get('order_frequency', {})
            for supplier_id, metrics in self.supplier_metrics.items()
        }
        
        # Generate order volume by supplier
        self.order_volume_by_supplier = {
            supplier_id: metrics.get('order_volume_trend', {}).get('monthly_volumes', {})
            for supplier_id, metrics in self.supplier_metrics.items()
        }
        
        # Generate lead times by supplier
        self.lead_times_by_supplier = {
            supplier_id: metrics.get('average_lead_time', 0.0)
            for supplier_id, metrics in self.supplier_metrics.items()
        }
        
        logger.info("Supplier metrics generated successfully")
    
    def get_supplier_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get supplier metrics.
        
        Returns:
            Dictionary of supplier metrics
        """
        return self.supplier_metrics
    
    def get_order_frequency_by_supplier(self) -> Dict[str, Dict[str, Any]]:
        """
        Get order frequency by supplier.
        
        Returns:
            Dictionary of order frequency by supplier
        """
        return self.order_frequency_by_supplier
    
    def get_order_volume_by_supplier(self) -> Dict[str, Dict[str, Any]]:
        """
        Get order volume by supplier.
        
        Returns:
            Dictionary of order volume by supplier
        """
        return self.order_volume_by_supplier
    
    def get_lead_times_by_supplier(self) -> Dict[str, float]:
        """
        Get lead times by supplier.
        
        Returns:
            Dictionary of lead times by supplier
        """
        return self.lead_times_by_supplier
