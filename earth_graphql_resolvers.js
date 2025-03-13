/**
 * Earth Module GraphQL Resolvers
 * 
 * This file implements the resolvers for the Earth module GraphQL schema.
 * It connects the GraphQL API to the Snowflake connector.
 */

const { GraphQLScalarType, Kind } = require('graphql');
const { SnowflakeConnector } = require('./snowflake_connector');

// Custom Date scalar type
const dateScalar = new GraphQLScalarType({
  name: 'Date',
  description: 'Date custom scalar type',
  serialize(value) {
    return value.toISOString(); // Convert outgoing Date to ISO string
  },
  parseValue(value) {
    return new Date(value); // Convert incoming string to Date
  },
  parseLiteral(ast) {
    if (ast.kind === Kind.STRING) {
      return new Date(ast.value); // Convert AST string to Date
    }
    return null;
  },
});

// Create resolvers
const resolvers = {
  Date: dateScalar,
  
  Query: {
    // Daily Sales Summary resolver
    dailySalesSummary: async (_, { dateRange }, { tenantId }) => {
      const connector = new SnowflakeConnector(tenantId);
      try {
        const results = await connector.get_daily_sales_summary(
          dateRange.startDate, 
          dateRange.endDate
        );
        
        // Transform results to match GraphQL schema
        return results.map(row => ({
          date: new Date(row.DATE),
          totalSales: row.TOTAL_SALES,
          totalOrders: row.TOTAL_ORDERS,
          averageOrderValue: row.AVERAGE_ORDER_VALUE,
          totalUnitsSold: row.TOTAL_UNITS_SOLD,
          totalUniqueCustomers: row.TOTAL_UNIQUE_CUSTOMERS
        }));
      } finally {
        connector.disconnect();
      }
    },
    
    // Customer Insights resolvers
    customerInsights: async (_, { pagination = { limit: 100, offset: 0 } }, { tenantId }) => {
      const connector = new SnowflakeConnector(tenantId);
      try {
        const results = await connector.get_customer_insights(
          pagination.limit, 
          pagination.offset
        );
        
        // Transform results to match GraphQL schema
        return results.map(row => ({
          customerId: row.CUSTOMER_ID,
          customerName: row.CUSTOMER_NAME,
          lifetimeValue: row.LIFETIME_VALUE,
          lastPurchaseDate: row.LAST_PURCHASE_DATE ? new Date(row.LAST_PURCHASE_DATE) : null,
          purchaseFrequency: row.PURCHASE_FREQUENCY,
          totalOrders: row.TOTAL_ORDERS,
          averageOrderValue: row.AVERAGE_ORDER_VALUE,
          favoriteProductCategory: row.FAVORITE_PRODUCT_CATEGORY
        }));
      } finally {
        connector.disconnect();
      }
    },
    
    customerDetail: async (_, { customerId }, { tenantId }) => {
      const connector = new SnowflakeConnector(tenantId);
      try {
        const query = `
          SELECT 
            CUSTOMER_ID,
            CUSTOMER_NAME,
            LIFETIME_VALUE,
            LAST_PURCHASE_DATE,
            PURCHASE_FREQUENCY,
            TOTAL_ORDERS,
            AVERAGE_ORDER_VALUE,
            FAVORITE_PRODUCT_CATEGORY
          FROM 
            CUSTOMER_INSIGHTS
          WHERE 
            CUSTOMER_ID = %s
            /* TENANT_FILTER */
        `;
        
        const results = await connector.execute_query(query, { customerId });
        
        if (results.length === 0) {
          return null;
        }
        
        const row = results[0];
        return {
          customerId: row.CUSTOMER_ID,
          customerName: row.CUSTOMER_NAME,
          lifetimeValue: row.LIFETIME_VALUE,
          lastPurchaseDate: row.LAST_PURCHASE_DATE ? new Date(row.LAST_PURCHASE_DATE) : null,
          purchaseFrequency: row.PURCHASE_FREQUENCY,
          totalOrders: row.TOTAL_ORDERS,
          averageOrderValue: row.AVERAGE_ORDER_VALUE,
          favoriteProductCategory: row.FAVORITE_PRODUCT_CATEGORY
        };
      } finally {
        connector.disconnect();
      }
    },
    
    // Product Performance resolvers
    productPerformance: async (_, { pagination = { limit: 100, offset: 0 } }, { tenantId }) => {
      const connector = new SnowflakeConnector(tenantId);
      try {
        const results = await connector.get_product_performance(
          pagination.limit, 
          pagination.offset
        );
        
        // Transform results to match GraphQL schema
        return results.map(row => ({
          productId: row.PRODUCT_ID,
          productName: row.PRODUCT_NAME,
          totalSales: row.TOTAL_SALES,
          quantitySold: row.QUANTITY_SOLD,
          profitMargin: row.PROFIT_MARGIN,
          stockLevel: row.STOCK_LEVEL,
          reorderPoint: row.REORDER_POINT,
          daysOfSupply: row.DAYS_OF_SUPPLY
        }));
      } finally {
        connector.disconnect();
      }
    },
    
    productDetail: async (_, { productId }, { tenantId }) => {
      const connector = new SnowflakeConnector(tenantId);
      try {
        const query = `
          SELECT 
            PRODUCT_ID,
            PRODUCT_NAME,
            TOTAL_SALES,
            QUANTITY_SOLD,
            PROFIT_MARGIN,
            STOCK_LEVEL,
            REORDER_POINT,
            DAYS_OF_SUPPLY
          FROM 
            PRODUCT_PERFORMANCE
          WHERE 
            PRODUCT_ID = %s
            /* TENANT_FILTER */
        `;
        
        const results = await connector.execute_query(query, { productId });
        
        if (results.length === 0) {
          return null;
        }
        
        const row = results[0];
        return {
          productId: row.PRODUCT_ID,
          productName: row.PRODUCT_NAME,
          totalSales: row.TOTAL_SALES,
          quantitySold: row.QUANTITY_SOLD,
          profitMargin: row.PROFIT_MARGIN,
          stockLevel: row.STOCK_LEVEL,
          reorderPoint: row.REORDER_POINT,
          daysOfSupply: row.DAYS_OF_SUPPLY
        };
      } finally {
        connector.disconnect();
      }
    },
    
    // Inventory Status resolver
    inventoryStatus: async (_, { pagination = { limit: 100, offset: 0 } }, { tenantId }) => {
      const connector = new SnowflakeConnector(tenantId);
      try {
        const results = await connector.get_inventory_status(
          pagination.limit, 
          pagination.offset
        );
        
        // Transform results to match GraphQL schema
        return results.map(row => ({
          productId: row.PRODUCT_ID,
          productName: row.PRODUCT_NAME,
          currentStock: row.CURRENT_STOCK,
          reorderPoint: row.REORDER_POINT,
          daysOfSupply: row.DAYS_OF_SUPPLY,
          stockStatus: row.STOCK_STATUS,
          lastRestockDate: row.LAST_RESTOCK_DATE ? new Date(row.LAST_RESTOCK_DATE) : null,
          nextRestockDate: row.NEXT_RESTOCK_DATE ? new Date(row.NEXT_RESTOCK_DATE) : null
        }));
      } finally {
        connector.disconnect();
      }
    },
    
    // Shop Performance resolvers
    shopPerformance: async (_, { pagination = { limit: 100, offset: 0 } }, { tenantId }) => {
      const connector = new SnowflakeConnector(tenantId);
      try {
        const results = await connector.get_shop_performance(
          pagination.limit, 
          pagination.offset
        );
        
        // Transform results to match GraphQL schema
        return results.map(row => ({
          shopId: row.SHOP_ID,
          shopName: row.SHOP_NAME,
          totalSales: row.TOTAL_SALES,
          totalOrders: row.TOTAL_ORDERS,
          averageOrderValue: row.AVERAGE_ORDER_VALUE,
          totalCustomers: row.TOTAL_CUSTOMERS,
          topSellingCategory: row.TOP_SELLING_CATEGORY,
          salesGrowthRate: row.SALES_GROWTH_RATE
        }));
      } finally {
        connector.disconnect();
      }
    },
    
    shopDetail: async (_, { shopId }, { tenantId }) => {
      const connector = new SnowflakeConnector(tenantId);
      try {
        const query = `
          SELECT 
            SHOP_ID,
            SHOP_NAME,
            TOTAL_SALES,
            TOTAL_ORDERS,
            AVERAGE_ORDER_VALUE,
            TOTAL_CUSTOMERS,
            TOP_SELLING_CATEGORY,
            SALES_GROWTH_RATE
          FROM 
            SHOP_PERFORMANCE
          WHERE 
            SHOP_ID = %s
            /* TENANT_FILTER */
        `;
        
        const results = await connector.execute_query(query, { shopId });
        
        if (results.length === 0) {
          return null;
        }
        
        const row = results[0];
        return {
          shopId: row.SHOP_ID,
          shopName: row.SHOP_NAME,
          totalSales: row.TOTAL_SALES,
          totalOrders: row.TOTAL_ORDERS,
          averageOrderValue: row.AVERAGE_ORDER_VALUE,
          totalCustomers: row.TOTAL_CUSTOMERS,
          topSellingCategory: row.TOP_SELLING_CATEGORY,
          salesGrowthRate: row.SALES_GROWTH_RATE
        };
      } finally {
        connector.disconnect();
      }
    },
    
    // Business Dashboard resolver
    businessDashboard: async (_, __, { tenantId }) => {
      const connector = new SnowflakeConnector(tenantId);
      try {
        const metrics = await connector.get_business_dashboard_metrics();
        
        // Transform metrics to match GraphQL schema
        return {
          totalSales: metrics.TOTAL_SALES ? {
            value: metrics.TOTAL_SALES.value,
            comparisonValue: metrics.TOTAL_SALES.comparison_value,
            percentChange: metrics.TOTAL_SALES.percent_change,
            trendDirection: metrics.TOTAL_SALES.trend_direction,
            timePeriod: metrics.TOTAL_SALES.time_period
          } : null,
          totalOrders: metrics.TOTAL_ORDERS ? {
            value: metrics.TOTAL_ORDERS.value,
            comparisonValue: metrics.TOTAL_ORDERS.comparison_value,
            percentChange: metrics.TOTAL_ORDERS.percent_change,
            trendDirection: metrics.TOTAL_ORDERS.trend_direction,
            timePeriod: metrics.TOTAL_ORDERS.time_period
          } : null,
          averageOrderValue: metrics.AVERAGE_ORDER_VALUE ? {
            value: metrics.AVERAGE_ORDER_VALUE.value,
            comparisonValue: metrics.AVERAGE_ORDER_VALUE.comparison_value,
            percentChange: metrics.AVERAGE_ORDER_VALUE.percent_change,
            trendDirection: metrics.AVERAGE_ORDER_VALUE.trend_direction,
            timePeriod: metrics.AVERAGE_ORDER_VALUE.time_period
          } : null,
          customerCount: metrics.CUSTOMER_COUNT ? {
            value: metrics.CUSTOMER_COUNT.value,
            comparisonValue: metrics.CUSTOMER_COUNT.comparison_value,
            percentChange: metrics.CUSTOMER_COUNT.percent_change,
            trendDirection: metrics.CUSTOMER_COUNT.trend_direction,
            timePeriod: metrics.CUSTOMER_COUNT.time_period
          } : null,
          inventoryValue: metrics.INVENTORY_VALUE ? {
            value: metrics.INVENTORY_VALUE.value,
            comparisonValue: metrics.INVENTORY_VALUE.comparison_value,
            percentChange: metrics.INVENTORY_VALUE.percent_change,
            trendDirection: metrics.INVENTORY_VALUE.trend_direction,
            timePeriod: metrics.INVENTORY_VALUE.time_period
          } : null,
          topSellingProduct: metrics.TOP_SELLING_PRODUCT ? metrics.TOP_SELLING_PRODUCT.value : null,
          topSellingCategory: metrics.TOP_SELLING_CATEGORY ? metrics.TOP_SELLING_CATEGORY.value : null
        };
      } finally {
        connector.disconnect();
      }
    },
    
    // Inventory Recommendations resolver
    inventoryRecommendations: async (_, __, { tenantId }) => {
      const connector = new SnowflakeConnector(tenantId);
      try {
        const results = await connector.get_inventory_recommendations();
        
        // Transform results to match GraphQL schema
        return results.map(row => ({
          productId: row.PRODUCT_ID,
          productName: row.PRODUCT_NAME,
          currentStock: row.CURRENT_STOCK,
          reorderPoint: row.REORDER_POINT,
          daysOfSupply: row.DAYS_OF_SUPPLY,
          recommendationType: row.RECOMMENDATION_TYPE,
          recommendationText: row.RECOMMENDATION_TEXT,
          recommendedActionValue: row.RECOMMENDED_ACTION_VALUE
        }));
      } finally {
        connector.disconnect();
      }
    },
    
    // General Recommendations resolver
    recommendations: async (_, { type }, { tenantId }) => {
      const connector = new SnowflakeConnector(tenantId);
      try {
        // For now, we'll just return inventory recommendations
        // In a real implementation, this would be expanded to include other recommendation types
        const results = await connector.get_inventory_recommendations();
        
        // Transform results to match GraphQL schema
        return results.map((row, index) => ({
          id: `recommendation-${index}`,
          type: 'INVENTORY_OPTIMIZATION',
          title: row.RECOMMENDATION_TYPE === 'RESTOCK' 
            ? `Restock ${row.PRODUCT_NAME}`
            : `Reduce inventory for ${row.PRODUCT_NAME}`,
          description: row.RECOMMENDATION_TEXT,
          impact: row.RECOMMENDATION_TYPE === 'RESTOCK' 
            ? 0.8 // High impact for restocking
            : 0.6, // Medium impact for reducing inventory
          confidence: 0.9,
          suggestedActions: [
            row.RECOMMENDATION_TYPE === 'RESTOCK'
              ? `Order ${row.RECOMMENDED_ACTION_VALUE} units`
              : `Consider promotions to reduce inventory by ${row.RECOMMENDED_ACTION_VALUE} units`
          ],
          relatedEntityId: row.PRODUCT_ID,
          relatedEntityType: 'PRODUCT'
        }));
      } finally {
        connector.disconnect();
      }
    }
  }
};

module.exports = resolvers;
