# Mercurios.ai Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      Mercurios.ai Architecture                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                       ┌─────────────────────────────────────────────┐
                       │                                             │
                       ▼                                             ▼
┌─────────────────────────────────────┐           ┌─────────────────────────────────────┐
│         Data Ingestion Layer        │           │          Data Storage Layer         │
│                                     │           │                                     │
│  ┌─────────────┐    ┌─────────────┐ │           │  ┌─────────────┐    ┌─────────────┐ │
│  │  ProHandel  │    │   Other     │ │           │  │             │    │             │ │
│  │  Lambda     │───▶│   POS       │ │           │  │  Snowflake  │    │    S3       │ │
│  │  Connector  │    │  Connectors │ │──────────▶│  │   Data      │───▶│   Data      │ │
│  └─────────────┘    └─────────────┘ │           │  │  Warehouse  │    │    Lake     │ │
│                                     │           │  │             │    │             │ │
│  ┌─────────────┐    ┌─────────────┐ │           │  └─────────────┘    └─────────────┘ │
│  │  Fivetran   │    │   Tenant    │ │           │                                     │
│  │  Service    │◀──▶│   Manager   │ │           │  ┌─────────────┐    ┌─────────────┐ │
│  └─────────────┘    └─────────────┘ │           │  │             │    │             │ │
│                                     │           │  │   Vector    │    │   Redis     │ │
└─────────────────────────────────────┘           │  │  Database   │    │   Cache     │ │
                       │                          │  │             │    │             │ │
                       │                          │  └─────────────┘    └─────────────┘ │
                       │                          └─────────────────────────────────────┘
                       │                                             │
                       ▼                                             │
┌─────────────────────────────────────┐                              │
│      Data Transformation Layer      │                              │
│                                     │                              │
│  ┌─────────────┐    ┌─────────────┐ │                              │
│  │             │    │             │ │                              │
│  │     dbt     │───▶│  Scheduled  │ │                              │
│  │             │    │    Jobs     │ │                              │
│  └─────────────┘    └─────────────┘ │                              │
│                                     │                              │
│  ┌─────────────┐    ┌─────────────┐ │                              │
│  │  Data       │    │  Quality    │ │                              │
│  │  Validation │───▶│  Monitoring │ │                              │
│  └─────────────┘    └─────────────┘ │                              │
└─────────────────────────────────────┘                              │
                       │                                             │
                       ▼                                             ▼
┌─────────────────────────────────────┐           ┌─────────────────────────────────────┐
│         API & Service Layer         │           │       ML & Analytics Layer          │
│                                     │           │                                     │
│  ┌─────────────┐    ┌─────────────┐ │           │  ┌─────────────┐    ┌─────────────┐ │
│  │             │    │             │ │           │  │             │    │             │ │
│  │  GraphQL    │───▶│   Lambda    │ │◀─────────▶│  │ Forecasting │    │    LLM      │ │
│  │    API      │    │  Functions  │ │           │  │   Models    │    │  Interface  │ │
│  └─────────────┘    └─────────────┘ │           │  │             │    │             │ │
│                                     │           │  └─────────────┘    └─────────────┘ │
│  ┌─────────────┐    ┌─────────────┐ │           │                                     │
│  │             │    │             │ │           │  ┌─────────────┐    ┌─────────────┐ │
│  │    Auth     │───▶│   Tenant    │ │           │  │  Customer   │    │ Inventory   │ │
│  │   Service   │    │   Routing   │ │           │  │ Segmentation│    │Optimization │ │
│  └─────────────┘    └─────────────┘ │           │  │             │    │             │ │
└─────────────────────────────────────┘           │  └─────────────┘    └─────────────┘ │
                       │                          └─────────────────────────────────────┘
                       ▼                                             
┌─────────────────────────────────────┐           
│        Presentation Layer           │           
│                                     │           
│  ┌─────────────┐    ┌─────────────┐ │           
│  │             │    │             │ │           
│  │   Next.js   │───▶│   Vercel    │ │           
│  │  Frontend   │    │  Deployment │ │           
│  └─────────────┘    └─────────────┘ │           
│                                     │           
│  ┌─────────────┐    ┌─────────────┐ │           
│  │  Multi-     │    │   Role-     │ │           
│  │  Tenant UI  │───▶│   Based     │ │           
│  │             │    │   Access    │ │           
│  └─────────────┘    └─────────────┘ │           
└─────────────────────────────────────┘           
```

## Architecture Components

### 1. Data Ingestion Layer
- **ProHandel Lambda Connector**: Custom AWS Lambda function to extract data from ProHandel API
- **Other POS Connectors**: Extensible framework for connecting to other POS systems
- **Fivetran Service**: Manages data synchronization and scheduling
- **Tenant Manager**: Handles tenant registration, configuration, and resource provisioning

### 2. Data Storage Layer
- **Snowflake Data Warehouse**: Primary storage for structured data with multi-tenant isolation
- **S3 Data Lake**: Long-term storage for raw data and large datasets
- **Vector Database**: Stores embeddings for LLM context and semantic search
- **Redis Cache**: High-performance caching for API responses and frequent queries

### 3. Data Transformation Layer
- **dbt**: Defines and manages data transformations as code
- **Scheduled Jobs**: Runs transformations on a regular schedule
- **Data Validation**: Ensures data quality and consistency
- **Quality Monitoring**: Tracks data quality metrics over time

### 4. API & Service Layer
- **GraphQL API**: Flexible API for frontend data access
- **Lambda Functions**: Serverless compute for API backend
- **Auth Service**: Handles authentication and authorization
- **Tenant Routing**: Routes requests to tenant-specific resources

### 5. ML & Analytics Layer
- **Forecasting Models**: Predicts inventory needs and sales trends
- **LLM Interface**: Provides natural language interface to data
- **Customer Segmentation**: Identifies customer groups and behaviors
- **Inventory Optimization**: Recommends optimal inventory levels

### 6. Presentation Layer
- **Next.js Frontend**: Server-side rendered React application
- **Vercel Deployment**: Edge deployment for global low-latency
- **Multi-Tenant UI**: Customizable interface for each tenant
- **Role-Based Access**: Different views for different user roles

## Data Flow

1. Data is extracted from ProHandel API (or other POS systems) via Lambda connectors
2. Fivetran loads the data into Snowflake with tenant isolation
3. Raw data is archived in S3 Data Lake for long-term storage
4. dbt transforms raw data into analytics-ready models
5. GraphQL API provides access to transformed data for the frontend
6. ML models process the data to generate insights and forecasts
7. Next.js frontend displays dashboards and insights to users
8. LLM interface allows users to query their data using natural language
