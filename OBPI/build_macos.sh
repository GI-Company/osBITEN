#!/bin/bash
echo "Building OBPI for macOS..."

# Using icon.png for the application icon

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Install requirements
pip install -r requirements.txt

# Build with PyInstaller
pyinstaller obpi_macos.spec

echo "Build complete. Application is in dist/OBPI.app"

# Optional: Create a DMG file for distribution
# This requires create-dmg to be installed: brew install create-dmg
if command -v create-dmg &> /dev/null; then
    echo "Creating DMG file..."
    create-dmg \
        --volname "OBPI Installer" \
        --volicon "icon.icns" \
        --window-pos 200 120 \
        --window-size 800 400 \
        --icon-size 100 \
        --icon "OBPI.app" 200 190 \
        --hide-extension "OBPI.app" \
        --app-drop-link 600 185 \
        "dist/OBPI-macOS.dmg" \
        "dist/OBPI.app"
    echo "DMG file created at dist/OBPI-macOS.dmg"
else
    echo "create-dmg not found. Skipping DMG creation."
    echo "To create a DMG file, install create-dmg: brew install create-dmg"
fi
