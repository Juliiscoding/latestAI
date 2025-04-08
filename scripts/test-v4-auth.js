// Test ProHandel API using the v4 authentication endpoint
require('dotenv').config({ path: '.env.local' });
const fetch = require('node-fetch');

// Get config from environment variables
const config = {
  AUTH_URL: process.env.PROHANDEL_AUTH_URL,     // https://auth.prohandel.cloud/api/v4
  API_URL: process.env.PROHANDEL_API_URL,       // https://api.prohandel.de/api/v2
  API_KEY: process.env.PROHANDEL_API_KEY,       // 7e7c639358434c4fa215d4e3978739d0
  API_SECRET: process.env.PROHANDEL_API_SECRET, // 1cjnuux79d
  TENANT_ID: process.env.TENANT_ID              // mercurios
};

console.log('=== ProHandel API V4 Authentication Test ===');
console.log('AUTH_URL:', config.AUTH_URL);
console.log('API_URL:', config.API_URL);
console.log('TENANT_ID:', config.TENANT_ID);
console.log('API_KEY:', config.API_KEY ? '✓ Set' : '✗ Missing');
console.log('API_SECRET:', config.API_SECRET ? '✓ Set' : '✗ Missing');

// Authenticate using client credentials flow with v4 auth endpoint
async function authenticateV4() {
  try {
    console.log('\nAttempting v4 authentication...');
    // Try the /token endpoint directly as mentioned in your API docs
    const tokenUrl = `${config.AUTH_URL}/token`;
    console.log('Token URL:', tokenUrl);
    
    const response = await fetch(tokenUrl, {
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
    
    console.log('Response status:', response.status, response.statusText);
    
    if (!response.ok) {
      console.log('Authentication failed');
      try {
        const errorBody = await response.text();
        console.log('Error details:', errorBody);
      } catch (e) {
        console.log('Could not parse error body');
      }
      return null;
    }
    
    const data = await response.json();
    console.log('Auth response structure:', Object.keys(data));
    
    // Log the entire response structure for debugging
    console.log('Full auth response:', JSON.stringify(data, null, 2));
    
    // Try to extract token from the response (handling nested structure)
    let token = null;
    if (data.token && data.token.token && data.token.token.value) {
      token = data.token.token.value;
      console.log('Successfully extracted token from nested structure');
    } else if (data.token && typeof data.token === 'string') {
      token = data.token;
      console.log('Found token as direct string property');
    } else if (data.access_token) {
      token = data.access_token;
      console.log('Found token as access_token property');
    } else {
      console.log('Could not find token in response. Available fields:', JSON.stringify(Object.keys(data)));
      return null;
    }
    
    console.log('Authentication successful!');
    console.log('Token type:', typeof token);
    console.log('Token length:', token.length);
    console.log('Token preview:', token.substring(0, 20) + '...');
    
    return token;
  } catch (error) {
    console.error('Authentication error:', error.message);
    return null;
  }
}

// Test the /locations endpoint with auth token
async function testLocationsEndpoint(token) {
  try {
    console.log('\nTesting locations endpoint with auth token...');
    const locationsUrl = `${config.API_URL}/locations`;
    console.log('Locations URL:', locationsUrl);
    
    const response = await fetch(locationsUrl, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Tenant-ID': config.TENANT_ID
      }
    });
    
    console.log('Response status:', response.status, response.statusText);
    
    if (!response.ok) {
      console.log('Request failed');
      try {
        const errorBody = await response.text();
        console.log('Error details:', errorBody);
      } catch (e) {
        console.log('Could not parse error body');
      }
      return null;
    }
    
    const data = await response.json();
    console.log('Locations response:', JSON.stringify(data, null, 2));
    return data;
  } catch (error) {
    console.error('Error fetching locations:', error.message);
    return null;
  }
}

// Test for alternative endpoints
async function tryAlternativeEndpoints(token) {
  const endpoints = [
    '/warehouses',
    '/branches',
    '/stores',
    '/shops',
    '/subsidiaries'
  ];
  
  console.log('\nTrying alternative endpoints for locations/warehouses...');
  
  for (const endpoint of endpoints) {
    try {
      const url = `${config.API_URL}${endpoint}`;
      console.log(`\nTrying endpoint: ${url}`);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Tenant-ID': config.TENANT_ID
        }
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (response.ok) {
        console.log('✅ Found working endpoint:', endpoint);
        const data = await response.json();
        console.log('Response:', JSON.stringify(data, null, 2));
        return { endpoint, data };
      }
    } catch (error) {
      console.log(`Error with ${endpoint}:`, error.message);
    }
  }
  
  return null;
}

// Test article endpoint with auth token
async function testArticleEndpoint(token) {
  try {
    console.log('\nTesting article endpoint with auth token...');
    const url = `${config.API_URL}/article?PageSize=2`;
    console.log('URL:', url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Tenant-ID': config.TENANT_ID
      }
    });
    
    console.log('Response status:', response.status, response.statusText);
    
    if (!response.ok) {
      console.log('Request failed');
      try {
        const errorBody = await response.text();
        console.log('Error details:', errorBody);
      } catch (e) {
        console.log('Could not parse error body');
      }
      return null;
    }
    
    const data = await response.json();
    console.log('Articles sample:', JSON.stringify(data.slice(0, 2), null, 2));
    return data;
  } catch (error) {
    console.error('Error fetching articles:', error.message);
    return null;
  }
}

// Run all tests
async function runTests() {
  try {
    // Step 1: Authenticate with v4 endpoint
    const token = await authenticateV4();
    if (!token) {
      console.log('\n❌ Authentication failed. Cannot proceed with further tests.');
      return;
    }
    
    // Step 2: Test the locations endpoint with the token
    const locations = await testLocationsEndpoint(token);
    
    // Step 3: If locations endpoint fails, try alternative endpoints
    if (!locations) {
      console.log('\nLocations endpoint failed, trying alternatives...');
      const alternative = await tryAlternativeEndpoints(token);
      
      if (alternative) {
        console.log(`\n✅ Found working alternative for locations: ${alternative.endpoint}`);
      } else {
        console.log('\n❌ Could not find a working endpoint for locations/warehouses.');
      }
    }
    
    // Step 4: Test article endpoint
    await testArticleEndpoint(token);
    
    console.log('\n=== Test Summary ===');
    console.log('Authentication:', token ? '✅ Success' : '❌ Failed');
    console.log('Locations endpoint:', locations ? '✅ Success' : '❌ Failed');
    console.log('\nTest complete!');
  } catch (error) {
    console.error('Test execution failed:', error);
  }
}

// Execute all tests
runTests();
