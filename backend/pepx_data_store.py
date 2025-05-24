# backend/pepx_data_store.py
import base64
import logging
from backend.vfs_manager import VFSManager

logger = logging.getLogger('PEPx_Data_Store')

# Define a VFS path for PEPx raw data storage
PEPX_RAW_DATA_VFS_PATH = "/pepx_raw_data"

class PEPxDataStore:
  def __init__(self, vfs_manager: VFSManager):
    self.vfs = vfs_manager
    # Ensure the base directory for PEPx raw data exists in VFS
    self._ensure_pepx_vfs_path()
    logger.info(f"PEPx Data Store initialized. Raw data stored in VFS path: {PEPX_RAW_DATA_VFS_PATH}")

  def _ensure_pepx_vfs_path(self):
    """Ensures the dedicated VFS path for PEPx raw data exists."""
    response = self.vfs.create_directory(PEPX_RAW_DATA_VFS_PATH)
    if response.get("error") and "already exists" not in response.get("error", ""):
      logger.error(f"Failed to ensure PEPx raw data VFS path: {response['error']}")
    else:
      logger.info(f"PEPx raw data VFS path '{PEPX_RAW_DATA_VFS_PATH}' ensured.")

  def _get_pepx_file_path(self, file_id):
    """Generates the VFS path for a PEPx raw data file."""
    return f"{PEPX_RAW_DATA_VFS_PATH}/{file_id}.bin"

  def store_raw_data(self, file_id, base64_data):
    """
    Stores base64 encoded raw data into a VFS file.
    :param file_id: Unique ID for the PEPx file.
    :param base64_data: The raw data, base64 encoded.
    :return: Success/error dictionary.
    """
    file_path = self._get_pepx_file_path(file_id)
    logger.info(f"PEPx Data Store: Storing raw data for ID '{file_id}' to VFS path '{file_path}'")
    try:
      # Decode base64 to bytes before storing, or store as base64 string directly
      # Storing as base64 string for simplicity as VFS stores text content.
      # If large binary data needs to be efficient, VFSManager.write_file might need
      # to handle bytes directly or use a different storage backend (e.g., host filesystem).
      # For now, base64 is fine for text content in VFS.
      write_response = self.vfs.write_file(file_path, base64_data)
      if write_response.get("error"):
        raise Exception(write_response["error"])
      logger.info(f"PEPx Data Store: Raw data for ID '{file_id}' stored successfully.")
      return {"status": "success"}
    except Exception as e:
      logger.error(f"PEPx Data Store: Failed to store raw data for ID '{file_id}': {e}")
      return {"error": str(e)}

  def get_raw_data(self, file_id):
    """
    Retrieves base64 encoded raw data from a VFS file.
    :param file_id: Unique ID for the PEPx file.
    :return: Dictionary with 'rawData' (base64 string) or 'error'.
    """
    file_path = self._get_pepx_file_path(file_id)
    logger.info(f"PEPx Data Store: Retrieving raw data for ID '{file_id}' from VFS path '{file_path}'")
    try:
      read_response = self.vfs.get_file_content(file_path)
      if read_response.get("error"):
        raise Exception(read_response["error"])
      raw_data_base64 = read_response.get("content", "")
      if not raw_data_base64:
        raise Exception(f"No raw data found for ID: {file_id}")
      logger.info(f"PEPx Data Store: Raw data for ID '{file_id}' retrieved successfully.")
      return {"rawData": raw_data_base64, "error": None}
    except Exception as e:
      logger.error(f"PEPx Data Store: Failed to retrieve raw data for ID '{file_id}': {e}")
      return {"rawData": None, "error": str(e)}

  def delete_raw_data(self, file_id):
    """
    Deletes raw data file from VFS.
    :param file_id: Unique ID for the PEPx file.
    :return: Success/error dictionary.
    """
    file_path = self._get_pepx_file_path(file_id)
    logger.info(f"PEPx Data Store: Deleting raw data for ID '{file_id}' from VFS path '{file_path}'")
    try:
      delete_response = self.vfs.delete_path(file_path, recursive=False)
      if delete_response.get("error"):
        raise Exception(delete_response["error"])
      logger.info(f"PEPx Data Store: Raw data for ID '{file_id}' deleted successfully.")
      return {"status": "success"}
    except Exception as e:
      logger.error(f"PEPx Data Store: Failed to delete raw data for ID '{file_id}': {e}")
      return {"error": str(e)}

  def reset_pepx_raw_data(self):
    """Deletes the entire PEPx raw data VFS path."""
    logger.warning(f"PEPx Data Store: Resetting all raw data in '{PEPX_RAW_DATA_VFS_PATH}'!")
    delete_response = self.vfs.delete_path(PEPX_RAW_DATA_VFS_PATH, recursive=True)
    if delete_response.get("error"):
      logger.error(f"Failed to reset PEPx raw data: {delete_response['error']}")
      return {"status": "error", "message": f"Failed to reset PEPx raw data: {delete_response['error']}"}
    # Re-create the base directory
    self._ensure_pepx_vfs_path()
    logger.info("PEPx Data Store: All raw data deleted and base directory re-created.")
    return {"status": "success", "message": "PEPx raw data reset successfully."}
