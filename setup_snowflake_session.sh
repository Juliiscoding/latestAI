#!/bin/bash
# Snowflake Session Setup Script
# This script helps set up a persistent Snowflake session with minimal Duo prompts

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "===== Mercurios.ai Snowflake Session Setup ====="
echo "This script will set up a persistent Snowflake session to minimize Duo prompts."

# Check if account and user are set
if [ -z "$SNOWFLAKE_ACCOUNT" ] || [ -z "$SNOWFLAKE_USER" ]; then
    echo "Error: SNOWFLAKE_ACCOUNT or SNOWFLAKE_USER not set in .env file."
    exit 1
fi

echo "Setting up session for account: $SNOWFLAKE_ACCOUNT, user: $SNOWFLAKE_USER"

# Create a temporary file for SQL commands
TMP_SQL=$(mktemp)
cat > $TMP_SQL << EOF
-- Set session parameters to extend timeout
ALTER SESSION SET SESSION_TIMEOUT_MINS = 480; -- 8 hours
ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 3600; -- 1 hour
ALTER SESSION SET AUTOCOMMIT = TRUE;

-- Display current session parameters
SELECT 
    CURRENT_USER() as USER,
    CURRENT_ROLE() as ROLE,
    CURRENT_WAREHOUSE() as WAREHOUSE,
    CURRENT_DATABASE() as DATABASE,
    CURRENT_SCHEMA() as SCHEMA,
    CURRENT_SESSION() as SESSION_ID;

-- Show session timeout settings
SHOW PARAMETERS LIKE '%timeout%' IN SESSION;
EOF

echo "Starting persistent Snowflake connection..."
echo "You will need to authenticate with Duo once, then the session will remain active."
echo "Use Ctrl+D to exit the interactive SQL session when finished."
echo ""

# Run the Python script in interactive mode
python snowflake_persistent_connection.py --account "$SNOWFLAKE_ACCOUNT" --user "$SNOWFLAKE_USER" --warehouse "${SNOWFLAKE_WAREHOUSE:-MERCURIOS_ANALYTICS_WH}" --database "${SNOWFLAKE_DATABASE:-MERCURIOS_DATA}" --role "${SNOWFLAKE_ROLE:-ACCOUNTADMIN}" --file "$TMP_SQL"

# Clean up
rm $TMP_SQL

echo ""
echo "Session ended. To start a new persistent session, run this script again."
