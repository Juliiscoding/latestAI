# Predictive Inventory Management System

This project implements an AI-enhanced Predictive Inventory Management system using data from the ProHandel API. The system analyzes historical sales data to forecast future demand, generate reorder recommendations, and help reduce stockouts and overstock situations.

## Features

- **Sales Data Analysis**: Analyzes historical sales patterns to identify trends and seasonality
- **Demand Forecasting**: Uses machine learning to predict future product demand
- **Inventory Optimization**: Calculates optimal reorder points and quantities
- **Stockout Prevention**: Identifies products at risk of stockout
- **Dashboard Integration**: Visualizes inventory insights in a user-friendly dashboard

## Components

1. **Data Collection**: Scripts to fetch data from the ProHandel API
2. **ETL Pipeline**: Extract, Transform, Load pipeline for data processing
3. **Fivetran Integration**: AWS Lambda connector for integrating with Fivetran
4. **Inventory Prediction Engine**: ML models to forecast demand and generate recommendations
5. **API Server**: FastAPI server to expose predictions and recommendations
6. **Dashboard**: Web-based dashboard for visualizing inventory insights

## ETL Pipeline Architecture

The ETL (Extract, Transform, Load) pipeline is the backbone of our data processing system:

### 1. Data Extraction Layer
- **ProHandelConnector**: Handles data extraction from the ProHandel API
  - Supports incremental loading to process only new/updated data
  - Implements automatic token refreshing
  - Includes robust error handling and retry mechanisms
  - Manages rate limiting and pagination

### 2. Data Transformation Layer
- **BaseTransformer**: Provides common transformation methods
  - Timestamp standardization
  - Currency conversion with real-time exchange rates
  - Product ID normalization
  
- **Entity-Specific Transformers**:
  - **ArticleTransformer**: Normalizes product data and calculates product metrics
  - **SalesTransformer**: Processes sales data and calculates sales metrics
  - **InventoryTransformer**: Analyzes inventory levels and calculates inventory metrics
  - **CustomerTransformer**: Processes customer data and calculates customer metrics
  - **SupplierTransformer**: Analyzes supplier order patterns and calculates reliability metrics

### 3. Data Loading Layer
- **DatabaseLoader**: Manages loading data into PostgreSQL
  - Supports upserts and transactions
  - Implements error handling and rollback
  - Optimizes bulk loading operations

### 4. Fivetran Integration
- **AWS Lambda Connector**: Custom connector for Fivetran integration
  - Handles Fivetran's test, schema, and sync operations
  - Integrates with existing ProHandel connector for data extraction
  - Implements incremental loading based on timestamps
  - Includes data validation using schema validators
  - Provides data enhancement and aggregation capabilities

### 5. Data Warehouse & Data Marts
- **Star Schema**: Optimized for inventory analytics
  - Dimension tables: DimDate, DimProduct, DimLocation, DimCustomer, DimSupplier
  - Fact tables: FactSales, FactInventory, FactOrders
  - Aggregated fact tables: FactSalesDaily, FactSalesWeekly, FactSalesMonthly
  
- **Data Marts**: Specialized views for specific analytics needs
  - Inventory Analytics Mart
  - Supplier Analytics Mart
  - Sales Analytics Mart

### 6. Orchestration
- **ETLOrchestrator**: Coordinates the entire ETL process
  - Manages extraction, validation, transformation, and loading
  - Handles dependencies between different data entities
  - Implements logging and error reporting

## ProHandel API Integration

The system integrates with the ProHandel API to fetch retail data for inventory management and prediction. The integration includes:

### Authentication

- **Token-based Authentication**: Uses API key and secret to obtain access tokens
- **Automatic Token Refresh**: Handles token expiration and refresh
- **Server-specific URLs**: Dynamically adapts to the server URL returned during authentication

### API Endpoints

The following ProHandel API endpoints are integrated:

| Endpoint | Description | Key Fields |
|----------|-------------|------------|
| `/article` | Product information | id, number, price, purchasePrice, lastChange |
| `/customer` | Customer data | id, number, name1, city, lastChange |
| `/order` | Order information | id, number, created, status, positions |
| `/sale` | Sales transactions | id, articleNumber, date, quantity, salePrice |
| `/inventory` | Inventory levels | id, branchNumber, date, stocktakingDate, lastChange |
| `/branch` | Store locations | id, number, name1, city, lastChange |
| `/supplier` | Supplier information | id, number, name1, lastChange |
| `/category` | Product categories | id, number, name, lastChange |
| `/staff` | Staff information | id, number, firstName, lastName, lastChange |
| `/shop` | Shop information | id, number, name, lastChange |
| `/articlesize` | Article size details | id, articleNumber, size, ean, stockQuantity |
| `/country` | Country information | id, number, countryName, isoAlpha2 |
| `/currency` | Currency information | id, number, isoAlpha3, course |
| `/invoice` | Invoice data | id, number, date, amount, status |
| `/payment` | Payment information | id, number, date, amount, status |
| `/season` | Season information | id, name, validFrom, validUntil |
| `/size` | Size information | id, name, position |
| `/voucher` | Voucher information | id, number, value, status |

