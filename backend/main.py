# backend/main.py
import webview
import os
import sys
import logging
import platform
import psutil # For system resource monitoring

from backend.backend_api import BackendAPI
from backend.db_manager import DBManager
from backend.vfs_manager import VFSManager

# --- Logging Configuration ---
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True) # Ensure logs directory exists

# Configure logging for the entire application
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    logging.FileHandler(os.path.join(log_dir, "obpi_standalone.log")), # Log to file
    logging.StreamHandler(sys.stdout) # Log to console
  ]
)
logger = logging.getLogger('OBPI_Main')

# --- Path Configuration for Cross-Platform Compatibility ---
# Determine the base path for assets, essential for PyInstaller bundling.
if getattr(sys, 'frozen', False):
  # Running in a PyInstaller bundle
  BASE_DIR = sys._MEIPASS # Directory where PyInstaller extracts bundled files
  # Store persistent data (DB) in a user-specific data directory
  if platform.system() == "Windows":
    APP_DATA_DIR = os.path.join(os.environ.get('APPDATA', ''), '.obpi_data')
  elif platform.system() == "Darwin": # macOS
    APP_DATA_DIR = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', '.obpi_data')
  else: # Linux/Unix
    APP_DATA_DIR = os.path.join(os.path.expanduser('~'), '.obpi_data')

  os.makedirs(APP_DATA_DIR, exist_ok=True) # Ensure data directory exists
  DB_PATH = os.path.join(APP_DATA_DIR, 'obpi_persistent_data.db')
  HTML_PATH = os.path.join(BASE_DIR, 'src', 'index.html')
else:
  # Running in a normal Python development environment
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  DB_PATH = os.path.join(BASE_DIR, '..', 'obpi_data.db') # Relative path for dev mode
  HTML_PATH = os.path.join(BASE_DIR, '..', 'src', 'index.html')

logger.info(f"Application Base Directory: {BASE_DIR}")
logger.info(f"Database Path: {DB_PATH}")
logger.info(f"Frontend HTML Path: {HTML_PATH}")

# --- System Load Check on Launch ---
def perform_system_check():
  cpu_percent = psutil.cpu_percent(interval=1) # Measure CPU usage over 1 second
  ram_info = psutil.virtual_memory()
  ram_percent = ram_info.percent

  logger.info(f"System Check: CPU Usage: {cpu_percent}% | RAM Usage: {ram_percent}%")

  if cpu_percent > 80:
    logger.warning("High CPU usage detected. Consider closing other demanding applications for optimal performance.")
  if ram_percent > 85:
    logger.warning("High RAM usage detected. OBPI performance might be affected.")

