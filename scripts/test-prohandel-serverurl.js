// Test ProHandel API using the serverUrl from auth response
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

console.log('=== ProHandel API ServerUrl Test ===');

// Authenticate using v4 endpoint
async function authenticate() {
  try {
    console.log('Authenticating with ProHandel API...');
    const tokenUrl = `${config.AUTH_URL}/token`;
    
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
    
    if (!response.ok) {
      throw new Error(`Authentication failed: ${response.status} ${response.statusText}`);
    }

    const responseData = await response.json();
    console.log('Auth response serverUrl:', responseData.serverUrl);
    
    // Extract token and serverUrl from the nested response format
    if (!responseData.token || !responseData.token.token || !responseData.token.token.value) {
      throw new Error('Unexpected authentication response format: token not found');
    }
    
    const token = responseData.token.token.value;
    const serverUrl = responseData.serverUrl || null;
    
    console.log('Authentication successful! Token obtained.');
    
    return { token, serverUrl };
  } catch (error) {
    console.error('Authentication error:', error.message);
    return { token: null, serverUrl: null };
  }
}

// Test various API endpoints using different URL combinations
async function testEndpoints(token, serverUrl) {
  // Base URLs to try
  const baseUrls = [
    serverUrl,                                // serverUrl from auth response
    `${serverUrl}/api/v2`,                    // serverUrl with /api/v2
    config.API_URL,                           // Original API_URL
    'https://linde.prohandel.de/api/v2',      // Hardcoded combination
    'https://api.prohandel.cloud/v2.29.1'     // URL from user suggestion
  ];
  
  // Endpoints to try
  const endpoints = [
    '/locations',
    '/warehouses',
    '/branches',
    '/shops',
    '/article'
  ];
  
  console.log('\nTesting API endpoints with different base URLs...');
  
  const successfulEndpoints = [];
  
  for (const baseUrl of baseUrls) {
    if (!baseUrl) continue;
    
    console.log(`\n--- Testing base URL: ${baseUrl} ---`);
    
    for (const endpoint of endpoints) {
      try {
        const url = `${baseUrl}${endpoint}`;
        console.log(`\nTrying: ${url}`);
        
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
          console.log('✅ Endpoint works!');
          const data = await response.json();
          console.log('Response sample:', JSON.stringify(data).substring(0, 200) + '...');
          
          successfulEndpoints.push({
            url,
            endpoint,
            baseUrl
          });
        } else {
          if (response.status === 401) {
            console.log('❌ Authentication issue with this endpoint');
          } else if (response.status === 404) {
            console.log('❌ Endpoint not found');
          } else {
            console.log(`❌ Failed with status ${response.status}`);
          }
        }
      } catch (error) {
        console.log(`Error with ${baseUrl}${endpoint}:`, error.message);
      }
    }
  }
  
  return successfulEndpoints;
}

// Try with different tenantId header variations
async function testTenantIdVariations(token, serverUrl, workingBaseUrl) {
  const tenantIdVariations = [
    { name: 'X-Tenant-ID', value: config.TENANT_ID },
    { name: 'x-tenant-id', value: config.TENANT_ID },
    { name: 'tenant_id', value: config.TENANT_ID },
    { name: 'tenant-id', value: config.TENANT_ID },
    { name: 'TenantId', value: config.TENANT_ID }
  ];
  
  if (!workingBaseUrl) {
    workingBaseUrl = `${serverUrl}/api/v2`;
  }
  
  console.log('\nTesting different tenant ID header variations...');
  
  const endpoint = '/article?PageSize=1';
  const url = `${workingBaseUrl}${endpoint}`;
  
  for (const variation of tenantIdVariations) {
    try {
      console.log(`\nTrying with ${variation.name}: ${variation.value}`);
      
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };
      
      headers[variation.name] = variation.value;
      
      const response = await fetch(url, {
        method: 'GET',
        headers
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (response.ok) {
        console.log(`✅ Success with ${variation.name} header!`);
        const data = await response.json();
        console.log('Response sample:', JSON.stringify(data).substring(0, 200) + '...');
        return variation;
      }
    } catch (error) {
      console.log(`Error with ${variation.name}:`, error.message);
    }
  }
  
  return null;
}

// Run all tests
async function runTests() {
  try {
    // Step 1: Authenticate and get token + serverUrl
    const { token, serverUrl } = await authenticate();
    if (!token) {
      console.log('❌ Authentication failed. Cannot continue tests.');
      return;
    }
    
    // Step 2: Test various endpoints with different base URLs
    const successfulEndpoints = await testEndpoints(token, serverUrl);
    
    // Step 3: If we found working endpoints, print summary
    if (successfulEndpoints.length > 0) {
      console.log('\n✅ Found working endpoints:');
      successfulEndpoints.forEach(endpoint => {
        console.log(`- ${endpoint.url}`);
      });
      
      // Use the baseUrl from first successful endpoint for tenant ID tests
      const workingBaseUrl = successfulEndpoints[0].baseUrl;
      
      // Step 4: Test tenant ID header variations
      const workingTenantIdHeader = await testTenantIdVariations(token, serverUrl, workingBaseUrl);
      
      if (workingTenantIdHeader) {
        console.log(`\n✅ Found working tenant ID header: ${workingTenantIdHeader.name}`);
      } else {
        console.log('\n❌ Could not find a working tenant ID header variation.');
      }
    } else {
      console.log('\n❌ Could not find any working endpoints.');
      console.log('\nRecommendations:');
      console.log('1. Try these environment variables:');
      console.log('   PROHANDEL_API_URL=https://linde.prohandel.de/api/v2');
      console.log('   or');
      console.log('   PROHANDEL_API_URL=https://api.prohandel.cloud/v2.29.1');
      console.log('2. Check if your API key and tenant ID have access to these endpoints');
      console.log('3. Contact ProHandel support for endpoint documentation');
      
      // Try tenant ID header variations anyway as a last resort
      console.log('\nTrying tenant ID header variations as a last resort...');
      const workingTenantIdHeader = await testTenantIdVariations(token, serverUrl);
      
      if (workingTenantIdHeader) {
        console.log(`\n✅ Found working tenant ID header: ${workingTenantIdHeader.name}`);
      }
    }
    
    console.log('\nTest complete!');
  } catch (error) {
    console.error('Test execution failed:', error);
  }
}

// Execute the tests
runTests();
