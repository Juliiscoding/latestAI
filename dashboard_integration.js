// Inventory Management Dashboard Integration for Vercel v0
// This file provides the integration between the inventory prediction API and the Vercel v0 dashboard

// API endpoint configuration
const API_BASE_URL = 'http://localhost:8000/api';
const STATIC_URL = 'http://localhost:8080'; // URL for static files

// Fetch inventory status data
async function fetchInventoryStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/inventory/status`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching inventory status:', error);
        return null;
    }
}

// Fetch inventory recommendations
async function fetchInventoryRecommendations() {
    try {
        const response = await fetch(`${API_BASE_URL}/inventory/recommendations`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        return [];
    }
}

// Fetch forecast for a specific article
async function fetchArticleForecast(articleNumber) {
    try {
        const response = await fetch(`${API_BASE_URL}/inventory/forecast/${articleNumber}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching forecast for article ${articleNumber}:`, error);
        return null;
    }
}

// Render inventory status dashboard
function renderInventoryStatusDashboard(containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container with ID ${containerId} not found`);
        return;
    }
    
    // Create dashboard structure
    container.innerHTML = `
        <div class="inventory-dashboard">
            <div class="dashboard-header">
                <h1>Predictive Inventory Management</h1>
                <p>AI-powered insights to optimize your inventory levels</p>
            </div>
            
            <div class="metrics-container">
                <div class="metric-card" id="total-items">
                    <h3>Total Items</h3>
                    <div class="metric-value">Loading...</div>
                </div>
                <div class="metric-card" id="items-to-reorder">
                    <h3>Items to Reorder</h3>
                    <div class="metric-value">Loading...</div>
                    <div class="metric-percentage"></div>
                </div>
                <div class="metric-card" id="stockout-risk">
                    <h3>Stockout Risk</h3>
                    <div class="metric-value">Loading...</div>
                    <div class="metric-percentage"></div>
                </div>
                <div class="metric-card" id="inventory-value">
                    <h3>Inventory Value</h3>
                    <div class="metric-value">Loading...</div>
                </div>
            </div>
            
            <div class="recommendations-container">
                <h2>Reorder Recommendations</h2>
                <div class="recommendations-table-container">
                    <table class="recommendations-table">
                        <thead>
                            <tr>
                                <th>Article</th>
                                <th>Current Stock</th>
                                <th>Days to Stockout</th>
                                <th>Reorder Point</th>
                                <th>Recommended Order</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="recommendations-table-body">
                            <tr>
                                <td colspan="6">Loading recommendations...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="forecast-container" id="forecast-container" style="display: none;">
                <h2>Demand Forecast</h2>
                <div id="forecast-content"></div>
            </div>
        </div>
    `;
    
    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        .inventory-dashboard {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .dashboard-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .dashboard-header h1 {
            font-size: 28px;
            margin-bottom: 5px;
            color: #1a73e8;
        }
        
        .dashboard-header p {
            font-size: 16px;
            color: #666;
        }
        
        .metrics-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            text-align: center;
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .metric-card h3 {
            font-size: 16px;
            margin-top: 0;
            margin-bottom: 15px;
            color: #666;
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #1a73e8;
        }
        
        .metric-percentage {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        
        .recommendations-container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            margin-bottom: 30px;
        }
        
        .recommendations-container h2 {
            font-size: 20px;
            margin-top: 0;
            margin-bottom: 20px;
            color: #333;
        }
        
        .recommendations-table-container {
            overflow-x: auto;
        }
        
        .recommendations-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .recommendations-table th, 
        .recommendations-table td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        .recommendations-table th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #666;
        }
        
        .recommendations-table tbody tr:hover {
            background-color: #f8f9fa;
        }
        
        .forecast-container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .forecast-container h2 {
            font-size: 20px;
            margin-top: 0;
            margin-bottom: 20px;
            color: #333;
        }
        
        .btn {
            display: inline-block;
            padding: 8px 12px;
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s;
        }
        
        .btn:hover {
            background-color: #0d62d1;
        }
        
        .stockout-warning {
            color: #d93025;
        }
        
        .stockout-caution {
            color: #f29900;
        }
        
        .stockout-safe {
            color: #188038;
        }
    `;
    document.head.appendChild(style);
    
    // Load data
    loadDashboardData();
}

// Load dashboard data
async function loadDashboardData() {
    // Fetch inventory status
    const status = await fetchInventoryStatus();
    if (status) {
        // Update metrics
        document.getElementById('total-items').querySelector('.metric-value').textContent = status.total_items;
        
        const reorderElement = document.getElementById('items-to-reorder');
        reorderElement.querySelector('.metric-value').textContent = status.items_to_reorder;
        reorderElement.querySelector('.metric-percentage').textContent = `${status.reorder_percentage.toFixed(1)}% of inventory`;
        
        const stockoutElement = document.getElementById('stockout-risk');
        stockoutElement.querySelector('.metric-value').textContent = status.stockout_risk;
        stockoutElement.querySelector('.metric-percentage').textContent = `${status.stockout_risk_percentage.toFixed(1)}% of inventory`;
        
        const inventoryValueElement = document.getElementById('inventory-value');
        inventoryValueElement.querySelector('.metric-value').textContent = `$${status.total_inventory_value.toFixed(2)}`;
    }
    
    // Fetch recommendations
    const recommendations = await fetchInventoryRecommendations();
    const tableBody = document.getElementById('recommendations-table-body');
    
    if (recommendations && recommendations.length > 0) {
        // Sort recommendations by priority (reorder needed and days to stockout)
        recommendations.sort((a, b) => {
            if (a.reorder_needed !== b.reorder_needed) {
                return a.reorder_needed ? -1 : 1;
            }
            return a.days_to_stockout - b.days_to_stockout;
        });
        
        // Generate table rows
        tableBody.innerHTML = recommendations.map(item => {
            const articleName = item.article_info ? item.article_info.name : `Article ${item.article_number}`;
            const daysToStockout = item.days_to_stockout;
            
            let stockoutClass = 'stockout-safe';
            if (daysToStockout <= 3) {
                stockoutClass = 'stockout-warning';
            } else if (daysToStockout <= 7) {
                stockoutClass = 'stockout-caution';
            }
            
            return `
                <tr>
                    <td>${articleName}</td>
                    <td>${item.current_stock}</td>
                    <td class="${stockoutClass}">${daysToStockout} days</td>
                    <td>${item.reorder_point}</td>
                    <td>${item.economic_order_quantity}</td>
                    <td>
                        <button class="btn" onclick="showForecast('${item.article_number}')">View Forecast</button>
                    </td>
                </tr>
            `;
        }).join('');
    } else {
        tableBody.innerHTML = '<tr><td colspan="6">No recommendations available</td></tr>';
    }
}

// Show forecast for a specific article
async function showForecast(articleNumber) {
    const forecastContainer = document.getElementById('forecast-container');
    const forecastContent = document.getElementById('forecast-content');
    
    // Show loading
    forecastContainer.style.display = 'block';
    forecastContent.innerHTML = '<p>Loading forecast data...</p>';
    
    // Fetch forecast data
    const forecast = await fetchArticleForecast(articleNumber);
    
    if (forecast) {
        // Display forecast
        forecastContent.innerHTML = `
            <h3>Demand Forecast for Article ${forecast.article_number}</h3>
            <div class="forecast-details">
                <p><strong>Predicted Monthly Demand:</strong> ${forecast.forecast.monthly_demand.toFixed(2)} units</p>
                <p><strong>Lead Time Demand:</strong> ${forecast.forecast.lead_time_demand.toFixed(2)} units</p>
                <p><strong>Safety Stock:</strong> ${forecast.forecast.safety_stock.toFixed(2)} units</p>
                <p><strong>Reorder Point:</strong> ${forecast.forecast.reorder_point.toFixed(2)} units</p>
            </div>
            <div class="forecast-image">
                <img src="${STATIC_URL}/${forecast.image_path}" alt="Demand Forecast Chart" style="max-width: 100%;">
            </div>
        `;
    } else {
        forecastContent.innerHTML = '<p>Unable to load forecast data for this article.</p>';
    }
    
    // Scroll to forecast
    forecastContainer.scrollIntoView({ behavior: 'smooth' });
}

// Make functions available globally
window.showForecast = showForecast;

// Export functions for use in Vercel v0
export {
    renderInventoryStatusDashboard,
    fetchInventoryStatus,
    fetchInventoryRecommendations,
    fetchArticleForecast
};
