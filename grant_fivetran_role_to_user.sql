-- Grant Fivetran Service Role to User
-- This script grants the MERCURIOS_FIVETRAN_SERVICE role to the current user

-- Step 1: Grant the Fivetran service role to the user
GRANT ROLE MERCURIOS_FIVETRAN_SERVICE TO USER JULIUSRECHENBACH;

-- Step 2: Verify the grant
SHOW GRANTS TO USER JULIUSRECHENBACH;
