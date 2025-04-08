/**
 * ProHandel API Client
 * 
 * Direct integration with the ProHandel API using the credentials provided in the environment.
 * This client handles authentication and provides methods to access various endpoints.
 */

import Cookies from 'js-cookie';
import * as mockData from '../../mock/prohandel-mock';

// Configuration for ProHandel API - values from environment variables with fallbacks
// Based on the known working configuration from API testing
const PROHANDEL_CONFIG = {
  AUTH_URL: process.env.PROHANDEL_AUTH_URL || 'https://auth.prohandel.cloud/api/v4',
  API_KEY: process.env.PROHANDEL_API_KEY,
  API_SECRET: process.env.PROHANDEL_API_SECRET,
  TENANT_ID: process.env.TENANT_ID
};

// Response type for authentication - handles the different response formats
interface AuthResponse {
  token: {
    token: {
      value: string;
      name: string;
      expiresIn: number;
    };
    refreshToken: {
      value: string;
      name: string;
      expiresIn: number;
    };
  };
  serverUrl: string;
  requiredActions: any[];
}

// Cache for access token and server URL
let tokenCache: {
  token: string | null;
  expiresAt: number | null;
  serverUrl: string | null;
  retryCount: number;
} = {
  token: null,
  expiresAt: null,
  serverUrl: null,
  retryCount: 0
};

/**
 * Authenticate with the ProHandel API
 * 
 * ProHandel API authentication can be tricky:
 * 1. The auth endpoint response format can vary - we handle multiple formats
 * 2. The real API URL is returned in the serverUrl field after authentication
 * 3. The token is typically valid for 30 minutes
 * 
 * @returns Access token and server URL
 */
export const authenticate = async (): Promise<{ token: string; serverUrl: string }> => {
  try {
    const now = Date.now();

    // Return cached token if it's still valid
    if (tokenCache.token && tokenCache.expiresAt && tokenCache.serverUrl && tokenCache.expiresAt > now) {
      console.log('Using cached ProHandel token');
      return { token: tokenCache.token, serverUrl: tokenCache.serverUrl };
    }

    console.log('Authenticating with ProHandel API...');
    const authUrl = `${PROHANDEL_CONFIG.AUTH_URL}/token`;
    
    // Alternative authentication URLs in case the primary fails
    const alternativeAuthUrls = [
      'https://auth.prohandel.de/api/v4/token',
      'https://linde.prohandel.de/auth/api/v4/token'
    ];
    
    // Try the primary auth URL first
    try {
      const response = await fetch(authUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ApiKey: PROHANDEL_CONFIG.API_KEY,
          Secret: PROHANDEL_CONFIG.API_SECRET,
          TenantId: PROHANDEL_CONFIG.TENANT_ID
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Authentication failed: ${response.status} ${errorText}`);
      }

      const auth: AuthResponse = await response.json();
      
      // Extract token from the nested response format
      if (!auth.token || !auth.token.token || !auth.token.token.value) {
        throw new Error('Unexpected authentication response format: token not found');
      }
      
      const token = auth.token.token.value;
      const serverUrl = auth.serverUrl;
      
      // Cache the token with expiration time (subtracting 1 minute for safety)
      tokenCache = {
        token,
        expiresAt: now + (auth.token.token.expiresIn * 1000) - 60000,
        serverUrl,
        retryCount: 0
      };
      
      console.log('Authentication successful! Token obtained from primary auth URL.');
      return { token, serverUrl };
    } catch (error: any) {
      // If primary auth URL fails, try alternatives if we haven't exhausted retries
      if (tokenCache.retryCount < alternativeAuthUrls.length) {
        console.error(`Primary auth URL failed: ${error.message || 'Unknown error'}`);
        console.log(`Trying alternative auth URL #${tokenCache.retryCount + 1}`);
        
        const alternativeUrl = alternativeAuthUrls[tokenCache.retryCount];
        tokenCache.retryCount++;
        
        try {
          const response = await fetch(alternativeUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              ApiKey: PROHANDEL_CONFIG.API_KEY,
              Secret: PROHANDEL_CONFIG.API_SECRET,
              TenantId: PROHANDEL_CONFIG.TENANT_ID
            }),
          });
          
          if (!response.ok) {
            throw new Error(`Alternative auth failed: ${response.status}`);
          }

          const auth = await response.json();
          
          // Check different potential response formats
          let token = null;
          let serverUrl = null;
          
          if (auth.token?.token?.value) {
            token = auth.token.token.value;
            serverUrl = auth.serverUrl;
          } else if (auth.token?.value) {
            token = auth.token.value;
            serverUrl = auth.serverUrl;
          } else if (auth.access_token) {
            token = auth.access_token;
            serverUrl = auth.serverUrl || 'https://linde.prohandel.de/api/v2';
          }
          
          if (!token) {
            throw new Error('Could not extract token from authentication response');
          }
          
          // Cache the token with a default expiration of 30 minutes if not specified
          tokenCache = {
            token,
            expiresAt: now + ((auth.token?.token?.expiresIn || 1800) * 1000) - 60000,
            serverUrl,
            retryCount: 0 // Reset retry count on success
          };
          
          console.log('Authentication successful with alternative auth URL!');
          return { token, serverUrl };
        } catch (altError: any) {
          console.error(`Alternative auth URL failed: ${altError.message || 'Unknown error'}`);
          // Continue to throw the initial error
        }
      }
      
      // If we've exhausted all retries, throw the original error
      throw error;
    }
  } catch (error: any) {
    console.error('ProHandel authentication error:', error);
    throw error;
  }
};

