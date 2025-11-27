#!/bin/bash
# ETL Runner Script - Runs both data generation and database loading

set -e

echo "=========================================="
echo "Starting ETL Process"
echo "=========================================="

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set!"
    echo "Please check your .env file or docker-compose.yaml"
    exit 1
fi

echo "DATABASE_URL is set (hostname: $(echo $DATABASE_URL | grep -oP '://[^:]+' | cut -d'/' -f3))"

# Wait for database to be ready
echo "Waiting for database to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
until python -c "from Database.database import engine; from sqlalchemy import text; engine.connect().execute(text('SELECT 1'))" 2>&1; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "ERROR: Database connection failed after $MAX_RETRIES attempts"
    echo "Please check:"
    echo "  1. Database service is running"
    echo "  2. DATABASE_URL uses 'db' as hostname (not 'localhost')"
    echo "  3. Database credentials are correct"
    exit 1
  fi
  echo "Database not ready yet (attempt $RETRY_COUNT/$MAX_RETRIES), waiting 2 seconds..."
  sleep 2
done
echo "Database is ready!"

# Step 1: Generate CSV data
echo ""
echo "=========================================="
echo "Step 1: Generating University Data (CSV files)"
echo "=========================================="
python generate_university_data.py

# Step 2: Create tables and load data into database
echo ""
echo "=========================================="
echo "Step 2: Creating Tables and Loading Data into Database"
echo "=========================================="
python load_data_to_db.py

echo ""
echo "=========================================="
echo "ETL Process Completed Successfully!"
echo "=========================================="

