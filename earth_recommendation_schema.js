/**
 * Earth Module Recommendation Schema
 * 
 * This file defines the GraphQL schema for the recommendation engine,
 * which provides AI-driven insights based on Snowflake analytics data.
 */

const { gql } = require('apollo-server-micro');

const typeDefs = gql`
  enum RecommendationType {
    INVENTORY_OPTIMIZATION
    CUSTOMER_TARGETING
    PRICING_STRATEGY
    MARKETING_CAMPAIGN
    PRODUCT_BUNDLING
  }

  type Recommendation {
    id: ID!
    type: String!
    title: String!
    description: String!
    impact: Float!
    confidence: Float!
    suggestedActions: [String!]!
    relatedEntityId: String
    relatedEntityType: String
    createdAt: String!
    expiresAt: String
    status: String
  }

  type InventoryRecommendation {
    productId: ID!
    productName: String!
    currentStock: Int!
    reorderPoint: Int!
    daysOfSupply: Int!
    recommendationType: String!
    recommendationText: String!
    recommendedActionValue: Int!
    impact: Float!
    confidence: Float!
  }

  type CustomerRecommendation {
    customerId: ID!
    customerName: String!
    segment: String!
    lastPurchaseDate: String!
    recommendationType: String!
    recommendationText: String!
    potentialValue: Float!
    impact: Float!
    confidence: Float!
  }

  type PricingRecommendation {
    productId: ID!
    productName: String!
    currentPrice: Float!
    recommendedPrice: Float!
    recommendationType: String!
    recommendationText: String!
    potentialRevenue: Float!
    impact: Float!
    confidence: Float!
  }

  extend type Query {
    # Get all recommendations or filter by type
    recommendations(type: RecommendationType): [Recommendation!]!
    
    # Get a specific recommendation by ID
    recommendation(id: ID!): Recommendation
    
    # Get top recommendations with optional limit
    topRecommendations(limit: Int): [Recommendation!]!
    
    # Get inventory-specific recommendations
    inventoryRecommendations: [InventoryRecommendation!]!
    
    # Get customer-specific recommendations
    customerRecommendations: [CustomerRecommendation!]!
    
    # Get pricing-specific recommendations
    pricingRecommendations: [PricingRecommendation!]!
  }

  extend type Mutation {
    # Mark a recommendation as implemented
    implementRecommendation(id: ID!): Recommendation
    
    # Dismiss a recommendation
    dismissRecommendation(id: ID!): Recommendation
    
    # Rate a recommendation's helpfulness
    rateRecommendation(id: ID!, helpful: Boolean!): Recommendation
  }
`;

module.exports = typeDefs;
