# backend/db_manager.py
import sqlite3
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DB_Manager')

class DBManager:
  def __init__(self, db_path="obpi_data.db"):
    self.db_path = db_path
    self._ensure_db_path_exists()
    self.conn = None
    self.connect()
    self.initialize_db()

  def _ensure_db_path_exists(self):
    db_dir = os.path.dirname(self.db_path)
    if db_dir and not os.path.exists(db_dir):
      os.makedirs(db_dir)

  def connect(self):
    try:
      self.conn = sqlite3.connect(self.db_path)
      self.conn.row_factory = sqlite3.Row # Allows accessing columns by name
      logger.info(f"Connected to database: {self.db_path}")
    except sqlite3.Error as e:
      logger.error(f"Database connection error: {e}")
      self.conn = None # Ensure conn is None if connection fails

  def close(self):
    if self.conn:
      self.conn.close()
      logger.info("Database connection closed.")
      self.conn = None

  def execute_query(self, query, params=(), fetch_one=False, fetch_all=False):
    if not self.conn:
      logger.error("Database not connected. Cannot execute query.")
      return None if fetch_one else []

    try:
      cursor = self.conn.cursor()
      cursor.execute(query, params)
      self.conn.commit()
      if fetch_one:
        return cursor.fetchone()
      elif fetch_all:
        return cursor.fetchall()
      return cursor.rowcount # For INSERT/UPDATE/DELETE
    except sqlite3.Error as e:
      logger.error(f"Database query error: {e} - Query: {query} - Params: {params}")
      return None if fetch_one else []

  def initialize_db(self):
    if not self.conn:
      logger.error("Database not connected. Cannot initialize tables.")
      return

    # VFS metadata table
    self.execute_query("""
                       CREATE TABLE IF NOT EXISTS vfs_nodes (
                                                              path TEXT PRIMARY KEY,
                                                              name TEXT NOT NULL,
                                                              type TEXT NOT NULL, -- 'file' or 'dir'
                                                              size INTEGER DEFAULT 0,
                                                              content BLOB,       -- Only for files, stored directly in DB for simplicity
                                                              created_at TEXT NOT NULL,
                                                              modified_at TEXT NOT NULL
                       )
                       """)
    logger.info("Table 'vfs_nodes' ensured.")

    # Browser History table
    self.execute_query("""
                       CREATE TABLE IF NOT EXISTS browser_history (
                                                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                    url TEXT NOT NULL,
                                                                    title TEXT NOT NULL,
                                                                    timestamp TEXT NOT NULL
                       )
                       """)
    self.execute_query("CREATE INDEX IF NOT EXISTS idx_history_url ON browser_history (url)")
    logger.info("Table 'browser_history' ensured.")

    # Browser Bookmarks table
    self.execute_query("""
                       CREATE TABLE IF NOT EXISTS browser_bookmarks (
                                                                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                      url TEXT NOT NULL UNIQUE,
                                                                      title TEXT NOT NULL,
                                                                      timestamp TEXT NOT NULL
                       )
                       """)
    logger.info("Table 'browser_bookmarks' ensured.")

    # PEPx Metadata table (no raw data here, just metadata)
    self.execute_query("""
                       CREATE TABLE IF NOT EXISTS pepx_metadata (
                                                                  id TEXT PRIMARY KEY,
                                                                  name TEXT NOT NULL,
                                                                  path TEXT NOT NULL,
                                                                  type TEXT NOT NULL, -- 'file' or 'folder'
                                                                  size INTEGER NOT NULL,
                                                                  stored_byte_length INTEGER,
                                                                  created TEXT NOT NULL,
                                                                  modified TEXT NOT NULL
                       )
                       """)
    logger.info("Table 'pepx_metadata' ensured.")

  def reset_db(self):
    """Resets the entire database by dropping all tables."""
    if not self.conn:
      logger.error("Database not connected. Cannot reset.")
      return

    logger.warning("Resetting all database tables!")
    try:
      cursor = self.conn.cursor()
      cursor.execute("DROP TABLE IF EXISTS vfs_nodes")
      cursor.execute("DROP TABLE IF EXISTS browser_history")
      cursor.execute("DROP TABLE IF EXISTS browser_bookmarks")
      cursor.execute("DROP TABLE IF EXISTS pepx_metadata")
      self.conn.commit()
      self.initialize_db() # Re-initialize empty tables
      logger.info("All tables dropped and re-initialized.")
      return {"status": "success", "message": "Database reset successfully."}
    except sqlite3.Error as e:
      logger.error(f"Error during database reset: {e}")
      return {"status": "error", "message": f"Database reset failed: {e}"}

# Global DB instance (or initialize in main.py)
# db_manager = DBManager()
