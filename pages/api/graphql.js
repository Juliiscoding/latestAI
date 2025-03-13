/**
 * Mock GraphQL API endpoint for Earth module preview
 */

import { ApolloServer } from 'apollo-server-micro';
import { gql } from 'apollo-server-micro';

// Mock data for the preview
const mockData = {
  dailySalesSummary: Array.from({ length: 30 }, (_, i) => ({
    date: new Date(2025, 2, i + 1).toISOString(),
    totalSales: 15000 + Math.random() * 10000,
    totalOrders: 120 + Math.random() * 50,
    averageOrderValue: 125 + Math.random() * 20,
    comparisonSales: 14000 + Math.random() * 9000,
    comparisonOrders: 110 + Math.random() * 40,
  })),
  customerInsights: [
    { segment: 'VIP', count: 120, revenue: 45000, frequency: 3.2 },
    { segment: 'Regular', count: 450, revenue: 67000, frequency: 1.8 },
    { segment: 'Occasional', count: 780, revenue: 42000, frequency: 0.7 },
    { segment: 'New', count: 210, revenue: 18000, frequency: 1.0 },
  ],
  productPerformance: Array.from({ length: 10 }, (_, i) => ({
    productId: `PROD-${1000 + i}`,
    productName: `Product ${i + 1}`,
    sales: 5000 + Math.random() * 15000,
    quantity: 50 + Math.random() * 200,
    profit: 2000 + Math.random() * 8000,
    returnRate: Math.random() * 0.05,
    rating: 3.5 + Math.random() * 1.5,
  })),
  shopPerformance: Array.from({ length: 5 }, (_, i) => ({
    shopId: `SHOP-${100 + i}`,
    shopName: `Shop ${i + 1}`,
    totalSales: 120000 + Math.random() * 80000,
    totalOrders: 1200 + Math.random() * 800,
    customerCount: 500 + Math.random() * 300,
    averageOrderValue: 100 + Math.random() * 50,
    yearOverYearGrowth: -0.05 + Math.random() * 0.2,
  })),
  recommendations: Array.from({ length: 15 }, (_, i) => {
    const types = ['INVENTORY_OPTIMIZATION', 'CUSTOMER_TARGETING', 'PRICING_STRATEGY', 'MARKETING_CAMPAIGN', 'PRODUCT_BUNDLING'];
    const type = types[Math.floor(Math.random() * types.length)];
    
    let title, description, suggestedActions;
    
    switch (type) {
      case 'INVENTORY_OPTIMIZATION':
        title = `${Math.random() > 0.5 ? 'Restock' : 'Reduce inventory for'} Product ${i + 1}`;
        description = Math.random() > 0.5 
          ? `Inventory level below reorder point. Consider restocking soon.` 
          : `Excess inventory detected. Consider promotions to reduce stock.`;
        suggestedActions = Math.random() > 0.5
          ? [`Order ${Math.floor(Math.random() * 100) + 20} units of Product ${i + 1}`]
          : [`Consider promotions to reduce inventory by ${Math.floor(Math.random() * 50) + 10} units`];
        break;
      case 'CUSTOMER_TARGETING':
        title = `${Math.random() > 0.5 ? 'Reactivate' : 'Upsell'} ${Math.random() > 0.5 ? 'VIP' : 'Regular'} Customers`;
        description = Math.random() > 0.5
          ? `Several customers have not made purchases in over 60 days.`
          : `Identified customers likely to upgrade to premium products.`;
        suggestedActions = Math.random() > 0.5
          ? [`Send personalized email campaign`, `Offer exclusive discount`]
          : [`Promote premium products to selected customers`, `Create bundle offers`];
        break;
      default:
        title = `Optimize ${type.replace(/_/g, ' ').toLowerCase()} for Product ${i + 1}`;
        description = `Opportunity identified to improve performance through ${type.replace(/_/g, ' ').toLowerCase()}.`;
        suggestedActions = [`Review current strategy`, `Implement suggested changes`, `Monitor results`];
    }
    
    return {
      id: `REC-${1000 + i}`,
      type,
      title,
      description,
      impact: 0.3 + Math.random() * 0.7,
      confidence: 0.5 + Math.random() * 0.5,
      suggestedActions,
      relatedEntityId: Math.random() > 0.5 ? `PROD-${1000 + i}` : null,
      relatedEntityType: Math.random() > 0.5 ? 'PRODUCT' : null,
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'ACTIVE',
    };
  }),
  inventoryRecommendations: Array.from({ length: 8 }, (_, i) => ({
    productId: `PROD-${1000 + i}`,
    productName: `Product ${i + 1}`,
    currentStock: Math.floor(Math.random() * 50),
    reorderPoint: 30,
    daysOfSupply: Math.random() > 0.5 ? Math.floor(Math.random() * 20) : Math.floor(Math.random() * 100) + 90,
    recommendationType: Math.random() > 0.5 ? 'RESTOCK' : 'REDUCE_INVENTORY',
    recommendationText: Math.random() > 0.5 
      ? `Inventory level below reorder point. Consider restocking soon.` 
      : `Excess inventory detected. Consider promotions to reduce stock.`,
    recommendedActionValue: Math.floor(Math.random() * 50) + 10,
    impact: 0.3 + Math.random() * 0.7,
    confidence: 0.5 + Math.random() * 0.5,
  })),
  customerRecommendations: Array.from({ length: 6 }, (_, i) => ({
    customerId: `CUST-${10000 + i}`,
    customerName: `Customer ${i + 1}`,
    segment: Math.random() > 0.3 ? 'VIP' : 'Regular',
    lastPurchaseDate: new Date(Date.now() - Math.floor(Math.random() * 120) * 24 * 60 * 60 * 1000).toISOString(),
    recommendationType: Math.random() > 0.5 ? 'REACTIVATION' : 'UPSELL',
    recommendationText: Math.random() > 0.5
      ? `Customer has not purchased in over 60 days. Consider a win-back campaign.`
      : `High-value customer with potential for premium products.`,
    potentialValue: 500 + Math.random() * 2000,
    impact: 0.3 + Math.random() * 0.7,
    confidence: 0.5 + Math.random() * 0.5,
  })),
  pricingRecommendations: Array.from({ length: 5 }, (_, i) => ({
    productId: `PROD-${1000 + i}`,
    productName: `Product ${i + 1}`,
    currentPrice: 50 + Math.random() * 200,
    recommendedPrice: (50 + Math.random() * 200) * (Math.random() > 0.5 ? 1.1 : 0.9),
    recommendationType: Math.random() > 0.5 ? 'INCREASE_PRICE' : 'DECREASE_PRICE',
    recommendationText: Math.random() > 0.5
      ? `Popular product with low margin. Consider increasing price.`
      : `High margin but low sales. Consider decreasing price to boost volume.`,
    potentialRevenue: 1000 + Math.random() * 5000,
    impact: 0.3 + Math.random() * 0.7,
    confidence: 0.5 + Math.random() * 0.5,
  })),
};