/**
 * Generic API client for ProHandel API
 * 
 * Key points about the ProHandel API:
 * 1. The base URL comes from the serverUrl in the authentication response
 * 2. All endpoints require Authorization and X-Tenant-ID headers
 * 3. Error handling should account for rate limiting and token expiration
 * 
 * @param endpoint API endpoint path
 * @param options Request options
 * @returns Response data
 */
const apiClient = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  try {
    // Get authentication token and server URL
    const { token, serverUrl } = await authenticate();

    // Build the full URL using the dynamic server URL from auth
    const url = `${serverUrl}/api/v2${endpoint}`;
    
    // Set the required headers
    const headers: HeadersInit = {
      'Authorization': `Bearer ${token}`,
      'X-Tenant-ID': PROHANDEL_CONFIG.TENANT_ID as string,
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-API-Version': 'v2.29.1', // Include API version for better compatibility
      ...(options.headers || {}),
    };

    const config: RequestInit = {
      ...options,
      headers,
    };

    console.log(`ProHandel API request to: ${url}`);
    const response = await fetch(url, config);

    // Handle common error scenarios
    if (!response.ok) {
      // If unauthorized, try refreshing the token
      if (response.status === 401) {
        // Clear token cache to force re-authentication
        tokenCache.token = null;
        tokenCache.expiresAt = null;
        
        // Retry the request once with a fresh token
        const { token: newToken } = await authenticate();
        
        const retryConfig = {
          ...config,
          headers: {
            ...config.headers,
            'Authorization': `Bearer ${newToken}`
          }
        };
        
        console.log('Retrying request with fresh token...');
        const retryResponse = await fetch(url, retryConfig);
        
        if (!retryResponse.ok) {
          const errorText = await retryResponse.text();
          throw new Error(`ProHandel API error after token refresh: ${retryResponse.status} ${errorText}`);
        }
        
        return await retryResponse.json();
      }
      
      // Handle other errors
      const errorText = await response.text();
      throw new Error(`ProHandel API error ${response.status}: ${errorText}`);
    }

    return await response.json();
  } catch (error: any) {
    console.error('ProHandel API request error:', error);
    throw error;
  }
};

/**
 * Get all warehouses/locations
 * 
 * Note: The correct endpoint for warehouse data in ProHandel is '/branch'
 * Based on testing multiple endpoints, this is the one that provides location data
 * with names, addresses, and other relevant information.
 * 
 * @param useRealData Whether to use real API data or mock data
 * @returns List of warehouses
 */
export const getWarehouses = async (useRealData: boolean = true) => {
  try {
    if (!useRealData) {
      console.log('Using mock warehouse data');
      return mockData.warehouses;
    }

    // Get the endpoint for warehouses
    const endpoint = '/branch';
    const data = await apiClient<any[]>(endpoint);
    
    // Transform to match the Warehouse interface
    return data.map(warehouse => ({
      id: warehouse.id.toString(),
      name: warehouse.name,
      description: warehouse.description || '',
      address: warehouse.address || '',
      active: warehouse.active === true || warehouse.active === 'true',
      isWebshop: warehouse.isWebshop === true || warehouse.isWebshop === 'true'
    }));
  } catch (error: any) {
    console.error('Error fetching warehouses:', error);
    return [];
  }
};

/**
 * Get stockout risks, optionally filtered by warehouse
 * 
 * @param warehouseId Optional warehouse ID to filter by
 * @param useRealData Whether to use real API data or mock data
 * @returns List of stockout risks
 */
export const getStockoutRisks = async (warehouseId?: string, useRealData: boolean = true) => {
  try {
    if (!useRealData) {
      console.log('Using mock stockout risk data');
      return mockData.stockoutRisks;
    }

    // Base endpoint for stockout risks
    let endpoint = '/stockout-risk';
    
    // Add warehouse filter if provided
    if (warehouseId) {
      endpoint += `?location_id=${warehouseId}`;
    }
    
    const data = await apiClient<any[]>(endpoint);
    
    // Transform to match the required format
    return data.map(risk => ({
      id: risk.id.toString(),
      productId: risk.productId.toString(),
      name: risk.productName,
      sku: risk.sku,
      categoryId: risk.categoryId?.toString() || '',
      categoryName: risk.categoryName || 'Uncategorized',
      stockLevel: risk.stockLevel || 0,
      reorderPoint: risk.reorderPoint || 0,
      riskLevel: risk.riskLevel || 'medium',
      lastRestockDate: risk.lastRestockDate,
      averageDailySales: risk.averageDailySales || 0,
      daysUntilStockout: risk.daysUntilStockout
    }));
  } catch (error: any) {
    console.error('Error fetching stockout risks:', error);
    return [];
  }
};

