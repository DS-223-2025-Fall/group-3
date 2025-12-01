#!/bin/bash
# Simple script to initialize the database
# Usage: ./init_db.sh

set -e

echo "=========================================="
echo "Database Initialization Script"
echo "=========================================="
echo ""
echo "This script will:"
echo "1. Stop all containers"
echo "2. Remove the database volume (postgres_data)"
echo "3. Start the database"
echo "4. Run the ETL process to load data"
echo ""
read -p "This will DELETE all existing database data. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "Step 1: Stopping containers and removing volumes..."
docker compose down -v

echo ""
echo "Step 2: Cleaning up old database directory (if exists)..."
# Clean up old directory if it exists (for backward compatibility with bind mounts)
rm -rf postgres_data/ 2>/dev/null || true

echo ""
echo "Step 3: Starting database..."
docker compose up -d db

echo ""
echo "Step 4: Waiting for database to be ready..."
sleep 5

echo ""
echo "Step 5: Running ETL to load data..."
docker compose run --rm etl bash run_etl.sh

echo ""
echo "=========================================="
echo "Database initialization complete!"
echo "=========================================="
echo ""
echo "You can now start all services with:"
echo "  docker compose up -d"

