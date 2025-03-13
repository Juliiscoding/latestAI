#!/bin/bash
# Script to run dbt models for Mercurios.ai with key pair authentication

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Mercurios.ai dbt Model Runner ===${NC}"
echo "This script will run all dbt models in a single authenticated session"
echo -e "${YELLOW}Using key pair authentication (no Duo prompts)${NC}"

# Navigate to dbt project directory
cd "$(dirname "$0")/dbt_mercurios"
PROJECT_DIR=$(pwd)

echo -e "${YELLOW}Using project directory: ${PROJECT_DIR}${NC}"

# Run all models in a single session to minimize authentication prompts
echo -e "${YELLOW}Starting single-session dbt run...${NC}"

# Run a single dbt debug to authenticate once
echo -e "${YELLOW}Authenticating with Snowflake using key pair...${NC}"
dbt debug || {
    echo -e "${RED}Authentication failed. Please check your key pair configuration.${NC}"
    exit 1
}

# Install dependencies
echo -e "${YELLOW}Installing dbt dependencies...${NC}"
dbt deps

# Run all models in sequence
echo -e "${GREEN}Authentication successful! Running models...${NC}"

# Run staging models first
echo -e "${YELLOW}Running staging models...${NC}"
dbt run --models staging

# Run intermediate models next
echo -e "${YELLOW}Running intermediate models...${NC}"
dbt run --models intermediate

# Run mart models last
echo -e "${YELLOW}Running mart models...${NC}"
dbt run --models marts

# Run all tests
echo -e "${YELLOW}Running tests...${NC}"
dbt test

# Generate documentation
echo -e "${YELLOW}Generating documentation...${NC}"
dbt docs generate
dbt docs serve &
DBT_DOCS_PID=$!

echo -e "${GREEN}=== All dbt models run successfully ===${NC}"
echo "Documentation server started at http://localhost:8080"
echo -e "${YELLOW}Press Ctrl+C to stop the documentation server${NC}"

# Wait for user to stop the documentation server
trap "kill $DBT_DOCS_PID; echo -e '${GREEN}Documentation server stopped${NC}'" INT
wait $DBT_DOCS_PID
