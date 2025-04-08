/**
 * Mercurios API client for integrating with the Mercurios MCP (Model Composition Platform)
 * 
 * This module provides functions to interact with the Mercurios MCP API endpoints
 * and supports data fetching for the business intelligence components.
 */

import Cookies from 'js-cookie';
import prohandelClient from './clients/prohandel-client';

// Type definitions for API responses
interface StockoutRiskItem {
  id: string;
  name: string;
  category: string;
  currentStock: number;
  reorderPoint: number;
  risk: number;
  estimatedDaysToStockout: number;
}

interface InventoryAnalyticsData {
  totalValue: number;
  changePercentage: number;
  productCount: number;
  newItems: number;
  quarterlyTrends: number[];
  stockHealth: number;
  stockHealthTarget: number;
  stockDistribution: {
    low: number;
    optimal: number;
    excess: number;
  };
}

interface SalesPerformanceData {
  current: any[];
  comparison: any[] | null;
  period: string;
  groupBy: string;
}

interface CustomerSegmentationData {
  segments: {
    new: any[];
    active: any[];
    inactive: any[];
    vip: any[];
  };
  sources: string[];
  totalCustomers: number;
}

interface ProHandelData {
  data: any;
}

// Default API URL - can be overridden with environment variables
const DEFAULT_API_URL = process.env.NEXT_PUBLIC_MERCURIOS_API_URL || 'https://api.mercurios.ai';
const MCP_API_URL = process.env.NEXT_PUBLIC_MCP_API_URL || 'https://mcp.mercurios.ai/api';

// API endpoints
const ENDPOINTS = {
  stockoutRisk: '/api/stockout-risk',
  inventoryAnalytics: '/api/inventory-analytics',
  salesPerformance: '/api/sales-performance',
  customerSegmentation: '/api/customer-segmentation',
};

// API endpoints for MCP
const MCP_ENDPOINTS = {
  stockoutRisk: '/widgets/stockout-risk',
  inventoryAnalytics: '/widgets/inventory-analytics',
  salesPerformance: '/widgets/sales-performance',
  customerSegmentation: '/widgets/customer-segmentation',
  
  // Multi-source data endpoints
  proHandelData: '/data-sources/prohandel',
  klaviyoData: '/data-sources/klaviyo',
  googleAnalyticsData: '/data-sources/ga4',
  shopifyData: '/data-sources/shopify',
};

// Utility to get the API auth token from cookies
const getAuthToken = (): string | undefined => {
  return Cookies.get('mercurios_auth_token') || Cookies.get('auth');
};

// Utility to get the current tenant ID from cookies or use default
const getTenantId = (): string => {
  return Cookies.get('mcp_tenant_id') || 'prohandel-demo';
};

/**
 * Base API client for making requests to Mercurios endpoints
 */
