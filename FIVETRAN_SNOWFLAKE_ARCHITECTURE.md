# Fivetran-Snowflake Integration in Mercurios.ai Architecture

This document details how the Fivetran-Snowflake integration fits into the overall Mercurios.ai architecture and provides guidance for scaling this component as we onboard more customers with diverse POS systems.

## Position in Overall Architecture

The Fivetran-Snowflake integration is a critical component in the data flow between steps 1 (Data Extraction) and 2 (Data Loading) of our architecture:

```
ProHandel API → AWS Lambda → Fivetran → Snowflake → dbt Transformations → GraphQL API → Next.js Frontend
```

### Key Functions in the Architecture

1. **Data Loading Bridge**: Connects our extraction layer (Lambda functions) to our data warehouse (Snowflake)
2. **Data Normalization**: Standardizes data from different sources into a consistent format
3. **Multi-tenant Data Management**: Maintains isolation between different customer datasets
4. **Metadata Management**: Tracks data lineage, sync history, and schema changes

## Current Implementation

We have successfully implemented:

1. **Snowflake Destination**:
   - Configured with key-pair authentication for enhanced security
   - Set up proper permissions for the FIVETRAN_USER
   - Established default warehouse for efficient processing

2. **Fivetran Metadata Connector**:
   - Provides visibility into connector status and sync history
   - Enables monitoring and alerting on data pipeline health
   - Tracks usage metrics for capacity planning

## Scaling Strategy for Multi-Tenant, Multi-Source Architecture

### 1. Multi-Tenant Schema Design in Snowflake

For proper tenant isolation, implement one of these patterns:

#### Option A: Schema-per-Tenant
```sql
-- Example structure
CREATE SCHEMA MERCURIOS_DATA.TENANT_123;
CREATE SCHEMA MERCURIOS_DATA.TENANT_456;

-- Tables within tenant schemas
CREATE TABLE MERCURIOS_DATA.TENANT_123.PRODUCTS (...);
CREATE TABLE MERCURIOS_DATA.TENANT_456.PRODUCTS (...);
```

#### Option B: Shared Schema with Tenant ID Column
```sql
-- Example structure
CREATE SCHEMA MERCURIOS_DATA.SHARED;

-- Tables with tenant_id column
CREATE TABLE MERCURIOS_DATA.SHARED.PRODUCTS (
    tenant_id VARCHAR NOT NULL,
    product_id VARCHAR NOT NULL,
    ...
    PRIMARY KEY (tenant_id, product_id)
);

-- Row-level security policy
CREATE OR REPLACE ROW ACCESS POLICY tenant_isolation_policy ON MERCURIOS_DATA.SHARED.PRODUCTS
    FOR SELECT
    USING (tenant_id = current_tenant_id());
```

### 2. Fivetran Connector Strategy for Multiple POS Systems

#### ProHandel Connectors
For each new ProHandel customer:

1. **Lambda Function Template**:
   ```bash
   # Deploy new Lambda function from template
   aws lambda create-function \
     --function-name prohandel-fivetran-connector-tenant-${TENANT_ID} \
     --runtime python3.9 \
     --role arn:aws:iam::689864027744:role/ProHandelFivetranConnectorRole \
     --handler lambda_function.lambda_handler \
     --zip-file fileb://deployment-package.zip \
     --environment "Variables={TENANT_ID=${TENANT_ID},API_BASE_URL=${API_URL}}"
   ```

2. **Fivetran Configuration**:
   - Create new connector pointing to customer-specific Lambda function
   - Configure schema mapping to include tenant ID
   - Set appropriate sync frequency based on customer needs

#### Non-ProHandel Connectors
For customers with different POS systems:

1. **Standard Connectors**: Use Fivetran's pre-built connectors where available
2. **Custom Connectors**: Build custom Lambda functions for unsupported systems
3. **Adapter Layer**: Implement data standardization to map diverse schemas to our canonical model

### 3. Canonical Data Model

Implement a standardized data model across all sources:

```
Core Entities:
- Products
- Inventory
- Customers
- Orders
- Sales
- Suppliers

Each with:
- Standard fields (common across all POS systems)
- Extension fields (source-specific data stored as JSON)
- Tenant identification
```

### 4. Automated Onboarding Process

1. **Customer Registration**:
   - Collect API credentials and endpoint information
   - Determine data scope and historical data requirements
   - Assign tenant ID and create tenant resources

2. **Infrastructure Provisioning**:
   - Deploy tenant-specific Lambda function
   - Configure Fivetran connector
   - Create Snowflake resources (schemas, tables, security policies)

3. **Data Validation**:
   - Test initial data load
   - Verify data quality and completeness
   - Confirm business metrics match customer expectations

## Implementation Roadmap

### Phase 1: Foundation (Current)
- ✅ Set up Snowflake destination with secure authentication
- ✅ Configure Fivetran metadata connector
- ⬜ Design and implement multi-tenant schema structure
- ⬜ Enhance Lambda function with tenant identification

### Phase 2: Scaling (Next)
- ⬜ Create automated deployment process for new tenants
- ⬜ Implement tenant isolation in Snowflake
- ⬜ Build monitoring dashboard for connector health
- ⬜ Develop data quality validation framework

### Phase 3: Multi-Source (Future)
- ⬜ Create connector framework for additional POS systems
- ⬜ Implement canonical data model across all sources
- ⬜ Build adapter layer for source-specific transformations
- ⬜ Develop connector marketplace for third-party integrations

## Next Steps

1. **Implement Tenant Identification**:
   - Update Lambda function to include tenant_id in all data
   - Modify Fivetran schema mapping to preserve tenant_id

2. **Design Multi-Tenant Schema**:
   - Choose between schema-per-tenant or shared schema approach
   - Implement appropriate security policies

3. **Create Deployment Automation**:
   - Build scripts for tenant provisioning
   - Implement CI/CD pipeline for connector deployment

4. **Develop Monitoring**:
   - Create dashboard for connector health
   - Set up alerts for sync failures
   - Implement data quality checks

By following this architecture and implementation plan, Mercurios.ai will be well-positioned to scale efficiently as we onboard new customers with diverse POS systems while maintaining a standardized approach to data management and analytics.
