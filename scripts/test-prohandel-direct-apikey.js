// Test ProHandel API using direct API key authentication
require('dotenv').config({ path: '.env.local' });
const fetch = require('node-fetch');

// Get config from environment variables
const config = {
  API_URL: process.env.PROHANDEL_API_URL,
  API_KEY: process.env.PROHANDEL_API_KEY,
  API_SECRET: process.env.PROHANDEL_API_SECRET, // May not be needed
  TENANT_ID: process.env.TENANT_ID
};

console.log('=== ProHandel API Direct Connection Test ===');
console.log('API_URL:', config.API_URL);
console.log('TENANT_ID:', config.TENANT_ID);
console.log('API_KEY:', config.API_KEY ? '✓ Set' : '✗ Missing');

// Test getting articles directly with API key in headers
async function testGetArticles() {
  try {
    console.log('\nTesting article endpoint with API key headers...');
    const url = `${config.API_URL}/article?PageSize=2`;
    console.log('URL:', url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': config.API_KEY,
        'x-tenant-id': config.TENANT_ID
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
      return;
    }
    
    const data = await response.json();
    console.log('API request successful!');
    console.log('Articles sample:', JSON.stringify(data.slice(0, 2), null, 2));
  } catch (error) {
    console.error('API request error:', error.message);
  }
}

// Test with alternative auth method (Auth header with API key & secret)
async function testWithAlternativeAuth() {
  try {
    console.log('\nTrying alternative auth method (Authorization header)...');
    const url = `${config.API_URL}/article?PageSize=2`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `ApiKey ${config.API_KEY}:${config.API_SECRET}`,
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
      return;
    }
    
    const data = await response.json();
    console.log('API request successful!');
    console.log('Articles sample:', JSON.stringify(data.slice(0, 2), null, 2));
  } catch (error) {
    console.error('API request error:', error.message);
  }
}

// Test getting locations (warehouses)
async function testGetLocations(authMethod) {
  try {
    console.log(`\nTesting locations endpoint with ${authMethod} auth...`);
    const url = `${config.API_URL}/locations`;
    console.log('URL:', url);
    
    let headers = {
      'Content-Type': 'application/json'
    };
    
    if (authMethod === 'api-key') {
      headers['x-api-key'] = config.API_KEY;
      headers['x-tenant-id'] = config.TENANT_ID;
    } else if (authMethod === 'authorization') {
      headers['Authorization'] = `ApiKey ${config.API_KEY}:${config.API_SECRET}`;
      headers['X-Tenant-ID'] = config.TENANT_ID;
    }
    
    const response = await fetch(url, {
      method: 'GET',
      headers
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
      return;
    }
    
    const data = await response.json();
    console.log('API request successful!');
    console.log('Locations:', JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('API request error:', error.message);
  }
}

// Test other common auth patterns for REST APIs
async function testCommonAuthPatterns() {
  const patterns = [
    {
      name: "Bearer Token",
      headers: {
        'Authorization': `Bearer ${config.API_KEY}`,
        'X-Tenant-ID': config.TENANT_ID
      }
    },
    {
      name: "API-Key Header",
      headers: {
        'API-Key': config.API_KEY,
        'X-Tenant-ID': config.TENANT_ID
      }
    },
    {
      name: "API-Token Header",
      headers: {
        'API-Token': config.API_KEY,
        'X-Tenant-ID': config.TENANT_ID
      }
    },
    {
      name: "Basic Auth",
      headers: {
        'Authorization': `Basic ${Buffer.from(`${config.API_KEY}:${config.API_SECRET}`).toString('base64')}`,
        'X-Tenant-ID': config.TENANT_ID
      }
    }
  ];
  
  console.log('\nTesting common auth patterns...');
  const url = `${config.API_URL}/article?PageSize=1`;
  
  for (const pattern of patterns) {
    try {
      console.log(`\nTrying ${pattern.name}...`);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...pattern.headers
        }
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (response.ok) {
        console.log('✅ Success with', pattern.name);
        const data = await response.json();
        console.log('Sample response:', JSON.stringify(data[0], null, 2));
        return pattern; // Return the successful pattern
      } else {
        console.log('❌ Failed with', pattern.name);
      }
    } catch (error) {
      console.error(`Error with ${pattern.name}:`, error.message);
    }
  }
  
  return null;
}

// Run tests
async function runTests() {
  await testGetArticles();
  await testWithAlternativeAuth();
  
  // Test locations with both auth methods
  await testGetLocations('api-key');
  await testGetLocations('authorization');
  
  // If all else fails, try common patterns
  console.log('\nTrying common auth patterns as a last resort...');
  const successfulPattern = await testCommonAuthPatterns();
  
  if (successfulPattern) {
    console.log('\n✅ Found working authentication pattern:', successfulPattern.name);
    console.log('Headers:', JSON.stringify(successfulPattern.headers, null, 2));
  } else {
    console.log('\n❌ Could not find a working authentication pattern.');
    console.log('Recommendations:');
    console.log('1. Check if API URL is correct: ', config.API_URL);
    console.log('2. Verify your API key and tenant ID are valid');
    console.log('3. Contact ProHandel API support for the correct authentication method');
  }
  
  console.log('\nTesting complete');
}

runTests();
