// Test script for ProHandel API integration
require('dotenv').config({ path: '.env.local' });
const fetch = require('node-fetch');

const PROHANDEL_CONFIG = {
  API_KEY: process.env.PROHANDEL_API_KEY,
  API_SECRET: process.env.PROHANDEL_API_SECRET,
  AUTH_URL: process.env.PROHANDEL_AUTH_URL,
  API_URL: process.env.PROHANDEL_API_URL,
  TENANT_ID: process.env.TENANT_ID,
};

// Authenticate and get token
async function authenticate() {
  try {
    console.log('Authenticating with ProHandel API...');
    const response = await fetch(`${PROHANDEL_CONFIG.AUTH_URL}/oauth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        grant_type: 'client_credentials',
        client_id: PROHANDEL_CONFIG.API_KEY,
        client_secret: PROHANDEL_CONFIG.API_SECRET,
        tenant_id: PROHANDEL_CONFIG.TENANT_ID
      }),
    });

    if (!response.ok) {
      throw new Error(`Authentication failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Authentication successful!');
    return data.access_token;
  } catch (error) {
    console.error('Authentication error:', error.message);
    process.exit(1);
  }
}

// Test getting warehouses/locations
async function testGetWarehouses(token) {
  try {
    console.log('\nTesting /locations endpoint...');
    const response = await fetch(`${PROHANDEL_CONFIG.API_URL}/locations`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Tenant-ID': PROHANDEL_CONFIG.TENANT_ID,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch warehouses: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Warehouse/Locations data:');
    console.log(JSON.stringify(data, null, 2));
    return data;
  } catch (error) {
    console.error('Error fetching warehouses:', error.message);
    return null;
  }
}

// Test getting stockout risk data with warehouse filter
async function testGetStockoutRiskByWarehouse(token, warehouseId) {
  try {
    console.log(`\nTesting /inventory/stockout-risks with warehouse ${warehouseId}...`);
    const response = await fetch(`${PROHANDEL_CONFIG.API_URL}/inventory/stockout-risks?location_id=${warehouseId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Tenant-ID': PROHANDEL_CONFIG.TENANT_ID,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch stockout data: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Stockout risk data for warehouse:');
    console.log(JSON.stringify(data.slice(0, 2), null, 2)); // Show just the first 2 items
    console.log(`...and ${data.length - 2} more items`);
    return data;
  } catch (error) {
    console.error('Error fetching stockout data for warehouse:', error.message);
    return null;
  }
}

// Test getting sales data with warehouse filter
async function testGetSalesByWarehouse(token, warehouseId) {
  try {
    const today = new Date();
    const fromDate = new Date(today);
    fromDate.setDate(today.getDate() - 30);

    const from = fromDate.toISOString().split('T')[0];
    const to = today.toISOString().split('T')[0];

    console.log(`\nTesting /sales with warehouse ${warehouseId} from ${from} to ${to}...`);
    const response = await fetch(`${PROHANDEL_CONFIG.API_URL}/sales?from=${from}&to=${to}&location_id=${warehouseId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Tenant-ID': PROHANDEL_CONFIG.TENANT_ID,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch sales data: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Sales data for warehouse:');
    console.log(JSON.stringify(data.slice(0, 2), null, 2)); // Show just the first 2 items
    console.log(`...and ${data.length - 2} more items`);
    return data;
  } catch (error) {
    console.error('Error fetching sales data for warehouse:', error.message);
    return null;
  }
}

// Run all tests
async function runTests() {
  console.log('Testing ProHandel API integration...');
  console.log('================================');
  
  const token = await authenticate();
  
  // Test warehouses endpoint
  const warehousesData = await testGetWarehouses(token);
  
  if (warehousesData && warehousesData.locations && warehousesData.locations.length > 0) {
    const firstWarehouseId = warehousesData.locations[0].id;
    
    // Test stockout risk with warehouse filter
    await testGetStockoutRiskByWarehouse(token, firstWarehouseId);
    
    // Test sales with warehouse filter
    await testGetSalesByWarehouse(token, firstWarehouseId);
  }
  
  console.log('\nAll tests completed!');
}

// Execute tests
runTests().catch(err => {
  console.error('Test execution failed:', err);
  process.exit(1);
});
