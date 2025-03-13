# ProHandel Shop Endpoint Investigation Findings

## Summary

We investigated the ProHandel API's shop endpoint and discovered that while the endpoint exists, it returns an empty array. However, we found that the same data is available through the `branch` endpoint, which returns store/shop information.

## Detailed Findings

1. **Shop Endpoint Tests**:
   - The `/shop` endpoint exists and returns a valid response (empty array `[]`)
   - Various parameters (active=True, larger page size) did not change the result
   - Direct API request to the endpoint confirms it returns an empty array

2. **Alternative Endpoint Tests**:
   - Tested alternative names: 'shops', 'store', 'stores', 'branch', 'branches'
   - The `branch` endpoint returned 5 records with store/shop information
   - Other alternative names returned "Unknown entity" errors

3. **Branch Endpoint Data**:
   - The `branch` endpoint returns complete store information including:
     - Store IDs, names, and numbers
     - Addresses and contact information
     - Active status
     - Whether it's a webshop
     - GLN numbers
     - Opening hours (though null in the test data)

## Conclusion

The ProHandel API appears to use `branch` as the endpoint for store/shop data rather than `shop`. This is likely a naming convention in their system where physical locations are referred to as "branches" rather than "shops".

## Recommendations

1. **Update Code to Use Branch Endpoint**:
   - Modify the code to use the `branch` endpoint instead of `shop` when retrieving store data
   - Update any schema definitions or documentation to reflect this naming

2. **Code Example**:
   ```python
   # Instead of:
   shops = connector.get_entity_list('shop')
   
   # Use:
   shops = connector.get_entity_list('branch')
   ```

3. **Mapping Fields**:
   - Create a mapping between expected shop fields and branch fields if necessary
   - Key fields in the branch data include:
     - `id`: Unique identifier
     - `number`: Branch/store number
     - `name1`: Primary store name
     - `isActive`: Whether the store is active
     - `isWebshop`: Whether it's an online store
     - Address fields: `street`, `city`, `zipCode`, `countryNumber`
     - Contact: `telephoneNumber`, `email`, `fax`

4. **Update Lambda Function**:
   - Ensure the Lambda function uses 'branch' instead of 'shop' when fetching store data
   - Update any schema definitions in the Lambda function to reflect the correct field names

## Next Steps

1. Update the connector code to use the correct endpoint
2. Update documentation to reflect the correct endpoint name
3. Test the Lambda function with the updated endpoint name
4. Deploy the updated code to AWS
