#!/bin/bash
set -e

SYLLABI_DIR="/api/syllabi"
ZIP_FILE="$SYLLABI_DIR/syllabi.zip"

# Extract syllabi.zip if it exists and no PDFs are present
if [ -f "$ZIP_FILE" ]; then
PDF_COUNT=$(find "$SYLLABI_DIR" -maxdepth 1 -name "*.pdf" 2>/dev/null | wc -l)
    if [ "$PDF_COUNT" -eq 0 ]; then
        echo "Extracting syllabi.zip..."
        unzip -qo "$ZIP_FILE" -d "$SYLLABI_DIR"
        # Handle nested directory structure
        [ -d "$SYLLABI_DIR/syllabi" ] && mv "$SYLLABI_DIR/syllabi"/* "$SYLLABI_DIR/" 2>/dev/null && rm -rf "$SYLLABI_DIR/syllabi"
        rm -rf "$SYLLABI_DIR/__MACOSX" 2>/dev/null || true
        echo "Syllabi extracted successfully"
    fi
fi

exec "$@"

