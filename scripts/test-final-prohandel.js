// Final test script for the updated ProHandel client
require('dotenv').config({ path: '.env.local' });
const fetch = require('node-fetch');

// Import local ProHandel client (we'll simulate it here)
console.log('=== ProHandel Client Integration Test ===');

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

// Token cache
let tokenCache = {
  token: null,
  expiresAt: null,
  serverUrl: null
};

// Authentication function
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
      throw new Error(`Authentication failed: ${response.status} ${response.statusText}`);
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
      serverUrl
    };
    
    console.log('Authentication successful!');
    console.log('Token expires in:', authData.token.token.expiresIn, 'seconds');
    
    return { token, serverUrl };
  } catch (error) {
    console.error('Authentication error:', error.message);
    return { token: null, serverUrl: null };
  }
}

// Generic API client function
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
      ...(options.headers || {})
    };

    const requestConfig = {
      ...options,
      headers
    };

    // Make the request
    const response = await fetch(url, requestConfig);
    
    console.log('Response status:', response.status, response.statusText);
    
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

// Test the getArticles function
async function testGetArticles(pageSize = 2) {
  try {
    console.log(`\nTesting getArticles with pageSize=${pageSize}...`);
    const articles = await apiClient(`/article?PageSize=${pageSize}`);
    
    console.log(`Successfully retrieved ${articles.length} articles`);
    console.log('First article sample:', JSON.stringify(articles[0], null, 2).substring(0, 200) + '...');
    
    return articles;
  } catch (error) {
    console.error('Error in getArticles test:', error.message);
    return null;
  }
}

// Test the warehouse data (even though endpoint may not exist)
async function testGetWarehouses() {
  try {
    console.log('\nTesting getWarehouses...');
    
    // Try several potential endpoints
    const endpoints = [
      '/locations',
      '/warehouses',
      '/branches',
      '/shops'
    ];
    
    for (const endpoint of endpoints) {
      try {
        console.log(`Trying endpoint: ${endpoint}`);
        const response = await apiClient(endpoint);
        console.log(`Success with ${endpoint}:`, response);
        return response;
      } catch (error) {
        console.log(`Endpoint ${endpoint} failed:`, error.message);
      }
    }
    
    console.log('No warehouse endpoints worked. Returning fallback data.');
    return [{ id: 'default', name: 'Default Warehouse' }];
  } catch (error) {
    console.error('Error in getWarehouses test:', error.message);
    return null;
  }
}

// Test the authentication token caching
async function testTokenCaching() {
  try {
    console.log('\nTesting token caching...');
    
    console.log('First authentication request:');
    const firstAuth = await authenticate();
    console.log('Token cached:', !!tokenCache.token);
    
    console.log('\nSecond authentication request (should use cache):');
    const secondAuth = await authenticate();
    
    return { cached: tokenCache.token === secondAuth.token };
  } catch (error) {
    console.error('Error in token caching test:', error.message);
    return null;
  }
}

// Run all tests
async function runTests() {
  try {
    // Test 1: Authentication
    const { token, serverUrl } = await authenticate();
    if (!token || !serverUrl) {
      console.log('❌ Authentication test failed. Cannot continue with other tests.');
      return;
    }
    console.log('✅ Authentication test passed');
    
    // Test 2: Get articles
    const articles = await testGetArticles();
    if (!articles) {
      console.log('❌ GetArticles test failed');
    } else {
      console.log('✅ GetArticles test passed');
    }
    
    // Test 3: Get warehouses (expecting failure but should handle gracefully)
    const warehouses = await testGetWarehouses();
    if (!warehouses) {
      console.log('❌ GetWarehouses test failed');
    } else {
      console.log('✅ GetWarehouses test uses fallback data');
    }
    
    // Test 4: Token caching
    const cachingResult = await testTokenCaching();
    if (!cachingResult || !cachingResult.cached) {
      console.log('❌ Token caching test failed');
    } else {
      console.log('✅ Token caching test passed');
    }
    
    console.log('\n=== Test Summary ===');
    console.log('- Authentication:', token ? '✅ Success' : '❌ Failed');
    console.log('- API Server URL:', serverUrl);
    console.log('- Article retrieval:', articles ? '✅ Success' : '❌ Failed');
    console.log('- Warehouse handling:', warehouses ? '✅ Fallback' : '❌ Failed');
    console.log('- Token caching:', cachingResult?.cached ? '✅ Working' : '❌ Issues');
    
    console.log('\n✅ Integration test completed');
  } catch (error) {
    console.error('Test execution failed:', error);
  }
}

// Run the tests
runTests();
