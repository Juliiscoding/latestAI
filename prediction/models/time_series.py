"""
Time-series forecasting models for the Mercurios.ai Predictive Inventory Management tool.
"""
import os
import pickle
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pmdarima as pm
from sklearn.metrics import mean_absolute_error, mean_squared_error

from prediction.models.base_model import BasePredictionModel
from etl.utils.logger import logger


class ARIMAModel(BasePredictionModel):
    """
    ARIMA (AutoRegressive Integrated Moving Average) model for time-series forecasting.
    
    This model is suitable for univariate time-series forecasting with trend and seasonality.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ARIMA model.
        
        Args:
            config (Dict[str, Any], optional): Configuration parameters for the model
                - p (int): Order of the AR term
                - d (int): Order of the I term
                - q (int): Order of the MA term
                - seasonal (bool): Whether to use seasonal ARIMA
                - P (int): Seasonal order of the AR term
                - D (int): Seasonal order of the I term
                - Q (int): Seasonal order of the MA term
                - s (int): Seasonal period
                - auto (bool): Whether to use auto-ARIMA
        """
        super().__init__(name="ARIMA", config=config)
        self.p = self.config.get('p', 1)
        self.d = self.config.get('d', 1)
        self.q = self.config.get('q', 1)
        self.seasonal = self.config.get('seasonal', False)
        self.P = self.config.get('P', 1)
        self.D = self.config.get('D', 0)
        self.Q = self.config.get('Q', 1)
        self.s = self.config.get('s', 12)
        self.auto = self.config.get('auto', True)
        
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the data for ARIMA model.
        
        Args:
            data (pd.DataFrame): Raw data with date and value columns
            
        Returns:
            pd.DataFrame: Preprocessed data
        """
        # Ensure data has date and value columns
        if 'date' not in data.columns or 'value' not in data.columns:
            raise ValueError("Data must have 'date' and 'value' columns")
        
        # Convert date to datetime if not already
        if not pd.api.types.is_datetime64_dtype(data['date']):
            data['date'] = pd.to_datetime(data['date'])
        
        # Sort by date
        data = data.sort_values(by='date')
        
        # Set date as index
        data = data.set_index('date')
        
        # Resample to regular frequency if needed
        freq = self.config.get('frequency', 'D')
        if freq:
            data = data.resample(freq).mean().fillna(method='ffill')
        
        # Handle missing values
        data = data.fillna(method='ffill').fillna(method='bfill')
        
        # Log transform if specified
        if self.config.get('log_transform', False):
            data['value'] = np.log1p(data['value'])
        
        self.training_data = data
        return data
    
    def train(self, data: pd.DataFrame, **kwargs) -> None:
        """
        Train the ARIMA model.
        
        Args:
            data (pd.DataFrame): Training data with date index and value column
            **kwargs: Additional training parameters
        """
        # Preprocess data if not already done
        if self.training_data is None or not data.equals(self.training_data):
            data = self.preprocess_data(data)
        
        # Extract values
        values = data['value'].values
        
        # Use auto-ARIMA if specified
        if self.auto:
            logger.info("Using auto-ARIMA to find optimal parameters")
            try:
                # Find optimal parameters
                auto_model = pm.auto_arima(
                    values,
                    seasonal=self.seasonal,
                    m=self.s if self.seasonal else 1,
                    suppress_warnings=True,
                    error_action='ignore',
                    trace=kwargs.get('trace', False)
                )
                
                # Extract parameters
                order = auto_model.order
                self.p, self.d, self.q = order
                
                if self.seasonal:
                    seasonal_order = auto_model.seasonal_order
                    self.P, self.D, self.Q, self.s = seasonal_order
                
                logger.info(f"Auto-ARIMA selected parameters: p={self.p}, d={self.d}, q={self.q}")
                if self.seasonal:
                    logger.info(f"Seasonal parameters: P={self.P}, D={self.D}, Q={self.Q}, s={self.s}")
                
                # Use the auto-ARIMA model
                self.model = auto_model
                
            except Exception as e:
                logger.error(f"Error in auto-ARIMA: {e}")
                logger.info("Falling back to manual ARIMA parameters")
                self.auto = False
        
        # Use manual parameters if auto-ARIMA is not used or failed
        if not self.auto:
            try:
                if self.seasonal:
                    # Use SARIMAX for seasonal ARIMA
                    self.model = SARIMAX(
                        values,
                        order=(self.p, self.d, self.q),
                        seasonal_order=(self.P, self.D, self.Q, self.s)
                    )
                else:
                    # Use ARIMA for non-seasonal
                    self.model = ARIMA(values, order=(self.p, self.d, self.q))
                
                # Fit the model
                self.model = self.model.fit()
                logger.info(f"ARIMA model trained with parameters: p={self.p}, d={self.d}, q={self.q}")
                
            except Exception as e:
                logger.error(f"Error training ARIMA model: {e}")
                raise
        
        self.is_trained = True
    
    def predict(self, data: pd.DataFrame, horizon: int, **kwargs) -> pd.DataFrame:
        """
        Generate forecasts using the trained ARIMA model.
        
        Args:
            data (pd.DataFrame): Data to use for prediction (can be training data or new data)
            horizon (int): Number of time periods to forecast
            **kwargs: Additional prediction parameters
            
        Returns:
            pd.DataFrame: Predictions for the specified horizon
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Preprocess data if not already done
        if self.training_data is None or not data.equals(self.training_data):
            data = self.preprocess_data(data)
        
        # Generate forecast
        try:
            if self.auto:
                # Use pmdarima's predict method
                forecast = self.model.predict(n_periods=horizon)
            else:
                # Use statsmodels' forecast method
                forecast = self.model.forecast(steps=horizon)
            
            # Create date range for forecast
            last_date = data.index[-1]
            freq = self.config.get('frequency', 'D')
            forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq=freq)
            
            # Create forecast DataFrame
            forecast_df = pd.DataFrame({
                'date': forecast_dates,
                'value': forecast
            })
            
            # Inverse log transform if needed
            if self.config.get('log_transform', False):
                forecast_df['value'] = np.expm1(forecast_df['value'])
            
            # Add prediction intervals if available
            if hasattr(self.model, 'get_forecast') and not self.auto:
                try:
                    forecast_obj = self.model.get_forecast(steps=horizon)
                    conf_int = forecast_obj.conf_int(alpha=0.05)
                    forecast_df['lower_bound'] = conf_int.iloc[:, 0]
                    forecast_df['upper_bound'] = conf_int.iloc[:, 1]
                    
                    # Inverse log transform if needed
                    if self.config.get('log_transform', False):
                        forecast_df['lower_bound'] = np.expm1(forecast_df['lower_bound'])
                        forecast_df['upper_bound'] = np.expm1(forecast_df['upper_bound'])
                except:
                    logger.warning("Could not generate prediction intervals")
            
            return forecast_df
            
        except Exception as e:
            logger.error(f"Error generating ARIMA forecast: {e}")
            raise
    
    def save(self, path: str) -> None:
        """
        Save the ARIMA model to disk.
        
        Args:
            path (str): Path to save the model
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model and parameters
        model_data = {
            'model': self.model,
            'config': self.config,
            'p': self.p,
            'd': self.d,
            'q': self.q,
            'seasonal': self.seasonal,
            'P': self.P,
            'D': self.D,
            'Q': self.Q,
            's': self.s,
            'auto': self.auto,
            'is_trained': self.is_trained,
            'metrics': self.metrics
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"ARIMA model saved to {path}")
    
    def load(self, path: str) -> None:
        """
        Load the ARIMA model from disk.
        
        Args:
            path (str): Path to load the model from
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.config = model_data['config']
        self.p = model_data['p']
        self.d = model_data['d']
        self.q = model_data['q']
        self.seasonal = model_data['seasonal']
        self.P = model_data['P']
        self.D = model_data['D']
        self.Q = model_data['Q']
        self.s = model_data['s']
        self.auto = model_data['auto']
        self.is_trained = model_data['is_trained']
        self.metrics = model_data['metrics']
        
        logger.info(f"ARIMA model loaded from {path}")


