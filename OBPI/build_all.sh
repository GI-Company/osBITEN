#!/bin/bash
echo "OBPI Multi-Platform Build Script"
echo "================================"

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Determine the operating system
OS="$(uname -s)"
case "${OS}" in
    Linux*)     CURRENT_OS=Linux;;
    Darwin*)    CURRENT_OS=macOS;;
    CYGWIN*|MINGW*|MSYS*) CURRENT_OS=Windows;;
    *)          CURRENT_OS="UNKNOWN:${OS}"
esac

echo "Detected operating system: ${CURRENT_OS}"
echo ""

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    echo "Activating virtual environment..."
    source venv/Scripts/activate
fi

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Ask user which platforms to build for
echo "Which platforms would you like to build for?"
echo "1. Windows"
echo "2. macOS"
echo "3. Linux"
echo "4. Web OS"
echo "5. All platforms"
echo "6. Current platform only (${CURRENT_OS})"
read -p "Enter your choice (1-6): " CHOICE

build_windows() {
    echo ""
    echo "Building for Windows..."
    if [ "${CURRENT_OS}" = "Windows" ]; then
        # On Windows, use the batch file
        cmd.exe /c build_windows.bat
    else
        # On other platforms, use PyInstaller directly
        pyinstaller obpi_windows.spec
        echo "Windows build complete. Executable is in dist/OBPI-Windows.exe"
    fi
}

build_macos() {
    echo ""
    echo "Building for macOS..."
    if [ "${CURRENT_OS}" = "macOS" ]; then
        # On macOS, use the shell script
        chmod +x build_macos.sh
        ./build_macos.sh
    else
        # On other platforms, use PyInstaller directly
        pyinstaller obpi_macos.spec
        echo "macOS build complete. Application is in dist/OBPI.app"
        echo "Note: Building a macOS app on a non-macOS platform may not produce a fully functional application."
    fi
}

build_linux() {
    echo ""
    echo "Building for Linux..."
    if [ "${CURRENT_OS}" = "Linux" ]; then
        # On Linux, use the shell script
        chmod +x build_linux.sh
        ./build_linux.sh
    else
        # On other platforms, use PyInstaller directly
        pyinstaller obpi_linux.spec
        echo "Linux build complete. Executable is in dist/OBPI-Linux"
        echo "Note: Building a Linux executable on a non-Linux platform may not produce a fully functional application."
    fi
}

build_web() {
    echo ""
    echo "Building for Web OS..."
    chmod +x build_web.sh
    ./build_web.sh
}

case $CHOICE in
    1) build_windows ;;
    2) build_macos ;;
    3) build_linux ;;
    4) build_web ;;
    5)
        build_windows
        build_macos
        build_linux
        build_web
        ;;
    6)
        case "${CURRENT_OS}" in
            Windows) build_windows ;;
            macOS) build_macos ;;
            Linux) build_linux ;;
            *) echo "Unknown platform. Please choose a specific platform (1-4)." ;;
        esac
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "Build process completed."
echo "Check the dist/ directory for the built application(s)."
