# Earth Module Dashboard for Mercurios.ai

This branch contains the Earth module dashboard for Mercurios.ai, providing business intelligence and analytics capabilities through interactive visualizations and AI-driven recommendations.

## Features

- **Business Insights Dashboard**: Interactive visualizations of key business metrics using shadcn/ui charts
- **Recommendation Engine**: AI-driven recommendations for inventory optimization, customer targeting, and pricing strategies
- **GraphQL API**: Integration with Snowflake analytics views for real-time data access

## Tech Stack

- **Next.js**: React framework for building the user interface
- **Apollo Client**: GraphQL client for data fetching
- **Chakra UI**: UI library for consistent styling
- **shadcn/ui**: Chart components for data visualization

## Getting Started

1. Install dependencies:
   ```
   npm install
   ```

2. Run the development server:
   ```
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view the dashboard

## Deployment

This branch is optimized for deployment with Vercel and contains only the essential files needed for the Earth module dashboard.

## Analytics Views

This dashboard connects to the following Snowflake analytics views:

- DAILY_SALES_SUMMARY
- CUSTOMER_INSIGHTS
- PRODUCT_PERFORMANCE
- INVENTORY_STATUS
- SHOP_PERFORMANCE
- BUSINESS_DASHBOARD

## Integration with Mercurios.ai

The Earth module is designed to be integrated as a product within the overall Mercurios.ai platform, providing advanced analytics capabilities while leveraging the existing Snowflake foundation.
