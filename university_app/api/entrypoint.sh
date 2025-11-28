#!/bin/bash
set -e

# Directory where syllabi will be extracted
SYLLABI_DIR="/api/syllabi"
ZIP_FILE="/api/syllabi.zip"

# Create syllabi directory if it doesn't exist
mkdir -p "$SYLLABI_DIR"

# If zip file exists, unzip it
if [ -f "$ZIP_FILE" ]; then
    echo "Found syllabi zip file, extracting..."
    unzip -o "$ZIP_FILE" -d "$SYLLABI_DIR"
    
    # Handle nested syllabi directory (if zip contains syllabi/ folder)
    if [ -d "$SYLLABI_DIR/syllabi" ]; then
        echo "Moving files from nested syllabi directory..."
        mv "$SYLLABI_DIR/syllabi"/* "$SYLLABI_DIR/" 2>/dev/null || true
        rm -rf "$SYLLABI_DIR/syllabi"
        # Also clean up __MACOSX if present
        rm -rf "$SYLLABI_DIR/__MACOSX" 2>/dev/null || true
    fi
    
    echo "Syllabi extracted successfully to $SYLLABI_DIR"
else
    echo "No syllabi zip file found at $ZIP_FILE, skipping extraction"
fi

# Execute the main command (uvicorn)
exec "$@"

