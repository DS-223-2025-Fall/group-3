#!/bin/bash
set -e

# Directory where syllabi will be extracted
SYLLABI_DIR="/api/syllabi"
# Zip file is mounted from ./syllabi directory (works even if file doesn't exist)
ZIP_FILE="/syllabi_source/syllabi.zip"

# Create syllabi directory if it doesn't exist
mkdir -p "$SYLLABI_DIR"

# Check if syllabi are already extracted (avoid re-extracting on every restart)
# Count PDF files in the syllabi directory
PDF_COUNT=$(find "$SYLLABI_DIR" -maxdepth 1 -name "*.pdf" 2>/dev/null | wc -l)

if [ -f "$ZIP_FILE" ] && [ "$PDF_COUNT" -eq 0 ]; then
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
elif [ -f "$ZIP_FILE" ] && [ "$PDF_COUNT" -gt 0 ]; then
    echo "Syllabi directory already contains $PDF_COUNT PDF file(s), skipping extraction"
elif [ ! -f "$ZIP_FILE" ]; then
    echo "No syllabi zip file found at $ZIP_FILE, skipping extraction"
    echo "Note: Place syllabi.zip in ./syllabi/ directory to enable syllabus file serving"
fi

# Execute the main command (uvicorn)
exec "$@"

