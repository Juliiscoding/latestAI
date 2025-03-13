# Earth Module Integration Plan for Mercurios.ai

## Overview

This document outlines the plan to integrate the "Earth" module (Business Intelligence & Analytics) into the existing Mercurios.ai platform. The Earth module will connect the Snowflake analytics views with the existing Next.js frontend to provide actionable business insights and AI-driven recommendations.

## Current Assets

- **Frontend**: Existing Next.js application at https://mercurios.ai with dashboard at https://mercurios.ai/dashboard
- **Repository**: https://github.com/Juliiscoding/latestAI.git
- **Data Foundation**: Snowflake analytics views (DAILY_SALES_SUMMARY, CUSTOMER_INSIGHTS, etc.)
- **Infrastructure**: Cost-optimized warehouses with resource monitors and auto-suspension

## Integration Architecture

```
┌─────────────────────┐      ┌───────────────────┐      ┌─────────────────────┐
│  Snowflake          │      │  GraphQL API      │      │  Next.js Frontend   │
│  Analytics Views    │──────▶  (Data Access)    │──────▶  (Earth Module)     │
└─────────────────────┘      └───────────────────┘      └─────────────────────┘
         │                            │                           │
         │                            │                           │
         ▼                            ▼                           ▼
┌─────────────────────┐      ┌───────────────────┐      ┌─────────────────────┐
│  ML/LLM Models      │──────▶  Recommendation   │──────▶  Insights &         │
│  (Prediction)       │      │  Engine           │      │  Recommendations    │
└─────────────────────┘      └───────────────────┘      └─────────────────────┘
```

## Implementation Plan

### Phase 1: Earth Module Structure (Week 1)

1. **Module Setup**
   - Create `/earth` directory in the Next.js pages structure
   - Implement base layout and navigation components
   - Set up role-based access control for Earth module

2. **Authentication Integration**
   - Ensure existing auth system supports Earth module access
   - Implement tenant-specific routing and data isolation
   - Create middleware for role verification

3. **Design System Extensions**
   - Extend existing design system for analytics components
   - Create reusable chart and visualization components
   - Implement responsive dashboard layouts

### Phase 2: Data Integration (Week 2)

1. **GraphQL Schema Design**
   - Define GraphQL types for all analytics views
   - Create queries for dashboard metrics and insights
   - Implement pagination and filtering for large datasets

2. **API Integration**
   - Connect Earth module to GraphQL endpoints
   - Implement data fetching with proper error handling
   - Set up caching strategy to minimize Snowflake queries

3. **Data Transformation Layer**
   - Create utility functions for data formatting
   - Implement time series transformations for trend analysis
   - Build comparison functions for period-over-period analysis

### Phase 3: Visualization & Insights (Week 3)

1. **Dashboard Components**
   - Implement key metrics dashboard with KPI cards
   - Create trend visualization components
   - Build drill-down capabilities for detailed analysis

2. **Insight Generation**
   - Develop algorithms to identify notable trends
   - Create anomaly detection for key metrics
   - Implement natural language descriptions of data insights

3. **Interactive Exploration**
   - Build filtering and segmentation controls
   - Implement date range selection
   - Create export and sharing functionality

### Phase 4: AI Recommendations (Week 4)

1. **Recommendation Engine Integration**
   - Connect to ML/LLM models via API
   - Implement recommendation display components
   - Create feedback mechanism for recommendation quality

2. **Initial Use Cases**
   - Inventory optimization recommendations
   - Customer segmentation insights
   - Sales forecasting and trend predictions

3. **Explanation & Context**
   - Provide context for each recommendation
   - Implement "why this matters" explanations
   - Create action items based on recommendations

## Technical Implementation Details

### Next.js Structure

```
/pages
  /earth
    index.js             # Main Earth dashboard
    insights.js          # Detailed insights page
    recommendations.js   # AI recommendations page
    /analytics
      [metric].js        # Dynamic metric detail pages
    /reports
      [reportId].js      # Saved/scheduled reports
  
/components
  /earth
    /charts              # Reusable chart components
    /metrics             # KPI and metric components
    /recommendations     # Recommendation UI components
    /filters             # Filter and control components
```

### GraphQL Schema (Key Types)

```graphql
type DailySalesSummary {
  date: Date!
  totalSales: Float!
  totalOrders: Int!
  averageOrderValue: Float!
  # Additional fields from DAILY_SALES_SUMMARY view
}

type CustomerInsight {
  customerId: ID!
  customerName: String
  lifetimeValue: Float!
  lastPurchaseDate: Date
  purchaseFrequency: Float
  # Additional fields from CUSTOMER_INSIGHTS view
}

type ProductPerformance {
  productId: ID!
  productName: String!
  totalSales: Float!
  quantitySold: Int!
  profitMargin: Float!
  # Additional fields from PRODUCT_PERFORMANCE view
}

type Recommendation {
  id: ID!
  type: RecommendationType!
  title: String!
  description: String!
  impact: Float
  confidence: Float
  suggestedActions: [String!]
}

enum RecommendationType {
  INVENTORY_OPTIMIZATION
  CUSTOMER_TARGETING
  PRICING_STRATEGY
  MARKETING_CAMPAIGN
  PRODUCT_BUNDLING
}

# Queries
type Query {
  dailySalesSummary(dateRange: DateRangeInput!): [DailySalesSummary!]!
  customerInsights(filters: CustomerFiltersInput): [CustomerInsight!]!
  productPerformance(filters: ProductFiltersInput): [ProductPerformance!]!
  recommendations(type: RecommendationType): [Recommendation!]!
  # Additional queries for other analytics views
}
```

### Data Access Strategy

1. **Read-Only Access**
   - Create dedicated read-only Snowflake role for Earth module
   - Implement query monitoring and logging
   - Set up query timeout limits to prevent runaway queries

2. **Caching Strategy**
   - Implement Redis caching for frequent queries
   - Use stale-while-revalidate pattern for dashboard data
   - Cache invalidation based on data refresh schedule

3. **Query Optimization**
   - Use materialized views for common dashboard queries
   - Implement query parameterization to leverage query result cache
   - Monitor and optimize slow-running queries

## Staging & Deployment

1. **Staging Environment**
   - Set up staging.mercurios.ai subdomain
   - Configure CI/CD pipeline for Earth module
   - Implement feature flags for gradual rollout

2. **Testing Strategy**
   - Create automated tests for data accuracy
   - Implement performance testing for dashboard load times
   - Conduct usability testing with internal stakeholders

3. **Monitoring & Analytics**
   - Set up error tracking and performance monitoring
   - Implement usage analytics to track feature adoption
   - Create alerting for data pipeline issues

## Success Metrics

1. **Technical Metrics**
   - Dashboard load time < 2 seconds
   - Query response time < 500ms for cached data
   - 99.9% uptime for Earth module

2. **Business Metrics**
   - User engagement with recommendations (click-through rate)
   - Time spent on Earth module pages
   - Number of insights exported or shared

3. **Value Metrics**
   - Reported business value from recommendations
   - User satisfaction scores
   - Feature request and feedback volume

## Next Steps

1. Set up the Earth module structure in the existing Next.js codebase
2. Design and implement the GraphQL schema for Snowflake data access
3. Create the first dashboard components using the existing design system
4. Implement basic recommendation display with placeholder data
5. Connect to Snowflake analytics views via secure API endpoints
