#!/bin/bash
echo "Building OBPI for Linux..."

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Install requirements
pip install -r requirements.txt

# Build with PyInstaller
pyinstaller obpi_linux.spec

echo "Build complete. Executable is in dist/OBPI-Linux"

# Create a .desktop file for Linux desktop integration
echo "Creating .desktop file..."
cat > dist/OBPI.desktop << EOL
[Desktop Entry]
Type=Application
Name=OBPI
Comment=Operational in Browser Persisted Instance
Exec=dist/OBPI-Linux
Icon=$(pwd)/icon.png
Terminal=false
Categories=Utility;Development;
EOL

echo ".desktop file created at dist/OBPI.desktop"
echo "To install the application system-wide, copy the executable and .desktop file to the appropriate locations:"
echo "sudo cp dist/OBPI-Linux /usr/local/bin/"
echo "sudo cp dist/OBPI.desktop /usr/share/applications/"
echo "sudo cp icon.png /usr/share/icons/hicolor/256x256/apps/obpi.png"
