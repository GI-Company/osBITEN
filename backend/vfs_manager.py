# backend/vfs_manager.py
import os
import datetime
import logging
from backend.db_manager import DBManager

logger = logging.getLogger('VFS_Manager')

class VFSManager:
  def __init__(self, db_manager: DBManager):
    self.db = db_manager
    # Ensure root directory exists on initialization if it's not already there
    self._ensure_root_exists()

  def _ensure_root_exists(self):
    # The root "/" itself is a conceptual directory, its presence is implied
    # by having no parent, but for ls purposes, we consider it a 'dir'
    # Check for any entry with path '/' or where name is '/' and type is 'dir'
    root_node = self.db.execute_query("SELECT * FROM vfs_nodes WHERE path = '/'", fetch_one=True)
    if not root_node:
      logger.info("VFS root '/' not found, creating conceptual entry.")
      now = datetime.datetime.now().isoformat()
      self.db.execute_query(
        "INSERT OR IGNORE INTO vfs_nodes (path, name, type, created_at, modified_at) VALUES (?, ?, ?, ?, ?)",
        ('/', '/', 'dir', now, now)
      )

  def _normalize_path(self, path):
    # Handles '..' and '.' in paths
    parts = path.split('/')
    normalized_parts = []
    for part in parts:
      if part == '' or part == '.':
        continue
      elif part == '..':
        if normalized_parts:
          normalized_parts.pop()
      else:
        normalized_parts.append(part)
    return '/' + '/'.join(normalized_parts) if normalized_parts else '/'

  def _path_exists(self, path):
    return self.db.execute_query("SELECT 1 FROM vfs_nodes WHERE path = ?", (path,), fetch_one=True) is not None

  def list_directory(self, path):
    normalized_path = self._normalize_path(path)
    logger.info(f"VFS: Listing directory: {normalized_path}")

    # Check if the path itself exists and is a directory
    node_info = self.db.execute_query("SELECT type FROM vfs_nodes WHERE path = ?", (normalized_path,), fetch_one=True)
    if node_info and node_info['type'] != 'dir':
      return {"error": f"Path is not a directory: {normalized_path}"}
    elif not node_info and normalized_path != '/':
      # If path is not root and doesn't exist, it's an error
      return {"error": f"No such directory: {normalized_path}"}
    elif not node_info and normalized_path == '/':
      # If root doesn't have an explicit entry, still allow listing children
      pass # Continue to list children

    # List direct children
    prefix = normalized_path if normalized_path == '/' else normalized_path + '/'
    query = f"SELECT path, name, type, size, created_at, modified_at FROM vfs_nodes WHERE path LIKE ? ESCAPE '!'"
    # Use LIKE with ESCAPE for paths that might contain '%' or '_'
    # Also need to ensure we only get direct children, not deeper descendants
    # For direct children, the path must start with 'prefix' and contain no further '/'
    # after 'prefix'.
    like_pattern = prefix.replace('%', '!%').replace('_', '!_') + '%'
    rows = self.db.execute_query(query, (like_pattern,), fetch_all=True)

    contents = []
    for row in rows:
      child_path_suffix = row['path'][len(prefix):]
      if normalized_path == '/':
        # For root, children are like '/dir' or '/file.txt', no further '/'
        if '/' not in child_path_suffix and child_path_suffix:
          contents.append(dict(row))
      else:
        # For subdirectories, children are like 'dir/child' or 'file.txt'
        if '/' not in child_path_suffix:
          contents.append(dict(row))

    # Special handling for root to explicitly include itself if listing its properties
    if normalized_path == '/' and not contents:
      # If no children and root itself wasn't found as a file, treat it as empty dir
      pass # No need to add it, empty list is fine for ls output

    # Deduplicate and sort, ensure dirs are listed first
    unique_contents = {item['path']: item for item in contents}
    sorted_contents = sorted(unique_contents.values(), key=lambda x: (0 if x['type'] == 'dir' else 1, x['name'].lower()))

    logger.info(f"VFS: Listed {len(sorted_contents)} items in {normalized_path}")
    return {"contents": sorted_contents}


  def create_directory(self, path):
    normalized_path = self._normalize_path(path)
    logger.info(f"VFS: Creating directory: {normalized_path}")

    if self._path_exists(normalized_path):
      return {"error": f"Directory already exists: {normalized_path}"}

    parent_path = os.path.dirname(normalized_path)
    if parent_path == '': # means it's a root level item like /dir, parent is /
      parent_path = '/'
    if parent_path != '/' and not self._path_exists(parent_path):
      return {"error": f"Parent directory does not exist: {parent_path}"}
    if parent_path != '/' and self.db.execute_query("SELECT type FROM vfs_nodes WHERE path = ?", (parent_path,), fetch_one=True)['type'] != 'dir':
      return {"error": f"Parent path is not a directory: {parent_path}"}


    now = datetime.datetime.now().isoformat()
    self.db.execute_query(
      "INSERT INTO vfs_nodes (path, name, type, created_at, modified_at) VALUES (?, ?, ?, ?, ?)",
      (normalized_path, os.path.basename(normalized_path) or '/', 'dir', now, now)
    )
    logger.info(f"VFS: Directory created: {normalized_path}")
    return {"status": "success", "message": f"Directory '{normalized_path}' created."}

  def get_file_content(self, path):
    normalized_path = self._normalize_path(path)
    logger.info(f"VFS: Getting file content: {normalized_path}")

    node = self.db.execute_query("SELECT type, content FROM vfs_nodes WHERE path = ?", (normalized_path,), fetch_one=True)
    if not node:
      return {"error": f"No such file or directory: {normalized_path}"}
    if node['type'] == 'dir':
      return {"error": f"Path is a directory: {normalized_path}"}

    return {"content": node['content'] if node['content'] is not None else ""}

  def write_file(self, path, content):
    normalized_path = self._normalize_path(path)
    logger.info(f"VFS: Writing file: {normalized_path}")

    now = datetime.datetime.now().isoformat()
    file_size = len(content.encode('utf-8')) # Approximate size in bytes

    # Check if parent directory exists and is a directory
    parent_path = os.path.dirname(normalized_path)
    if parent_path == '':
      parent_path = '/' # Root directory is conceptual parent for top-level files

    if parent_path != '/' and not self._path_exists(parent_path):
      return {"error": f"Parent directory does not exist: {parent_path}"}
    elif parent_path != '/':
      parent_node = self.db.execute_query("SELECT type FROM vfs_nodes WHERE path = ?", (parent_path,), fetch_one=True)
      if parent_node and parent_node['type'] != 'dir':
        return {"error": f"Parent path is not a directory: {parent_path}"}


    self.db.execute_query(
      """
      INSERT OR REPLACE INTO vfs_nodes (path, name, type, size, content, created_at, modified_at)
      VALUES (?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM vfs_nodes WHERE path = ?), ?), ?)
      """,
      (normalized_path, os.path.basename(normalized_path), 'file', file_size, content, normalized_path, now, now)
    )
    logger.info(f"VFS: File written: {normalized_path}")
    return {"status": "success", "message": f"File '{normalized_path}' written."}

  def delete_path(self, path, recursive=False):
    normalized_path = self._normalize_path(path)
    logger.info(f"VFS: Deleting path: {normalized_path}, recursive: {recursive}")

    node = self.db.execute_query("SELECT type FROM vfs_nodes WHERE path = ?", (normalized_path,), fetch_one=True)
    if not node:
      return {"error": f"No such file or directory: {normalized_path}"}

    if node['type'] == 'dir':
      # Check for children
      prefix = normalized_path if normalized_path == '/' else normalized_path + '/'
      children = self.db.execute_query(f"SELECT path FROM vfs_nodes WHERE path LIKE ? ESCAPE '!' AND path != ?",
                                       (prefix.replace('%', '!%').replace('_', '!_') + '%', normalized_path), fetch_all=True)
      if children and not recursive:
        return {"error": f"Directory not empty: {normalized_path}. Use -r to remove recursively."}

      # Delete all children first (if recursive)
      for child_row in children:
        self.db.execute_query("DELETE FROM vfs_nodes WHERE path = ?", (child_row['path'],))
        logger.info(f"VFS: Deleted child: {child_row['path']}")

      # Then delete the directory itself
      self.db.execute_query("DELETE FROM vfs_nodes WHERE path = ?", (normalized_path,))
      logger.info(f"VFS: Directory deleted: {normalized_path}")
    else:
      # It's a file, just delete it
      self.db.execute_query("DELETE FROM vfs_nodes WHERE path = ?", (normalized_path,))
      logger.info(f"VFS: File deleted: {normalized_path}")

    return {"status": "success", "message": f"Path '{normalized_path}' deleted."}

  def move_path(self, source_path, dest_path):
    normalized_source = self._normalize_path(source_path)
    normalized_dest = self._normalize_path(dest_path)
    logger.info(f"VFS: Moving '{normalized_source}' to '{normalized_dest}'")

    source_node = self.db.execute_query("SELECT * FROM vfs_nodes WHERE path = ?", (normalized_source,), fetch_one=True)
    if not source_node:
      return {"error": f"Source path does not exist: {normalized_source}"}

    if self._path_exists(normalized_dest):
      # If destination exists and is a directory, move source into it
      dest_node = self.db.execute_query("SELECT type FROM vfs_nodes WHERE path = ?", (normalized_dest,), fetch_one=True)
      if dest_node['type'] == 'dir':
        new_dest_path = os.path.join(normalized_dest, os.path.basename(normalized_source)).replace('\\', '/')
        if self._path_exists(new_dest_path):
          return {"error": f"Cannot move: destination '{new_dest_path}' already exists inside directory."}
        normalized_dest = new_dest_path
      else:
        # If destination exists and is a file, cannot move/rename to it (overwrite protection)
        return {"error": f"Destination already exists and is a file: {normalized_dest}"}

    now = datetime.datetime.now().isoformat()
    # Update the source node
    self.db.execute_query(
      "UPDATE vfs_nodes SET path = ?, name = ?, modified_at = ? WHERE path = ?",
      (normalized_dest, os.path.basename(normalized_dest), now, normalized_source)
    )

    # If it was a directory, update all its children's paths
    if source_node['type'] == 'dir':
      old_prefix = normalized_source if normalized_source == '/' else normalized_source + '/'
      new_prefix = normalized_dest if normalized_dest == '/' else normalized_dest + '/'

      # Get all children that start with the old_prefix (excluding the source itself)
      children = self.db.execute_query(f"SELECT path FROM vfs_nodes WHERE path LIKE ? ESCAPE '!' AND path != ?",
                                       (old_prefix.replace('%', '!%').replace('_', '!_') + '%', normalized_source), fetch_all=True)

      for child_row in children:
        original_child_path = child_row['path']
        relative_path = original_child_path[len(old_prefix):]
        new_child_path = new_prefix + relative_path
        self.db.execute_query(
          "UPDATE vfs_nodes SET path = ?, modified_at = ? WHERE path = ?",
          (new_child_path, now, original_child_path)
        )
        logger.info(f"VFS: Updated child path: {original_child_path} -> {new_child_path}")

    logger.info(f"VFS: Moved '{normalized_source}' to '{normalized_dest}' successfully.")
    return {"status": "success", "message": f"Moved '{source_path}' to '{dest_path}'."}

  def copy_path(self, source_path, dest_path):
    normalized_source = self._normalize_path(source_path)
    normalized_dest = self._normalize_path(dest_path)
    logger.info(f"VFS: Copying '{normalized_source}' to '{normalized_dest}'")

    source_node = self.db.execute_query("SELECT * FROM vfs_nodes WHERE path = ?", (normalized_source,), fetch_one=True)
    if not source_node:
      return {"error": f"Source path does not exist: {normalized_source}"}

    # Determine final destination path (if dest is a directory, copy into it)
    final_dest_path = normalized_dest
    if self._path_exists(normalized_dest):
      dest_node = self.db.execute_query("SELECT type FROM vfs_nodes WHERE path = ?", (normalized_dest,), fetch_one=True)
      if dest_node and dest_node['type'] == 'dir':
        final_dest_path = os.path.join(normalized_dest, source_node['name']).replace('\\', '/')
      elif dest_node and dest_node['type'] == 'file':
        return {"error": f"Cannot copy: destination '{normalized_dest}' already exists and is a file."}

    if self._path_exists(final_dest_path):
      return {"error": f"Cannot copy: destination '{final_dest_path}' already exists."}

    now = datetime.datetime.now().isoformat()
    # Copy the source node itself
    new_name = os.path.basename(final_dest_path)
    self.db.execute_query(
      "INSERT INTO vfs_nodes (path, name, type, size, content, created_at, modified_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
      (final_dest_path, new_name, source_node['type'], source_node['size'], source_node['content'], now, now)
    )

    # If it's a directory, recursively copy its children
    if source_node['type'] == 'dir':
      old_prefix = normalized_source if normalized_source == '/' else normalized_source + '/'
      new_prefix = final_dest_path if final_dest_path == '/' else final_dest_path + '/'

      children = self.db.execute_query(f"SELECT * FROM vfs_nodes WHERE path LIKE ? ESCAPE '!' AND path != ?",
                                       (old_prefix.replace('%', '!%').replace('_', '!_') + '%', normalized_source), fetch_all=True)

      for child_row in children:
        original_child_path = child_row['path']
        relative_path = original_child_path[len(old_prefix):]
        new_child_path = new_prefix + relative_path

        self.db.execute_query(
          "INSERT INTO vfs_nodes (path, name, type, size, content, created_at, modified_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
          (new_child_path, child_row['name'], child_row['type'], child_row['size'], child_row['content'], now, now)
        )
        logger.info(f"VFS: Copied child path: {original_child_path} -> {new_child_path}")

    logger.info(f"VFS: Copied '{normalized_source}' to '{final_dest_path}' successfully.")
    return {"status": "success", "message": f"Copied '{source_path}' to '{dest_path}'."}

  def reset_vfs(self):
    """Removes all VFS nodes from the database except the conceptual root."""
    logger.warning("VFS: Resetting all VFS data!")
    # Delete all files and directories except the root entry (if it exists)
    self.db.execute_query("DELETE FROM vfs_nodes WHERE path != '/'")
    # Ensure root is always there
    self._ensure_root_exists()
    logger.info("VFS: All VFS nodes (except root) deleted.")
    return {"status": "success", "message": "Virtual File System reset."}

  def get_node_info(self, path):
    normalized_path = self._normalize_path(path)
    return self.db.execute_query("SELECT * FROM vfs_nodes WHERE path = ?", (normalized_path,), fetch_one=True)