/**
 * Get all articles with their latest stock information
 */
export const getAllArticles = async (params?: {
  limit?: number;
  offset?: number;
  searchTerm?: string;
}): Promise<any> => {
  try {
    // Build query parameters
    const queryParams = new URLSearchParams();
    
    if (params?.limit) {
      queryParams.append('PageSize', params.limit.toString());
    }
    
    if (params?.offset) {
      queryParams.append('Page', Math.floor(params.offset / (params.limit || 20) + 1).toString());
    }
    
    // API request with query parameters
    const endpoint = `/article${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const articlesData = await apiClient<any[]>(endpoint);
    
    // Process and return the data
    return articlesData;
  } catch (error: any) {
    console.error('Error fetching articles:', error);
    throw error;
  }
};

/**
 * Get article by ID
 */
export const getArticleById = async (id: string): Promise<any> => {
  try {
    return apiClient<any>(`/article/${id}`);
  } catch (error: any) {
    console.error(`Error fetching article ${id}:`, error);
    throw error;
  }
};

/**
 * Get order by ID
 */
export const getOrderById = async (id: string): Promise<any> => {
  try {
    return apiClient<any>(`/order/${id}`);
  } catch (error: any) {
    console.error(`Error fetching order ${id}:`, error);
    throw error;
  }
};

/**
 * Get customer by ID
 */
export const getCustomerById = async (id: string): Promise<any> => {
  try {
    return apiClient<any>(`/customer/${id}`);
  } catch (error: any) {
    console.error(`Error fetching customer ${id}:`, error);
    throw error;
  }
};

/**
 * Get customer purchase history
 */
export const getCustomerPurchaseHistory = async (customerId: string, limit: number = 10): Promise<any> => {
  try {
    return apiClient<any>(`/customer/${customerId}/purchases?limit=${limit}`);
  } catch (error: any) {
    console.error(`Error fetching purchases for customer ${customerId}:`, error);
    throw error;
  }
};

/**
 * Get sales data for a specified period
 */
export const getSalesData = async (params: {
  from: string; // ISO date format
  to: string; // ISO date format
  groupBy?: 'day' | 'week' | 'month';
  warehouseId?: string;
}): Promise<any> => {
  try {
    let endpoint = `/sales?from=${params.from}&to=${params.to}`;
    
    if (params.groupBy) {
      endpoint += `&groupBy=${params.groupBy}`;
    }
    
    if (params.warehouseId) {
      endpoint += `&location_id=${params.warehouseId}`;
    }
    
    return apiClient<any>(endpoint);
  } catch (error: any) {
    console.error('Error fetching sales data:', error);
    throw error;
  }
};

/**
 * Get sales data with optional date range and warehouse filter
 * @param fromDate Start date (default: 30 days ago)
 * @param toDate End date (default: today)
 * @param warehouseId Optional warehouse ID to filter by
 * @param useRealData Whether to use real API data or mock data
 * @returns Sales data
 */
export const getSales = async (
  fromDate?: string,
  toDate?: string,
  warehouseId?: string,
  useRealData: boolean = true
) => {
  try {
    if (!useRealData) {
      console.log('Using mock sales data');
      return mockData.sales;
    }

    // Set default date range if not provided
    const now = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(now.getDate() - 30);
    
    const from = fromDate || thirtyDaysAgo.toISOString().split('T')[0];
    const to = toDate || now.toISOString().split('T')[0];
    
    // Build the endpoint with query parameters
    let endpoint = `/sales?from=${from}&to=${to}`;
    if (warehouseId) {
      endpoint += `&location_id=${warehouseId}`;
    }
    
    return apiClient<any[]>(endpoint);
  } catch (error: any) {
    console.error('Error fetching sales data:', error);
    return [];
  }
};

/**
 * Test the ProHandel API connection
 * @returns Boolean indicating whether the connection was successful
 */
export const testConnection = async (): Promise<boolean> => {
  try {
    // Try to fetch articles as a connection test
    const articles = await getAllArticles();
    console.log('ProHandel connection test successful:', articles);
    
    // Log the connection details to verify the environment variables
    console.log('API credentials working properly');
    console.log('TENANT ID:', PROHANDEL_CONFIG.TENANT_ID);
    console.log('Token exists:', !!tokenCache.token);
    
    return true;
  } catch (error: any) {
    console.error('ProHandel connection test failed:', error);
    return false;
  }
};

// Export all methods
export default {
  authenticate,
  getArticles: getAllArticles,
  getAllArticles,
  getArticleById,
  getSales,
  getSalesData,
  getStockoutRisks,
  getWarehouses,
  testConnection,
  getOrderById,
  getCustomerById,
  getCustomerPurchaseHistory
};
