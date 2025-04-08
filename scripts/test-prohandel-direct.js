// Direct test of ProHandel API endpoints for warehouse filtering
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

console.log('Using API configuration:');
console.log('AUTH_URL:', config.AUTH_URL);
console.log('API_URL:', config.API_URL);
console.log('TENANT_ID:', config.TENANT_ID);
console.log('API_KEY:', config.API_KEY ? '✓ Set' : '✗ Missing');
console.log('API_SECRET:', config.API_SECRET ? '✓ Set' : '✗ Missing');

// Authentication function
async function authenticate() {
  try {
    console.log('\nAuthenticating with ProHandel API...');
    const response = await fetch(`${config.AUTH_URL}/oauth/token`, {
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

// Test warehouses endpoint
async function getWarehouses(token) {
  try {
    console.log('\nTesting warehouses endpoint...');
    const response = await fetch(`${config.API_URL}/locations`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Tenant-ID': config.TENANT_ID,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch warehouses: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Warehouse data:', JSON.stringify(data, null, 2));
    return data.locations || [];
  } catch (error) {
    console.error('Error fetching warehouses:', error.message);
    return [];
  }
}

// Test stockout risk data with warehouse filter
async function getStockoutRiskByWarehouse(token, warehouseId) {
  try {
    console.log(`\nTesting stockout risks with warehouse filter: ${warehouseId}`);
    const response = await fetch(`${config.API_URL}/inventory/stockout-risks?location_id=${warehouseId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Tenant-ID': config.TENANT_ID,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch stockout data: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    if (Array.isArray(data) && data.length > 0) {
      console.log(`Found ${data.length} stockout risk items`);
      console.log('Sample item:', JSON.stringify(data[0], null, 2));
    } else {
      console.log('No stockout risk data found for this warehouse');
    }
    return data;
  } catch (error) {
    console.error('Error fetching stockout data:', error.message);
    return [];
  }
}

// Test sales data with warehouse filter
async function getSalesByWarehouse(token, warehouseId) {
  try {
    const today = new Date();
    const fromDate = new Date(today);
    fromDate.setDate(today.getDate() - 30);

    const from = fromDate.toISOString().split('T')[0];
    const to = today.toISOString().split('T')[0];

    console.log(`\nTesting sales with warehouse filter: ${warehouseId} (${from} to ${to})`);
    const response = await fetch(`${config.API_URL}/sales?from=${from}&to=${to}&location_id=${warehouseId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Tenant-ID': config.TENANT_ID,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch sales data: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    if (Array.isArray(data) && data.length > 0) {
      console.log(`Found ${data.length} sales records`);
      console.log('Sample item:', JSON.stringify(data[0], null, 2));
    } else {
      console.log('No sales data found for this warehouse in the time period');
    }
    return data;
  } catch (error) {
    console.error('Error fetching sales data:', error.message);
    return [];
  }
}

// Run all the tests
async function runTests() {
  try {
    // Authenticate
    const token = await authenticate();
    
    // Get warehouses
    const warehouses = await getWarehouses(token);
    
    if (warehouses.length > 0) {
      const firstWarehouse = warehouses[0];
      console.log(`\nSelected warehouse for testing: ${firstWarehouse.name} (ID: ${firstWarehouse.id})`);
      
      // Test stockout risk data
      await getStockoutRiskByWarehouse(token, firstWarehouse.id);
      
      // Test sales data
      await getSalesByWarehouse(token, firstWarehouse.id);
    } else {
      console.log('No warehouses found to test with');
    }
    
    console.log('\nAll tests completed!');
  } catch (error) {
    console.error('Test execution failed:', error);
  }
}

// Run the tests
runTests();
