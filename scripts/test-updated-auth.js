// Test ProHandel API connection with updated authentication format
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

console.log('=== Testing Updated ProHandel Authentication ===');
console.log('AUTH_URL:', config.AUTH_URL);
console.log('API_KEY:', config.API_KEY ? '✓ Set' : '✗ Missing');
console.log('API_SECRET:', config.API_SECRET ? '✓ Set' : '✗ Missing');
console.log('TENANT_ID:', config.TENANT_ID);

async function testAuthentication() {
  try {
    console.log('\nAuthenticating with new format...');
    const authUrl = `${config.AUTH_URL}/token`;
    console.log('Using URL:', authUrl);
    
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

    const tokens = await response.json();
    console.log('Authentication successful!');
    console.log('Full response:', JSON.stringify(tokens, null, 2));
    
    // Examine the structure to find the token
    const possibleTokenFields = ['access_token', 'token', 'accessToken', 'jwt', 'bearerToken'];
    let foundToken = null;
    
    for (const field of possibleTokenFields) {
      if (tokens[field]) {
        console.log(`Found token in field "${field}"`);
        foundToken = tokens[field];
        break;
      }
    }
    
    // If token is nested deeper in the response
    if (!foundToken && typeof tokens === 'object') {
      console.log('Looking for nested token fields...');
      const flattenObj = (obj, prefix = '') => {
        return Object.keys(obj).reduce((acc, key) => {
          const pre = prefix.length ? `${prefix}.` : '';
          if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
            Object.assign(acc, flattenObj(obj[key], pre + key));
          } else {
            acc[pre + key] = obj[key];
          }
          return acc;
        }, {});
      };
      
      const flatObj = flattenObj(tokens);
      for (const key in flatObj) {
        if (possibleTokenFields.some(field => key.toLowerCase().includes(field.toLowerCase()))) {
          console.log(`Found possible token in nested field "${key}": ${flatObj[key].toString().substring(0, 15)}...`);
          foundToken = flatObj[key];
        }
      }
    }
    
    return foundToken;
  } catch (error) {
    console.error('Authentication error:', error.message);
    return null;
  }
}

async function testApiEndpoint(token) {
  if (!token) {
    console.log('Cannot test API without token');
    return;
  }
  
  try {
    console.log('\nTesting API endpoint with token...');
    const url = `${config.API_URL}/locations`;
    console.log('URL:', url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Tenant-ID': config.TENANT_ID,
      },
    });
    
    console.log('Response status:', response.status, response.statusText);
    
    if (!response.ok) {
      console.log('API request failed');
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
    console.log('Warehouses:', JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('API request error:', error.message);
  }
}

// Run tests
async function runTests() {
  const token = await testAuthentication();
  if (token) {
    await testApiEndpoint(token);
  } else {
    console.log('\nAuthentication failed, cannot test API endpoints');
  }
  console.log('\nTesting complete');
}

runTests();
