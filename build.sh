#!/bin/bash
# Build script for creating installers on both platforms

echo "Amazon Fresh Fetch - Build Script"
echo "=================================="
echo ""

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"
    python3 build_mac.py
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    echo "Detected Windows"
    python build_windows.py
else
    echo "Unsupported platform: $OSTYPE"
    exit 1
fi