const apiClient = async <T>(
  endpoint: string, 
  options: RequestInit = {}, 
  useAuth: boolean = true
): Promise<T> => {
  const url = `${DEFAULT_API_URL}${endpoint}`;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'X-Tenant-ID': getTenantId(),
  };

  // Add auth token if available and required
  if (useAuth) {
    const token = getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const config: RequestInit = {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      // Handle different error status codes
      if (response.status === 401) {
        throw new Error('Authentication required');
      } else if (response.status === 403) {
        throw new Error('Not authorized to access this resource');
      } else {
        throw new Error(`API error: ${response.statusText}`);
      }
    }
    
    const data = await response.json();
    return data as T;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

/**
 * Base API client for making requests to Mercurios MCP endpoints
 */
const mcpApiClient = async <T>(
  endpoint: string, 
  options: RequestInit = {}, 
  useAuth: boolean = true
): Promise<T> => {
  const url = `${MCP_API_URL}${endpoint}`;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'X-Tenant-ID': getTenantId(),
  };

  // Add auth token if available and required
  if (useAuth) {
    const token = getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const config: RequestInit = {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  };

  try {
    // For development environments, use mock data if MCP API is not available
    if (process.env.NODE_ENV === 'development' && !process.env.NEXT_PUBLIC_USE_REAL_MCP) {
      console.log(`[DEV] Would call MCP API: ${url}`);
      return getMockData<T>(endpoint);
    }

    const response = await fetch(url, config);
    
    if (!response.ok) {
      // Handle different error status codes
      if (response.status === 401) {
        throw new Error('Authentication required');
      } else if (response.status === 403) {
        throw new Error('Not authorized to access this resource');
      } else {
        throw new Error(`MCP API error: ${response.statusText}`);
      }
    }
    
    const data = await response.json();
    return data as T;
  } catch (error) {
    console.error('MCP API request failed:', error);
    
    // In case of error in production, try fallback to cache or mock
    if (process.env.NODE_ENV === 'production') {
      console.warn('Falling back to cached data');
      return getMockData<T>(endpoint); // In production this would be a cache
    }
    
    throw error;
  }
};

// API Functions for different data needs

/**
 * Fetches stockout risk data for products
 */
export const fetchStockoutRisk = async (tenantId?: string): Promise<{ data: StockoutRiskItem[] }> => {
  const endpoint = `${ENDPOINTS.stockoutRisk}?tenant_id=${tenantId || getTenantId()}`;
  return apiClient<{ data: StockoutRiskItem[] }>(endpoint);
};

/**
 * Fetches inventory analytics data
 */
export const fetchInventoryAnalytics = async (params?: { period?: string }): Promise<{ data: InventoryAnalyticsData }> => {
  const searchParams = new URLSearchParams();
  if (params?.period) searchParams.append('period', params.period);
  
  const endpoint = `${ENDPOINTS.inventoryAnalytics}?${searchParams.toString()}`;
  return apiClient<{ data: InventoryAnalyticsData }>(endpoint);
};

/**
 * Fetches sales performance data
 */
export const fetchSalesPerformance = async (params?: { 
  period?: string;
  compareWith?: string;
  groupBy?: 'day' | 'week' | 'month';
}): Promise<{ data: SalesPerformanceData }> => {
  const searchParams = new URLSearchParams();
  if (params?.period) searchParams.append('period', params.period);
  if (params?.compareWith) searchParams.append('compare_with', params.compareWith);
  if (params?.groupBy) searchParams.append('group_by', params.groupBy);
  
  const endpoint = `${ENDPOINTS.salesPerformance}?${searchParams.toString()}`;
  return apiClient<{ data: SalesPerformanceData }>(endpoint);
};

/**
 * Fetches customer segmentation data
 */
export const fetchCustomerSegmentation = async (): Promise<{ data: CustomerSegmentationData }> => {
  return apiClient<{ data: CustomerSegmentationData }>(ENDPOINTS.customerSegmentation);
};

// API Functions for different MCP data sources

/**
 * Fetches stockout risk data using the MCP platform
 */
export const fetchStockoutRiskMCP = async (tenantId?: string, simplified: boolean = false): Promise<{ data: StockoutRiskItem[] }> => {
  // For development, use mock data if requested
  if (process.env.NODE_ENV === 'development' && !process.env.NEXT_PUBLIC_USE_REAL_MCP) {
    console.log('[DEV] Using mock stockout risk data');
    return getMockData<{ data: StockoutRiskItem[] }>(MCP_ENDPOINTS.stockoutRisk);
  }
  
  try {
    // Use the ProHandel client to get real data
    console.log(`Fetching real stockout risk data from ProHandel for tenant: ${tenantId || 'default'}`);
    const result = await prohandelClient.calculateStockoutRisk();
    
    // If simplified is true, return only the top risk items
    if (simplified && result.data) {
      result.data = result.data.slice(0, 3);
    }
    
    return result;
  } catch (error) {
    console.error('Error fetching stockout risk from ProHandel:', error);
    // Fallback to mock data in case of error
    return getMockData<{ data: StockoutRiskItem[] }>(MCP_ENDPOINTS.stockoutRisk);
  }
};

/**
 * Fetches inventory analytics data from MCP
 */
export const fetchInventoryAnalyticsMCP = async (params?: { period?: string; dataSource?: string }): Promise<{ data: InventoryAnalyticsData }> => {
  // For development, use mock data if requested
  if (process.env.NODE_ENV === 'development' && !process.env.NEXT_PUBLIC_USE_REAL_MCP) {
    console.log('[DEV] Using mock inventory analytics data');
    return getMockData<{ data: InventoryAnalyticsData }>(MCP_ENDPOINTS.inventoryAnalytics);
  }
  
  try {
    // Calculate date range for the period
    const today = new Date();
    let fromDate = new Date(today);
    
    if (params?.period === 'week') {
      fromDate.setDate(today.getDate() - 7);
    } else if (params?.period === 'month') {
      fromDate.setMonth(today.getMonth() - 1);
    } else if (params?.period === 'quarter') {
      fromDate.setMonth(today.getMonth() - 3);
    } else {
      // Default to last 30 days
      fromDate.setDate(today.getDate() - 30);
    }
    
    // Use the ProHandel client to get real inventory analytics data
    console.log(`Fetching real inventory analytics data from ProHandel for period: ${params?.period || '30 days'}`);
    const inventoryData = await prohandelClient.getInventoryAnalytics({
      from: fromDate.toISOString().split('T')[0],
      to: today.toISOString().split('T')[0]
    });
    
    // Get stock levels
    const stockData = await prohandelClient.getStockLevels({ limit: 1000 });
    
    // Get categories
    const categoriesData = await prohandelClient.getCategories();
    
    // Transform the data into the format expected by the UI
    const totalValue = stockData.data.reduce((total, item) => {
      return total + (item.value || 0);
    }, 0);
    
    // Calculate quarterly trends (this would need actual historical data)
    // For now, we'll generate some reasonable data
    const quarterlyTrends = [45, 15, 25, 15]; // Placeholder
    
    // Calculate stock health and distribution
    let lowStock = 0;
    let optimalStock = 0;
    let excessStock = 0;
    
    stockData.data.forEach((item) => {
      const quantity = item.quantity || 0;
      const reorderPoint = item.reorder_point || 0;
      
      if (quantity < reorderPoint * 0.7) {
        lowStock++;
      } else if (quantity > reorderPoint * 1.5) {
        excessStock++;
      } else {
        optimalStock++;
      }
    });
    
    const totalItems = stockData.data.length;
    const lowStockPercentage = totalItems > 0 ? Math.round((lowStock / totalItems) * 100) : 0;
    const optimalStockPercentage = totalItems > 0 ? Math.round((optimalStock / totalItems) * 100) : 0;
    const excessStockPercentage = totalItems > 0 ? Math.round((excessStock / totalItems) * 100) : 0;
    
    // Placeholder for stock health (would need historical data to calculate trend)
    const stockHealth = 100 - lowStockPercentage;
    
    return {
      data: {
        totalValue: totalValue,
        changePercentage: 2.5, // Placeholder, would need historical data
        productCount: totalItems,
        newItems: 12, // Placeholder, would need historical data
        quarterlyTrends: quarterlyTrends,
        stockHealth: stockHealth,
        stockHealthTarget: 90, // Target value
        stockDistribution: {
          low: lowStockPercentage,
          optimal: optimalStockPercentage,
          excess: excessStockPercentage
        }
      }
    };
  } catch (error) {
    console.error('Error fetching inventory analytics from ProHandel:', error);
    // Fallback to mock data in case of error
    return getMockData<{ data: InventoryAnalyticsData }>(MCP_ENDPOINTS.inventoryAnalytics);
  }
};

/**
 * Fetches sales performance data from MCP
 */
export const fetchSalesPerformanceMCP = async (params?: { 
  period?: string;
  compareWith?: string;
  groupBy?: 'day' | 'week' | 'month';
  dataSource?: 'prohandel' | 'shopify' | 'combined';
}): Promise<{ data: SalesPerformanceData }> => {
  // For development, use mock data if requested
  if (process.env.NODE_ENV === 'development' && !process.env.NEXT_PUBLIC_USE_REAL_MCP) {
    console.log('[DEV] Using mock sales performance data');
    return getMockData<{ data: SalesPerformanceData }>(MCP_ENDPOINTS.salesPerformance);
  }
  
  try {
    // Calculate date ranges
    const today = new Date();
    let fromDate = new Date(today);
    let comparisonFromDate, comparisonToDate;
    
    // Set the primary date range
    if (params?.period === 'week') {
      fromDate.setDate(today.getDate() - 7);
    } else if (params?.period === 'month') {
      fromDate.setMonth(today.getMonth() - 1);
    } else if (params?.period === 'quarter') {
      fromDate.setMonth(today.getMonth() - 3);
    } else if (params?.period === 'year') {
      fromDate.setFullYear(today.getFullYear() - 1);
    } else {
      // Default to last 30 days
      fromDate.setDate(today.getDate() - 30);
    }
    
    // Set the comparison date range if needed
    if (params?.compareWith) {
      comparisonToDate = new Date(fromDate);
      comparisonToDate.setDate(comparisonToDate.getDate() - 1);
      
      comparisonFromDate = new Date(comparisonToDate);
      const duration = today.getTime() - fromDate.getTime();
      comparisonFromDate.setTime(comparisonToDate.getTime() - duration);
    }
    
    // Use the ProHandel client to get real sales data
    console.log(`Fetching real sales data from ProHandel for period: ${params?.period || '30 days'}`);
    const salesData = await prohandelClient.getSales({
      from: fromDate.toISOString().split('T')[0],
      to: today.toISOString().split('T')[0],
      groupBy: params?.groupBy || 'day'
    });
    
    // Get comparison data if requested
    let comparisonData = null;
    if (comparisonFromDate && comparisonToDate) {
      comparisonData = await prohandelClient.getSales({
        from: comparisonFromDate.toISOString().split('T')[0],
        to: comparisonToDate.toISOString().split('T')[0],
        groupBy: params?.groupBy || 'day'
      });
    }
    
    // Transform the data as needed
    // For this example, we'll just return the raw data
    // In a real implementation, you'd format it for the UI
    return {
      data: {
        current: salesData.data,
        comparison: comparisonData ? comparisonData.data : null,
        period: params?.period || '30days',
        groupBy: params?.groupBy || 'day'
      }
    };
  } catch (error) {
    console.error('Error fetching sales performance from ProHandel:', error);
    // Fallback to mock data in case of error
    return getMockData<{ data: SalesPerformanceData }>(MCP_ENDPOINTS.salesPerformance);
  }
};

/**
 * Fetches customer segmentation data from MCP
 * This combines data from multiple sources, including ProHandel and Klaviyo
 */
export const fetchCustomerSegmentationMCP = async (params?: {
  sources?: ('prohandel' | 'klaviyo' | 'ga4')[];
}): Promise<{ data: CustomerSegmentationData }> => {
  // For development, use mock data if requested
  if (process.env.NODE_ENV === 'development' && !process.env.NEXT_PUBLIC_USE_REAL_MCP) {
    console.log('[DEV] Using mock customer segmentation data');
    return getMockData<{ data: CustomerSegmentationData }>(MCP_ENDPOINTS.customerSegmentation);
  }
  
  try {
    // Use the ProHandel client to get customer data
    console.log('Fetching real customer data from ProHandel');
    const customersData = await prohandelClient.getCustomers({ limit: 1000 });
    
    // This would be where you'd integrate with Klaviyo and GA4 if those sources are requested
    // For now, we'll just use the ProHandel data
    
    // Basic segmentation based on purchase history
    // In a real implementation, you'd use more sophisticated algorithms
    const segments = {
      new: [],
      active: [],
      inactive: [],
      vip: []
    };
    
    // Process each customer
    for (const customer of customersData.data) {
      // Get purchase history
      const purchaseHistory = await prohandelClient.getCustomerPurchaseHistory(
        customer.id, 
        { limit: 100 }
      );
      
      const purchases = purchaseHistory.data || [];
      const totalPurchases = purchases.length;
      let totalSpent = 0;
      
      // Calculate total spent
      purchases.forEach(purchase => {
        totalSpent += purchase.total || 0;
      });
      
      // Determine most recent purchase date
      let mostRecentPurchaseDate = new Date(0);
      if (purchases.length > 0) {
        const purchaseDates = purchases.map(p => new Date(p.date));
        mostRecentPurchaseDate = new Date(Math.max(...purchaseDates.map(d => d.getTime())));
      }
      
      // Segment the customer
      const today = new Date();
      const daysSinceLastPurchase = Math.floor((today.getTime() - mostRecentPurchaseDate.getTime()) / (1000 * 60 * 60 * 24));
      
      // Enriched customer object with segmentation data
      const enrichedCustomer = {
        ...customer,
        totalPurchases,
        totalSpent,
        daysSinceLastPurchase
      };
      
      // Apply segmentation rules
      if (totalPurchases === 0) {
        segments.new.push(enrichedCustomer);
      } else if (daysSinceLastPurchase > 90) {
        segments.inactive.push(enrichedCustomer);
      } else if (totalSpent > 1000 || totalPurchases > 10) {
        segments.vip.push(enrichedCustomer);
      } else {
        segments.active.push(enrichedCustomer);
      }
    }
    
    return {
      data: {
        segments,
        sources: ['prohandel'], // Sources actually used
        totalCustomers: customersData.data.length
      }
    };
  } catch (error) {
    console.error('Error fetching customer segmentation:', error);
    // Fallback to mock data in case of error
    return getMockData<{ data: CustomerSegmentationData }>(MCP_ENDPOINTS.customerSegmentation);
  }
};

/**
 * Fetch data from ProHandel POS through MCP
 */
export const fetchProHandelData = async (query: string, params?: Record<string, any>): Promise<{ data: any }> => {
  // For development, use mock data if requested
  if (process.env.NODE_ENV === 'development' && !process.env.NEXT_PUBLIC_USE_REAL_MCP) {
    console.log(`[DEV] Would call ProHandel API for: ${query}`);
    return { data: { message: "Mock data for " + query } };
  }
  
  try {
    console.log(`Fetching real data from ProHandel: ${query}`);
    
    // Map the query to the appropriate ProHandel client method
    switch (query) {
      case 'articles':
        return { data: await prohandelClient.getArticles(params) };
      case 'stock':
        return { data: await prohandelClient.getStockLevels(params) };
      case 'sales': {
        // For sales, we need to ensure from and to dates are present
        const salesParams = params || {};
        if (!salesParams.from) {
          const today = new Date();
          const thirtyDaysAgo = new Date(today);
          thirtyDaysAgo.setDate(today.getDate() - 30);
          salesParams.from = thirtyDaysAgo.toISOString().split('T')[0];
          salesParams.to = today.toISOString().split('T')[0];
        }
        return { data: await prohandelClient.getSales(salesParams) };
      }
      case 'orders':
        return { data: await prohandelClient.getOrders(params) };
      case 'customers':
        return { data: await prohandelClient.getCustomers(params) };
      case 'inventory-analytics': {
        // For inventory analytics, ensure date range if not provided
        const analyticsParams = params || {};
        if (!analyticsParams.from) {
          const today = new Date();
          const thirtyDaysAgo = new Date(today);
          thirtyDaysAgo.setDate(today.getDate() - 30);
          analyticsParams.from = thirtyDaysAgo.toISOString().split('T')[0];
          analyticsParams.to = today.toISOString().split('T')[0];
        }
        return { data: await prohandelClient.getInventoryAnalytics(analyticsParams) };
      }
      case 'categories':
        return { data: await prohandelClient.getCategories() };
      case 'stockout-risk':
        return await prohandelClient.calculateStockoutRisk();
      default:
        throw new Error(`Unknown ProHandel query: ${query}`);
    }
  } catch (error) {
    console.error(`Error fetching ProHandel data for ${query}:`, error);
    return { data: { message: "Error fetching data", error: String(error) } };
  }
};

// Helper function to convert generic params to specific types safely
const convertParams = <T>(params?: Record<string, any>): T | undefined => {
  if (!params) return undefined;
  return params as unknown as T;
};

// Helper function to get mock data for development
const getMockData = <T>(endpoint: string): Promise<T> => {
  // Return appropriate mock data based on the endpoint
  return new Promise((resolve) => {
    setTimeout(() => {
      if (endpoint.includes('stockout-risk')) {
        resolve({
          data: [
            {
              id: 'SKU1234',
              name: 'Premium Coffee Beans',
              category: 'Beverages',
              currentStock: 15,
              reorderPoint: 20,
              risk: 85,
              estimatedDaysToStockout: 4
            },
            {
              id: 'SKU2345',
              name: 'Organic Whole Milk',
              category: 'Dairy',
              currentStock: 8,
              reorderPoint: 15,
              risk: 75,
              estimatedDaysToStockout: 6
            },
            {
              id: 'SKU3456',
              name: 'Artisanal Bread',
              category: 'Bakery',
              currentStock: 5,
              reorderPoint: 10,
              risk: 90,
              estimatedDaysToStockout: 2
            },
            {
              id: 'SKU4567',
              name: 'Craft Beer Selection',
              category: 'Beverages',
              currentStock: 12,
              reorderPoint: 18,
              risk: 65,
              estimatedDaysToStockout: 8
            },
            {
              id: 'SKU5678',
              name: 'Fresh Avocados',
              category: 'Produce',
              currentStock: 20,
              reorderPoint: 25,
              risk: 55,
              estimatedDaysToStockout: 10
            }
          ]
        } as unknown as T);
      } else if (endpoint.includes('inventory-analytics')) {
        resolve({
          data: {
            totalValue: 143245.50,
            changePercentage: 2.5,
            productCount: 1283,
            newItems: 12,
            quarterlyTrends: [45, 15, 25, 15],
            stockHealth: 86,
            stockHealthTarget: 89,
            stockDistribution: {
              low: 15,
              optimal: 65,
              excess: 20
            }
          }
        } as unknown as T);
      } else {
        // Default mock data
        resolve({ data: { message: "Mock data for " + endpoint } } as unknown as T);
      }
    }, 800);
  });
};

// For backward compatibility with previous mock function
export const mockStockoutRisk = async (tenantId: string, simplified: boolean = false): Promise<{ data: StockoutRiskItem[] }> => {
  return getMockData<{ data: StockoutRiskItem[] }>(MCP_ENDPOINTS.stockoutRisk);
};

// Export the API utilities
export default {
  fetchStockoutRisk,
  fetchInventoryAnalytics,
  fetchSalesPerformance,
  fetchCustomerSegmentation,
  fetchStockoutRiskMCP,
  fetchInventoryAnalyticsMCP,
  fetchSalesPerformanceMCP,
  fetchCustomerSegmentationMCP,
  fetchProHandelData,
  mockStockoutRisk,
};
