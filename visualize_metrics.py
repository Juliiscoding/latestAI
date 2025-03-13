#!/usr/bin/env python
"""
Visualization script for the ETL metrics.
This script creates visualizations for supplier metrics.
"""
import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

from etl.transformers.supplier_transformer import SupplierTransformer
from etl.utils.logger import logger

def create_sample_data():
    """Create sample data for visualization."""
    # Sample orders data for multiple suppliers
    orders = []
    suppliers = []
    
    # Create data for 5 suppliers with different characteristics
    supplier_data = [
        {
            "id": "SUP001",
            "name": "Fast & Reliable Inc.",
            "orders_per_month": 12,
            "lead_time": 2,
            "on_time_rate": 0.98,
            "avg_order_size": 1200
        },
        {
            "id": "SUP002",
            "name": "Budget Supplies Ltd.",
            "orders_per_month": 4,
            "lead_time": 5,
            "on_time_rate": 0.85,
            "avg_order_size": 3500
        },
        {
            "id": "SUP003",
            "name": "Premium Products Co.",
            "orders_per_month": 2,
            "lead_time": 3,
            "on_time_rate": 0.95,
            "avg_order_size": 8000
        },
        {
            "id": "SUP004",
            "name": "Global Imports",
            "orders_per_month": 1,
            "lead_time": 15,
            "on_time_rate": 0.75,
            "avg_order_size": 12000
        },
        {
            "id": "SUP005",
            "name": "Local Distributors",
            "orders_per_month": 8,
            "lead_time": 1,
            "on_time_rate": 0.99,
            "avg_order_size": 900
        }
    ]
    
    # Create supplier records
    for supplier in supplier_data:
        suppliers.append({
            "supplier_id": supplier["id"],
            "name": supplier["name"],
            "contact_name": f"Contact {supplier['id']}",
            "email": f"contact@{supplier['id'].lower()}.com",
            "phone": "+1-555-000-0000",
            "address": "123 Supplier St",
            "city": "Supplier City",
            "state": "SC",
            "postal_code": "12345",
            "country": "USA",
            "created_at": (datetime.now() - timedelta(days=365)).isoformat(),
            "updated_at": datetime.now().isoformat()
        })
    
    # Create orders for each supplier
    base_date = datetime.now() - timedelta(days=90)
    
    for supplier in supplier_data:
        # Calculate interval between orders based on orders per month
        days_between_orders = 30 / supplier["orders_per_month"]
        
        # Create orders
        num_orders = int(90 / days_between_orders)
        for i in range(num_orders):
            order_date = base_date + timedelta(days=i*days_between_orders)
            expected_delivery_date = order_date + timedelta(days=supplier["lead_time"])
            
            # Determine if this delivery will be on time (based on on-time rate)
            is_on_time = np.random.random() < supplier["on_time_rate"]
            if is_on_time:
                actual_delivery_date = expected_delivery_date
            else:
                delay_days = np.random.randint(1, 5)
                actual_delivery_date = expected_delivery_date + timedelta(days=delay_days)
            
            # Create order
            order = {
                "order_id": f"{supplier['id']}_ORD{i+1:03d}",
                "supplier_id": supplier["id"],
                "order_date": order_date.isoformat(),
                "expected_delivery_date": expected_delivery_date.isoformat(),
                "actual_delivery_date": actual_delivery_date.isoformat(),
                "status": "completed",
                "items": [
                    {
                        "product_id": f"PROD{j+1:03d}",
                        "quantity": np.random.randint(5, 20),
                        "unit_price": 20 + np.random.randint(0, 100),
                        "total_price": 0  # Will be calculated below
                    }
                    for j in range(np.random.randint(1, 5))  # Random number of items
                ],
                "total_amount": 0  # Will be calculated below
            }
            
            # Calculate totals
            for item in order["items"]:
                item["total_price"] = item["quantity"] * item["unit_price"]
            
            order["total_amount"] = sum(item["total_price"] for item in order["items"])
            
            # Adjust total to match the average order size (approximately)
            scale_factor = supplier["avg_order_size"] / max(order["total_amount"], 1)
            order["total_amount"] = order["total_amount"] * scale_factor
            for item in order["items"]:
                item["total_price"] = item["total_price"] * scale_factor
                item["unit_price"] = item["total_price"] / item["quantity"]
            
            orders.append(order)
    
    return {
        "order": orders,
        "supplier": suppliers
    }

