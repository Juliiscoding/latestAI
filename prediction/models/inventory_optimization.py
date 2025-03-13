"""
Inventory optimization models for the Mercurios.ai Predictive Inventory Management tool.

This module contains models for reorder point calculation and safety stock optimization.
"""
import os
import pickle
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy import stats

from prediction.models.base_model import BasePredictionModel
from etl.utils.logger import logger


class ReorderPointCalculator(BasePredictionModel):
    """
    Reorder Point Calculator for inventory management.
    
    This model calculates the optimal reorder point based on demand forecasts,
    lead time predictions, and desired service level.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Reorder Point Calculator.
        
        Args:
            config (Dict[str, Any], optional): Configuration parameters for the model
                - service_level (float): Desired service level (0.0-1.0)
                - lead_time_factor (float): Factor to adjust lead time estimates
                - safety_factor (float): Additional safety factor
        """
        super().__init__(name="ReorderPointCalculator", config=config)
        self.service_level = self.config.get('service_level', 0.95)
        self.lead_time_factor = self.config.get('lead_time_factor', 1.0)
        self.safety_factor = self.config.get('safety_factor', 1.0)
        
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the data for reorder point calculation.
        
        Args:
            data (pd.DataFrame): Raw data with demand and lead time information
            
        Returns:
            pd.DataFrame: Preprocessed data
        """
        # Check required columns
        required_columns = ['product_id', 'demand', 'lead_time']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Group by product_id if not already aggregated
        if len(data['product_id'].unique()) > 1:
            data = data.groupby('product_id').agg({
                'demand': list,
                'lead_time': list
            }).reset_index()
        
        # Calculate demand statistics
        data['avg_demand'] = data['demand'].apply(lambda x: np.mean(x))
        data['std_demand'] = data['demand'].apply(lambda x: np.std(x))
        
        # Calculate lead time statistics
        data['avg_lead_time'] = data['lead_time'].apply(lambda x: np.mean(x))
        data['std_lead_time'] = data['lead_time'].apply(lambda x: np.std(x))
        
        return data
    
    def train(self, data: pd.DataFrame, **kwargs) -> None:
        """
        Train the Reorder Point Calculator.
        
        For this model, training simply involves storing the preprocessed data
        and calculating model parameters.
        
        Args:
            data (pd.DataFrame): Training data with demand and lead time information
            **kwargs: Additional training parameters
        """
        # Preprocess data
        self.training_data = self.preprocess_data(data)
        
        # Calculate safety factor based on service level
        # Using the inverse of the standard normal cumulative distribution
        self.z_score = stats.norm.ppf(self.service_level)
        logger.info(f"Calculated Z-score for service level {self.service_level}: {self.z_score}")
        
        self.is_trained = True
    
    def predict(self, data: pd.DataFrame, horizon: int = None, **kwargs) -> pd.DataFrame:
        """
        Calculate reorder points for products.
        
        Args:
            data (pd.DataFrame): Product data with demand and lead time information
            horizon (int): Not used for this model
            **kwargs: Additional calculation parameters
            
        Returns:
            pd.DataFrame: Calculated reorder points
        """
        # Use training data if no new data provided
        if data is None:
            if self.training_data is None:
                raise ValueError("No data provided and no training data available")
            data = self.training_data
        else:
            # Preprocess new data
            data = self.preprocess_data(data)
        
        # Calculate reorder points
        results = []
        
        for _, row in data.iterrows():
            product_id = row['product_id']
            avg_demand = row['avg_demand']
            std_demand = row['std_demand']
            avg_lead_time = row['avg_lead_time'] * self.lead_time_factor
            std_lead_time = row['std_lead_time']
            
            # Calculate demand during lead time
            demand_during_lead_time = avg_demand * avg_lead_time
            
            # Calculate standard deviation of demand during lead time
            # Using the formula: sqrt(L * σ_d^2 + d^2 * σ_L^2)
            # where L is average lead time, d is average demand,
            # σ_d is standard deviation of demand, and σ_L is standard deviation of lead time
            std_demand_during_lead_time = np.sqrt(
                avg_lead_time * std_demand**2 + avg_demand**2 * std_lead_time**2
            )
            
            # Calculate safety stock
            safety_stock = self.z_score * std_demand_during_lead_time * self.safety_factor
            
            # Calculate reorder point
            reorder_point = demand_during_lead_time + safety_stock
            
            results.append({
                'product_id': product_id,
                'avg_demand': avg_demand,
                'avg_lead_time': avg_lead_time,
                'demand_during_lead_time': demand_during_lead_time,
                'safety_stock': safety_stock,
                'reorder_point': reorder_point
            })
        
        return pd.DataFrame(results)
    
    def save(self, path: str) -> None:
        """
        Save the Reorder Point Calculator to disk.
        
        Args:
            path (str): Path to save the model
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model and parameters
        model_data = {
            'config': self.config,
            'service_level': self.service_level,
            'lead_time_factor': self.lead_time_factor,
            'safety_factor': self.safety_factor,
            'z_score': getattr(self, 'z_score', None),
            'is_trained': self.is_trained,
            'training_data': self.training_data
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Reorder Point Calculator saved to {path}")
    
    def load(self, path: str) -> None:
        """
        Load the Reorder Point Calculator from disk.
        
        Args:
            path (str): Path to load the model from
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.config = model_data['config']
        self.service_level = model_data['service_level']
        self.lead_time_factor = model_data['lead_time_factor']
        self.safety_factor = model_data['safety_factor']
        self.z_score = model_data['z_score']
        self.is_trained = model_data['is_trained']
        self.training_data = model_data['training_data']
        
        logger.info(f"Reorder Point Calculator loaded from {path}")


class SafetyStockOptimizer(BasePredictionModel):
    """
    Safety Stock Optimizer for inventory management.
    
    This model optimizes safety stock levels based on demand variability,
    lead time uncertainty, service level targets, and holding costs.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Safety Stock Optimizer.
        
        Args:
            config (Dict[str, Any], optional): Configuration parameters for the model
                - service_level (float): Desired service level (0.0-1.0)
                - holding_cost_rate (float): Annual holding cost as a percentage of item value
                - stockout_cost_factor (float): Factor to estimate stockout cost relative to item value
                - review_period (int): Inventory review period in days
        """
        super().__init__(name="SafetyStockOptimizer", config=config)
        self.service_level = self.config.get('service_level', 0.95)
        self.holding_cost_rate = self.config.get('holding_cost_rate', 0.25)  # 25% per year
        self.stockout_cost_factor = self.config.get('stockout_cost_factor', 1.5)
        self.review_period = self.config.get('review_period', 7)  # 7 days
        
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the data for safety stock optimization.
        
        Args:
            data (pd.DataFrame): Raw data with demand, lead time, and cost information
            
        Returns:
            pd.DataFrame: Preprocessed data
        """
        # Check required columns
        required_columns = ['product_id', 'demand', 'lead_time', 'unit_cost']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Group by product_id if not already aggregated
        if len(data['product_id'].unique()) > 1:
            data = data.groupby('product_id').agg({
                'demand': list,
                'lead_time': list,
                'unit_cost': 'first'
            }).reset_index()
        
        # Calculate demand statistics
        data['avg_demand'] = data['demand'].apply(lambda x: np.mean(x))
        data['std_demand'] = data['demand'].apply(lambda x: np.std(x))
        
        # Calculate lead time statistics
        data['avg_lead_time'] = data['lead_time'].apply(lambda x: np.mean(x))
        data['std_lead_time'] = data['lead_time'].apply(lambda x: np.std(x))
        
        # Calculate daily holding cost
        data['daily_holding_cost'] = data['unit_cost'] * self.holding_cost_rate / 365
        
        # Calculate stockout cost (estimated)
        data['stockout_cost'] = data['unit_cost'] * self.stockout_cost_factor
        
        return data
    
    def train(self, data: pd.DataFrame, **kwargs) -> None:
        """
        Train the Safety Stock Optimizer.
        
        For this model, training involves storing the preprocessed data
        and calculating model parameters.
        
        Args:
            data (pd.DataFrame): Training data with demand, lead time, and cost information
            **kwargs: Additional training parameters
        """
        # Preprocess data
        self.training_data = self.preprocess_data(data)
        
        # Calculate safety factor based on service level
        self.z_score = stats.norm.ppf(self.service_level)
        logger.info(f"Calculated Z-score for service level {self.service_level}: {self.z_score}")
        
        self.is_trained = True
    
    def predict(self, data: pd.DataFrame, horizon: int = None, **kwargs) -> pd.DataFrame:
        """
        Optimize safety stock levels for products.
        
        Args:
            data (pd.DataFrame): Product data with demand, lead time, and cost information
            horizon (int): Not used for this model
            **kwargs: Additional optimization parameters
            
        Returns:
            pd.DataFrame: Optimized safety stock levels
        """
        # Use training data if no new data provided
        if data is None:
            if self.training_data is None:
                raise ValueError("No data provided and no training data available")
            data = self.training_data
        else:
            # Preprocess new data
            data = self.preprocess_data(data)
        
        # Override service level if provided
        service_level = kwargs.get('service_level', self.service_level)
        z_score = stats.norm.ppf(service_level)
        
        # Optimize safety stock levels
        results = []
        
        for _, row in data.iterrows():
            product_id = row['product_id']
            avg_demand = row['avg_demand']
            std_demand = row['std_demand']
            avg_lead_time = row['avg_lead_time']
            std_lead_time = row['std_lead_time']
            unit_cost = row['unit_cost']
            daily_holding_cost = row['daily_holding_cost']
            stockout_cost = row['stockout_cost']
            
            # Calculate standard deviation of demand during lead time + review period
            protection_period = avg_lead_time + self.review_period
            std_demand_during_protection = np.sqrt(
                protection_period * std_demand**2 + avg_demand**2 * std_lead_time**2
            )
            
            # Calculate safety stock based on service level
            service_level_safety_stock = z_score * std_demand_during_protection
            
            # Calculate optimal safety stock based on costs
            # Using the newsvendor model
            critical_ratio = stockout_cost / (stockout_cost + daily_holding_cost)
            cost_optimal_z = stats.norm.ppf(critical_ratio)
            cost_optimal_safety_stock = cost_optimal_z * std_demand_during_protection
            
            # Calculate expected stockout units
            expected_stockout = std_demand_during_protection * stats.norm.pdf(z_score) - z_score * (1 - stats.norm.cdf(z_score))
            
            # Calculate expected annual holding cost
            annual_holding_cost = service_level_safety_stock * daily_holding_cost * 365
            
            # Calculate expected annual stockout cost
            annual_demand = avg_demand * 365
            annual_order_cycles = annual_demand / (avg_demand * protection_period)
            annual_stockout_cost = expected_stockout * stockout_cost * annual_order_cycles
            
            # Calculate total cost
            total_annual_cost = annual_holding_cost + annual_stockout_cost
            
            results.append({
                'product_id': product_id,
                'avg_demand': avg_demand,
                'avg_lead_time': avg_lead_time,
                'protection_period': protection_period,
                'std_demand_during_protection': std_demand_during_protection,
                'service_level': service_level,
                'service_level_safety_stock': service_level_safety_stock,
                'cost_optimal_safety_stock': cost_optimal_safety_stock,
                'annual_holding_cost': annual_holding_cost,
                'annual_stockout_cost': annual_stockout_cost,
                'total_annual_cost': total_annual_cost
            })
        
        return pd.DataFrame(results)
    
    def save(self, path: str) -> None:
        """
        Save the Safety Stock Optimizer to disk.
        
        Args:
            path (str): Path to save the model
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model and parameters
        model_data = {
            'config': self.config,
            'service_level': self.service_level,
            'holding_cost_rate': self.holding_cost_rate,
            'stockout_cost_factor': self.stockout_cost_factor,
            'review_period': self.review_period,
            'z_score': getattr(self, 'z_score', None),
            'is_trained': self.is_trained,
            'training_data': self.training_data
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Safety Stock Optimizer saved to {path}")
    
    def load(self, path: str) -> None:
        """
        Load the Safety Stock Optimizer from disk.
        
        Args:
            path (str): Path to load the model from
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.config = model_data['config']
        self.service_level = model_data['service_level']
        self.holding_cost_rate = model_data['holding_cost_rate']
        self.stockout_cost_factor = model_data['stockout_cost_factor']
        self.review_period = model_data['review_period']
        self.z_score = model_data['z_score']
        self.is_trained = model_data['is_trained']
        self.training_data = model_data['training_data']
        
        logger.info(f"Safety Stock Optimizer loaded from {path}")
