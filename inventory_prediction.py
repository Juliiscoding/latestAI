import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import warnings
warnings.filterwarnings('ignore')

class InventoryPredictor:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.models = {}
        self.scalers = {}
        self.model_dir = "models"
        
        # Create model directory if it doesn't exist
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
    
    def load_data(self):
        """Load and prepare data for inventory prediction"""
        # Load sales data
        with open(f"{self.data_dir}/sale.json", "r") as f:
            sales_data = json.load(f)
            
        # Load inventory data
        with open(f"{self.data_dir}/inventory.json", "r") as f:
            inventory_data = json.load(f)
            
        # Load article data
        with open(f"{self.data_dir}/article.json", "r") as f:
            article_data = json.load(f)
        
        # Convert to DataFrames
        sales_df = pd.DataFrame(sales_data)
        inventory_df = pd.DataFrame(inventory_data)
        article_df = pd.DataFrame(article_data)
        
        # Map inventory to articles using common fields
        # Since inventory doesn't have articleNumber directly, we'll use other common fields
        # For this example, we'll assume inventory can be linked to articles via supplierNumber and categoryNumber
        
        # Create a mapping from article to inventory
        article_to_inventory = {}
        
        # For each article, find matching inventory items
        for _, article in article_df.iterrows():
            article_number = article['number']
            supplier_number = article.get('supplierNumber')
            category_number = article.get('categoryNumber')
            
            # Find matching inventory items
            matching_inventory = inventory_df[
                (inventory_df['supplierNumber'] == supplier_number) & 
                (inventory_df['categoryNumber'] == category_number)
            ]
            
            # Assign a random quantity for demonstration purposes
            # In a real system, you would have a more accurate way to match inventory to articles
            if len(matching_inventory) > 0:
                article_to_inventory[article_number] = {
                    'inventory_id': matching_inventory.iloc[0]['id'],
                    'quantity': np.random.randint(0, 100)  # Random quantity for demonstration
                }
        
        # Add articleNumber to inventory_df for easier processing
        inventory_with_article = []
        for article_number, inv_data in article_to_inventory.items():
            inventory_with_article.append({
                'articleNumber': article_number,
                'inventory_id': inv_data['inventory_id'],
                'quantity': inv_data['quantity']
            })
        
        # Create a new inventory DataFrame with articleNumber
        inventory_df_with_article = pd.DataFrame(inventory_with_article)
        
        # Convert date strings to datetime objects
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        
        # Extract features from date
        sales_df['year'] = sales_df['date'].dt.year
        sales_df['month'] = sales_df['date'].dt.month
        sales_df['day'] = sales_df['date'].dt.day
        sales_df['day_of_week'] = sales_df['date'].dt.dayofweek
        sales_df['quarter'] = sales_df['date'].dt.quarter
        
        # Aggregate sales by article and date
        sales_agg = sales_df.groupby(['articleNumber', 'year', 'month', 'day']).agg({
            'quantity': 'sum',
            'salePrice': 'sum'
        }).reset_index()
        
        # Create a complete date range for each article
        min_date = sales_df['date'].min()
        max_date = sales_df['date'].max()
        
        # Create a dictionary to store processed data
        self.processed_data = {
            'sales_df': sales_df,
            'inventory_df': inventory_df_with_article,  # Use the inventory with articleNumber
            'article_df': article_df,
            'sales_agg': sales_agg,
            'min_date': min_date,
            'max_date': max_date
        }
        
        return self.processed_data
    
    def prepare_features(self, article_number, use_synthetic=False):
        """Prepare features for a specific article"""
        # If we're already using synthetic data, don't recurse
        if use_synthetic:
            # Create synthetic data for demonstration
            start_date = datetime.now() - timedelta(days=365)  # One year of data
            dates = [start_date + timedelta(days=i) for i in range(365)]
            
            # Create seasonal pattern with some randomness
            base_quantity = np.random.randint(5, 20)
            seasonal_factor = np.sin(np.array(range(365)) * (2 * np.pi / 365)) + 1  # Seasonal component
            weekly_factor = np.sin(np.array(range(365)) * (2 * np.pi / 7)) * 0.3 + 1  # Weekly component
            trend_factor = np.array(range(365)) * 0.001  # Slight upward trend
            random_factor = np.random.normal(0, 0.5, 365)  # Random noise
            
            quantities = np.maximum(0, np.round(base_quantity * (seasonal_factor + weekly_factor + trend_factor + random_factor)))
            
            # Create synthetic DataFrame
            synthetic_data = pd.DataFrame({
                'date': dates,
                'quantity': quantities,
                'salePrice': quantities * np.random.uniform(10, 50, 365)  # Random price between 10 and 50
            })
            
            # Set index to date
            synthetic_data.set_index('date', inplace=True)
            
            # Add day of week, month, quarter features
            synthetic_data['day_of_week'] = synthetic_data.index.dayofweek
            synthetic_data['month'] = synthetic_data.index.month
            synthetic_data['quarter'] = synthetic_data.index.quarter
            synthetic_data['year'] = synthetic_data.index.year
            
            # Create lagged features
            for lag in [1, 2, 3, 7, 14, 30]:
                synthetic_data[f'quantity_lag_{lag}'] = synthetic_data['quantity'].shift(lag)
                
            # Create rolling window features
            for window in [7, 14, 30]:
                synthetic_data[f'quantity_rolling_mean_{window}'] = synthetic_data['quantity'].rolling(window=window).mean()
                synthetic_data[f'quantity_rolling_std_{window}'] = synthetic_data['quantity'].rolling(window=window).std()
            
            # Drop rows with NaN values
            synthetic_data.dropna(inplace=True)
            
            # Prepare features and target
            X = synthetic_data.drop(['quantity', 'salePrice'], axis=1)
            y = synthetic_data['quantity']
            
            return X, y
            
        # Use real data if available
        sales_df = self.processed_data['sales_df']
        
        # Filter sales data for the specific article
        article_sales = sales_df[sales_df['articleNumber'] == article_number].copy()
        
        if len(article_sales) < 10:
            print(f"Not enough real data for article {article_number}. Creating synthetic data.")
            # Use synthetic data instead
            return self.prepare_features(article_number, use_synthetic=True)
        
        # Continue with real data processing
        article_sales['date'] = pd.to_datetime(article_sales['date']).dt.date
        daily_sales = article_sales.groupby('date').agg({
            'quantity': 'sum',
            'salePrice': 'sum'
        }).reset_index()
        
        # Convert to time series
        daily_sales['date'] = pd.to_datetime(daily_sales['date'])
        daily_sales.set_index('date', inplace=True)
        
        # Resample to daily frequency and fill missing values
        daily_sales = daily_sales.resample('D').sum().fillna(0)
        
        # Create lagged features (previous days' sales)
        for lag in [1, 2, 3, 7, 14, 30]:
            daily_sales[f'quantity_lag_{lag}'] = daily_sales['quantity'].shift(lag)
            
        # Create rolling window features
        for window in [7, 14, 30]:
            daily_sales[f'quantity_rolling_mean_{window}'] = daily_sales['quantity'].rolling(window=window).mean()
            daily_sales[f'quantity_rolling_std_{window}'] = daily_sales['quantity'].rolling(window=window).std()
        
        # Add day of week, month, quarter features
        daily_sales['day_of_week'] = daily_sales.index.dayofweek
        daily_sales['month'] = daily_sales.index.month
        daily_sales['quarter'] = daily_sales.index.quarter
        daily_sales['year'] = daily_sales.index.year
        
        # Drop rows with NaN values
        daily_sales.dropna(inplace=True)
        
        if len(daily_sales) < 10:
            print(f"Not enough processed data for article {article_number}. Creating synthetic data.")
            # Use synthetic data instead
            return self.prepare_features(article_number, use_synthetic=True)
        
        # Prepare features and target
        X = daily_sales.drop(['quantity', 'salePrice'], axis=1)
        y = daily_sales['quantity']
        
        return X, y
    
    def train_model(self, article_number):
        """Train a prediction model for a specific article"""
        X, y = self.prepare_features(article_number)
        
        if X is None or y is None:
            print(f"Not enough data to train model for article {article_number}")
            return None
        
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        print(f"Article {article_number} - Train score: {train_score:.4f}, Test score: {test_score:.4f}")
        
        # Save model and scaler
        self.models[article_number] = model
        self.scalers[article_number] = scaler
        
        # Save to disk
        joblib.dump(model, f"{self.model_dir}/model_{article_number}.pkl")
        joblib.dump(scaler, f"{self.model_dir}/scaler_{article_number}.pkl")
        
        return {
            'model': model,
            'scaler': scaler,
            'train_score': train_score,
            'test_score': test_score
        }
    
    def train_all_models(self, min_sales=10):
        """Train models for all articles with sufficient data"""
        if not hasattr(self, 'processed_data'):
            self.load_data()
        
        sales_df = self.processed_data['sales_df']
        
        # Get articles with sufficient sales data
        article_counts = sales_df['articleNumber'].value_counts()
        articles_to_model = article_counts[article_counts >= min_sales].index.tolist()
        
        results = {}
        for article_number in articles_to_model:
            print(f"Training model for article {article_number}...")
            result = self.train_model(article_number)
            if result:
                results[article_number] = result
        
        return results
    
    def predict_future_demand(self, article_number, days=30):
        """Predict future demand for a specific article"""
        if article_number not in self.models:
            # Try to load model from disk
            try:
                model_path = f"{self.model_dir}/model_{article_number}.pkl"
                scaler_path = f"{self.model_dir}/scaler_{article_number}.pkl"
                
                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    self.models[article_number] = joblib.load(model_path)
                    self.scalers[article_number] = joblib.load(scaler_path)
                else:
                    print(f"No model found for article {article_number}")
                    return None
            except Exception as e:
                print(f"Error loading model for article {article_number}: {str(e)}")
                return None
        
        # Get the latest data for prediction
        X, _ = self.prepare_features(article_number)
        
        if X is None:
            return None
        
        # Get the last date in the data
        last_date = X.index[-1]
        
        # Create a DataFrame for future dates
        future_dates = [last_date + timedelta(days=i+1) for i in range(days)]
        future_df = pd.DataFrame(index=future_dates)
        
        # Add features for future dates
        future_df['day_of_week'] = future_df.index.dayofweek
        future_df['month'] = future_df.index.month
        future_df['quarter'] = future_df.index.quarter
        future_df['year'] = future_df.index.year
        
        # Use the last known values for lagged features
        for lag in [1, 2, 3, 7, 14, 30]:
            future_df[f'quantity_lag_{lag}'] = X[f'quantity_lag_{lag}'].iloc[-1]
        
        # Use the last known values for rolling features
        for window in [7, 14, 30]:
            future_df[f'quantity_rolling_mean_{window}'] = X[f'quantity_rolling_mean_{window}'].iloc[-1]
            future_df[f'quantity_rolling_std_{window}'] = X[f'quantity_rolling_std_{window}'].iloc[-1]
        
        # Scale features
        future_scaled = self.scalers[article_number].transform(future_df)
        
        # Make predictions
        predictions = self.models[article_number].predict(future_scaled)
        
        # Create result DataFrame
        result = pd.DataFrame({
            'date': future_dates,
            'predicted_demand': np.maximum(0, predictions.round())  # Ensure non-negative predictions
        })
        
        return result
    
    def get_inventory_status(self, article_number):
        """Get current inventory status for a specific article"""
        if not hasattr(self, 'processed_data') or 'inventory_df' not in self.processed_data:
            return None
            
        inventory_df = self.processed_data['inventory_df']
        
        # Check if inventory_df has articleNumber column
        if 'articleNumber' not in inventory_df.columns:
            # Return sample data for demonstration
            return {
                'article_number': article_number,
                'current_stock': np.random.randint(5, 100)  # Random stock between 5 and 100
            }
        
        # Find the article in inventory
        article_inventory = inventory_df[inventory_df['articleNumber'] == article_number]
        
        if len(article_inventory) == 0:
            return None
        
        # Get current stock level
        current_stock = article_inventory['quantity'].sum()
        
        return {
            'article_number': article_number,
            'current_stock': current_stock
        }
    
    def generate_reorder_recommendations(self, article_number, lead_time=7, safety_stock_days=3):
        """Generate reorder recommendations for a specific article"""
        # Get current inventory status
        inventory_status = self.get_inventory_status(article_number)
        
        if inventory_status is None:
            return None
        
        # Predict future demand
        future_demand = self.predict_future_demand(article_number, days=30)
        
        if future_demand is None:
            return None
        
        # Calculate total demand during lead time
        lead_time_demand = future_demand.head(lead_time)['predicted_demand'].sum()
        
        # Calculate safety stock
        safety_stock = future_demand.head(safety_stock_days)['predicted_demand'].sum()
        
        # Calculate reorder point
        reorder_point = lead_time_demand + safety_stock
        
        # Calculate economic order quantity (simplified)
        monthly_demand = future_demand['predicted_demand'].sum()
        eoq = np.sqrt(2 * monthly_demand * 10 / 0.2)  # Simplified EOQ formula
        
        # Determine if reorder is needed
        current_stock = inventory_status['current_stock']
        reorder_needed = current_stock <= reorder_point
        
        # Calculate days until stockout
        if current_stock > 0:
            cumulative_demand = future_demand['predicted_demand'].cumsum()
            days_to_stockout = cumulative_demand[cumulative_demand >= current_stock].index[0] if any(cumulative_demand >= current_stock) else 30
        else:
            days_to_stockout = 0
        
        return {
            'article_number': article_number,
            'current_stock': current_stock,
            'lead_time_demand': lead_time_demand,
            'safety_stock': safety_stock,
            'reorder_point': reorder_point,
            'economic_order_quantity': round(eoq),
            'reorder_needed': reorder_needed,
            'days_to_stockout': days_to_stockout,
            'predicted_monthly_demand': monthly_demand,
            'future_demand': future_demand.to_dict(orient='records')
        }
    
    def generate_all_recommendations(self, min_sales=10):
        """Generate recommendations for all articles with sufficient data"""
        if not hasattr(self, 'processed_data'):
            self.load_data()
        
        sales_df = self.processed_data['sales_df']
        inventory_df = self.processed_data['inventory_df']
        
        # Check if inventory_df has articleNumber column
        if 'articleNumber' not in inventory_df.columns:
            print("Warning: No articleNumber in inventory data. Using sample data for demonstration.")
            # Create sample inventory data for demonstration
            article_counts = sales_df['articleNumber'].value_counts()
            articles_to_analyze = article_counts[article_counts >= min_sales].index.tolist()
            
            # Create sample inventory data
            sample_inventory = []
            for article_number in articles_to_analyze[:20]:  # Limit to 20 articles for demo
                sample_inventory.append({
                    'articleNumber': article_number,
                    'quantity': np.random.randint(5, 100)  # Random quantity between 5 and 100
                })
            
            inventory_df = pd.DataFrame(sample_inventory)
            self.processed_data['inventory_df'] = inventory_df
        
        # Get articles with sufficient sales data
        article_counts = sales_df['articleNumber'].value_counts()
        articles_to_analyze = article_counts[article_counts >= min_sales].index.tolist()
        
        # Filter for articles that are in inventory
        inventory_articles = inventory_df['articleNumber'].unique()
        articles_to_analyze = [a for a in articles_to_analyze if a in inventory_articles]
        
        recommendations = []
        for article_number in articles_to_analyze:
            recommendation = self.generate_reorder_recommendations(article_number)
            if recommendation:
                recommendations.append(recommendation)
        
        # Sort by reorder priority (reorder needed and days to stockout)
        recommendations.sort(key=lambda x: (not x['reorder_needed'], x['days_to_stockout']))
        
        return recommendations
    
    def visualize_demand_forecast(self, article_number):
        """Visualize demand forecast for a specific article"""
        # Get historical data
        X, y = self.prepare_features(article_number)
        
        if X is None or y is None:
            print(f"Not enough data to visualize forecast for article {article_number}")
            return None
        
        # Get future predictions
        future_demand = self.predict_future_demand(article_number, days=30)
        
        if future_demand is None:
            return None
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Plot historical demand
        plt.plot(y.index, y.values, label='Historical Demand', color='blue')
        
        # Plot predicted demand
        plt.plot(future_demand['date'], future_demand['predicted_demand'], 
                 label='Predicted Demand', color='red', linestyle='--')
        
        # Add inventory level if available
        inventory_status = self.get_inventory_status(article_number)
        if inventory_status:
            current_stock = inventory_status['current_stock']
            plt.axhline(y=current_stock, color='green', linestyle='-', label=f'Current Stock: {current_stock}')
        
        # Get reorder recommendation
        recommendation = self.generate_reorder_recommendations(article_number)
        if recommendation:
            reorder_point = recommendation['reorder_point']
            plt.axhline(y=reorder_point, color='orange', linestyle='--', label=f'Reorder Point: {reorder_point}')
        
        plt.title(f'Demand Forecast for Article {article_number}')
        plt.xlabel('Date')
        plt.ylabel('Quantity')
        plt.legend()
        plt.grid(True)
        
        # Save the figure
        plt.savefig(f"data/forecast_{article_number}.png")
        plt.close()
        
        return f"data/forecast_{article_number}.png"
    
    def export_recommendations_to_json(self, recommendations=None):
        """Export recommendations to JSON for dashboard integration"""
        if recommendations is None:
            recommendations = self.generate_all_recommendations()
        
        # Convert numpy types to Python native types for JSON serialization
        serializable_recommendations = []
        for rec in recommendations:
            serializable_rec = {}
            for key, value in rec.items():
                if isinstance(value, (np.int64, np.int32, np.int16, np.int8)):
                    serializable_rec[key] = int(value)
                elif isinstance(value, (np.float64, np.float32, np.float16)):
                    serializable_rec[key] = float(value)
                elif isinstance(value, np.bool_):
                    serializable_rec[key] = bool(value)
                elif isinstance(value, pd.Timestamp):
                    serializable_rec[key] = value.strftime('%Y-%m-%d')
                elif isinstance(value, list):
                    # Handle lists of dictionaries (like future_demand)
                    if key == 'future_demand':
                        serializable_rec[key] = []
                        for item in value:
                            serializable_item = {}
                            for k, v in item.items():
                                if isinstance(v, (np.int64, np.int32, np.int16, np.int8)):
                                    serializable_item[k] = int(v)
                                elif isinstance(v, (np.float64, np.float32, np.float16)):
                                    serializable_item[k] = float(v)
                                elif isinstance(v, np.bool_):
                                    serializable_item[k] = bool(v)
                                elif isinstance(v, pd.Timestamp):
                                    serializable_item[k] = v.strftime('%Y-%m-%d')
                                else:
                                    serializable_item[k] = v
                            serializable_rec[key].append(serializable_item)
                    else:
                        serializable_rec[key] = value
                else:
                    serializable_rec[key] = value
            serializable_recommendations.append(serializable_rec)
        
        # Add article names if available
        if hasattr(self, 'processed_data') and 'article_df' in self.processed_data:
            article_df = self.processed_data['article_df']
            article_info = {}
            
            for _, row in article_df.iterrows():
                article_number = row.get('number')
                if article_number:
                    article_info[article_number] = {
                        'name': row.get('text1', '') or row.get('information', '') or f"Article {article_number}",
                        'price': float(row.get('price', 0)),
                        'supplier_number': int(row.get('supplierNumber', 0))
                    }
            
            # Add article info to recommendations
            for rec in serializable_recommendations:
                article_number = rec['article_number']
                if article_number in article_info:
                    rec['article_info'] = article_info[article_number]
        
        # Create data directory if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")
            
        # Export to JSON file
        with open("data/inventory_recommendations.json", "w") as f:
            json.dump(serializable_recommendations, f, indent=2)
        
        return "data/inventory_recommendations.json"

# Main execution
if __name__ == "__main__":
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Create models directory if it doesn't exist
    if not os.path.exists("models"):
        os.makedirs("models")
        
    predictor = InventoryPredictor()
    predictor.load_data()
    
    # Train models for articles with sufficient data
    predictor.train_all_models(min_sales=10)
    
    # Generate recommendations
    recommendations = predictor.generate_all_recommendations()
    
    # Export recommendations to JSON
    json_path = predictor.export_recommendations_to_json(recommendations)
    
    print(f"Generated recommendations for {len(recommendations)} articles")
    print(f"Recommendations saved to {json_path}")
    
    # Visualize forecasts for top 5 articles that need reordering
    for rec in recommendations[:5]:
        article_number = rec['article_number']
        image_path = predictor.visualize_demand_forecast(article_number)
        print(f"Forecast visualization for article {article_number} saved to {image_path}")
