import os
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from inventory_prediction import InventoryPredictor

app = FastAPI(title="Inventory Prediction API")

# Add CORS middleware to allow requests from the Vercel v0 dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the inventory predictor
predictor = InventoryPredictor()

# Load data and train models on startup
@app.on_event("startup")
async def startup_event():
    try:
        # Load data
        predictor.load_data()
        
        # Train models for articles with sufficient data
        predictor.train_all_models(min_sales=10)
        
        # Generate recommendations if they don't exist
        if not os.path.exists("data/inventory_recommendations.json"):
            recommendations = predictor.generate_all_recommendations()
            predictor.export_recommendations_to_json(recommendations)
    except Exception as e:
        print(f"Error during startup: {e}")

# Define API endpoints
@app.get("/api/inventory/recommendations", response_model=List[Dict[str, Any]])
async def get_inventory_recommendations():
    """Get inventory recommendations for all articles"""
    try:
        # Check if recommendations file exists
        if os.path.exists("data/inventory_recommendations.json"):
            with open("data/inventory_recommendations.json", "r") as f:
                recommendations = json.load(f)
            return recommendations
        else:
            # Generate recommendations on the fly
            recommendations = predictor.generate_all_recommendations()
            predictor.export_recommendations_to_json(recommendations)
            return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/api/inventory/forecast/{article_number}", response_model=Dict[str, Any])
async def get_article_forecast(article_number: str):
    """Get demand forecast for a specific article"""
    try:
        # Check if article exists
        forecast = predictor.get_demand_forecast(float(article_number))
        if not forecast:
            raise HTTPException(status_code=404, detail=f"Article {article_number} not found or has insufficient data")
        
        # Generate visualization
        image_path = predictor.visualize_demand_forecast(float(article_number))
        
        # Return forecast data with image path
        return {
            "article_number": article_number,
            "forecast": forecast,
            "image_path": f"static/{os.path.basename(image_path)}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")

@app.get("/api/inventory/status", response_model=Dict[str, Any])
async def get_inventory_status():
    """Get overall inventory status metrics"""
    try:
        # Load recommendations
        if os.path.exists("data/inventory_recommendations.json"):
            with open("data/inventory_recommendations.json", "r") as f:
                recommendations = json.load(f)
        else:
            recommendations = predictor.generate_all_recommendations()
        
        # Calculate metrics
        total_items = len(recommendations)
        items_to_reorder = sum(1 for rec in recommendations if rec.get("reorder_needed", False))
        stockout_risk = sum(1 for rec in recommendations if rec.get("days_to_stockout", 30) < 7)
        
        # Calculate inventory value
        total_inventory_value = 0
        for rec in recommendations:
            current_stock = rec.get("current_stock", 0)
            price = rec.get("article_info", {}).get("price", 0)
            total_inventory_value += current_stock * price
        
        return {
            "total_items": total_items,
            "items_to_reorder": items_to_reorder,
            "stockout_risk": stockout_risk,
            "total_inventory_value": total_inventory_value,
            "reorder_percentage": (items_to_reorder / total_items) * 100 if total_items > 0 else 0,
            "stockout_risk_percentage": (stockout_risk / total_items) * 100 if total_items > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating inventory status: {str(e)}")

# Run the server
if __name__ == "__main__":
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