class ExponentialSmoothingModel(BasePredictionModel):
    """
    Exponential Smoothing model for time-series forecasting.
    
    This model is suitable for univariate time-series forecasting with trend and seasonality.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Exponential Smoothing model.
        
        Args:
            config (Dict[str, Any], optional): Configuration parameters for the model
                - trend (str): Type of trend component ('add', 'mul', None)
                - seasonal (str): Type of seasonal component ('add', 'mul', None)
                - seasonal_periods (int): Number of periods in a seasonal cycle
                - damped (bool): Whether to use damped trend
        """
        super().__init__(name="ExponentialSmoothing", config=config)
        self.trend = self.config.get('trend', 'add')
        self.seasonal = self.config.get('seasonal', None)
        self.seasonal_periods = self.config.get('seasonal_periods', 12)
        self.damped = self.config.get('damped', False)
        
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the data for Exponential Smoothing model.
        
        Args:
            data (pd.DataFrame): Raw data with date and value columns
            
        Returns:
            pd.DataFrame: Preprocessed data
        """
        # Ensure data has date and value columns
        if 'date' not in data.columns or 'value' not in data.columns:
            raise ValueError("Data must have 'date' and 'value' columns")
        
        # Convert date to datetime if not already
        if not pd.api.types.is_datetime64_dtype(data['date']):
            data['date'] = pd.to_datetime(data['date'])
        
        # Sort by date
        data = data.sort_values(by='date')
        
        # Set date as index
        data = data.set_index('date')
        
        # Resample to regular frequency if needed
        freq = self.config.get('frequency', 'D')
        if freq:
            data = data.resample(freq).mean().fillna(method='ffill')
        
        # Handle missing values
        data = data.fillna(method='ffill').fillna(method='bfill')
        
        # Ensure positive values for multiplicative models
        if self.trend == 'mul' or self.seasonal == 'mul':
            if (data['value'] <= 0).any():
                logger.warning("Data contains non-positive values. Adding constant for multiplicative model.")
                min_val = data['value'].min()
                if min_val <= 0:
                    data['value'] = data['value'] - min_val + 1
        
        self.training_data = data
        return data
    
    def train(self, data: pd.DataFrame, **kwargs) -> None:
        """
        Train the Exponential Smoothing model.
        
        Args:
            data (pd.DataFrame): Training data with date index and value column
            **kwargs: Additional training parameters
        """
        # Preprocess data if not already done
        if self.training_data is None or not data.equals(self.training_data):
            data = self.preprocess_data(data)
        
        # Extract values
        values = data['value'].values
        
        # Check if we have enough data for seasonal model
        if self.seasonal and len(values) < 2 * self.seasonal_periods:
            logger.warning(f"Not enough data for seasonal model. Need at least {2 * self.seasonal_periods} points, but got {len(values)}.")
            if len(values) < self.seasonal_periods:
                logger.warning("Disabling seasonality due to insufficient data.")
                self.seasonal = None
        
        try:
            # Create and fit the model
            self.model = ExponentialSmoothing(
                values,
                trend=self.trend,
                seasonal=self.seasonal,
                seasonal_periods=self.seasonal_periods if self.seasonal else None,
                damped_trend=self.damped
            )
            
            self.model = self.model.fit(**kwargs)
            logger.info(f"Exponential Smoothing model trained with parameters: trend={self.trend}, seasonal={self.seasonal}, periods={self.seasonal_periods}, damped={self.damped}")
            
        except Exception as e:
            logger.error(f"Error training Exponential Smoothing model: {e}")
            raise
        
        self.is_trained = True
    
    def predict(self, data: pd.DataFrame, horizon: int, **kwargs) -> pd.DataFrame:
        """
        Generate forecasts using the trained Exponential Smoothing model.
        
        Args:
            data (pd.DataFrame): Data to use for prediction (can be training data or new data)
            horizon (int): Number of time periods to forecast
            **kwargs: Additional prediction parameters
            
        Returns:
            pd.DataFrame: Predictions for the specified horizon
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Preprocess data if not already done
        if self.training_data is None or not data.equals(self.training_data):
            data = self.preprocess_data(data)
        
        # Generate forecast
        try:
            forecast = self.model.forecast(horizon)
            
            # Create date range for forecast
            last_date = data.index[-1]
            freq = self.config.get('frequency', 'D')
            forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq=freq)
            
            # Create forecast DataFrame
            forecast_df = pd.DataFrame({
                'date': forecast_dates,
                'value': forecast
            })
            
            # Add prediction intervals if available
            try:
                conf_int = self.model.get_prediction(start=len(data), end=len(data) + horizon - 1).conf_int(alpha=0.05)
                forecast_df['lower_bound'] = conf_int.iloc[:, 0]
                forecast_df['upper_bound'] = conf_int.iloc[:, 1]
            except:
                logger.warning("Could not generate prediction intervals")
            
            return forecast_df
            
        except Exception as e:
            logger.error(f"Error generating Exponential Smoothing forecast: {e}")
            raise
    
    def save(self, path: str) -> None:
        """
        Save the Exponential Smoothing model to disk.
        
        Args:
            path (str): Path to save the model
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model and parameters
        model_data = {
            'model': self.model,
            'config': self.config,
            'trend': self.trend,
            'seasonal': self.seasonal,
            'seasonal_periods': self.seasonal_periods,
            'damped': self.damped,
            'is_trained': self.is_trained,
            'metrics': self.metrics
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Exponential Smoothing model saved to {path}")
    
    def load(self, path: str) -> None:
        """
        Load the Exponential Smoothing model from disk.
        
        Args:
            path (str): Path to load the model from
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.config = model_data['config']
        self.trend = model_data['trend']
        self.seasonal = model_data['seasonal']
        self.seasonal_periods = model_data['seasonal_periods']
        self.damped = model_data['damped']
        self.is_trained = model_data['is_trained']
        self.metrics = model_data['metrics']
        
        logger.info(f"Exponential Smoothing model loaded from {path}")


# Factory function to create time-series models
def create_time_series_model(model_type: str, config: Optional[Dict[str, Any]] = None) -> BasePredictionModel:
    """
    Create a time-series forecasting model.
    
    Args:
        model_type (str): Type of model to create ('arima', 'exp_smoothing')
        config (Dict[str, Any], optional): Configuration parameters for the model
        
    Returns:
        BasePredictionModel: Time-series forecasting model
    """
    model_type = model_type.lower()
    
    if model_type == 'arima':
        return ARIMAModel(config)
    elif model_type == 'exp_smoothing':
        return ExponentialSmoothingModel(config)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
