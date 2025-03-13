"""
Prediction engine for the Mercurios.ai Predictive Inventory Management tool.

This module provides a unified interface for all prediction models.
"""
import os
import pickle
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
from datetime import datetime, timedelta

from prediction.models.time_series import create_time_series_model
from prediction.models.lead_time import LeadTimePredictionModel
from prediction.models.inventory_optimization import ReorderPointCalculator, SafetyStockOptimizer
from etl.utils.logger import logger
from etl.utils.database import SessionLocal

# Import data quality modules
from data_quality.manager import DataQualityManager
from data_quality.monitors.completeness_monitor import CompletenessMonitor
from data_quality.monitors.outlier_monitor import OutlierMonitor
from data_quality.monitors.consistency_monitor import ConsistencyMonitor


class PredictionEngine:
    """
    Prediction engine for the Mercurios.ai Predictive Inventory Management tool.
    
    This class provides a unified interface for all prediction models,
    including time-series forecasting, lead time prediction, reorder point
    calculation, and safety stock optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the prediction engine.
        
        Args:
            config (Dict[str, Any], optional): Configuration parameters for the engine
        """
        self.config = config or {}
        self.models = {}
        self.model_configs = {}
        self.model_paths = {}
        self.session = None
        self.data_quality_manager = None
        
        # Initialize database session if needed
        if self.config.get('use_database', True):
            self.session = SessionLocal()
        
        # Set up model directory
        self.model_dir = self.config.get('model_dir', 'models')
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Initialize data quality manager if configured
        if self.config.get('data_quality', {}).get('enabled', False):
            self._initialize_data_quality_manager()
        
        logger.info("Initialized prediction engine")
    
    def _initialize_data_quality_manager(self) -> None:
        """
        Initialize the data quality manager.
        """
        data_quality_config = self.config.get('data_quality', {})
        
        # Create data quality manager
        self.data_quality_manager = DataQualityManager(config=data_quality_config)
        
        logger.info("Initialized data quality manager")
    
    def check_data_quality(self, data: pd.DataFrame, data_type: str = 'demand') -> Dict[str, Any]:
        """
        Check data quality before training or prediction.
        
        Args:
            data (pd.DataFrame): Data to check
            data_type (str): Type of data ('demand', 'lead_time', 'inventory')
            
        Returns:
            Dict[str, Any]: Data quality results
        """
        if self.data_quality_manager is None:
            logger.warning("Data quality manager not initialized, skipping quality checks")
            return {'enabled': False}
        
        logger.info(f"Checking data quality for {data_type} data")
        
        # Run data quality checks
        results = self.data_quality_manager.run_monitors(data)
        
        # Check if there are any critical alerts
        critical_alerts = [alert for alert in results['all_alerts'] if alert['severity'] == 'critical']
        
        if critical_alerts:
            logger.error(f"Found {len(critical_alerts)} critical data quality issues")
            for alert in critical_alerts:
                logger.error(f"  {alert['message']}")
        
        # Save results
        if self.config.get('data_quality', {}).get('save_reports', True):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_quality_{data_type}_{timestamp}.json"
            self.data_quality_manager.save_results(filename)
        
        return results
    
    def initialize_models(self, model_configs: Dict[str, Dict[str, Any]]) -> None:
        """
        Initialize prediction models with the given configurations.
        
        Args:
            model_configs (Dict[str, Dict[str, Any]]): Dictionary of model configurations
                - Key: Model name
                - Value: Model configuration
        """
        self.model_configs = model_configs
        
        for model_name, config in model_configs.items():
            model_type = config.get('type', 'arima')
            
            if model_type in ['arima', 'exp_smoothing']:
                self.models[model_name] = create_time_series_model(model_type, config)
            elif model_type == 'lead_time':
                self.models[model_name] = LeadTimePredictionModel(config)
            elif model_type == 'reorder_point':
                self.models[model_name] = ReorderPointCalculator(config)
            elif model_type == 'safety_stock':
                self.models[model_name] = SafetyStockOptimizer(config)
            else:
                logger.warning(f"Unknown model type: {model_type}")
                continue
            
            # Set model path
            self.model_paths[model_name] = os.path.join(self.model_dir, f"{model_name}.pkl")
            
            # Try to load existing model
            if os.path.exists(self.model_paths[model_name]):
                try:
                    self.models[model_name].load(self.model_paths[model_name])
                    logger.info(f"Loaded existing model: {model_name}")
                except Exception as e:
                    logger.error(f"Error loading model {model_name}: {e}")
            
        logger.info(f"Initialized {len(self.models)} prediction models")
    
    def train_model(self, model_name: str, data: pd.DataFrame, **kwargs) -> None:
        """
        Train a specific model.
        
        Args:
            model_name (str): Name of the model to train
            data (pd.DataFrame): Training data
            **kwargs: Additional training parameters
        """
        if model_name not in self.models:
            raise ValueError(f"Model not found: {model_name}")
        
        # Check data quality before training if enabled
        if self.data_quality_manager is not None:
            data_type = 'demand'
            if 'lead_time' in model_name:
                data_type = 'lead_time'
            elif 'reorder' in model_name or 'safety' in model_name:
                data_type = 'inventory'
            
            quality_results = self.check_data_quality(data, data_type)
            
            # Check if there are critical issues that should prevent training
            critical_alerts = [alert for alert in quality_results.get('all_alerts', []) 
                              if alert['severity'] == 'critical']
            
            if critical_alerts and not kwargs.get('force_train', False):
                logger.error(f"Training aborted due to critical data quality issues. "
                            f"Use force_train=True to override.")
                return
        
        logger.info(f"Training model: {model_name}")
        self.models[model_name].train(data, **kwargs)
        
        # Save the trained model
        self.models[model_name].save(self.model_paths[model_name])
        logger.info(f"Model {model_name} trained and saved")
    
    def predict(self, model_name: str, data: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        """
        Generate predictions using a specific model.
        
        Args:
            model_name (str): Name of the model to use
            data (pd.DataFrame): Input data for prediction
            *args: Additional prediction parameters
            **kwargs: Additional prediction parameters
            
        Returns:
            pd.DataFrame: Predictions
        """
        if model_name not in self.models:
            raise ValueError(f"Model not found: {model_name}")
        
        if not self.models[model_name].is_trained:
            raise ValueError(f"Model {model_name} is not trained")
        
        # Check data quality before prediction if enabled
        if self.data_quality_manager is not None:
            data_type = 'demand'
            if 'lead_time' in model_name:
                data_type = 'lead_time'
            elif 'reorder' in model_name or 'safety' in model_name:
                data_type = 'inventory'
            
            quality_results = self.check_data_quality(data, data_type)
            
            # Check if there are critical issues that should prevent prediction
            critical_alerts = [alert for alert in quality_results.get('all_alerts', []) 
                              if alert['severity'] == 'critical']
            
            if critical_alerts and not kwargs.get('force_predict', False):
                logger.error(f"Prediction aborted due to critical data quality issues. "
                            f"Use force_predict=True to override.")
                return pd.DataFrame()
        
        logger.info(f"Generating predictions with model: {model_name}")
        predictions = self.models[model_name].predict(data, *args, **kwargs)
        
        return predictions
    
    def forecast_demand(self, product_id: Union[int, List[int]], horizon: int = 30, 
                       model_name: Optional[str] = None) -> pd.DataFrame:
        """
        Forecast demand for the specified product(s).
        
        Args:
            product_id (Union[int, List[int]]): Product ID(s) to forecast demand for
            horizon (int): Number of days to forecast
            model_name (str, optional): Name of the time-series model to use
            
        Returns:
            pd.DataFrame: Demand forecast
        """
        # Use the first time-series model if not specified
        if model_name is None:
            for name, model in self.models.items():
                if hasattr(model, 'model_type') and model.model_type in ['arima', 'exp_smoothing']:
                    model_name = name
                    break
            
            if model_name is None:
                raise ValueError("No time-series model found")
        
        # Convert product_id to list if it's a single ID
        if isinstance(product_id, int):
            product_id = [product_id]
        
        # Fetch historical demand data from the database
        if self.session is not None:
            # Query the data warehouse for historical demand
            from etl.models.data_warehouse import FactSalesDaily, DimProduct, DimDate
            
            query = (
                self.session.query(
                    DimDate.date,
                    DimProduct.product_id,
                    FactSalesDaily.quantity
                )
                .join(FactSalesDaily, FactSalesDaily.date_id == DimDate.date_id)
                .join(DimProduct, FactSalesDaily.product_id == DimProduct.product_id)
                .filter(DimProduct.product_id.in_(product_id))
                .order_by(DimDate.date, DimProduct.product_id)
            )
            
            # Convert to DataFrame
            data = pd.read_sql(query.statement, self.session.bind)
            
            # Pivot to get one column per product
            data = data.pivot(index='date', columns='product_id', values='quantity').reset_index()
            
            # Rename columns for the model
            data.rename(columns={'date': 'date'}, inplace=True)
            for pid in product_id:
                data.rename(columns={pid: 'value'}, inplace=True)
                
                # Generate forecast for this product
                forecast = self.predict(model_name, data[['date', 'value']], horizon)
                
                # Add product_id column
                forecast['product_id'] = pid
                
                # Store or return the forecast
                if 'result' not in locals():
                    result = forecast
                else:
                    result = pd.concat([result, forecast])
            
            return result
        else:
            raise ValueError("Database session not available")
    
    def predict_lead_time(self, order_data: pd.DataFrame, model_name: Optional[str] = None) -> pd.DataFrame:
        """
        Predict lead times for the specified orders.
        
        Args:
            order_data (pd.DataFrame): Order data
            model_name (str, optional): Name of the lead time prediction model to use
            
        Returns:
            pd.DataFrame: Lead time predictions
        """
        # Use the first lead time model if not specified
        if model_name is None:
            for name, model in self.models.items():
                if hasattr(model, 'model_type') and model.model_type == 'lead_time':
                    model_name = name
                    break
            
            if model_name is None:
                raise ValueError("No lead time prediction model found")
        
        # Generate predictions
        predictions = self.predict(model_name, order_data)
        
        return predictions
    
    def calculate_reorder_points(self, product_data: pd.DataFrame, model_name: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate reorder points for the specified products.
        
        Args:
            product_data (pd.DataFrame): Product data
            model_name (str, optional): Name of the reorder point calculator to use
            
        Returns:
            pd.DataFrame: Calculated reorder points
        """
        # Use the first reorder point model if not specified
        if model_name is None:
            for name, model in self.models.items():
                if hasattr(model, 'model_type') and model.model_type == 'reorder_point':
                    model_name = name
                    break
            
            if model_name is None:
                raise ValueError("No reorder point calculator found")
        
        # Generate calculations
        results = self.predict(model_name, product_data)
        
        return results
    
    def optimize_safety_stock(self, product_data: pd.DataFrame, model_name: Optional[str] = None) -> pd.DataFrame:
        """
        Optimize safety stock levels for the specified products.
        
        Args:
            product_data (pd.DataFrame): Product data
            model_name (str, optional): Name of the safety stock optimizer to use
            
        Returns:
            pd.DataFrame: Optimized safety stock levels
        """
        # Use the first safety stock model if not specified
        if model_name is None:
            for name, model in self.models.items():
                if hasattr(model, 'model_type') and model.model_type == 'safety_stock':
                    model_name = name
                    break
            
            if model_name is None:
                raise ValueError("No safety stock optimizer found")
        
        # Generate optimizations
        results = self.predict(model_name, product_data)
        
        return results
    
    def generate_inventory_recommendations(self, product_ids: List[int]) -> pd.DataFrame:
        """
        Generate comprehensive inventory recommendations for the specified products.
        
        This method combines demand forecasting, lead time prediction, reorder point
        calculation, and safety stock optimization to generate actionable recommendations.
        
        Args:
            product_ids (List[int]): List of product IDs to generate recommendations for
            
        Returns:
            pd.DataFrame: Inventory recommendations
        """
        # Fetch product data from the database
        if self.session is not None:
            # Query the data warehouse for product information
            from etl.models.data_warehouse import DimProduct, FactInventory, FactSales
            
            # Get current inventory levels
            inventory_query = (
                self.session.query(
                    DimProduct.product_id,
                    FactInventory.quantity.label('current_stock')
                )
                .join(FactInventory, FactInventory.product_id == DimProduct.product_id)
                .filter(DimProduct.product_id.in_(product_ids))
                .order_by(DimProduct.product_id)
            )
            
            inventory_data = pd.read_sql(inventory_query.statement, self.session.bind)
            
            # Get historical demand data
            demand_query = (
                self.session.query(
                    DimProduct.product_id,
                    FactSales.quantity,
                    FactSales.order_date
                )
                .join(FactSales, FactSales.product_id == DimProduct.product_id)
                .filter(DimProduct.product_id.in_(product_ids))
                .order_by(DimProduct.product_id, FactSales.order_date)
            )
            
            demand_data = pd.read_sql(demand_query.statement, self.session.bind)
            
            # Get historical lead time data
            lead_time_query = (
                self.session.query(
                    DimProduct.product_id,
                    FactSales.supplier_id,
                    FactSales.order_date,
                    FactSales.delivery_date,
                    FactSales.quantity,
                    FactSales.total_amount
                )
                .join(FactSales, FactSales.product_id == DimProduct.product_id)
                .filter(DimProduct.product_id.in_(product_ids))
                .filter(FactSales.delivery_date.isnot(None))
                .order_by(DimProduct.product_id, FactSales.order_date)
            )
            
            lead_time_data = pd.read_sql(lead_time_query.statement, self.session.bind)
            
            # Calculate lead time in days
            lead_time_data['lead_time_days'] = (
                pd.to_datetime(lead_time_data['delivery_date']) - 
                pd.to_datetime(lead_time_data['order_date'])
            ).dt.days
            
            # Prepare data for each model
            # 1. Demand forecasting
            demand_forecast = self.forecast_demand(product_ids, horizon=30)
            
            # 2. Lead time prediction
            lead_time_predictions = self.predict_lead_time(lead_time_data)
            
            # 3. Reorder point calculation
            # Prepare data for reorder point calculation
            reorder_data = []
            for product_id in product_ids:
                product_demand = demand_data[demand_data['product_id'] == product_id]['quantity'].tolist()
                product_lead_time = lead_time_data[lead_time_data['product_id'] == product_id]['lead_time_days'].tolist()
                
                if product_demand and product_lead_time:
                    reorder_data.append({
                        'product_id': product_id,
                        'demand': product_demand,
                        'lead_time': product_lead_time
                    })
            
            reorder_df = pd.DataFrame(reorder_data)
            reorder_points = self.calculate_reorder_points(reorder_df)
            
            # 4. Safety stock optimization
            # Prepare data for safety stock optimization
            safety_data = []
            for product_id in product_ids:
                product_demand = demand_data[demand_data['product_id'] == product_id]['quantity'].tolist()
                product_lead_time = lead_time_data[lead_time_data['product_id'] == product_id]['lead_time_days'].tolist()
                
                if product_demand and product_lead_time:
                    # Estimate unit cost from sales data
                    product_sales = lead_time_data[lead_time_data['product_id'] == product_id]
                    if not product_sales.empty:
                        total_quantity = product_sales['quantity'].sum()
                        total_amount = product_sales['total_amount'].sum()
                        unit_cost = total_amount / total_quantity if total_quantity > 0 else 0
                    else:
                        unit_cost = 0
                    
                    safety_data.append({
                        'product_id': product_id,
                        'demand': product_demand,
                        'lead_time': product_lead_time,
                        'unit_cost': unit_cost
                    })
            
            safety_df = pd.DataFrame(safety_data)
            safety_stock = self.optimize_safety_stock(safety_df)
            
            # Combine all results into recommendations
            recommendations = []
            
            for product_id in product_ids:
                # Get current stock
                current_stock = inventory_data[inventory_data['product_id'] == product_id]['current_stock'].values
                current_stock = current_stock[0] if len(current_stock) > 0 else 0
                
                # Get forecasted demand
                product_forecast = demand_forecast[demand_forecast['product_id'] == product_id]
                forecasted_demand_30d = product_forecast['value'].sum() if not product_forecast.empty else 0
                
                # Get reorder point
                product_reorder = reorder_points[reorder_points['product_id'] == product_id]
                reorder_point = product_reorder['reorder_point'].values[0] if not product_reorder.empty else 0
                
                # Get safety stock
                product_safety = safety_stock[safety_stock['product_id'] == product_id]
                safety_stock_level = product_safety['service_level_safety_stock'].values[0] if not product_safety.empty else 0
                
                # Get lead time
                product_lead_time = lead_time_predictions[lead_time_predictions['product_id'] == product_id]
                avg_lead_time = product_lead_time['predicted_lead_time_days'].mean() if not product_lead_time.empty else 0
                
                # Calculate days of supply
                days_of_supply = current_stock / (forecasted_demand_30d / 30) if forecasted_demand_30d > 0 else float('inf')
                
                # Determine if reorder is needed
                reorder_needed = current_stock <= reorder_point
                
                # Calculate order quantity if reorder is needed
                if reorder_needed:
                    # Calculate economic order quantity (simplified)
                    avg_daily_demand = forecasted_demand_30d / 30
                    order_quantity = avg_daily_demand * avg_lead_time + safety_stock_level - current_stock
                    order_quantity = max(0, order_quantity)
                else:
                    order_quantity = 0
                
                recommendations.append({
                    'product_id': product_id,
                    'current_stock': current_stock,
                    'forecasted_demand_30d': forecasted_demand_30d,
                    'avg_daily_demand': forecasted_demand_30d / 30,
                    'days_of_supply': days_of_supply,
                    'reorder_point': reorder_point,
                    'safety_stock': safety_stock_level,
                    'avg_lead_time': avg_lead_time,
                    'reorder_needed': reorder_needed,
                    'recommended_order_quantity': order_quantity,
                    'stockout_risk': 'High' if days_of_supply < avg_lead_time else 'Medium' if days_of_supply < avg_lead_time * 2 else 'Low'
                })
            
            return pd.DataFrame(recommendations)
        else:
            raise ValueError("Database session not available")
    
    def close(self) -> None:
        """
        Close the prediction engine and release resources.
        """
        if self.session is not None:
            self.session.close()
            logger.info("Closed database session")
        
        logger.info("Closed prediction engine")
