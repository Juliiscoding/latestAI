# Mercurios.ai Architecture Implementation Guide

This document provides a detailed implementation guide for the Mercurios.ai B2B SaaS platform, which delivers AI-enhanced retail analytics and inventory management for German retailers.

## System Architecture Overview

![Architecture Diagram](architecture_diagram.png)

The Mercurios.ai platform follows a modern, cloud-native architecture with the following key components:

1. **Data Extraction Layer**
2. **Data Loading Layer**
3. **Data Warehouse & Lake**
4. **Data Transformation Layer**
5. **API Layer**
6. **AI/ML Layer**
7. **Presentation Layer**

## 1. Data Extraction Layer

### Components
- **ProHandel Connector**: AWS Lambda function that extracts data from ProHandel API
- **Connector Framework**: Extensible framework for adding new POS system connectors
- **Tenant Manager**: System for managing tenant-specific configurations and credentials

### Implementation Details

#### ProHandel Lambda Connector
```python
# Key components in lambda_function.py
def lambda_handler(event, context):
    """Handle Fivetran connector requests."""
    request_type = event.get('type', '')
    
    if request_type == 'test':
        return handle_test_connection(event)
    elif request_type == 'schema':
        return handle_schema_request(event)
    elif request_type == 'sync':
        return handle_sync_request(event)
    else:
        raise ValueError(f"Unknown request type: {request_type}")
```

#### Multi-Tenant Support
- Each tenant gets a dedicated Lambda function with isolated credentials
- Tenant ID is added to all data records for multi-tenant isolation
- AWS Secrets Manager stores API credentials securely

#### Deployment
- Automated deployment using AWS CloudFormation or Terraform
- CI/CD pipeline for testing and deploying connector updates
- Monitoring and alerting for connector health

## 2. Data Loading Layer

### Components
- **Fivetran**: Managed service for reliable data loading
- **Connector Configuration**: Settings for incremental loading and scheduling
- **Monitoring**: Tracking sync status and data volumes

### Implementation Details

#### Fivetran Configuration
- Connection to ProHandel Lambda connector
- Scheduling for regular data syncs (every 6 hours)
- Error handling and notifications

#### Snowflake Destination
- Connection to Snowflake RAW schema
- Service account with appropriate permissions
- Table creation and schema management

## 3. Data Warehouse & Lake

### Components
- **Snowflake**: Primary data warehouse with multi-tenant isolation
- **S3 Data Lake**: Long-term storage for raw data and large datasets
- **Access Control**: Role-based security model

### Implementation Details

#### Snowflake Structure
- **Warehouses**:
  - `MERCURIOS_LOADING_WH`: For ETL processes
  - `MERCURIOS_ANALYTICS_WH`: For reporting and analytics
  - `MERCURIOS_DEV_WH`: For development and testing
  
- **Database**: `MERCURIOS_DATA`
  
- **Schemas**:
  - `RAW`: Landing zone for Fivetran data
  - `STANDARD`: Standardized and cleaned data
  - `ANALYTICS`: Analytics-ready data for reporting
  - `TENANT_CUSTOMIZATIONS`: Customer-specific customizations

#### Row-Level Security
```sql
-- Row access policy for tenant isolation
CREATE OR REPLACE ROW ACCESS POLICY tenant_isolation_policy
    AS (tenant_id VARCHAR) RETURNS BOOLEAN ->
    current_role() IN ('MERCURIOS_ADMIN', 'MERCURIOS_DEVELOPER') 
    OR EXISTS (
        SELECT 1 FROM MERCURIOS_DATA.STANDARD.TENANT_USER_MAPPING
        WHERE TENANT_USER_MAPPING.USER_ROLE = current_role()
        AND TENANT_USER_MAPPING.TENANT_ID = tenant_id
    );

-- Apply to all multi-tenant tables
ALTER TABLE MERCURIOS_DATA.STANDARD.ARTICLES ADD ROW ACCESS POLICY tenant_isolation_policy ON (TENANT_ID);
```

#### S3 Data Lake
- **Buckets**:
  - `mercurios-raw`: Original API responses
  - `mercurios-processed`: Transformed data
  - `mercurios-archive`: Historical data archives
  
- **Data Format**: Parquet files with partitioning by tenant and date
- **Lifecycle Policies**: Automatic archiving of older data

## 4. Data Transformation Layer

### Components
- **dbt**: Data build tool for transformations as code
- **Transformation Models**: SQL models for business logic
- **Testing**: Data quality tests and validation

### Implementation Details

#### dbt Project Structure
```
dbt_prohandel/
├── models/
│   ├── staging/       # Raw to standardized
│   ├── intermediate/  # Business logic
│   └── marts/         # Analytics models
│       ├── inventory/
│       └── sales/
├── tests/             # Data tests
├── macros/            # Reusable SQL
└── dbt_project.yml    # Project configuration
```

#### Key Transformations
- Data cleaning and standardization
- Business metric calculations
- Time-series aggregations
- Customer segmentation

#### Scheduling
- Daily full refresh of models
- Incremental models for large tables
- Dependencies managed by dbt

## 5. API Layer

