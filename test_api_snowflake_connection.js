// Test script for API Snowflake connection
require('dotenv').config();
const { SnowflakeAPI } = require('../mercurios_api/src/datasources/snowflake');

async function testConnection() {
  console.log('Testing Snowflake connection from API...');
  console.log('Environment variables:');
  console.log(`  SNOWFLAKE_ACCOUNT: ${process.env.SNOWFLAKE_ACCOUNT}`);
  console.log(`  SNOWFLAKE_USERNAME: ${process.env.SNOWFLAKE_USERNAME}`);
  console.log(`  SNOWFLAKE_WAREHOUSE: ${process.env.SNOWFLAKE_WAREHOUSE}`);
  console.log(`  SNOWFLAKE_DATABASE: ${process.env.SNOWFLAKE_DATABASE}`);
  console.log(`  SNOWFLAKE_SCHEMA: ${process.env.SNOWFLAKE_SCHEMA}`);
  console.log(`  SNOWFLAKE_ROLE: ${process.env.SNOWFLAKE_ROLE}`);
  
  // Create Snowflake API instance
  const snowflakeAPI = new SnowflakeAPI();
  
  // Wait for connection to initialize
  console.log('Waiting for connection to initialize...');
  await new Promise(resolve => setTimeout(resolve, 5000));
  
  // Test connection
  console.log('\nTesting connection...');
  const connectionTest = await snowflakeAPI.testConnection();
  console.log('Connection test result:', connectionTest);
  
  if (connectionTest.success) {
    // Query sample data
    console.log('\nQuerying sample inventory data...');
    const inventoryData = await snowflakeAPI.query('SELECT * FROM inventory LIMIT 5');
    
    if (inventoryData) {
      console.log('Successfully retrieved inventory data:');
      console.log(JSON.stringify(inventoryData, null, 2));
    } else {
      console.log('Failed to retrieve inventory data');
    }
    
    // Query sample Shopify orders
    console.log('\nQuerying sample Shopify orders...');
    const shopifyData = await snowflakeAPI.query('SELECT * FROM shopify_orders LIMIT 5');
    
    if (shopifyData) {
      console.log('Successfully retrieved Shopify orders:');
      console.log(JSON.stringify(shopifyData, null, 2));
    } else {
      console.log('Failed to retrieve Shopify orders');
    }
  }
  
  // Close connection
  console.log('\nTest complete. Exiting...');
  process.exit(0);
}

// Run the test
testConnection().catch(error => {
  console.error('Error during test:', error);
  process.exit(1);
});
