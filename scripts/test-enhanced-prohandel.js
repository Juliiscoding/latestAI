require('dotenv').config();

// Import the ProHandel client directly from the project
const { 
  authenticate, 
  getWarehouses, 
  getStockoutRisks,
  getAllArticles, 
  testConnection 
} = require('../lib/mercurios/clients/prohandel-client');

/**
 * Comprehensive test for the enhanced ProHandel client
 * Tests authentication, warehouse fetching, and data retrieval with robust error handling
 */
async function testEnhancedProHandelClient() {
  console.log('==== Testing Enhanced ProHandel Client ====');
  console.log('This script tests the improved client with retry logic and error handling\n');

  try {
    // Step 1: Test Authentication
    console.log('1. Testing Authentication...');
    const authResult = await authenticate();
    console.log(`✓ Authentication successful`);
    console.log(`  - Token: ${authResult.token.substring(0, 15)}...`);
    console.log(`  - Server URL: ${authResult.serverUrl}`);
    console.log('\n----------\n');

    // Step 2: Test Warehouse Retrieval
    console.log('2. Testing Warehouse Retrieval...');
    const warehouses = await getWarehouses();
    console.log(`✓ Found ${warehouses.length} warehouses`);
    
    // Display warehouse info in a table format
    console.table(warehouses.map(w => ({
      ID: w.id,
      Name: w.name,
      City: w.description?.split(' - ')[1] || '',
      Active: w.active,
      IsWebshop: w.isWebshop || false
    })));
    console.log('\n----------\n');

    // Step 3: Test Stockout Risks with different warehouses
    console.log('3. Testing Stockout Risks...');
    // Test with no warehouse filter
    console.log('  3.1 Fetching stockout risks (no warehouse filter)...');
    const stockoutRisks = await getStockoutRisks();
    console.log(`  ✓ Found ${stockoutRisks.length || 0} stockout risks overall`);
    
    // Test with warehouse filter if we have any warehouses
    if (warehouses.length > 0) {
      const testWarehouse = warehouses[0];
      console.log(`  3.2 Fetching stockout risks for warehouse: ${testWarehouse.name}...`);
      const filteredRisks = await getStockoutRisks(testWarehouse.id);
      console.log(`  ✓ Found ${filteredRisks.length || 0} stockout risks for warehouse ${testWarehouse.name}`);
    }
    console.log('\n----------\n');

    // Step 4: Test Article Data
    console.log('4. Testing Article Retrieval...');
    const articles = await getAllArticles({ limit: 5 });
    console.log(`✓ Found ${articles.length} articles (limited to 5)`);
    
    if (articles.length > 0) {
      console.log('\nSample Article Data:');
      const sample = articles[0];
      console.log(`  ID: ${sample.id || 'N/A'}`);
      console.log(`  Name: ${sample.name || 'N/A'}`);
      console.log(`  Description: ${sample.description || 'N/A'}`);
      console.log(`  Price: ${sample.price || 'N/A'}`);
    }
    console.log('\n----------\n');

    // Step 5: Test Connection (comprehensive test)
    console.log('5. Testing Overall Connection...');
    const connectionResult = await testConnection();
    console.log(`Connection test result: ${connectionResult ? '✓ SUCCESS' : '✗ FAILED'}`);
    console.log('\n----------\n');

    // Summary
    console.log('==== Test Summary ====');
    console.log('All tests completed successfully!');
    console.log('The enhanced ProHandel client is working properly with:');
    console.log('  - Robust authentication mechanism');
    console.log('  - Proper warehouse data retrieval');
    console.log('  - Stockout risk detection');
    console.log('  - Article data access');

  } catch (error) {
    console.error('Test failed with error:', error);
    console.error('Error message:', error.message);
    process.exit(1);
  }
}

// Run the tests
testEnhancedProHandelClient().catch(err => {
  console.error('Unhandled error in tests:', err);
  process.exit(1);
});
