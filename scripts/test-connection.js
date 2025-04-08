// Test ProHandel API connection directly using the existing client implementation
require('dotenv').config({ path: '.env.local' });

// Import directly from the module (not as default)
const prohandelClient = require('../lib/mercurios/clients/prohandel-client');

async function testConnection() {
  try {
    console.log('Testing ProHandel API connection...');
    console.log('ENVIRONMENT:', process.env.NODE_ENV || 'development');
    console.log('API URLs:', {
      PROHANDEL_AUTH_URL: process.env.PROHANDEL_AUTH_URL,
      TENANT_ID: process.env.TENANT_ID ? ' Set' : ' Missing',
      MCP_API_URL: process.env.NEXT_PUBLIC_MCP_API_URL,
      USE_REAL_MCP: process.env.NEXT_PUBLIC_USE_REAL_MCP
    });
    
    try {
      // First authenticate
      console.log('\n Testing authentication...');
      const auth = await prohandelClient.authenticate();
      console.log(' Authentication successful!');
      console.log('  Token received:', auth.token ? ' Yes' : ' No');
      console.log('  Server URL:', auth.serverUrl || 'Not provided');
      
      // Test warehouse endpoint
      console.log('\n Testing warehouses endpoint...');
      const warehouses = await prohandelClient.getWarehouses(true);
      console.log(' Warehouses retrieved:', warehouses.length);
      console.log(JSON.stringify(warehouses.slice(0, 2), null, 2));
      
      if (warehouses && warehouses.length > 0) {
        const firstWarehouse = warehouses[0];
        console.log(`\n Testing stockout risks with warehouse filter: ${firstWarehouse.id}`);
        
        // Test stockout data with warehouse filter
        const stockoutData = await prohandelClient.getStockoutRisks(firstWarehouse.id, true);
        console.log(' Stockout risks retrieved:', stockoutData.length);
        console.log(JSON.stringify(stockoutData.slice(0, 2), null, 2));
        
        // Test sales data
        console.log(`\n Testing sales data with warehouse filter: ${firstWarehouse.id}`);
        const salesData = await prohandelClient.getSales(
          undefined, // fromDate - default to 30 days ago
          undefined, // toDate - default to today
          firstWarehouse.id,
          true // useRealData
        );
        console.log(' Sales data retrieved:', salesData.length || (salesData ? 'Object returned' : 'No data'));
        console.log(JSON.stringify(salesData.slice ? salesData.slice(0, 2) : salesData, null, 2));
      }
    } catch (apiError) {
      console.error(' API test failed:', apiError);
    }
  } catch (error) {
    console.error(' Connection test failed:', error);
  }
}

// Run the tests
console.log(' STARTING PROHANDEL API CONNECTION TEST');
console.log('=============================================');
testConnection()
  .then(() => console.log('\n TEST COMPLETED'))
  .catch(error => console.error('\n TEST FAILED:', error));