### Data Validation

- **JSON Schema Validation**: Each entity type has a corresponding JSON schema
- **Automatic Schema Generation**: Schemas can be automatically generated from API responses
- **Data Type Validation**: Ensures data consistency and integrity

### Testing Tools

Several testing tools are provided to validate the API integration:

- **test_auth_simple.py**: Tests authentication with the ProHandel API
- **test_endpoints.py**: Tests all API endpoints and validates response schemas
- **explore_api.py**: Discovers available API endpoints and their field structures
- **test_lambda.py**: Tests the AWS Lambda function for Fivetran integration

### AWS Lambda Integration

The system includes an AWS Lambda function for integrating with Fivetran:

- **Lambda Function**: Handles Fivetran's test, schema, and sync operations
- **Incremental Loading**: Implements incremental loading based on timestamps
- **Data Enhancement**: Adds calculated fields and aggregations
- **Deployment Scripts**: Includes scripts for deploying to AWS

### Environment Configuration

The integration is configured using environment variables:

```
PROHANDEL_API_KEY=your_api_key
PROHANDEL_API_SECRET=your_api_secret
PROHANDEL_AUTH_URL=https://auth.prohandel.cloud/api/v4
PROHANDEL_API_URL=https://api.prohandel.de/api/v2
TOKEN_EXPIRY_BUFFER=300
```

### Running the API Tests

To test the API integration:

```bash
# Test authentication
python test_auth_simple.py

# Test all endpoints
python test_endpoints.py

# Explore available endpoints
python explore_api.py

# Test Lambda function
python test_lambda.py
```

## Fivetran Lambda Connector

The AWS Lambda connector for Fivetran enables seamless integration between the ProHandel API and your data warehouse. This connector:

1. **Extracts Data**: Fetches data from the ProHandel API including articles, customers, orders, sales, inventory, branches, suppliers, categories, and staff.

2. **Transforms Data**: Enhances the data with calculated fields and aggregations:
   - Adds profit margins, price tiers, and delivery time calculations
   - Creates full addresses from component fields
   - Adds age calculations for orders and sales
   - Categorizes inventory stock levels

3. **Aggregates Data**: Provides pre-aggregated views:
   - Daily sales aggregations (counts, quantities, amounts)
   - Article sales aggregations (sales by product)
   - Warehouse inventory aggregations (stock by location)

4. **Incremental Loading**: Only processes new or updated data since the last extraction to minimize API calls and processing time.

5. **Schema Validation**: Validates all data against predefined schemas to ensure data integrity.

### Deployment

For detailed deployment instructions, see the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) file.

### Testing

The connector includes comprehensive testing:
- Unit tests for individual components
- Integration tests for API connectivity
- End-to-end tests for the complete data flow

To run the tests:
```bash
cd lambda_connector
python test_end_to_end.py
```

### Configuration

The connector is configured using environment variables:
- `PROHANDEL_AUTH_URL`: Authentication URL for the ProHandel API
- `PROHANDEL_API_URL`: Base URL for the ProHandel API
- `PROHANDEL_USERNAME`: ProHandel API username
- `PROHANDEL_PASSWORD`: ProHandel API password

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for dashboard integration)
- ProHandel API credentials

### Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Fetch data from the ProHandel API:

```bash
python fetch_working_data.py
```

3. Start the prediction API server:

```bash
python api_server.py
```

4. Open the Earth dashboard in your browser:

```bash
# You can serve the HTML file using a simple HTTP server
python -m http.server 8080
# Then open http://localhost:8080/earth_dashboard.html
```

### Integration with Vercel v0 Dashboard

To integrate with your Vercel v0 dashboard:

1. Copy the `dashboard_integration.js` file to your dashboard project
2. Include the script in your dashboard HTML
3. Add the Earth dashboard components to your Vercel v0 dashboard

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  ProHandel API  │───▶│  Data Fetching  │───▶│  Data Storage   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └────────┬────────┘
                                                      │
                                                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Dashboard     │◀───│   API Server    │◀───│  ML Prediction  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Machine Learning Models

The system uses Random Forest Regression models to predict future demand based on:

- Historical sales patterns
- Seasonality factors
- Day of week effects
- Monthly and quarterly trends

Models are trained for each product with sufficient historical data and are automatically retrained as new data becomes available.

## API Endpoints

