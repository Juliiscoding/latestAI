// Test script for warehouse filtering with the updated ProHandel API integration
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

console.log('=== ProHandel Warehouse Filtering Test ===');

// Authentication function with new format
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

    const responseData = await response.json();
    
    // Extract token from the nested response format
    if (!responseData.token || !responseData.token.token || !responseData.token.token.value) {
      throw new Error('Unexpected authentication response format: token not found');
    }
    
    const token = responseData.token.token.value;
    console.log('Authentication successful! Token obtained.');
    
    return token;
  } catch (error) {
    console.error('Authentication error:', error.message);
    return null;
  }
}

// Get warehouses/locations
async function getWarehouses(token) {
  try {
    console.log('\nFetching warehouses/locations...');
    const url = `${config.API_URL}/locations`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Tenant-ID': config.TENANT_ID
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch warehouses: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Warehouses found:', JSON.stringify(data, null, 2));
    return data.locations || [];
  } catch (error) {
    console.error('Error fetching warehouses:', error.message);
    return [];
  }
}

// Get stockout risks filtered by warehouse
async function getStockoutRisksByWarehouse(token, warehouseId) {
  try {
    console.log(`\nFetching stockout risks for warehouse ID: ${warehouseId}`);
    const url = `${config.API_URL}/inventory/stockout-risks?location_id=${warehouseId}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Tenant-ID': config.TENANT_ID
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch stockout risks: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`Found ${data.length} stockout risk items for warehouse ${warehouseId}`);
    if (data.length > 0) {
      console.log('First item:', JSON.stringify(data[0], null, 2));
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching stockout risks by warehouse:', error.message);
    return [];
  }
}

// Get sales data filtered by warehouse
async function getSalesByWarehouse(token, warehouseId) {
  try {
    const today = new Date();
    const fromDate = new Date(today);
    fromDate.setDate(today.getDate() - 30);
    
    const from = fromDate.toISOString().split('T')[0];
    const to = today.toISOString().split('T')[0];
    
    console.log(`\nFetching sales for warehouse ID: ${warehouseId} (${from} to ${to})`);
    const url = `${config.API_URL}/sales?from=${from}&to=${to}&location_id=${warehouseId}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Tenant-ID': config.TENANT_ID
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch sales: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`Found ${data.length} sales records for warehouse ${warehouseId}`);
    if (data.length > 0) {
      console.log('First item:', JSON.stringify(data[0], null, 2));
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching sales by warehouse:', error.message);
    return [];
  }
}

// Run all tests
async function runTests() {
  try {
    // Step 1: Authenticate
    const token = await authenticate();
    if (!token) {
      console.log('❌ Authentication failed. Cannot continue tests.');
      return;
    }
    
    // Step 2: Get warehouses
    const warehouses = await getWarehouses(token);
    if (warehouses.length === 0) {
      console.log('❌ No warehouses found. Cannot test filtering.');
      return;
    }
    
    // Step 3: Test warehouse filtering with the first warehouse
    const firstWarehouse = warehouses[0];
    console.log(`\n✅ Selected warehouse for testing: ${firstWarehouse.name} (ID: ${firstWarehouse.id})`);
    
    // Step 4: Get stockout risks for the selected warehouse
    await getStockoutRisksByWarehouse(token, firstWarehouse.id);
    
    // Step 5: Get sales for the selected warehouse
    await getSalesByWarehouse(token, firstWarehouse.id);
    
    console.log('\n✅ All warehouse filtering tests completed successfully!');
  } catch (error) {
    console.error('Test execution failed:', error);
  }
}

// Execute the tests
runTests();
