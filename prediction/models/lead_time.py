"""
Lead time prediction models for the Mercurios.ai Predictive Inventory Management tool.
"""
import os
import pickle
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from prediction.models.base_model import BasePredictionModel
from etl.utils.logger import logger


class LeadTimePredictionModel(BasePredictionModel):
    """
    Lead time prediction model for supplier delivery times.
    
    This model predicts the lead time (time between order and delivery)
    based on supplier, product, order size, and other factors.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the lead time prediction model.
        
        Args:
            config (Dict[str, Any], optional): Configuration parameters for the model
                - model_type (str): Type of model to use ('rf', 'gb', 'linear')
                - test_size (float): Proportion of data to use for testing
                - random_state (int): Random seed for reproducibility
                - n_estimators (int): Number of estimators for ensemble models
                - max_depth (int): Maximum depth of trees for ensemble models
        """
        super().__init__(name="LeadTimePrediction", config=config)
        self.model_type = self.config.get('model_type', 'rf')
        self.test_size = self.config.get('test_size', 0.2)
        self.random_state = self.config.get('random_state', 42)
        
        # Initialize preprocessing components
        self.preprocessor = None
        self.X_train = None
        self.y_train = None
        
    def preprocess_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Preprocess the data for lead time prediction.
        
        Args:
            data (pd.DataFrame): Raw data with order and delivery information
            
        Returns:
            Tuple[pd.DataFrame, pd.Series]: Preprocessed features and target
        """
        # Check required columns
        required_columns = ['supplier_id', 'product_id', 'order_date', 'delivery_date', 'quantity', 'order_value']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Calculate lead time in days
        if 'lead_time_days' not in data.columns:
            data['lead_time_days'] = (pd.to_datetime(data['delivery_date']) - pd.to_datetime(data['order_date'])).dt.days
        
        # Filter out invalid lead times
        data = data[data['lead_time_days'] > 0]
        
        # Create features
        features = data.copy()
        
        # Extract date features
        features['order_date'] = pd.to_datetime(features['order_date'])
        features['order_month'] = features['order_date'].dt.month
        features['order_day_of_week'] = features['order_date'].dt.dayofweek
        features['order_quarter'] = features['order_date'].dt.quarter
        
        # Define feature columns
        categorical_features = ['supplier_id', 'product_id', 'order_month', 'order_day_of_week', 'order_quarter']
        numerical_features = ['quantity', 'order_value']
        
        # Add any additional features from the data
        additional_numerical = [col for col in features.columns if col.startswith('supplier_metric_') or col.startswith('product_metric_')]
        numerical_features.extend(additional_numerical)
        
        # Create column transformer for preprocessing
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ],
            remainder='drop'
        )
        
        # Extract features and target
        X = features[categorical_features + numerical_features]
        y = features['lead_time_days']
        
        # Store preprocessor
        self.preprocessor = preprocessor
        
        return X, y
    
    def train(self, data: pd.DataFrame, **kwargs) -> None:
        """
        Train the lead time prediction model.
        
        Args:
            data (pd.DataFrame): Training data with order and delivery information
            **kwargs: Additional training parameters
        """
        if data.empty:
            logger.warning("Empty dataset provided for lead time prediction model training")
            return
        
        # Preprocess data
        X, y = self.preprocess_data(data)
        
        # Split into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state
        )
        
        self.X_train = X_train
        self.y_train = y_train
        
        # Define features
        numerical_features = [col for col in X.columns if X[col].dtype in ['int64', 'float64']]
        categorical_features = [col for col in X.columns if X[col].dtype == 'object' or X[col].dtype.name == 'category']
        
        # Create preprocessing pipeline
        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numerical_features),
                ('cat', categorical_transformer, categorical_features)
            ]
        )
        
        # Create model based on configuration
        if self.model_type == 'rf':
            model = RandomForestRegressor(
                n_estimators=self.config.get('n_estimators', 100),
                max_depth=self.config.get('max_depth', None),
                random_state=self.random_state
            )
        elif self.model_type == 'gb':
            model = GradientBoostingRegressor(
                n_estimators=self.config.get('n_estimators', 100),
                max_depth=self.config.get('max_depth', 3),
                random_state=self.random_state
            )
        elif self.model_type == 'linear':
            model = LinearRegression()
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        
        # Create full pipeline
        self.model = Pipeline(steps=[
            ('preprocessor', self.preprocessor),
            ('regressor', model)
        ])
        
        # Train the model
        try:
            self.model.fit(X_train, y_train)
            logger.info(f"Lead time prediction model trained with {len(X_train)} samples")
            
            # Evaluate on test set
            y_pred = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            self.metrics = {
                'mae': mae,
                'rmse': rmse,
                'r2': r2
            }
            
            logger.info(f"Model evaluation metrics: MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.2f}")
            
            # Feature importance for tree-based models
            if self.model_type in ['rf', 'gb']:
                try:
                    feature_names = (
                        numerical_features + 
                        self.preprocessor.transformers_[1][1].get_feature_names_out(categorical_features).tolist()
                    )
                    importances = self.model.named_steps['regressor'].feature_importances_
                    feature_importance = pd.DataFrame({
                        'feature': feature_names,
                        'importance': importances
                    }).sort_values('importance', ascending=False)
                    
                    logger.info(f"Top 10 important features: {feature_importance.head(10)}")
                except Exception as e:
                    logger.warning(f"Could not calculate feature importance: {e}")
            
        except Exception as e:
            logger.error(f"Error training lead time prediction model: {e}")
            raise
        
        self.is_trained = True
    
    def predict(self, data: pd.DataFrame, horizon: int = None, **kwargs) -> pd.DataFrame:
        """
        Predict lead times for new orders.
        
        Args:
            data (pd.DataFrame): Order data to predict lead times for
            horizon (int): Not used for this model
            **kwargs: Additional prediction parameters
            
        Returns:
            pd.DataFrame: Predictions with lead time in days
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            # Preprocess data (without calculating lead_time_days)
            required_columns = ['supplier_id', 'product_id', 'order_date', 'quantity', 'order_value']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns for prediction: {missing_columns}")
            
            # Create features
            features = data.copy()
            
            # Extract date features
            features['order_date'] = pd.to_datetime(features['order_date'])
            features['order_month'] = features['order_date'].dt.month
            features['order_day_of_week'] = features['order_date'].dt.dayofweek
            features['order_quarter'] = features['order_date'].dt.quarter
            
            # Define feature columns (must match training)
            categorical_features = ['supplier_id', 'product_id', 'order_month', 'order_day_of_week', 'order_quarter']
            numerical_features = ['quantity', 'order_value']
            
            # Add any additional features from the data
            additional_numerical = [col for col in features.columns if col.startswith('supplier_metric_') or col.startswith('product_metric_')]
            numerical_features.extend(additional_numerical)
            
            # Extract features
            X = features[categorical_features + numerical_features]
            
            # Make predictions
            lead_time_predictions = self.model.predict(X)
            
            # Create result DataFrame
            result = data.copy()
            result['predicted_lead_time_days'] = lead_time_predictions
            result['predicted_delivery_date'] = pd.to_datetime(result['order_date']) + pd.to_timedelta(result['predicted_lead_time_days'], unit='D')
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting lead times: {e}")
            raise
    
    def save(self, path: str) -> None:
        """
        Save the lead time prediction model to disk.
        
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
            'model_type': self.model_type,
            'test_size': self.test_size,
            'random_state': self.random_state,
            'preprocessor': self.preprocessor,
            'is_trained': self.is_trained,
            'metrics': self.metrics
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Lead time prediction model saved to {path}")
    
    def load(self, path: str) -> None:
        """
        Load the lead time prediction model from disk.
        
        Args:
            path (str): Path to load the model from
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.config = model_data['config']
        self.model_type = model_data['model_type']
        self.test_size = model_data['test_size']
        self.random_state = model_data['random_state']
        self.preprocessor = model_data['preprocessor']
        self.is_trained = model_data['is_trained']
        self.metrics = model_data['metrics']
        
        logger.info(f"Lead time prediction model loaded from {path}")
