#!/bin/bash

# Run ETL Pipeline Script
# Usage: ./run_etl.sh [options]

# Set the directory to the script's directory
cd "$(dirname "$0")"

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "PostgreSQL is not running. Please start PostgreSQL and try again."
    exit 1
fi

# Check if the database exists, create it if it doesn't
if ! psql -h localhost -p 5432 -U postgres -lqt | cut -d \| -f 1 | grep -qw mercurios; then
    echo "Creating database 'mercurios'..."
    createdb -h localhost -p 5432 -U postgres mercurios
fi

# Setup the database schema
echo "Setting up database schema..."
python -m etl.run_etl --setup-db

# Generate JSON schemas
echo "Generating JSON schemas..."
python -m etl.run_etl --generate-schemas

# Run the ETL pipeline
echo "Running ETL pipeline..."
python -m etl.run_etl "$@"

# Show ETL status
echo "ETL status:"
python -m etl.run_etl --status
