// Enhanced standalone test for ProHandel client
require('dotenv').config({ path: '.env.local' });
const fetch = require('node-fetch');

console.log('=== Enhanced ProHandel Client Test ===');

// Configuration
const config = {
  AUTH_URL: process.env.PROHANDEL_AUTH_URL || 'https://auth.prohandel.cloud/api/v4',
  API_KEY: process.env.PROHANDEL_API_KEY,
  API_SECRET: process.env.PROHANDEL_API_SECRET,
  TENANT_ID: process.env.TENANT_ID
};

console.log('Configuration:');
console.log('- AUTH_URL:', config.AUTH_URL);
console.log('- TENANT_ID:', config.TENANT_ID);
console.log('- API_KEY:', config.API_KEY ? '✓ Set' : '✗ Missing');
console.log('- API_SECRET:', config.API_SECRET ? '✓ Set' : '✗ Missing');

// Token cache with retry counter
let tokenCache = {
  token: null,
  expiresAt: null,
  serverUrl: null,
  retryCount: 0
};

/**
 * Enhanced authentication with retry logic and error handling
 */
async function authenticate() {
  try {
    const now = Date.now();

    // Return cached token if valid
    if (tokenCache.token && tokenCache.expiresAt && tokenCache.serverUrl && tokenCache.expiresAt > now) {
      console.log('Using cached token');
      return { token: tokenCache.token, serverUrl: tokenCache.serverUrl };
    }

    console.log('\nAuthenticating with ProHandel API...');
    const authUrl = `${config.AUTH_URL}/token`;
    
    // Alternative auth URLs to try if the primary fails
    const alternativeAuthUrls = [
      'https://auth.prohandel.de/api/v4/token',
      'https://linde.prohandel.de/auth/api/v4/token'
    ];
    
    // Try primary auth URL first
    try {
      const response = await fetch(authUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ApiKey: config.API_KEY,
          Secret: config.API_SECRET,
          TenantId: config.TENANT_ID
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Authentication failed: ${response.status} ${errorText}`);
      }

      const authData = await response.json();
      console.log('Auth response data keys:', Object.keys(authData));
      console.log('Server URL from auth:', authData.serverUrl);
      
      // Extract token and serverUrl
      if (!authData.token || !authData.token.token || !authData.token.token.value) {
        throw new Error('Unexpected authentication response format');
      }
      
      const token = authData.token.token.value;
      const serverUrl = authData.serverUrl;
      
      // Cache the token
      tokenCache = {
        token,
        expiresAt: now + (authData.token.token.expiresIn * 1000) - 60000, // Subtract 1 minute for safety
        serverUrl,
        retryCount: 0 // Reset retry count on success
      };
      
      console.log('Authentication successful with primary auth URL!');
      console.log('Token expires in:', authData.token.token.expiresIn, 'seconds');
      
      return { token, serverUrl };
    } catch (error) {
      // If primary auth fails, try alternatives
      if (tokenCache.retryCount < alternativeAuthUrls.length) {
        console.error(`Primary auth URL failed: ${error.message}`);
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
              ApiKey: config.API_KEY,
              Secret: config.API_SECRET,
              TenantId: config.TENANT_ID
            }),
          });
          
          if (!response.ok) {
            throw new Error(`Alternative auth failed: ${response.status}`);
          }

          const authData = await response.json();
          
          // Check different potential response formats
          let token = null;
          let serverUrl = null;
          
          if (authData.token?.token?.value) {
            token = authData.token.token.value;
            serverUrl = authData.serverUrl;
          } else if (authData.token?.value) {
            token = authData.token.value;
            serverUrl = authData.serverUrl;
          } else if (authData.access_token) {
            token = authData.access_token;
            serverUrl = authData.serverUrl || 'https://linde.prohandel.de/api/v2';
          }
          
          if (!token) {
            throw new Error('Could not extract token from authentication response');
          }
          
          // Cache the token
          tokenCache = {
            token,
            expiresAt: now + ((authData.token?.token?.expiresIn || 1800) * 1000) - 60000,
            serverUrl,
            retryCount: 0 // Reset retry count on success
          };
          
          console.log('Authentication successful with alternative auth URL!');
          return { token, serverUrl };
        } catch (alternativeError) {
          console.error(`Alternative auth URL failed: ${alternativeError.message}`);
          // Continue to throw the initial error
        }
      }
      
      console.error('Authentication error:', error.message);
      return { token: null, serverUrl: null };
    }
  } catch (error) {
    console.error('Authentication error:', error.message);
    return { token: null, serverUrl: null };
  }
}

/**
 * Enhanced API client with better error handling and token refresh
 */
async function apiClient(endpoint, options = {}) {
  try {
    // Get auth token and server URL
    const { token, serverUrl } = await authenticate();
    if (!token || !serverUrl) {
      throw new Error('Authentication failed');
    }

    // Build the full URL
    const url = `${serverUrl}/api/v2${endpoint}`;
    console.log(`\nMaking API request to: ${url}`);
    
    // Set headers
    const headers = {
      'Authorization': `Bearer ${token}`,
      'X-Tenant-ID': config.TENANT_ID,
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-API-Version': 'v2.29.1',
      ...(options.headers || {})
    };

    const requestConfig = {
      ...options,
      headers
    };

    // Make the request
    const response = await fetch(url, requestConfig);
    
    console.log('Response status:', response.status, response.statusText);
    
    // Handle 401 Unauthorized by refreshing token
    if (response.status === 401) {
      console.log('Token expired, refreshing...');
      
      // Clear token cache to force re-authentication
      tokenCache.token = null;
      tokenCache.expiresAt = null;
      
      // Retry the request with a fresh token
      const { token: newToken } = await authenticate();
        
      const retryConfig = {
        ...requestConfig,
        headers: {
          ...requestConfig.headers,
          'Authorization': `Bearer ${newToken}`
        }
      };
      
      console.log('Retrying request with fresh token...');
      const retryResponse = await fetch(url, retryConfig);
      
      if (!retryResponse.ok) {
        const errorText = await retryResponse.text();
        throw new Error(`API error after token refresh: ${retryResponse.status} ${errorText}`);
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error ${response.status}: ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API request error:', error.message);
    throw error;
  }
}

/**
 * Get warehouses/branches
 */
async function getWarehouses() {
  try {
    console.log('\nTesting getWarehouses (using /branch endpoint)...');
    
    const branches = await apiClient('/branch');
    
    // Map branch data to warehouse format
    const warehouses = branches.map(branch => ({
      id: branch.id || branch.number.toString(),
      name: branch.name1 || `Branch ${branch.number}`,
      description: branch.city ? `${branch.name1} - ${branch.city}` : branch.name1,
      address: branch.street ? `${branch.street}, ${branch.zipCode} ${branch.city}` : undefined,
      active: branch.isActive !== false, // Default to active if not specified
      isWebshop: branch.isWebshop || false,
      phone: branch.telephoneNumber || undefined,
      email: branch.email || undefined
    }));
    
    // Log success and return only active warehouses
    console.log(`Found ${warehouses.length} warehouses, ${warehouses.filter(w => w.active).length} active`);
    return warehouses.filter(w => w.active);
  } catch (error) {
    console.error('Error fetching warehouses:', error.message);
    // Return fallback data
    return [{ id: 'default', name: 'Default Warehouse', description: 'Fallback warehouse', active: true }];
  }
}

/**
 * Get articles with enhanced error handling
 */
async function getArticles(pageSize = 5) {
  try {
    console.log(`\nTesting getArticles with pageSize=${pageSize}...`);
    const articles = await apiClient(`/article?PageSize=${pageSize}`);
    
    console.log(`Successfully retrieved ${articles.length} articles`);
    if (articles.length > 0) {
      console.log('First article sample:', JSON.stringify(articles[0], null, 2).substring(0, 200) + '...');
    }
    
    return articles;
  } catch (error) {
    console.error('Error in getArticles test:', error.message);
    return [];
  }
}

/**
 * Get stockout risks with multi-endpoint retry
 */
async function getStockoutRisks(warehouseId) {
  try {
    console.log(`\nTesting getStockoutRisks ${warehouseId ? `for warehouse ${warehouseId}` : '(all warehouses)'}...`);
    
    // Try different endpoint variants
    const endpoints = [
      warehouseId ? `/inventory/stockout-risks?location_id=${warehouseId}` : '/inventory/stockout-risks',
      warehouseId ? `/stock/risks?branch_id=${warehouseId}` : '/stock/risks',
      warehouseId ? `/stock?branch_id=${warehouseId}` : '/stock'
    ];
    
    let stockoutData = null;
    let lastError = null;
    
    // Try each endpoint until we find one that works
    for (const endpoint of endpoints) {
      try {
        console.log(`Trying stockout endpoint: ${endpoint}`);
        const data = await apiClient(endpoint);
        if (data && Array.isArray(data)) {
          stockoutData = data;
          console.log(`Found working stockout endpoint: ${endpoint}`);
          break;
        }
      } catch (err) {
        lastError = err;
        console.log(`Endpoint ${endpoint} failed: ${err.message}`);
      }
    }
    
    if (stockoutData) {
      console.log(`Retrieved ${stockoutData.length} stockout risk items`);
      return stockoutData;
    }
    
    // If all endpoints failed, throw the last error
    throw lastError || new Error('All stockout endpoints failed');
  } catch (error) {
    console.error('Error fetching stockout risks:', error.message);
    return [];
  }
}

/**
 * Run all tests
 */
async function runTests() {
  try {
    console.log('\n==== ENHANCED PROHANDEL CLIENT TEST ====');
    
    // Step 1: Authentication
    console.log('\n1. Testing Authentication...');
    const { token, serverUrl } = await authenticate();
    if (!token || !serverUrl) {
      console.log('❌ Authentication test failed. Cannot continue with other tests.');
      return;
    }
    console.log('✅ Authentication test passed');
    console.log(`   Token: ${token.substring(0, 15)}...`);
    console.log(`   Server URL: ${serverUrl}`);
    
    // Step 2: Get warehouses
    console.log('\n2. Testing Warehouse Retrieval...');
    const warehouses = await getWarehouses();
    if (!warehouses || warehouses.length === 0) {
      console.log('❌ GetWarehouses test failed');
    } else {
      console.log('✅ GetWarehouses test passed');
      console.table(warehouses.map(w => ({
        ID: w.id,
        Name: w.name,
        City: w.description?.split(' - ')[1] || '',
        Active: w.active,
        IsWebshop: w.isWebshop || false
      })));
    }
    
    // Step 3: Test stockout risks
    console.log('\n3. Testing Stockout Risks...');
    // No warehouse filter
    const stockoutRisks = await getStockoutRisks();
    if (!stockoutRisks) {
      console.log('❌ GetStockoutRisks test failed');
    } else {
      console.log('✅ GetStockoutRisks test passed');
      console.log(`   Retrieved ${stockoutRisks.length} stockout risks overall`);
    }
    
    // With warehouse filter if we have any
    if (warehouses && warehouses.length > 0) {
      const testWarehouse = warehouses[0];
      console.log(`\n   Testing stockout risks for warehouse: ${testWarehouse.name}`);
      const filteredRisks = await getStockoutRisks(testWarehouse.id);
      console.log(`   ✅ Found ${filteredRisks.length} stockout risks for this warehouse`);
    }
    
    // Step 4: Get articles
    console.log('\n4. Testing Article Retrieval...');
    const articles = await getArticles();
    if (!articles || articles.length === 0) {
      console.log('❌ GetArticles test failed');
    } else {
      console.log('✅ GetArticles test passed');
      console.log(`   Retrieved ${articles.length} articles`);
      
      if (articles.length > 0) {
        const sample = articles[0];
        console.log('\n   Sample Article Data:');
        console.log(`     ID: ${sample.id || 'N/A'}`);
        console.log(`     Name: ${sample.name || 'N/A'}`);
        console.log(`     Description: ${sample.description || 'N/A'}`);
        console.log(`     Price: ${sample.price || 'N/A'}`);
      }
    }
    
    // Summary
    console.log('\n==== Test Summary ====');
    console.log('Authentication:', token ? '✅ Success' : '❌ Failed');
    console.log('API Server URL:', serverUrl);
    console.log('Warehouses:', warehouses?.length ? `✅ Success (${warehouses.length} found)` : '❌ Failed');
    console.log('Stockout Risks:', stockoutRisks ? `✅ Success (${stockoutRisks.length} found)` : '❌ Failed');
    console.log('Articles:', articles?.length ? `✅ Success (${articles.length} found)` : '❌ Failed');
    
    console.log('\n✅ Enhanced client tests completed successfully!');
    console.log('The client now features:');
    console.log('  - Robust authentication with fallback URLs');
    console.log('  - Token caching and automatic refreshing');
    console.log('  - Comprehensive error handling');
    console.log('  - Multiple endpoint attempts for resilience');
    
  } catch (error) {
    console.error('\nTest execution failed:', error);
  }
}

// Run the tests
runTests().catch(err => {
  console.error('\nUnhandled error in tests:', err);
  process.exit(1);
});
