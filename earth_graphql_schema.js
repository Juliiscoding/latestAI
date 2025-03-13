/**
 * Earth Module GraphQL Schema
 * 
 * This file defines the GraphQL schema for the Earth module of Mercurios.ai.
 * It provides types and resolvers for accessing Snowflake analytics data.
 */

const { gql } = require('apollo-server-micro');

// Define GraphQL schema types
const typeDefs = gql`
  # Date scalar type for handling dates
  scalar Date

  # Input types for filtering and pagination
  input DateRangeInput {
    startDate: String!
    endDate: String!
  }

  input PaginationInput {
    limit: Int = 100
    offset: Int = 0
  }

  # Daily Sales Summary
  type DailySalesSummary {
    date: Date!
    totalSales: Float!
    totalOrders: Int!
    averageOrderValue: Float!
    totalUnitsSold: Int!
    totalUniqueCustomers: Int!
  }

  # Customer Insights
  type CustomerInsight {
    customerId: ID!
    customerName: String
    lifetimeValue: Float!
    lastPurchaseDate: Date
    purchaseFrequency: Float
    totalOrders: Int!
    averageOrderValue: Float!
    favoriteProductCategory: String
  }

  # Product Performance
  type ProductPerformance {
    productId: ID!
    productName: String!
    totalSales: Float!
    quantitySold: Int!
    profitMargin: Float!
    stockLevel: Int
    reorderPoint: Int
    daysOfSupply: Float
  }

  # Inventory Status
  type InventoryStatus {
    productId: ID!
    productName: String!
    currentStock: Int!
    reorderPoint: Int!
    daysOfSupply: Float!
    stockStatus: String!
    lastRestockDate: Date
    nextRestockDate: Date
  }

  # Shop Performance
  type ShopPerformance {
    shopId: ID!
    shopName: String!
    totalSales: Float!
    totalOrders: Int!
    averageOrderValue: Float!
    totalCustomers: Int!
    topSellingCategory: String
    salesGrowthRate: Float
  }

  # Business Dashboard Metric
  type BusinessMetric {
    value: Float!
    comparisonValue: Float
    percentChange: Float
    trendDirection: String!
    timePeriod: String!
  }

  # Business Dashboard
  type BusinessDashboard {
    totalSales: BusinessMetric
    totalOrders: BusinessMetric
    averageOrderValue: BusinessMetric
    customerCount: BusinessMetric
    inventoryValue: BusinessMetric
    topSellingProduct: String
    topSellingCategory: String
  }

  # Recommendation Types
  enum RecommendationType {
    INVENTORY_OPTIMIZATION
    CUSTOMER_TARGETING
    PRICING_STRATEGY
    MARKETING_CAMPAIGN
    PRODUCT_BUNDLING
  }

  # Recommendation
  type Recommendation {
    id: ID!
    type: RecommendationType!
    title: String!
    description: String!
    impact: Float
    confidence: Float
    suggestedActions: [String!]
    relatedEntityId: String
    relatedEntityType: String
  }

  # Inventory Recommendation
  type InventoryRecommendation {
    productId: ID!
    productName: String!
    currentStock: Int!
    reorderPoint: Int!
    daysOfSupply: Float!
    recommendationType: String!
    recommendationText: String!
    recommendedActionValue: Int!
  }

  # Query type
  type Query {
    # Daily Sales Summary
    dailySalesSummary(dateRange: DateRangeInput!): [DailySalesSummary!]!
    
    # Customer Insights
    customerInsights(pagination: PaginationInput): [CustomerInsight!]!
    customerDetail(customerId: ID!): CustomerInsight
    
    # Product Performance
    productPerformance(pagination: PaginationInput): [ProductPerformance!]!
    productDetail(productId: ID!): ProductPerformance
    
    # Inventory Status
    inventoryStatus(pagination: PaginationInput): [InventoryStatus!]!
    
    # Shop Performance
    shopPerformance(pagination: PaginationInput): [ShopPerformance!]!
    shopDetail(shopId: ID!): ShopPerformance
    
    # Business Dashboard
    businessDashboard: BusinessDashboard!
    
    # Recommendations
    inventoryRecommendations: [InventoryRecommendation!]!
    recommendations(type: RecommendationType): [Recommendation!]!
  }
`;

// Export the schema
module.exports = typeDefs;
