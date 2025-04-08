// Script to explore ProHandel API endpoints for finding warehouses/locations
require('dotenv').config({ path: '.env.local' });
const fetch = require('node-fetch');

// Configuration
const config = {
  AUTH_URL: process.env.PROHANDEL_AUTH_URL || 'https://auth.prohandel.cloud/api/v4',
  API_KEY: process.env.PROHANDEL_API_KEY,
  API_SECRET: process.env.PROHANDEL_API_SECRET,
  TENANT_ID: process.env.TENANT_ID
};

console.log('=== ProHandel API Endpoint Explorer ===');

// Authenticate and get server URL
async function authenticate() {
  try {
    console.log('Authenticating with ProHandel API...');
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
    const token = authData.token.token.value;
    const serverUrl = authData.serverUrl;
    
    console.log('Authentication successful!');
    console.log('Server URL:', serverUrl);
    
    return { token, serverUrl };
  } catch (error) {
    console.error('Authentication error:', error.message);
    return { token: null, serverUrl: null };
  }
}

// Try to access an endpoint
async function tryEndpoint(token, serverUrl, endpoint) {
  try {
    const url = `${serverUrl}/api/v2${endpoint}`;
    console.log(`Testing endpoint: ${url}`);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-Tenant-ID': config.TENANT_ID,
        'Content-Type': 'application/json',
      }
    });
    
    console.log(`Status: ${response.status} ${response.statusText}`);
    
    if (response.ok) {
      try {
        const data = await response.json();
        console.log('Response data structure:', Object.keys(data));
        if (Array.isArray(data)) {
          console.log(`Found ${data.length} items`);
          if (data.length > 0) {
            console.log('First item properties:', Object.keys(data[0]));
          }
        }
        return { success: true, data };
      } catch (e) {
        console.log('Could not parse JSON response');
        return { success: true, data: await response.text() };
      }
    } else {
      return { success: false };
    }
  } catch (error) {
    console.error(`Error with endpoint ${endpoint}:`, error.message);
    return { success: false };
  }
}

// List of potential store/warehouse related endpoints to try
const potentialEndpoints = [
  '/locations',
  '/branches',
  '/stores',
  '/warehouses',
  '/shops',
  '/branch',
  '/store',
  '/warehouse',
  '/shop',
  '/filiale',
  '/filialen',
  '/standorte',
  '/standort',
  '/lager',
  '/outlet',
  '/outlets',
  
  // Try to get API resources list endpoints - these might list all available endpoints
  '/',
  '/api',
  '/resources',
  '/endpoints',
  
  // Try to query branch data differently
  '/branch?active=true',
  '/branch/all',
  
  // Try variations with full paths
  '/api/v2/branch',
  '/api/v2/branches',
  
  // Try the path from the docs URL
  '/articlesize',
  
  // Try to explore the common data structures to find location data
  '/customer',
  '/customer/location',
  '/article?PageSize=1',
  
  // Try Redoc API endpoints that might list available endpoints
  '/swagger',
  '/swagger.json',
  '/openapi.json',
  '/swagger-ui'
];

// Run the endpoint tests
async function exploreEndpoints() {
  try {
    // First authenticate
    const { token, serverUrl } = await authenticate();
    if (!token || !serverUrl) {
      console.log('❌ Authentication failed. Cannot explore endpoints.');
      return;
    }
    
    console.log('\nExploring possible warehouse/location endpoints...');
    
    const results = [];
    
    // Try each endpoint
    for (const endpoint of potentialEndpoints) {
      const result = await tryEndpoint(token, serverUrl, endpoint);
      
      if (result.success) {
        console.log(`✅ Found working endpoint: ${endpoint}`);
        results.push({
          endpoint,
          data: result.data
        });
      } else {
        console.log(`❌ Endpoint not found: ${endpoint}`);
      }
      
      // Add a small delay between requests to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    // Try to discover endpoints by fetching a known entity and checking its fields
    console.log('\nExamining article data for location references...');
    const articleResult = await tryEndpoint(token, serverUrl, '/article?PageSize=1');
    if (articleResult.success && Array.isArray(articleResult.data) && articleResult.data.length > 0) {
      const article = articleResult.data[0];
      
      // Print all fields that might indicate location
      const locationFields = Object.entries(article)
        .filter(([key, value]) => {
          const keyLower = key.toLowerCase();
          return keyLower.includes('location') || 
                 keyLower.includes('branch') || 
                 keyLower.includes('warehouse') || 
                 keyLower.includes('store') || 
                 keyLower.includes('shop') ||
                 keyLower.includes('filiale') ||
                 keyLower.includes('standort') ||
                 keyLower.includes('lager');
        });
      
      if (locationFields.length > 0) {
        console.log('Found location-related fields in article:', locationFields);
      } else {
        console.log('No location-related fields found in article data');
      }
    }
    
    console.log('\n=== Summary ===');
    if (results.length > 0) {
      console.log(`Found ${results.length} working endpoints:`);
      results.forEach(result => console.log(`- ${result.endpoint}`));
    } else {
      console.log('No warehouse/location endpoints found.');
      console.log('\nRecommendations:');
      console.log('1. Check the API documentation at https://developer.prohandel.cloud/');
      console.log('2. Try exploring the German terms "Filiale" or "Standort" for branches');
      console.log('3. Contact ProHandel support for the correct endpoints');
    }
  } catch (error) {
    console.error('Exploration failed:', error);
  }
}

// Start the exploration
exploreEndpoints();
