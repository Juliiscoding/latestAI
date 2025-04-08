// Enhanced script to test ProHandel API connection with detailed logging
require('dotenv').config({ path: '.env.local' });
const fetch = require('node-fetch');

// Get config from environment variables
const config = {
  AUTH_URL: process.env.PROHANDEL_AUTH_URL,
  API_URL: process.env.PROHANDEL_API_URL,
  API_KEY: process.env.PROHANDEL_API_KEY,
  API_SECRET: process.env.PROHANDEL_API_SECRET,
  TENANT_ID: process.env.TENANT_ID
};

console.log('=== ProHandel API Connection Test ===');
console.log('Configuration:');
console.log('AUTH_URL:', config.AUTH_URL);
console.log('API_URL:', config.API_URL);
console.log('TENANT_ID:', config.TENANT_ID);
console.log('API_KEY:', config.API_KEY ? '✓ Set' : '✗ Missing');
console.log('API_SECRET:', config.API_SECRET ? '✓ Set' : '✗ Missing');
console.log('=======================================\n');

// Try different authentication endpoints
async function tryAuth(endpoint) {
  console.log(`Trying auth endpoint: ${endpoint}`);
  try {
    const url = `${config.AUTH_URL}${endpoint}`;
    console.log('Full URL:', url);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        grant_type: 'client_credentials',
        client_id: config.API_KEY,
        client_secret: config.API_SECRET,
        tenant_id: config.TENANT_ID
      }),
    });

    console.log('Response status:', response.status, response.statusText);
    
    if (!response.ok) {
      console.log('Error response (not OK)');
      try {
        const errorBody = await response.text();
        console.log('Error body:', errorBody);
      } catch (e) {
        console.log('Could not parse error body');
      }
      return null;
    }

    const data = await response.json();
    console.log('Auth successful with endpoint:', endpoint);
    console.log('Response data:', JSON.stringify(data, null, 2));
    return data.access_token;
  } catch (error) {
    console.error(`Error with endpoint ${endpoint}:`, error.message);
    return null;
  }
}

// Try GET request on a specific endpoint
async function tryGetEndpoint(endpoint, token) {
  console.log(`\nTrying GET endpoint: ${endpoint}`);
  try {
    const url = `${config.API_URL}${endpoint}`;
    console.log('Full URL:', url);
    
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
      headers['X-Tenant-ID'] = config.TENANT_ID;
    }
    
    const response = await fetch(url, {
      method: 'GET',
      headers,
    });

    console.log('Response status:', response.status, response.statusText);
    
    if (!response.ok) {
      console.log('Error response (not OK)');
      try {
        const errorBody = await response.text();
        console.log('Error body:', errorBody);
      } catch (e) {
        console.log('Could not parse error body');
      }
      return null;
    }

    const data = await response.json();
    console.log('GET request successful for:', endpoint);
    // Just show a sample of the data to avoid huge output
    if (Array.isArray(data)) {
      console.log(`Response contains ${data.length} items`);
      if (data.length > 0) {
        console.log('First item:', JSON.stringify(data[0], null, 2));
      }
    } else {
      console.log('Response data sample:', JSON.stringify(data).substring(0, 500) + '...');
    }
    return data;
  } catch (error) {
    console.error(`Error with GET endpoint ${endpoint}:`, error.message);
    return null;
  }
}

// Try all possible variations of authentication
async function testAllAuthVariations() {
  console.log('\n=== Testing Authentication Endpoints ===');
  
  // List of possible auth endpoints to try
  const authEndpoints = [
    '/oauth/token',
    '/auth/token',
    '/token',
    '/api/v4/oauth/token',
    '/api/oauth/token'
  ];
  
  let successfulToken = null;
  
  for (const endpoint of authEndpoints) {
    const token = await tryAuth(endpoint);
    if (token) {
      successfulToken = token;
      console.log(`\n✅ Authentication successful with endpoint: ${endpoint}`);
      break;
    } else {
      console.log(`❌ Authentication failed with endpoint: ${endpoint}`);
    }
  }
  
  return successfulToken;
}

// Test API endpoints
async function testApiEndpoints(token) {
  if (!token) {
    console.log('\n❌ Cannot test API endpoints without a valid token');
    return;
  }
  
  console.log('\n=== Testing API Endpoints ===');
  
  // Try some common API endpoints
  await tryGetEndpoint('/locations', token);
  await tryGetEndpoint('/articles?limit=5', token);
  await tryGetEndpoint('/inventory/stockout-risks', token);
  
  const today = new Date();
  const fromDate = new Date(today);
  fromDate.setDate(today.getDate() - 30);
  const from = fromDate.toISOString().split('T')[0];
  const to = today.toISOString().split('T')[0];
  
  await tryGetEndpoint(`/sales?from=${from}&to=${to}&limit=5`, token);
}

// Run all tests
async function runAllTests() {
  try {
    // Test authentication variations
    const token = await testAllAuthVariations();
    
    // Test API endpoints with the token (if we got one)
    await testApiEndpoints(token);
    
    console.log('\n=== Testing Complete ===');
    if (token) {
      console.log('✅ Successfully authenticated and tested endpoints');
    } else {
      console.log('❌ Failed to authenticate with any endpoint variation');
      console.log('Please check your credentials and try again');
    }
  } catch (error) {
    console.error('Test failed with error:', error);
  }
}

// Run the tests
runAllTests();