def visualize_supplier_metrics(metrics):
    """Create visualizations for supplier metrics."""
    # Extract data for plotting
    supplier_ids = list(metrics.keys())
    supplier_names = [f"Supplier {sid}" for sid in supplier_ids]  # Simplified names for display
    
    # Prepare data for each metric
    orders_per_month = [metrics[sid]['order_frequency']['orders_per_month'] for sid in supplier_ids]
    lead_times = [metrics[sid].get('lead_time', 0) for sid in supplier_ids]
    on_time_rates = [metrics[sid].get('on_time_delivery_rate', 0) * 100 for sid in supplier_ids]
    reliability_scores = [metrics[sid].get('reliability_score', 0) for sid in supplier_ids]
    avg_order_amounts = [metrics[sid]['average_order_size']['average_amount'] for sid in supplier_ids]
    
    # Create figure with subplots
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Supplier Metrics Analysis', fontsize=16)
    
    # Plot 1: Orders per Month
    axs[0, 0].bar(supplier_names, orders_per_month, color='skyblue')
    axs[0, 0].set_title('Orders per Month')
    axs[0, 0].set_ylabel('Orders')
    axs[0, 0].tick_params(axis='x', rotation=45)
    
    # Plot 2: Lead Time vs On-Time Delivery Rate
    ax2 = axs[0, 1]
    ax2.bar(supplier_names, lead_times, color='lightgreen', label='Lead Time (days)')
    ax2.set_title('Lead Time vs On-Time Delivery Rate')
    ax2.set_ylabel('Lead Time (days)')
    ax2.tick_params(axis='x', rotation=45)
    
    # Add On-Time Delivery Rate as a line on secondary y-axis
    ax2_twin = ax2.twinx()
    ax2_twin.plot(supplier_names, on_time_rates, 'ro-', label='On-Time Rate (%)')
    ax2_twin.set_ylabel('On-Time Delivery Rate (%)')
    ax2_twin.set_ylim([0, 100])
    
    # Add legend
    lines, labels = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right')
    
    # Plot 3: Average Order Amount
    axs[1, 0].bar(supplier_names, avg_order_amounts, color='salmon')
    axs[1, 0].set_title('Average Order Amount')
    axs[1, 0].set_ylabel('Amount ($)')
    axs[1, 0].tick_params(axis='x', rotation=45)
    
    # Format y-axis as currency
    axs[1, 0].yaxis.set_major_formatter('${x:,.0f}')
    
    # Plot 4: Reliability Score
    axs[1, 1].bar(supplier_names, reliability_scores, color='mediumpurple')
    axs[1, 1].set_title('Reliability Score (0-10)')
    axs[1, 1].set_ylabel('Score')
    axs[1, 1].set_ylim([0, 10])
    axs[1, 1].tick_params(axis='x', rotation=45)
    
    # Add horizontal line at score of 7 (good reliability threshold)
    axs[1, 1].axhline(y=7, color='green', linestyle='--', alpha=0.7)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    
    # Save the figure
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'supplier_metrics.png')
    plt.savefig(output_path)
    
    logger.info(f"Visualization saved to {output_path}")
    
    # Show the plot
    plt.show()

def main():
    """Main function to run the visualization."""
    logger.info("Starting supplier metrics visualization...")
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Create an instance of the SupplierTransformer
    transformer = SupplierTransformer(orders_data=sample_data["order"])
    
    # Generate supplier metrics
    transformer.transform_batch(sample_data["supplier"])
    metrics = transformer.get_supplier_metrics()
    
    # Visualize the metrics
    visualize_supplier_metrics(metrics)
    
    logger.info("Visualization completed successfully!")
    return 0

if __name__ == "__main__":
    main()
