"""
Base prediction model for the Mercurios.ai Predictive Inventory Management tool.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from etl.utils.logger import logger


class BasePredictionModel(ABC):
    """
    Base class for all prediction models.
    
    This abstract class defines the interface for all prediction models
    in the Mercurios.ai Predictive Inventory Management tool.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base prediction model.
        
        Args:
            name (str): Name of the model
            config (Dict[str, Any], optional): Configuration parameters for the model
        """
        self.name = name
        self.config = config or {}
        self.model = None
        self.is_trained = False
        self.training_data = None
        self.metrics = {}
        logger.info(f"Initialized {self.name} prediction model")
    
    @abstractmethod
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the data for model training and prediction.
        
        Args:
            data (pd.DataFrame): Raw data to preprocess
            
        Returns:
            pd.DataFrame: Preprocessed data
        """
        pass
    
    @abstractmethod
    def train(self, data: pd.DataFrame, **kwargs) -> None:
        """
        Train the model on the provided data.
        
        Args:
            data (pd.DataFrame): Training data
            **kwargs: Additional training parameters
        """
        pass
    
    @abstractmethod
    def predict(self, data: pd.DataFrame, horizon: int, **kwargs) -> pd.DataFrame:
        """
        Generate predictions using the trained model.
        
        Args:
            data (pd.DataFrame): Data to use for prediction
            horizon (int): Number of time periods to forecast
            **kwargs: Additional prediction parameters
            
        Returns:
            pd.DataFrame: Predictions for the specified horizon
        """
        pass
    
    def evaluate(self, actual: pd.DataFrame, predicted: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate the model performance.
        
        Args:
            actual (pd.DataFrame): Actual values
            predicted (pd.DataFrame): Predicted values
            
        Returns:
            Dict[str, float]: Dictionary of evaluation metrics
        """
        if len(actual) != len(predicted):
            logger.warning(f"Length mismatch: actual={len(actual)}, predicted={len(predicted)}")
            min_len = min(len(actual), len(predicted))
            actual = actual.iloc[:min_len]
            predicted = predicted.iloc[:min_len]
        
        # Calculate common evaluation metrics
        errors = actual.values - predicted.values
        abs_errors = np.abs(errors)
        
        metrics = {
            "mae": np.mean(abs_errors),  # Mean Absolute Error
            "mse": np.mean(np.square(errors)),  # Mean Squared Error
            "rmse": np.sqrt(np.mean(np.square(errors))),  # Root Mean Squared Error
            "mape": np.mean(np.abs(errors / actual.values)) * 100,  # Mean Absolute Percentage Error
        }
        
        self.metrics = metrics
        logger.info(f"Model evaluation metrics: {metrics}")
        return metrics
    
    def save(self, path: str) -> None:
        """
        Save the model to disk.
        
        Args:
            path (str): Path to save the model
        """
        raise NotImplementedError("Save method not implemented")
    
    def load(self, path: str) -> None:
        """
        Load the model from disk.
        
        Args:
            path (str): Path to load the model from
        """
        raise NotImplementedError("Load method not implemented")
    
    def detect_seasonality(self, data: pd.DataFrame, date_column: str, value_column: str) -> Dict[str, Any]:
        """
        Detect seasonality in the time series data.
        
        Args:
            data (pd.DataFrame): Time series data
            date_column (str): Name of the date column
            value_column (str): Name of the value column
            
        Returns:
            Dict[str, Any]: Dictionary with seasonality information
        """
        # Ensure data is sorted by date
        data = data.sort_values(by=date_column)
        
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_dtype(data[date_column]):
            data[date_column] = pd.to_datetime(data[date_column])
        
        # Set date as index
        ts_data = data.set_index(date_column)[value_column]
        
        # Check for daily seasonality
        daily_acf = self._autocorrelation(ts_data, 7)
        
        # Check for weekly seasonality
        weekly_acf = self._autocorrelation(ts_data, 7)
        
        # Check for monthly seasonality
        monthly_acf = self._autocorrelation(ts_data, 30)
        
        # Check for quarterly seasonality
        quarterly_acf = self._autocorrelation(ts_data, 90)
        
        # Check for yearly seasonality
        yearly_acf = self._autocorrelation(ts_data, 365)
        
        seasonality = {
            "daily": daily_acf > 0.2,
            "weekly": weekly_acf > 0.2,
            "monthly": monthly_acf > 0.2,
            "quarterly": quarterly_acf > 0.2,
            "yearly": yearly_acf > 0.2,
            "acf_values": {
                "daily": daily_acf,
                "weekly": weekly_acf,
                "monthly": monthly_acf,
                "quarterly": quarterly_acf,
                "yearly": yearly_acf
            }
        }
        
        logger.info(f"Detected seasonality: {seasonality}")
        return seasonality
    
    def _autocorrelation(self, series: pd.Series, lag: int) -> float:
        """
        Calculate autocorrelation for a given lag.
        
        Args:
            series (pd.Series): Time series data
            lag (int): Lag to calculate autocorrelation for
            
        Returns:
            float: Autocorrelation value
        """
        # Handle case where series is too short
        if len(series) <= lag:
            return 0.0
        
        # Calculate autocorrelation
        series_mean = series.mean()
        numerator = ((series.iloc[lag:] - series_mean) * (series.iloc[:-lag] - series_mean)).sum()
        denominator = ((series - series_mean) ** 2).sum()
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