- `/recommendations`: Get reorder recommendations
- `/recommendation/{article_number}`: Get detailed recommendation for a specific article
- `/forecast/{article_number}`: Get demand forecast visualization
- `/inventory/summary`: Get inventory summary statistics

## Dashboard Features

The Earth dashboard provides:

- Inventory overview with key metrics
- Reorder recommendations table
- Detailed product analysis with demand forecasts
- Stockout risk indicators

## Next Steps and Future Enhancements

- Implement multi-location inventory optimization
- Add supplier lead time analysis
- Integrate with order management system
- Implement automated reordering workflows
- Add price optimization recommendations

## License

This project is proprietary and confidential.

## Contact

For questions or support, please contact your system administrator.

## Running the System

To run the system, follow these steps:

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the inventory prediction script to generate initial recommendations:

```bash
python inventory_prediction.py
```

3. Start the API server:

```bash
python api_server.py
```

4. Start the dashboard server:

```bash
python serve_dashboard.py
```

5. Open the dashboard in your browser:

```
http://localhost:8080/dashboard.html
```

## API Endpoints

- `/api/inventory/recommendations`: Get inventory recommendations for all articles
- `/api/inventory/forecast/{article_number}`: Get demand forecast for a specific article
- `/api/inventory/status`: Get overall inventory status metrics

## Integration with Vercel v0

To integrate with Vercel v0, import the dashboard integration functions from `dashboard_integration.js`:

```javascript
import { renderInventoryStatusDashboard } from './dashboard_integration.js';

// Initialize dashboard
renderInventoryStatusDashboard('container-id');
```

## Directory Structure

- `inventory_prediction.py`: Core prediction engine
- `api_server.py`: FastAPI server for exposing API endpoints
- `dashboard_integration.js`: JavaScript functions for dashboard integration
- `dashboard.html`: HTML template for the dashboard
- `serve_dashboard.py`: Simple HTTP server for serving the dashboard
- `data/`: Directory for storing data and generated files
- `models/`: Directory for storing trained prediction models

## Requirements

- Python 3.8+
- FastAPI
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Statsmodels
- Uvicorn

## ETL Pipeline

The ETL (Extract, Transform, Load) pipeline is responsible for extracting data from the ProHandel API, transforming it into a structured format, and loading it into a PostgreSQL database for analysis and prediction.

### Features

- **Incremental Loading**: Only extracts new or updated data since the last extraction
- **Data Validation**: Validates incoming data against JSON schemas
- **Automatic Token Refreshing**: Handles API authentication and token refreshing
- **Error Handling**: Robust error handling and retry mechanisms
- **Logging**: Comprehensive logging of the ETL process

### Directory Structure

```
etl/
├── config/         # Configuration settings
├── connectors/     # API connectors for data extraction
├── loaders/        # Database loaders for data loading
├── models/         # Database models
├── schemas/        # JSON schemas for data validation
├── utils/          # Utility functions
├── validators/     # Data validation utilities
└── run_etl.py      # Main ETL script
```

### Running the ETL Pipeline

1. Set up your environment variables in the `.env` file:

```
# API Configuration
PROHANDEL_API_KEY=your_api_key
PROHANDEL_API_SECRET=your_api_secret
PROHANDEL_AUTH_URL=https://linde.prohandel.de/api/v2/auth
PROHANDEL_API_URL=https://linde.prohandel.de/api/v2

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mercurios
DB_USER=postgres
DB_PASSWORD=postgres
```

2. Run the ETL pipeline using the provided script:

```bash
./run_etl.sh
```

3. For more options, you can run the ETL script directly:

```bash
# Set up the database schema
python -m etl.run_etl --setup-db

# Generate JSON schemas from sample data
python -m etl.run_etl --generate-schemas

# Run the ETL pipeline for specific entities
python -m etl.run_etl --entities article customer sale

# Run the ETL pipeline with incremental loading
python -m etl.run_etl --incremental

# Run the ETL pipeline with full loading (not incremental)
python -m etl.run_etl --full

# Show ETL status
python -m etl.run_etl --status
```

### Database Models

The ETL pipeline uses SQLAlchemy to define the following database models:

- `Article`: Products/articles
- `Customer`: Customers
- `Order`: Orders
- `OrderPosition`: Order line items
- `Sale`: Sales transactions
- `Inventory`: Inventory items
- `CustomerCard`: Customer loyalty cards
- `Supplier`: Suppliers
- `Branch`: Branches/stores
- `Category`: Product categories
- `Voucher`: Vouchers
- `Invoice`: Invoices
- `Payment`: Payments
- `ETLMetadata`: Metadata about the ETL process

### ETL Process

1. **Extraction**: Data is extracted from the ProHandel API in batches
2. **Validation**: Data is validated against JSON schemas
3. **Loading**: Data is loaded into the PostgreSQL database
4. **Metadata**: ETL metadata is updated for tracking and incremental loading
