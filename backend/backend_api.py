# backend/backend_api.py
import json
import logging
from datetime import datetime
from backend.vfs_manager import VFSManager
from backend.ai_core import AICore
from backend.compiler_runner import CompilerRunner
from backend.peripheral_scanner import PeripheralScanner
from backend.pepx_data_store import PEPxDataStore
from backend.db_manager import DBManager # Import DBManager to pass to other modules

logger = logging.getLogger('Backend_API')

class BackendAPI:
  def __init__(self, window, db_file_path="obpi_data.db"):
    self.window = window
    self.db = DBManager(db_path=db_file_path)
    self.vfs_manager = VFSManager(self.db)
    self.ai_core = AICore()
    self.compiler_runner = CompilerRunner()
    self.peripheral_scanner = PeripheralScanner()
    self.pepx_data_store = PEPxDataStore(self.vfs_manager)
    logger.info("Backend API initialized.")

  def log_to_python(self, message, level="info"):
    """Receives log messages from JavaScript."""
    if level == "info":
      logger.info(f"[JS_LOG]: {message}")
    elif level == "warn":
      logger.warning(f"[JS_LOG]: {message}")
    elif level == "error":
      logger.error(f"[JS_LOG]: {message}")
    elif level == "success":
      logger.info(f"[JS_LOG][SUCCESS]: {message}")
    else:
      logger.debug(f"[JS_LOG][{level.upper()}]: {message}")

  # --- VFS Manager API Calls ---
  def list_directory_backend(self, path):
    logger.info(f"API: list_directory_backend called for path: {path}")
    return self.vfs_manager.list_directory(path)

  def create_directory_backend(self, path):
    logger.info(f"API: create_directory_backend called for path: {path}")
    return self.vfs_manager.create_directory(path)

  def get_file_content_backend(self, path):
    logger.info(f"API: get_file_content_backend called for path: {path}")
    return self.vfs_manager.get_file_content(path)

  def write_file_backend(self, path, content):
    logger.info(f"API: write_file_backend called for path: {path}")
    return self.vfs_manager.write_file(path, content)

  def delete_path_backend(self, path, recursive):
    logger.info(f"API: delete_path_backend called for path: {path}, recursive: {recursive}")
    return self.vfs_manager.delete_path(path, recursive)

  def move_path_backend(self, source, destination):
    logger.info(f"API: move_path_backend called for source: {source}, dest: {destination}")
    return self.vfs_manager.move_path(source, destination)

  def copy_path_backend(self, source, destination):
    logger.info(f"API: copy_path_backend called for source: {source}, dest: {destination}")
    return self.vfs_manager.copy_path(source, destination)

  def reset_vfs_backend(self):
    logger.warning("API: reset_vfs_backend called. Resetting VFS and PEPx raw data.")
    vfs_reset_response = self.vfs_manager.reset_vfs()
    pepx_reset_response = self.pepx_data_store.reset_pepx_raw_data()
    # Also clear PEPx metadata in DB as they are tied to VFS raw data
    pepx_metadata_response = self._reset_pepx_metadata_backend()
    return {"status": "success", "message": f"VFS: {vfs_reset_response.get('message', 'reset incomplete')}. PEPx Raw: {pepx_reset_response.get('message', 'reset incomplete')}. PEPx Metadata: {pepx_metadata_response.get('message', 'reset incomplete')}"}


  # --- Browser Data API Calls ---
  def add_browser_history_backend(self, url, title):
    logger.info(f"API: add_browser_history_backend called for url: {url}")
    now = datetime.now().isoformat()
    try:
      self.db.execute_query(
        "INSERT INTO browser_history (url, title, timestamp) VALUES (?, ?, ?)",
        (url, title, now)
      )
      return {"status": "success"}
    except Exception as e:
      logger.error(f"Error adding browser history: {e}")
      return {"error": str(e)}

  def get_browser_history_backend(self):
    logger.info("API: get_browser_history_backend called.")
    try:
      history_rows = self.db.execute_query(
        "SELECT url, title, timestamp FROM browser_history ORDER BY timestamp DESC LIMIT 100",
        fetch_all=True
      )
      history_list = [dict(row) for row in history_rows]
      return {"history": history_list}
    except Exception as e:
      logger.error(f"Error getting browser history: {e}")
      return {"error": str(e)}

  def add_browser_bookmark_backend(self, url, title):
    logger.info(f"API: add_browser_bookmark_backend called for url: {url}")
    now = datetime.now().isoformat()
    try:
      self.db.execute_query(
        "INSERT OR REPLACE INTO browser_bookmarks (url, title, timestamp) VALUES (?, ?, ?)",
        (url, title, now)
      )
      return {"status": "success"}
    except Exception as e:
      logger.error(f"Error adding browser bookmark: {e}")
      return {"error": str(e)}

  def get_browser_bookmarks_backend(self):
    logger.info("API: get_browser_bookmarks_backend called.")
    try:
      bookmark_rows = self.db.execute_query(
        "SELECT url, title, timestamp FROM browser_bookmarks ORDER BY title ASC",
        fetch_all=True
      )
      bookmark_list = [dict(row) for row in bookmark_rows]
      return {"bookmarks": bookmark_list}
    except Exception as e:
      logger.error(f"Error getting browser bookmarks: {e}")
      return {"error": str(e)}

  def delete_browser_bookmark_backend(self, url):
    logger.info(f"API: delete_browser_bookmark_backend called for url: {url}")
    try:
      self.db.execute_query(
        "DELETE FROM browser_bookmarks WHERE url = ?",
        (url,)
      )
      return {"status": "success"}
    except Exception as e:
      logger.error(f"Error deleting browser bookmark: {e}")
      return {"error": str(e)}


  # --- AI Assistant API Calls ---
  def assistant_process_query(self, query):
    logger.info(f"API: assistant_process_query called for query: {query}")
    return self.ai_core.process_query(query)

  def assistant_text_to_hex(self, text_input):
    logger.info(f"API: assistant_text_to_hex called for text: {text_input[:30]}...")
    return self.ai_core.text_to_hex(text_input)

  def assistant_hex_to_text(self, hex_input):
    logger.info(f"API: assistant_hex_to_text called for hex: {hex_input[:30]}...")
    return self.ai_core.hex_to_text(hex_input)

  # --- Compiler API Calls ---
  def compile_and_run_code(self, lang, code_content, emcc_lang=None):
    logger.info(f"API: compile_and_run_code for lang: {lang}")
    return self.compiler_runner.compile_and_run_code(lang, code_content, emcc_lang)

  def compile_hex_to_webgl_backend(self, hex_code):
    logger.info("API: compile_hex_to_webgl_backend called.")
    # This calls the dedicated conceptual script via compiler_runner
    return self.compiler_runner.compile_and_run_code('hex_to_webgl', hex_code)


  # --- Peripheral Scanner API Calls ---
  def get_system_info_backend(self):
    logger.info("API: get_system_info_backend called.")
    return self.peripheral_scanner.get_system_info()

  def get_usb_devices_backend(self):
    logger.info("API: get_usb_devices_backend called.")
    return self.peripheral_scanner.get_usb_devices()

  def get_camera_devices_backend(self):
    logger.info("API: get_camera_devices_backend called.")
    return self.peripheral_scanner.get_camera_devices()

  def get_microphone_devices_backend(self):
    logger.info("API: get_microphone_devices_backend called.")
    return self.peripheral_scanner.get_microphone_devices()


  # --- PEPx Storage API Calls (Metadata in DB, Raw Data in VFS) ---
  def pepx_get_metadata_backend(self):
    logger.info("API: pepx_get_metadata_backend called.")
    try:
      metadata_rows = self.db.execute_query("SELECT * FROM pepx_metadata", fetch_all=True)
      files = {row['id']: dict(row) for row in metadata_rows}
      return {"files": files, "error": None}
    except Exception as e:
      logger.error(f"Error retrieving PEPx metadata: {e}")
      return {"files": {}, "error": str(e)}

  def pepx_sync_metadata_backend(self, files_dict):
    logger.info("API: pepx_sync_metadata_backend called. Syncing metadata from JS.")
    try:
      self.db.execute_query("DELETE FROM pepx_metadata") # Clear existing
      for file_id, meta in files_dict.items():
        self.db.execute_query(
          """
          INSERT INTO pepx_metadata (id, name, path, type, size, stored_byte_length, created, modified)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?)
          """,
          (meta['id'], meta['name'], meta['path'], meta['type'], meta['size'],
           meta.get('storedByteLength', 0), meta['created'], meta['modified'])
        )
      self.db.conn.commit()
      return {"status": "success"}
    except Exception as e:
      logger.error(f"Error syncing PEPx metadata: {e}")
      return {"error": str(e)}

  def _reset_pepx_metadata_backend(self):
    logger.warning("API: _reset_pepx_metadata_backend called. Deleting all PEPx metadata.")
    try:
      self.db.execute_query("DELETE FROM pepx_metadata")
      self.db.conn.commit()
      return {"status": "success", "message": "PEPx metadata reset."}
    except Exception as e:
      logger.error(f"Error resetting PEPx metadata: {e}")
      return {"status": "error", "message": f"Failed to reset PEPx metadata: {e}"}

  def pepx_store_raw_data_backend(self, file_id, base64_data):
    logger.info(f"API: pepx_store_raw_data_backend for ID: {file_id}")
    return self.pepx_data_store.store_raw_data(file_id, base64_data)

  def pepx_get_raw_data_backend(self, file_id):
    logger.info(f"API: pepx_get_raw_data_backend for ID: {file_id}")
    return self.pepx_data_store.get_raw_data(file_id)

  # --- Python Code Execution API Call ---
  def execute_python_code(self, code):
    """
    Executes Python code provided by the frontend and returns the result.

    Args:
        code (str): The Python code to execute

    Returns:
        dict: A dictionary with status ('success' or 'error') and output (str)
    """
    logger.info("API: execute_python_code called.")
    import sys
    from io import StringIO

    # Capture stdout and stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = StringIO()
    redirected_error = StringIO()
    sys.stdout = redirected_output
    sys.stderr = redirected_error

    try:
        # Execute the code
        exec(code)
        output = redirected_output.getvalue()
        return {"status": "success", "output": output}
    except Exception as e:
        # Get the error message
        error_output = redirected_error.getvalue()
        if not error_output:
            error_output = str(e)
        return {"status": "error", "output": error_output}
    finally:
        # Restore stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
