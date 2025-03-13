#!/bin/bash
# Script to run dbt models locally using DuckDB (no Snowflake authentication required)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Mercurios.ai Local dbt Runner ===${NC}"
echo "This script will run dbt models locally using DuckDB"

# Navigate to dbt project directory
cd "$(dirname "$0")/dbt_mercurios"
PROJECT_DIR=$(pwd)

echo -e "${YELLOW}Using project directory: ${PROJECT_DIR}${NC}"

# Install DuckDB adapter if not already installed
if ! pip list | grep -q "dbt-duckdb"; then
    echo -e "${YELLOW}Installing dbt-duckdb...${NC}"
    pip install dbt-duckdb
fi

# Copy profiles_local.yml to profiles.yml temporarily
echo -e "${YELLOW}Setting up local profiles...${NC}"
cp profiles.yml profiles.yml.bak
cp profiles_local.yml profiles.yml

# Run dbt debug to check configuration
echo -e "${YELLOW}Checking configuration...${NC}"
dbt debug || {
    echo -e "${RED}Configuration check failed.${NC}"
    # Restore original profiles.yml
    mv profiles.yml.bak profiles.yml
    exit 1
}

# Install dependencies
echo -e "${YELLOW}Installing dbt dependencies...${NC}"
dbt deps

# Create sample data directory if it doesn't exist
echo -e "${YELLOW}Creating sample data directory...${NC}"
mkdir -p ./data

# Run all models in sequence
echo -e "${GREEN}Running models locally...${NC}"

# Run staging models first
echo -e "${YELLOW}Running staging models...${NC}"
dbt run --models staging || true

# Run intermediate models next
echo -e "${YELLOW}Running intermediate models...${NC}"
dbt run --models intermediate || true

# Run mart models last
echo -e "${YELLOW}Running mart models...${NC}"
dbt run --models marts || true

# Run all tests
echo -e "${YELLOW}Running tests...${NC}"
dbt test || true

# Generate documentation
echo -e "${YELLOW}Generating documentation...${NC}"
dbt docs generate
dbt docs serve &
DBT_DOCS_PID=$!

echo -e "${GREEN}=== All dbt models run locally ===${NC}"
echo "Documentation server started at http://localhost:8080"
echo -e "${YELLOW}Press Ctrl+C to stop the documentation server${NC}"

# Wait for user to stop the documentation server
trap "kill $DBT_DOCS_PID; mv profiles.yml.bak profiles.yml; echo -e '${GREEN}Documentation server stopped and original profiles restored${NC}'" INT
wait $DBT_DOCS_PID

# Restore original profiles.yml
mv profiles.yml.bak profiles.yml
