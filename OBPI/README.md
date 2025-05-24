# OBPI - Operational in Browser Persisted Instance (Standalone)

This is a standalone, self-contained desktop application version of the OBPI operating system, built using `pywebview`. It bundles a Python backend with a JavaScript/HTML/CSS frontend to provide a persistent, interactive in-browser environment.

## Features:

* **Persistent Virtual File System (VFS):** All file and directory changes are saved to an SQLite database on the host machine.
* **Web Browser:** An encapsulated browser with persistent history and bookmarks.
* **AI Assistant:** A conceptual AI assistant with text-to-hex and hex-to-text conversion. (Extendable with real LLM APIs).
* **Python IDE/Runner:** Run and save Python scripts directly from the environment.
* **PEPx Pixel Storage:** A conceptual pixel-based storage system, now storing raw data efficiently in the VFS with metadata in the database.
* **Real Peripheral Management:** Scan for actual USB devices, cameras, and microphones connected to the host system.
* **Conceptual Compiler Framework:** Execute (compile and run) code in various languages (C, C++, C#, Go, Rust, Haskell, Cobol, Fortran, Lua) by leveraging compilers installed on the host machine. Also includes conceptual Emscripten (WASM/JS) and Hex-to-WebGL compilation.
* **Full-featured CLI:** A powerful command-line interface with standard Unix-like commands (ls, cd, cat, write, rm, mv, cp, exec, etc.) and OBPI-specific commands.
* **Window Management & Desktop:** Drag-and-drop windows, desktop icons, start menu, and context menus.
* **Theming:** Toggle between dark and light themes.

## Setup & Running (Development Mode):

1.  **Clone this repository:**
    ```bash
    git clone <repository_url>
    cd obpi_standalone
    ```
2.  **Create a Python Virtual Environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Install System Dependencies:**
  * **libusb:** Required for `pyusb` (USB device scanning).
    * **Linux (Debian/Ubuntu):** `sudo apt-get install libusb-1.0-0-dev`
    * **macOS (Homebrew):** `brew install libusb`
    * **Windows:** Download `libusb` binaries and place `libusb-1.0.dll` (or similar) in your system's PATH or directly beside your executable.
  * **External Compilers:** For the compiler features (C, C++, C#, Go, Rust, Haskell, Cobol, Fortran, Lua, Emscripten), you need to have the respective compilers installed on your host system and accessible via your system's PATH. Examples: `gcc`, `g++`, `dotnet`, `go`, `rustc`, `ghc`, `cobc`, `gfortran`, `lua`, `emcc`.
5.  **Run the application:**
    ```bash
    python main.py
    # Or on Unix-like systems (Linux, macOS):
    ./main.py
    ```

## Building a Standalone Executable (with PyInstaller):

### Automated Build Scripts

We've provided a master build script that can build for all platforms:

```bash
chmod +x build_all.sh
./build_all.sh
```

This interactive script will detect your current operating system and ask which platform(s) you want to build for:
- Windows
- macOS
- Linux
- Web OS
- All platforms
- Current platform only

Alternatively, you can use the platform-specific build scripts directly:

1. **Windows:**
   ```batch
   build_windows.bat
   ```
   This creates a single executable file at `dist/OBPI-Windows.exe`.

2. **macOS:**
   ```bash
   chmod +x build_macos.sh
   ./build_macos.sh
   ```
   This creates an application bundle at `dist/OBPI.app` and optionally a DMG installer if `create-dmg` is installed.

3. **Linux:**
   ```bash
   chmod +x build_linux.sh
   ./build_linux.sh
   ```
   This creates a single executable file at `dist/OBPI-Linux` and a .desktop file for desktop integration.

4. **Web OS Version:**
   ```bash
   chmod +x build_web.sh
   ./build_web.sh
   ```
   This creates a web-deployable version at `dist/OBPI-Web` with a Flask-based web server, Dockerfile, and docker-compose.yml for easy deployment.

#### Running the Web OS Version

After building the Web OS version, you can run it locally:

```bash
cd dist/OBPI-Web
python run_web_server.py
```

Or deploy it using Docker:

```bash
cd dist/OBPI-Web
docker-compose up -d
```

Then access the application in your browser at `http://localhost:5000`.

### Manual Build Process

If you prefer to build manually, you can use PyInstaller directly:

1. **Ensure PyInstaller is installed:** (It's in `requirements.txt`)
   ```bash
   pip install PyInstaller
   ```
2. **Navigate to the root of the `obpi_standalone` directory.**
3. **Run PyInstaller with the appropriate spec file:**
   ```bash
   # For Windows:
   pyinstaller obpi_windows.spec

   # For macOS:
   pyinstaller obpi_macos.spec

   # For Linux:
   pyinstaller obpi_linux.spec

   # For Web:
   pyinstaller obpi_web.spec
   ```

4. **Find the executable:** The executable will be created in the `dist/` directory within your project root.

## Persistence and Data Storage:

All application data (VFS, browser history, bookmarks, PEPx metadata, PEPx raw data) is stored persistently in an SQLite database file (`obpi_persistent_data.db`).
* **During development:** The DB file is created in the `obpi_standalone/` directory.
* **In standalone executable:** The DB file is created in a user-specific data directory (e.g., `~/.obpi_data/` on Linux/macOS, `%APPDATA%\.obpi_data\` on Windows) to ensure it persists even if the executable is moved or deleted.

## Potential Enhancements:

* **Real LLM Integration:** Replace `ai_core.py`'s rule-based responses with calls to actual LLM APIs (Google Gemini, OpenAI, etc.).
* **Network/Payment/API Systems:** Implement the conceptual "payment portal and API system specific to that project with fundable live network accessible APIs and private internals routed with redirect hyperlinks through a public DNS to be able to render client-side front end globally." This would likely involve a separate web server (e.g., Flask/FastAPI) running alongside or as a part of the backend, exposed via a public IP/DNS or a tunneling service like ngrok.
* **WASM Actual Execution:** Integrate a WASM runtime into the Python backend or directly into the frontend (using a JS WASM loader) for `emcc_compile` outputs.
* **Advanced UI:** Incorporate more advanced UI components or a full-fledged UI framework for a richer desktop experience.
* **File Upload/Download Dialogs:** Implement native file dialogs using `pywebview`'s `file_dialog` functionality.
* **Error Handling and User Feedback:** Enhance error reporting and provide more detailed user feedback for all operations.

---