### Components
- **GraphQL API**: Flexible query interface
- **Redis Cache**: Performance optimization
- **Authentication**: JWT-based security
- **Rate Limiting**: Protection against abuse

### Implementation Details

#### GraphQL Schema
```graphql
type Article {
  id: ID!
  articleNumber: String
  name: String!
  description: String
  category: String
  brand: String
  supplier: String
  purchasePrice: Float
  sellingPrice: Float
  profitMargin: Float
  stockQuantity: Int
  stockStatus: String
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Query {
  articles(filter: ArticleFilter, limit: Int, offset: Int): [Article!]!
  article(id: ID!): Article
  # More queries...
}
```

#### API Implementation
- Node.js with Apollo Server
- Database access through Snowflake Node.js driver
- Redis caching for frequent queries
- Multi-tenant routing middleware

#### Security
- JWT authentication with tenant context
- Role-based access control
- Rate limiting by tenant and endpoint

## 6. AI/ML Layer

### Components
- **Vector Database**: Store embeddings for semantic search
- **Forecasting Models**: Predict inventory needs
- **LLM Integration**: Natural language interface
- **Feature Store**: Reusable ML features

### Implementation Details

#### Forecasting Pipeline
```python
# Example forecasting pipeline
def train_inventory_forecast_model(tenant_id, article_id):
    # Load historical data
    data = load_article_history(tenant_id, article_id)
    
    # Feature engineering
    features = create_time_series_features(data)
    
    # Train model
    model = train_prophet_model(features)
    
    # Save model
    save_model(tenant_id, article_id, model)
    
    return model
```

#### Vector Database Integration
- Store embeddings of product descriptions, categories, and customer data
- Enable semantic search and recommendations
- Support for LLM context retrieval

#### LLM Query Processing
- Parse natural language queries
- Retrieve relevant context from vector database
- Generate SQL or GraphQL queries
- Return formatted responses

## 7. Presentation Layer

### Components
- **Next.js Frontend**: React-based web application
- **Vercel Deployment**: Edge-optimized hosting
- **Theming**: Multi-tenant UI customization
- **Visualizations**: Interactive charts and dashboards

### Implementation Details

#### Application Structure
```
frontend/
├── app/                 # App router
│   ├── dashboard/       # Dashboard pages
│   ├── inventory/       # Inventory management
│   ├── analytics/       # Analytics and reports
│   └── settings/        # User and tenant settings
├── components/          # Reusable components
├── lib/                 # Utility functions
├── styles/              # Global styles
└── middleware.ts        # Auth and tenant routing
```

#### Multi-Tenant UI
- Tenant configuration stored in database
- Dynamic theme loading based on tenant
- Custom branding and layout options

#### Authentication Flow
- JWT-based authentication
- Role-based access control
- Tenant context in all requests

## Implementation Plan

### Phase 1: Foundation (1-2 months)
1. Set up Snowflake data warehouse
2. Enhance Lambda connector for multi-tenant support
3. Configure Fivetran integration
4. Implement basic dbt models
5. Create GraphQL API skeleton

### Phase 2: Advanced Analytics (2-3 months)
1. Expand dbt models for retail analytics
2. Set up S3 data lake
3. Implement Redis caching
4. Develop advanced GraphQL queries
5. Create basic forecasting models

### Phase 3: AI Capabilities (3-4 months)
1. Implement vector database
2. Integrate LLM for natural language queries
3. Enhance forecasting models
4. Develop recommendation system
5. Create AI-powered insights

### Phase 4: Scale & Optimize (2-3 months)
1. Performance optimization
2. Multi-region deployment
3. Advanced monitoring and alerting
4. Disaster recovery planning
5. Security hardening

## Tenant Onboarding Process

1. **Registration**
   - Collect tenant information and POS system details
   - Generate tenant ID and credentials

2. **Infrastructure Provisioning**
   - Deploy tenant-specific Lambda connector
   - Configure Fivetran connection
   - Set up Snowflake access policies

3. **Data Integration**
   - Connect to tenant's POS system
   - Perform initial data load
   - Validate data quality

4. **Configuration**
   - Set up tenant-specific customizations
   - Configure reporting preferences
   - Set user roles and permissions

5. **Training & Handover**
   - Train tenant users on platform
   - Provide documentation
   - Establish support channels

## Monitoring & Operations

### Key Metrics
- Data freshness and completeness
- API performance and error rates
- Model accuracy and prediction quality
- System resource utilization

### Alerting
- Data pipeline failures
- API availability issues
- Unusual prediction patterns
- Security incidents

### Maintenance
- Regular database optimization
- Model retraining schedule
- Security patches and updates
- Performance tuning

## Security Considerations

### Data Protection
- Encryption at rest and in transit
- Tenant isolation at all layers
- Regular security audits
- GDPR compliance measures

### Access Control
- Principle of least privilege
- Regular access reviews
- Audit logging of all actions
- Multi-factor authentication

## Conclusion

This architecture provides a scalable, secure, and flexible foundation for the Mercurios.ai platform. By leveraging modern cloud services and best practices in data engineering and AI/ML, the platform can efficiently onboard new customers with different POS systems while maintaining a standardized data model for analytics and AI enhancements.
