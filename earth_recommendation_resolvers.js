/**
 * Earth Module Recommendation Resolvers
 * 
 * This file implements the GraphQL resolvers for the recommendation engine,
 * connecting the schema to Snowflake data sources.
 */

const snowflakeConnector = require('./snowflake_connector_implementation');

// Helper function to execute Snowflake queries
const executeSnowflakeQuery = async (query, params = {}) => {
  try {
    const connection = await snowflakeConnector.getConnection();
    const result = await snowflakeConnector.executeQuery(connection, query, params);
    await snowflakeConnector.closeConnection(connection);
    return result;
  } catch (error) {
    console.error('Snowflake query error:', error);
    throw new Error(`Failed to execute Snowflake query: ${error.message}`);
  }
};

// Recommendation resolvers
const resolvers = {
  Query: {
    // Get all recommendations or filter by type
    recommendations: async (_, { type }) => {
      let query = `
        SELECT 
          RECOMMENDATION_ID as id,
          RECOMMENDATION_TYPE as type,
          TITLE,
          DESCRIPTION,
          IMPACT,
          CONFIDENCE,
          SUGGESTED_ACTIONS,
          RELATED_ENTITY_ID,
          RELATED_ENTITY_TYPE,
          CREATED_AT,
          EXPIRES_AT,
          STATUS
        FROM MERCURIOS_DATA.ANALYTICS.BUSINESS_RECOMMENDATIONS
      `;
      
      if (type) {
        query += ` WHERE RECOMMENDATION_TYPE = :type`;
      }
      
      query += ` ORDER BY IMPACT DESC, CONFIDENCE DESC`;
      
      const results = await executeSnowflakeQuery(query, { type });
      
      return results.map(rec => ({
        id: rec.ID,
        type: rec.TYPE,
        title: rec.TITLE,
        description: rec.DESCRIPTION,
        impact: parseFloat(rec.IMPACT),
        confidence: parseFloat(rec.CONFIDENCE),
        suggestedActions: rec.SUGGESTED_ACTIONS ? JSON.parse(rec.SUGGESTED_ACTIONS) : [],
        relatedEntityId: rec.RELATED_ENTITY_ID,
        relatedEntityType: rec.RELATED_ENTITY_TYPE,
        createdAt: rec.CREATED_AT,
        expiresAt: rec.EXPIRES_AT,
        status: rec.STATUS
      }));
    },
    
    // Get a specific recommendation by ID
    recommendation: async (_, { id }) => {
      const query = `
        SELECT 
          RECOMMENDATION_ID as id,
          RECOMMENDATION_TYPE as type,
          TITLE,
          DESCRIPTION,
          IMPACT,
          CONFIDENCE,
          SUGGESTED_ACTIONS,
          RELATED_ENTITY_ID,
          RELATED_ENTITY_TYPE,
          CREATED_AT,
          EXPIRES_AT,
          STATUS
        FROM MERCURIOS_DATA.ANALYTICS.BUSINESS_RECOMMENDATIONS
        WHERE RECOMMENDATION_ID = :id
      `;
      
      const results = await executeSnowflakeQuery(query, { id });
      
      if (results.length === 0) {
        return null;
      }
      
      const rec = results[0];
      return {
        id: rec.ID,
        type: rec.TYPE,
        title: rec.TITLE,
        description: rec.DESCRIPTION,
        impact: parseFloat(rec.IMPACT),
        confidence: parseFloat(rec.CONFIDENCE),
        suggestedActions: rec.SUGGESTED_ACTIONS ? JSON.parse(rec.SUGGESTED_ACTIONS) : [],
        relatedEntityId: rec.RELATED_ENTITY_ID,
        relatedEntityType: rec.RELATED_ENTITY_TYPE,
        createdAt: rec.CREATED_AT,
        expiresAt: rec.EXPIRES_AT,
        status: rec.STATUS
      };
    },
    
    // Get top recommendations with optional limit
    topRecommendations: async (_, { limit = 3 }) => {
      const query = `
        SELECT 
          RECOMMENDATION_ID as id,
          RECOMMENDATION_TYPE as type,
          TITLE,
          DESCRIPTION,
          IMPACT,
          CONFIDENCE,
          SUGGESTED_ACTIONS,
          RELATED_ENTITY_ID,
          RELATED_ENTITY_TYPE,
          CREATED_AT,
          EXPIRES_AT,
          STATUS
        FROM MERCURIOS_DATA.ANALYTICS.BUSINESS_RECOMMENDATIONS
        WHERE STATUS = 'ACTIVE'
        ORDER BY IMPACT DESC, CONFIDENCE DESC
        LIMIT :limit
      `;
      
      const results = await executeSnowflakeQuery(query, { limit });
      
      return results.map(rec => ({
        id: rec.ID,
        type: rec.TYPE,
        title: rec.TITLE,
        description: rec.DESCRIPTION,
        impact: parseFloat(rec.IMPACT),
        confidence: parseFloat(rec.CONFIDENCE),
        suggestedActions: rec.SUGGESTED_ACTIONS ? JSON.parse(rec.SUGGESTED_ACTIONS) : [],
        relatedEntityId: rec.RELATED_ENTITY_ID,
        relatedEntityType: rec.RELATED_ENTITY_TYPE,
        createdAt: rec.CREATED_AT,
        expiresAt: rec.EXPIRES_AT,
        status: rec.STATUS
      }));
    },
    
    // Get inventory-specific recommendations
    inventoryRecommendations: async () => {
      const query = `
        SELECT 
          p.PRODUCT_ID,
          p.PRODUCT_NAME,
          i.CURRENT_STOCK,
          i.REORDER_POINT,
          i.DAYS_OF_SUPPLY,
          CASE 
            WHEN i.CURRENT_STOCK < i.REORDER_POINT THEN 'RESTOCK'
            WHEN i.DAYS_OF_SUPPLY > 90 THEN 'REDUCE_INVENTORY'
            ELSE 'OPTIMAL'
          END as RECOMMENDATION_TYPE,
          CASE 
            WHEN i.CURRENT_STOCK < i.REORDER_POINT THEN 'Inventory level below reorder point. Consider restocking soon.'
            WHEN i.DAYS_OF_SUPPLY > 90 THEN 'Excess inventory detected. Consider promotions to reduce stock.'
            ELSE 'Inventory levels are optimal.'
          END as RECOMMENDATION_TEXT,
          CASE 
            WHEN i.CURRENT_STOCK < i.REORDER_POINT THEN i.REORDER_QUANTITY
            WHEN i.DAYS_OF_SUPPLY > 90 THEN i.CURRENT_STOCK - (i.CURRENT_STOCK * 0.7)
            ELSE 0
          END as RECOMMENDED_ACTION_VALUE,
          CASE 
            WHEN i.CURRENT_STOCK < i.REORDER_POINT THEN 0.8
            WHEN i.DAYS_OF_SUPPLY > 90 THEN 0.6
            ELSE 0.3
          END as IMPACT,
          0.9 as CONFIDENCE
        FROM MERCURIOS_DATA.ANALYTICS.INVENTORY_STATUS i
        JOIN MERCURIOS_DATA.STANDARD.PRODUCTS p ON i.PRODUCT_ID = p.PRODUCT_ID
        WHERE i.CURRENT_STOCK < i.REORDER_POINT OR i.DAYS_OF_SUPPLY > 90
        ORDER BY IMPACT DESC, CONFIDENCE DESC
      `;
      
      const results = await executeSnowflakeQuery(query);
      
      return results.map(rec => ({
        productId: rec.PRODUCT_ID,
        productName: rec.PRODUCT_NAME,
        currentStock: parseInt(rec.CURRENT_STOCK),
        reorderPoint: parseInt(rec.REORDER_POINT),
        daysOfSupply: parseInt(rec.DAYS_OF_SUPPLY),
        recommendationType: rec.RECOMMENDATION_TYPE,
        recommendationText: rec.RECOMMENDATION_TEXT,
        recommendedActionValue: parseInt(rec.RECOMMENDED_ACTION_VALUE),
        impact: parseFloat(rec.IMPACT),
        confidence: parseFloat(rec.CONFIDENCE)
      }));
    },
    
    // Get customer-specific recommendations
    customerRecommendations: async () => {
      const query = `
        WITH customer_metrics AS (
          SELECT 
            c.CUSTOMER_ID,
            c.CUSTOMER_NAME,
            c.SEGMENT,
            MAX(o.ORDER_DATE) as LAST_PURCHASE_DATE,
            DATEDIFF('day', MAX(o.ORDER_DATE), CURRENT_DATE()) as DAYS_SINCE_LAST_PURCHASE,
            AVG(o.TOTAL_AMOUNT) as AVG_ORDER_VALUE,
            COUNT(o.ORDER_ID) as ORDER_COUNT
          FROM MERCURIOS_DATA.STANDARD.CUSTOMERS c
          JOIN MERCURIOS_DATA.STANDARD.ORDERS o ON c.CUSTOMER_ID = o.CUSTOMER_ID
          GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME, c.SEGMENT
        )
        SELECT 
          CUSTOMER_ID,
          CUSTOMER_NAME,
          SEGMENT,
          LAST_PURCHASE_DATE,
          CASE 
            WHEN DAYS_SINCE_LAST_PURCHASE > 90 AND ORDER_COUNT > 5 THEN 'REACTIVATION'
            WHEN SEGMENT = 'VIP' AND DAYS_SINCE_LAST_PURCHASE > 30 THEN 'ENGAGEMENT'
            WHEN AVG_ORDER_VALUE > 500 THEN 'UPSELL'
            ELSE 'NURTURE'
          END as RECOMMENDATION_TYPE,
          CASE 
            WHEN DAYS_SINCE_LAST_PURCHASE > 90 AND ORDER_COUNT > 5 THEN 'This customer has not purchased in over 90 days. Consider a win-back campaign.'
            WHEN SEGMENT = 'VIP' AND DAYS_SINCE_LAST_PURCHASE > 30 THEN 'VIP customer has not engaged recently. Consider a personalized outreach.'
            WHEN AVG_ORDER_VALUE > 500 THEN 'High-value customer with potential for premium products.'
            ELSE 'Regular customer that should be included in nurture campaigns.'
          END as RECOMMENDATION_TEXT,
          AVG_ORDER_VALUE * 1.2 as POTENTIAL_VALUE,
          CASE 
            WHEN DAYS_SINCE_LAST_PURCHASE > 90 AND ORDER_COUNT > 5 THEN 0.7
            WHEN SEGMENT = 'VIP' AND DAYS_SINCE_LAST_PURCHASE > 30 THEN 0.8
            WHEN AVG_ORDER_VALUE > 500 THEN 0.6
            ELSE 0.4
          END as IMPACT,
          0.85 as CONFIDENCE
        FROM customer_metrics
        WHERE 
          (DAYS_SINCE_LAST_PURCHASE > 90 AND ORDER_COUNT > 5) OR
          (SEGMENT = 'VIP' AND DAYS_SINCE_LAST_PURCHASE > 30) OR
          (AVG_ORDER_VALUE > 500)
        ORDER BY IMPACT DESC, POTENTIAL_VALUE DESC
      `;
      
      const results = await executeSnowflakeQuery(query);
      
      return results.map(rec => ({
        customerId: rec.CUSTOMER_ID,
        customerName: rec.CUSTOMER_NAME,
        segment: rec.SEGMENT,
        lastPurchaseDate: rec.LAST_PURCHASE_DATE,
        recommendationType: rec.RECOMMENDATION_TYPE,
        recommendationText: rec.RECOMMENDATION_TEXT,
        potentialValue: parseFloat(rec.POTENTIAL_VALUE),
        impact: parseFloat(rec.IMPACT),
        confidence: parseFloat(rec.CONFIDENCE)
      }));
    },
    
    // Get pricing-specific recommendations
    pricingRecommendations: async () => {
      const query = `
        WITH product_metrics AS (
          SELECT 
            p.PRODUCT_ID,
            p.PRODUCT_NAME,
            p.CURRENT_PRICE,
            AVG(oi.UNIT_PRICE) as AVG_SOLD_PRICE,
            COUNT(oi.ORDER_ITEM_ID) as SALES_COUNT,
            SUM(oi.QUANTITY) as TOTAL_QUANTITY,
            p.COST_PRICE,
            (p.CURRENT_PRICE - p.COST_PRICE) / p.COST_PRICE as CURRENT_MARGIN
          FROM MERCURIOS_DATA.STANDARD.PRODUCTS p
          JOIN MERCURIOS_DATA.STANDARD.ORDER_ITEMS oi ON p.PRODUCT_ID = oi.PRODUCT_ID
          GROUP BY p.PRODUCT_ID, p.PRODUCT_NAME, p.CURRENT_PRICE, p.COST_PRICE
        )
        SELECT 
          PRODUCT_ID,
          PRODUCT_NAME,
          CURRENT_PRICE,
          CASE 
            WHEN CURRENT_MARGIN < 0.2 AND SALES_COUNT > 100 THEN ROUND(CURRENT_PRICE * 1.1, 2)
            WHEN CURRENT_MARGIN > 0.5 AND SALES_COUNT < 20 THEN ROUND(CURRENT_PRICE * 0.9, 2)
            ELSE CURRENT_PRICE
          END as RECOMMENDED_PRICE,
          CASE 
            WHEN CURRENT_MARGIN < 0.2 AND SALES_COUNT > 100 THEN 'INCREASE_PRICE'
            WHEN CURRENT_MARGIN > 0.5 AND SALES_COUNT < 20 THEN 'DECREASE_PRICE'
            ELSE 'MAINTAIN_PRICE'
          END as RECOMMENDATION_TYPE,
          CASE 
            WHEN CURRENT_MARGIN < 0.2 AND SALES_COUNT > 100 THEN 'Popular product with low margin. Consider increasing price.'
            WHEN CURRENT_MARGIN > 0.5 AND SALES_COUNT < 20 THEN 'High margin but low sales. Consider decreasing price to boost volume.'
            ELSE 'Price is optimal for current market conditions.'
          END as RECOMMENDATION_TEXT,
          CASE 
            WHEN CURRENT_MARGIN < 0.2 AND SALES_COUNT > 100 THEN (ROUND(CURRENT_PRICE * 1.1, 2) - CURRENT_PRICE) * TOTAL_QUANTITY
            WHEN CURRENT_MARGIN > 0.5 AND SALES_COUNT < 20 THEN (SALES_COUNT * 1.5) * (CURRENT_PRICE * 0.9)
            ELSE 0
          END as POTENTIAL_REVENUE,
          CASE 
            WHEN CURRENT_MARGIN < 0.2 AND SALES_COUNT > 100 THEN 0.75
            WHEN CURRENT_MARGIN > 0.5 AND SALES_COUNT < 20 THEN 0.65
            ELSE 0.3
          END as IMPACT,
          0.8 as CONFIDENCE
        FROM product_metrics
        WHERE 
          (CURRENT_MARGIN < 0.2 AND SALES_COUNT > 100) OR
          (CURRENT_MARGIN > 0.5 AND SALES_COUNT < 20)
        ORDER BY IMPACT DESC, POTENTIAL_REVENUE DESC
      `;
      
      const results = await executeSnowflakeQuery(query);
      
      return results.map(rec => ({
        productId: rec.PRODUCT_ID,
        productName: rec.PRODUCT_NAME,
        currentPrice: parseFloat(rec.CURRENT_PRICE),
        recommendedPrice: parseFloat(rec.RECOMMENDED_PRICE),
        recommendationType: rec.RECOMMENDATION_TYPE,
        recommendationText: rec.RECOMMENDATION_TEXT,
        potentialRevenue: parseFloat(rec.POTENTIAL_REVENUE),
        impact: parseFloat(rec.IMPACT),
        confidence: parseFloat(rec.CONFIDENCE)
      }));
    }
  },
  
  Mutation: {
    // Mark a recommendation as implemented
    implementRecommendation: async (_, { id }) => {
      const query = `
        UPDATE MERCURIOS_DATA.ANALYTICS.BUSINESS_RECOMMENDATIONS
        SET STATUS = 'IMPLEMENTED', UPDATED_AT = CURRENT_TIMESTAMP()
        WHERE RECOMMENDATION_ID = :id
        RETURNING *
      `;
      
      const results = await executeSnowflakeQuery(query, { id });
      
      if (results.length === 0) {
        throw new Error(`Recommendation with ID ${id} not found`);
      }
      
      const rec = results[0];
      return {
        id: rec.RECOMMENDATION_ID,
        type: rec.RECOMMENDATION_TYPE,
        title: rec.TITLE,
        description: rec.DESCRIPTION,
        impact: parseFloat(rec.IMPACT),
        confidence: parseFloat(rec.CONFIDENCE),
        suggestedActions: rec.SUGGESTED_ACTIONS ? JSON.parse(rec.SUGGESTED_ACTIONS) : [],
        relatedEntityId: rec.RELATED_ENTITY_ID,
        relatedEntityType: rec.RELATED_ENTITY_TYPE,
        createdAt: rec.CREATED_AT,
        expiresAt: rec.EXPIRES_AT,
        status: rec.STATUS
      };
    },
    
    // Dismiss a recommendation
    dismissRecommendation: async (_, { id }) => {
      const query = `
        UPDATE MERCURIOS_DATA.ANALYTICS.BUSINESS_RECOMMENDATIONS
        SET STATUS = 'DISMISSED', UPDATED_AT = CURRENT_TIMESTAMP()
        WHERE RECOMMENDATION_ID = :id
        RETURNING *
      `;
      
      const results = await executeSnowflakeQuery(query, { id });
      
      if (results.length === 0) {
        throw new Error(`Recommendation with ID ${id} not found`);
      }
      
      const rec = results[0];
      return {
        id: rec.RECOMMENDATION_ID,
        type: rec.RECOMMENDATION_TYPE,
        title: rec.TITLE,
        description: rec.DESCRIPTION,
        impact: parseFloat(rec.IMPACT),
        confidence: parseFloat(rec.CONFIDENCE),
        suggestedActions: rec.SUGGESTED_ACTIONS ? JSON.parse(rec.SUGGESTED_ACTIONS) : [],
        relatedEntityId: rec.RELATED_ENTITY_ID,
        relatedEntityType: rec.RELATED_ENTITY_TYPE,
        createdAt: rec.CREATED_AT,
        expiresAt: rec.EXPIRES_AT,
        status: rec.STATUS
      };
    },
    
    // Rate a recommendation's helpfulness
    rateRecommendation: async (_, { id, helpful }) => {
      const query = `
        UPDATE MERCURIOS_DATA.ANALYTICS.BUSINESS_RECOMMENDATIONS
        SET FEEDBACK = :feedback, UPDATED_AT = CURRENT_TIMESTAMP()
        WHERE RECOMMENDATION_ID = :id
        RETURNING *
      `;
      
      const results = await executeSnowflakeQuery(query, { 
        id, 
        feedback: helpful ? 'HELPFUL' : 'NOT_HELPFUL' 
      });
      
      if (results.length === 0) {
        throw new Error(`Recommendation with ID ${id} not found`);
      }
      
      const rec = results[0];
      return {
        id: rec.RECOMMENDATION_ID,
        type: rec.RECOMMENDATION_TYPE,
        title: rec.TITLE,
        description: rec.DESCRIPTION,
        impact: parseFloat(rec.IMPACT),
        confidence: parseFloat(rec.CONFIDENCE),
        suggestedActions: rec.SUGGESTED_ACTIONS ? JSON.parse(rec.SUGGESTED_ACTIONS) : [],
        relatedEntityId: rec.RELATED_ENTITY_ID,
        relatedEntityType: rec.RELATED_ENTITY_TYPE,
        createdAt: rec.CREATED_AT,
        expiresAt: rec.EXPIRES_AT,
        status: rec.STATUS
      };
    }
  }
};

module.exports = resolvers;
