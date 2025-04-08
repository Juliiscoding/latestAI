// Test ProHandel API connection directly using the existing client implementation
require('dotenv').config({ path: '.env.local' });

// Import directly the implementation we're already using in the application
const prohandelClient = require('../lib/mercurios/clients/prohandel-client.js').default;

async function testConnection() {
  try {
    console.log('Testing ProHandel API connection...');
    const connectionTest = await prohandelClient.testProHandelConnection();
    console.log('Connection test result:', connectionTest);
    
    if (connectionTest && connectionTest.success) {
      // Test warehouse endpoint
      console.log('\nTesting warehouses endpoint...');
      try {
        const warehouses = await prohandelClient.getWarehouses();
        console.log('Warehouses:', JSON.stringify(warehouses, null, 2));
        
        if (warehouses.data && warehouses.data.length > 0) {
          const firstWarehouse = warehouses.data[0];
          console.log(`\nTesting stockout data with warehouse filter: ${firstWarehouse.id}`);
          
          // Test stockout data with warehouse filter
          const stockoutData = await prohandelClient.getStockoutDataWithWarehouse(firstWarehouse.id);
          console.log('Stockout data sample:', JSON.stringify(stockoutData.slice(0, 2), null, 2));
          console.log(`...and ${stockoutData.length - 2} more items`);
        }
      } catch (apiError) {
        console.error('API test failed:', apiError);
      }
    }
  } catch (error) {
    console.error('Connection test failed:', error);
  }
}

// Run the tests
testConnection().catch(console.error);