# --- VFS Initialization ---
def create_initial_vfs_structure(vfs_manager: VFSManager):
  """
  Creates a default VFS structure if the database is new or empty.
  This ensures a consistent starting environment for the user.
  """
  logger.info("Checking initial VFS structure...")
  # Attempt to read a known default file; if it fails, assume VFS is empty
  readme_path = '/home/guest/readme.txt'
  readme_content = vfs_manager.get_file_content(readme_path)

  if readme_content.get('error') or not readme_content.get('content'):
    logger.info("VFS appears empty or default files are missing. Initializing default structure...")
    try:
      # Create core directories
      vfs_manager.create_directory('/home')
      vfs_manager.create_directory('/home/guest')
      vfs_manager.create_directory('/home/guest/Desktop')
      vfs_manager.create_directory('/home/guest/documents')
      vfs_manager.create_directory('/home/guest/downloads')
      vfs_manager.create_directory('/home/guest/python_scripts')
      vfs_manager.create_directory('/bin')
      vfs_manager.create_directory('/etc')
      vfs_manager.create_directory('/tmp')
      vfs_manager.create_directory('/pepx_raw_data') # Dedicated folder for PEPx raw data

      # Populate with initial files
      vfs_manager.write_file(readme_path,
                             f"Welcome to OBPI (Operational in Browser Persisted Instance) v1.0!\n"
                             f"This is a fully integrated virtual machine environment.\n"
                             f"All changes to the file system are persisted on your host machine at '{DB_PATH}'.\n\n"
                             f"Explore the Python IDE, embedded browser, and peripheral manager.\n"
                             f"Right-click desktop for options. Click 'OBPI' button for Start Menu.\n"
                             f"Type 'help' in the terminal for a list of commands.")
      vfs_manager.write_file('/home/guest/documents/project_plan_v1.0.txt',
                             f"Project Plan for OBPI v1.0 (Full Features)\n\n"
                             f"- Full Pywebview Integration\n"
                             f"- Persistent File System (SQLite backend)\n"
                             f"- Embedded Browser with History/Bookmarks\n"
                             f"- Complete Python IDE\n"
                             f"- PEPx Raw Data Storage (in VFS)\n"
                             f"- Real USB Peripheral Detection\n"
                             f"- Conceptual Compiler Framework\n"
                             f"- Enhanced AI Assistant")
      vfs_manager.write_file('/home/guest/python_scripts/hello.py',
                             'print("Hello from Python in OBPI!")\nprint("This script is managed by the backend VFS.")\n')
      vfs_manager.write_file('/home/guest/python_scripts/example.obsh',
                             'echo "Running OBPI Shell Script"\ndate\nls /home/guest/python_scripts\n')
      vfs_manager.write_file('/etc/obpi.config',
                             f"version=1.0\nprompt=guest@OBPI:~# \ntheme=dark\n")
      vfs_manager.write_file('/etc/hosts.sim',
                             '127.0.0.1 localhost.obpi\n10.0.0.1 virtual.server.obpi\n')

      # Populate /bin with dummy executables for CLI commands
      # These are just placeholders to make 'exec' and tab-completion work conceptually.
      # The actual logic is in AppManager.cliCommands in index.html.
      vfs_manager.write_file('/bin/curl', '#!/bin/simulated_executable\n# Handles web requests.')
      vfs_manager.write_file('/bin/wget', '#!/bin/simulated_executable\n# Downloads files from web.')
      vfs_manager.write_file('/bin/exec', '#!/bin/simulated_executable\n# Executes files.')
      vfs_manager.write_file('/bin/mv', '#!/bin/simulated_executable\n# Moves files.')
      vfs_manager.write_file('/bin/cp', '#!/bin/simulated_executable\n# Copies files.')
      vfs_manager.write_file('/bin/pkg_build', '#!/bin/obsh\n# Conceptual package builder.')
      vfs_manager.write_file('/bin/process_list', '#!/bin/obsh\n# Lists processes.')
      vfs_manager.write_file('/bin/resource_monitor', '#!/bin/obsh\n# Monitors system resources.')
      vfs_manager.write_file('/bin/usb_scan', '#!/bin/obsh\n# Scans USB devices.')
      vfs_manager.write_file('/bin/c_compile', '#!/bin/obsh\n# C compiler wrapper.')
      vfs_manager.write_file('/bin/cpp_compile', '#!/bin/obsh\n# C++ compiler wrapper.')
      vfs_manager.write_file('/bin/csharp_compile', '#!/bin/obsh\n# C# compiler wrapper.')
      vfs_manager.write_file('/bin/go_compile', '#!/bin/obsh\n# Go compiler wrapper.')
      vfs_manager.write_file('/bin/rust_compile', '#!/bin/obsh\n# Rust compiler wrapper.')
      vfs_manager.write_file('/bin/haskell_compile', '#!/bin/obsh\n# Haskell compiler wrapper.')
      vfs_manager.write_file('/bin/cobol_compile', '#!/bin/obsh\n# Cobol compiler wrapper.')
      vfs_manager.write_file('/bin/fortran_compile', '#!/bin/obsh\n# Fortran compiler wrapper.')
      vfs_manager.write_file('/bin/lua_run', '#!/bin/obsh\n# Lua interpreter wrapper.')
      vfs_manager.write_file('/bin/emcc_compile', '#!/bin/obsh\n# Emscripten conceptual compiler.')
      vfs_manager.write_file('/bin/hex_to_webgl', '#!/bin/obsh\n# Hex to WebGL conceptual compiler.')


      logger.info("Default VFS structure initialized successfully.")
    except Exception as e:
      logger.error(f"Error initializing default VFS structure: {e}")

# --- Main Application Launch Function ---
def main():
  logger.info("Starting OBPI application...")

  # 1. Perform System Check
  perform_system_check()

  # 2. Initialize DB Manager and VFS Manager
  db_manager = DBManager(db_path=DB_PATH)
  vfs_manager = VFSManager(db_manager) # VFSManager now takes db_manager as argument

  # 3. Create initial VFS structure if needed
  create_initial_vfs_structure(vfs_manager)

  # 4. Create the pywebview window and expose the BackendAPI
  # Pass the DB_PATH to BackendAPI so it can manage its own DBManager instance
  # The 'js_api' will be an instance of BackendAPI
  api = BackendAPI(None, db_file_path=DB_PATH) # Initialize with None for window, will set later

  window = webview.create_window(
    'OBPI - Operational in Browser Persisted Instance v1.0',
    url=HTML_PATH,
    js_api=api, # Pass the API instance
    min_size=(800, 600),
    frameless=False, # Set to True for a more "OS-like" feel without native frame
    easy_drag=True if platform.system() == "Windows" else False, # Easy drag for frameless windows
    # Ensure that the HTTP server for static files is enabled for pywebview
    # This is implicitly handled when `url` is a local file path.
  )

  # Now set the window object in the BackendAPI instance after it's created
  api.window = window

  # 5. Start the webview event loop
  # Set debug=False for production build to prevent console output
  webview.start(debug=True)
  logger.info("OBPI application closed.")

  # 6. Ensure database connection is closed on exit
  db_manager.close()

if __name__ == '__main__':
  main()WS
