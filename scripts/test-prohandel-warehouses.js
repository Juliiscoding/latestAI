// Test script to verify ProHandel warehouse/branch data
require('dotenv').config({ path: '.env.local' });
const fetch = require('node-fetch');

// Configuration
const config = {
  AUTH_URL: process.env.PROHANDEL_AUTH_URL || 'https://auth.prohandel.cloud/api/v4',
  API_KEY: process.env.PROHANDEL_API_KEY,
  API_SECRET: process.env.PROHANDEL_API_SECRET,
  TENANT_ID: process.env.TENANT_ID
};

console.log('=== ProHandel Warehouse/Branch Test ===');

// Authenticate
async function authenticate() {
  try {
    console.log('Authenticating with ProHandel API...');
    const response = await fetch(`${config.AUTH_URL}/token`, {
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
    
    if (!authData.token || !authData.token.token || !authData.token.token.value) {
      throw new Error('Unexpected authentication response format');
    }
    
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

// Get warehouse/branch data
async function getWarehouses(token, serverUrl) {
  try {
    console.log('\nFetching warehouse/branch data...');
    const url = `${serverUrl}/api/v2/branch`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-Tenant-ID': config.TENANT_ID,
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch warehouses: ${response.status} ${response.statusText}`);
    }
    
    const branches = await response.json();
    
    console.log(`Found ${branches.length} branches/warehouses`);
    
    // Map to warehouse format (as in our client)
    const warehouses = branches.map(branch => ({
      id: branch.id || branch.number.toString(),
      name: branch.name1 || `Branch ${branch.number}`,
      description: branch.city ? `${branch.name1} - ${branch.city}` : branch.name1,
      address: branch.street ? `${branch.street}, ${branch.zipCode} ${branch.city}` : undefined,
      active: branch.isActive !== false // Default to active if not specified
    }));
    
    console.log('\nWarehouse data:');
    warehouses.forEach((warehouse, index) => {
      console.log(`\n[${index + 1}] ${warehouse.name} (ID: ${warehouse.id})`);
      console.log(`   Description: ${warehouse.description}`);
      if (warehouse.address) console.log(`   Address: ${warehouse.address}`);
      console.log(`   Active: ${warehouse.active ? 'Yes' : 'No'}`);
    });
    
    return warehouses;
  } catch (error) {
    console.error('Error fetching warehouses:', error.message);
    return null;
  }
}

// Test filtering items by warehouse
async function testFilteringByWarehouse(token, serverUrl, warehouseId) {
  try {
    console.log(`\nTesting filtering with warehouse ID: ${warehouseId}`);
    
    // First try with the /article endpoint
    const articleUrl = `${serverUrl}/api/v2/article?PageSize=5&warehouse_id=${warehouseId}`;
    console.log('Testing article endpoint with warehouse filter...');
    
    let response = await fetch(articleUrl, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-Tenant-ID': config.TENANT_ID,
        'Content-Type': 'application/json',
      }
    });
    
    if (response.ok) {
      const articles = await response.json();
      console.log(`✅ Success! Found ${articles.length} articles for warehouse ${warehouseId}`);
      return true;
    } else {
      console.log(`❌ Article filtering failed: ${response.status} ${response.statusText}`);
    }
    
    // Try alternative query parameter formats
    const alternativeParams = [
      'branch_id',
      'branch',
      'location_id',
      'location',
      'shop_id',
      'shop',
      'store_id',
      'store'
    ];
    
    for (const param of alternativeParams) {
      const altUrl = `${serverUrl}/api/v2/article?PageSize=5&${param}=${warehouseId}`;
      console.log(`Testing with ${param} parameter...`);
      
      response = await fetch(altUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Tenant-ID': config.TENANT_ID,
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const articles = await response.json();
        console.log(`✅ Success with ${param}! Found ${articles.length} articles`);
        return true;
      } else {
        console.log(`❌ Failed with ${param}: ${response.status}`);
      }
    }
    
    console.log('Could not find a working filter parameter for warehouses');
    return false;
  } catch (error) {
    console.error('Error testing warehouse filtering:', error.message);
    return false;
  }
}

// Run all the tests
async function runTests() {
  try {
    // Step 1: Authenticate
    const { token, serverUrl } = await authenticate();
    if (!token || !serverUrl) {
      console.log('Authentication failed. Cannot proceed with tests.');
      return;
    }
    
    // Step 2: Get warehouses
    const warehouses = await getWarehouses(token, serverUrl);
    if (!warehouses || warehouses.length === 0) {
      console.log('No warehouses found. Cannot test filtering.');
      return;
    }
    
    // Step 3: Test filtering with the first warehouse
    const firstWarehouse = warehouses[0];
    const filteringWorks = await testFilteringByWarehouse(token, serverUrl, firstWarehouse.id);
    
    console.log('\n=== Test Summary ===');
    console.log('- Authentication: ✅ Successful');
    console.log(`- Warehouses: ✅ Found ${warehouses.length} warehouses`);
    console.log(`- Filtering by warehouse: ${filteringWorks ? '✅ Working' : '❌ Not supported'}`);
    
    if (!filteringWorks) {
      console.log('\nRecommendation:');
      console.log('The warehouses exist but filtering by warehouse might not be supported by the API.');
      console.log('You may need to fetch all data and filter it on the client side.');
    }
    
    console.log('\nTest completed successfully!');
  } catch (error) {
    console.error('Test execution failed:', error);
  }
}

// Run the tests
runTests();
