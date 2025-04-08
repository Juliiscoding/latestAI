# Changelog - ProHandel API Integration

## Overview
This changelog documents the integration of real-time ProHandel data into the Mercurios BI dashboard, replacing mock data with actual Point-of-Sale data using the Model Composition Platform (MCP) approach.

## v1.0.0 (2025-04-07)

### Added
- **ProHandel API Client**
  - Created dedicated client at `lib/mercurios/clients/prohandel-client.ts`
  - Implemented OAuth2 authentication with token caching
  - Added methods for fetching articles, stock levels, sales data, and customer information
  - Added test connection functionality with detailed logging
  - Implemented simplified data retrieval with fallback to mock data

- **MCP Integration**
  - Updated `lib/mercurios/api.ts` to connect to ProHandel API instead of using mock data
  - Added type definitions for API responses: StockoutRiskItem, InventoryAnalyticsData, etc.
  - Implemented robust error handling with fallback to mock data when needed
  - Created functions for accessing various ProHandel endpoints through MCP

- **Business Intelligence UI**
  - Added StockoutRiskWidget with toggle between mock and real data
  - Created test connection button for verifying ProHandel connectivity
  - Improved UI with progress indicators, badges, and better error handling
  - Added pagination support for large datasets

### Changed
- Refactored StockoutRiskWidget from named export to default export
- Modified data fetching approach to use TanStack Query for better caching
- Updated typing in API module to reduce TypeScript errors
- Improved error messages with actionable feedback

### Technical Improvements
- Added TypeScript interfaces for all ProHandel data structures
- Implemented proper authentication token handling with refresh logic
- Created safety mechanisms to prevent excessive API calls
- Added detailed logging for debugging connection issues

## Architecture

### Multi-tenant Data Architecture
The implementation follows the optimal architecture for Mercurios.ai:
- **Multi-Tenant Data Source**: Supports fetching data from ProHandel with tenant isolation
- **Materialized Views**: Prepares data for efficient UI rendering
- **Single Connection Strategy**: Minimizes authentication overhead 
- **Robust Caching Layer**: Implements configurable TTL for API responses
- **Direct API to Data Sources**: Connects directly to ProHandel's API

### Data Sources
The dashboard now integrates data from multiple sources:
1. **ProHandel German POS data** (primary source for inventory/sales)
2. **Klaviyo email marketing data** (prepared for future integration)
3. **Google Analytics 4 web analytics** (prepared for future integration)
4. **Shopify e-commerce data** (prepared for future integration)

## Future Development
- Add more visual data representations (charts, trends)
- Implement additional ProHandel API endpoints (orders, returns)
- Enhance error recovery mechanisms
- Add export functionality for reports
- Optimize queries for large datasets