// Define the schema
const typeDefs = gql`
  enum RecommendationType {
    INVENTORY_OPTIMIZATION
    CUSTOMER_TARGETING
    PRICING_STRATEGY
    MARKETING_CAMPAIGN
    PRODUCT_BUNDLING
  }

  type DailySalesSummary {
    date: String!
    totalSales: Float!
    totalOrders: Int!
    averageOrderValue: Float!
    comparisonSales: Float
    comparisonOrders: Int
  }

  type CustomerInsight {
    segment: String!
    count: Int!
    revenue: Float!
    frequency: Float!
  }

  type ProductPerformance {
    productId: ID!
    productName: String!
    sales: Float!
    quantity: Int!
    profit: Float!
    returnRate: Float!
    rating: Float!
  }

  type ShopPerformance {
    shopId: ID!
    shopName: String!
    totalSales: Float!
    totalOrders: Int!
    customerCount: Int!
    averageOrderValue: Float!
    yearOverYearGrowth: Float!
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

  type Query {
    dailySalesSummary(timeRange: String, shopId: ID): [DailySalesSummary!]!
    customerInsights(timeRange: String, shopId: ID): [CustomerInsight!]!
    productPerformance(timeRange: String, shopId: ID): [ProductPerformance!]!
    shopPerformance(timeRange: String): [ShopPerformance!]!
    recommendations(type: String): [Recommendation!]!
    recommendation(id: ID!): Recommendation
    topRecommendations(limit: Int): [Recommendation!]!
    inventoryRecommendations: [InventoryRecommendation!]!
    customerRecommendations: [CustomerRecommendation!]!
    pricingRecommendations: [PricingRecommendation!]!
  }

  type Mutation {
    implementRecommendation(id: ID!): Recommendation
    dismissRecommendation(id: ID!): Recommendation
    rateRecommendation(id: ID!, helpful: Boolean!): Recommendation
  }
`;

// Define the resolvers
const resolvers = {
  Query: {
    dailySalesSummary: (_, { timeRange, shopId }) => {
      return mockData.dailySalesSummary;
    },
    customerInsights: (_, { timeRange, shopId }) => {
      return mockData.customerInsights;
    },
    productPerformance: (_, { timeRange, shopId }) => {
      return mockData.productPerformance;
    },
    shopPerformance: (_, { timeRange }) => {
      return mockData.shopPerformance;
    },
    recommendations: (_, { type }) => {
      if (type) {
        return mockData.recommendations.filter(rec => rec.type === type);
      }
      return mockData.recommendations;
    },
    recommendation: (_, { id }) => {
      return mockData.recommendations.find(rec => rec.id === id);
    },
    topRecommendations: (_, { limit = 3 }) => {
      return mockData.recommendations
        .sort((a, b) => b.impact - a.impact)
        .slice(0, limit);
    },
    inventoryRecommendations: () => {
      return mockData.inventoryRecommendations;
    },
    customerRecommendations: () => {
      return mockData.customerRecommendations;
    },
    pricingRecommendations: () => {
      return mockData.pricingRecommendations;
    },
  },
  Mutation: {
    implementRecommendation: (_, { id }) => {
      const recommendation = mockData.recommendations.find(rec => rec.id === id);
      if (recommendation) {
        recommendation.status = 'IMPLEMENTED';
      }
      return recommendation;
    },
    dismissRecommendation: (_, { id }) => {
      const recommendation = mockData.recommendations.find(rec => rec.id === id);
      if (recommendation) {
        recommendation.status = 'DISMISSED';
      }
      return recommendation;
    },
    rateRecommendation: (_, { id, helpful }) => {
      return mockData.recommendations.find(rec => rec.id === id);
    },
  },
};

// Create the Apollo Server
const apolloServer = new ApolloServer({
  typeDefs,
  resolvers,
});

// Start the server
const startServer = apolloServer.start();

// Export the API handler
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader(
    'Access-Control-Allow-Origin',
    'https://studio.apollographql.com'
  );
  res.setHeader(
    'Access-Control-Allow-Headers',
    'Origin, X-Requested-With, Content-Type, Accept'
  );
  
  if (req.method === 'OPTIONS') {
    res.end();
    return false;
  }
  
  await startServer;
  
  await apolloServer.createHandler({
    path: '/api/graphql',
  })(req, res);
}

// Disable Next.js body parsing
export const config = {
  api: {
    bodyParser: false,
  },
};
