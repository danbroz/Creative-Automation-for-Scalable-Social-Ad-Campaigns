"""
Local Filesystem Storage Implementation
========================================

Implementation of the StorageBase interface for local filesystem storage.
This is the default storage provider and requires no external dependencies
beyond Python's standard library.

Features:
    - Direct filesystem access using pathlib
    - No network latency
    - Simple directory-based organization
    - Suitable for development and single-machine deployments

Limitations:
    - No built-in redundancy
    - Limited to single machine
    - No automatic backup
    - Not suitable for distributed systems
"""

from pathlib import Path
from typing import Union, BinaryIO, Optional, List
import shutil
import glob

from .storage_base import StorageBase


class LocalStorage(StorageBase):
    """
    Local filesystem storage implementation.
    
    This storage provider saves files directly to the local filesystem.
    It's the default provider and requires minimal configuration.
    
    Configuration:
        base_path (str): Root directory for all storage operations
                        Default: 'output/'
    
    Example Configuration:
        {
            "provider": "local",
            "local": {
                "base_path": "output/"
            }
        }
    
    Thread Safety:
        This implementation is thread-safe for read operations but may have
        race conditions for write operations if multiple threads write to the
        same file simultaneously. Use file locking if needed.
    """
    
    def __init__(self, config: dict):
        """
        Initialize local storage provider.
        
        Args:
            config (dict): Configuration dictionary with 'base_path' key
        
        Example:
            storage = LocalStorage({"base_path": "output/"})
        """
        super().__init__(config)
        self.provider_name = "local"
        
        # Get base path from config, default to 'output/'
        self.base_path = Path(config.get('base_path', 'output/'))
        
        # Ensure base directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _resolve_path(self, path: str) -> Path:
        """
        Resolve a relative path to an absolute path within the base directory.
        
        This method ensures all paths are relative to the base_path and prevents
        path traversal attacks by resolving .. and symbolic links.
        
        Args:
            path (str): Relative path within storage
        
        Returns:
            Path: Absolute path object
        
        Security:
            This method prevents path traversal by ensuring the final path
            is within the base_path directory.
        """
        # Combine base path with relative path
        full_path = (self.base_path / path).resolve()
        
        # Security check: Ensure the resolved path is within base_path
        # This prevents path traversal attacks like "../../../etc/passwd"
        if not str(full_path).startswith(str(self.base_path.resolve())):
            raise ValueError(f"Path {path} attempts to escape base directory")
        
        return full_path
    
    def save_file(self, data: Union[bytes, BinaryIO], path: str) -> bool:
        """
        Save binary data to local filesystem.
        
        Creates parent directories automatically if they don't exist.
        
        Args:
            data (Union[bytes, BinaryIO]): Binary data or file-like object
            path (str): Destination path relative to base_path
        
        Returns:
            bool: True if save was successful
        
        Example:
            storage.save_file(b"Hello World", "test/hello.txt")
            # Saves to output/test/hello.txt
        """
        try:
            file_path = self._resolve_path(path)
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write data based on type
            if isinstance(data, bytes):
                # Direct binary data
                file_path.write_bytes(data)
            else:
                # File-like object (BinaryIO)
                with file_path.open('wb') as f:
                    # Read in chunks to handle large files efficiently
                    chunk_size = 8192  # 8KB chunks
                    while True:
                        chunk = data.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
            
            return True
            
        except Exception as e:
            print(f"Error saving file to {path}: {e}")
            return False
    
    def read_file(self, path: str) -> bytes:
        """
        Read binary data from local filesystem.
        
        Args:
            path (str): Path to file relative to base_path
        
        Returns:
            bytes: Binary content of the file
        
        Raises:
            FileNotFoundError: If file doesn't exist
        
        Example:
            data = storage.read_file("test/hello.txt")
        """
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        return file_path.read_bytes()
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists in local filesystem.
        
        Args:
            path (str): Path to file relative to base_path
        
        Returns:
            bool: True if file exists
        
        Example:
            if storage.file_exists("test/hello.txt"):
                print("File exists!")
        """
        try:
            file_path = self._resolve_path(path)
            return file_path.exists() and file_path.is_file()
        except Exception:
            return False
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """
        List files in a directory matching a pattern.
        
        Args:
            directory (str): Directory path relative to base_path
            pattern (str): Glob pattern (e.g., "*.png", "**/*.json")
        
        Returns:
            List[str]: List of file paths relative to base_path
        
        Example:
            # List all PNG files in campaigns/campaign1/
            files = storage.list_files("campaigns/campaign1", "**/*.png")
        """
        try:
            dir_path = self._resolve_path(directory)
            
            if not dir_path.exists():
                return []
            
            # Use glob to find matching files
            matches = dir_path.glob(pattern)
            
            # Convert absolute paths back to relative paths
            relative_paths = []
            for match in matches:
                if match.is_file():
                    # Get path relative to base_path
                    rel_path = match.relative_to(self.base_path)
                    relative_paths.append(str(rel_path))
            
            return sorted(relative_paths)
            
        except Exception as e:
            print(f"Error listing files in {directory}: {e}")
            return []
    
    def delete_file(self, path: str) -> bool:
        """
        Delete a file from local filesystem.
        
        Args:
            path (str): Path to file relative to base_path
        
        Returns:
            bool: True if deletion was successful
        
        Example:
            storage.delete_file("test/temp.txt")
        """
        try:
            file_path = self._resolve_path(path)
            
            if file_path.exists():
                file_path.unlink()
                return True
            else:
                print(f"File not found: {path}")
                return False
                
        except Exception as e:
            print(f"Error deleting file {path}: {e}")
            return False
    
    def get_file_url(self, path: str, expiry: int = 3600) -> Optional[str]:
        """
        Get a file:// URL for local filesystem access.
        
        Note: file:// URLs are not accessible over network and only work
        on the local machine.
        
        Args:
            path (str): Path to file relative to base_path
            expiry (int): Not used for local storage (included for interface compatibility)
        
        Returns:
            Optional[str]: file:// URL or None if file doesn't exist
        
        Example:
            url = storage.get_file_url("test/image.png")
            # Returns: "file:///abs/path/to/output/test/image.png"
        """
        try:
            file_path = self._resolve_path(path)
            
            if file_path.exists():
                # Return file:// URL
                return file_path.as_uri()
            else:
                return None
                
        except Exception:
            return None
    
    def create_directory(self, directory: str) -> bool:
        """
        Create a directory in local filesystem.
        
        Creates all intermediate directories as needed (like mkdir -p).
        
        Args:
            directory (str): Directory path relative to base_path
        
        Returns:
            bool: True if directory was created or already exists
        
        Example:
            storage.create_directory("campaigns/campaign1/products")
        """
        try:
            dir_path = self._resolve_path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)
            return True
            
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            return False
    
    def copy_file(self, src_path: str, dest_path: str) -> bool:
        """
        Copy a file within local storage.
        
        This is a convenience method specific to local storage that allows
        efficient file copying without reading into memory.
        
        Args:
            src_path (str): Source file path relative to base_path
            dest_path (str): Destination file path relative to base_path
        
        Returns:
            bool: True if copy was successful
        
        Example:
            storage.copy_file("products/original.png", "products/copy.png")
        """
        try:
            src = self._resolve_path(src_path)
            dest = self._resolve_path(dest_path)
            
            if not src.exists():
                print(f"Source file not found: {src_path}")
                return False
            
            # Create destination directory if needed
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(src, dest)
            return True
            
        except Exception as e:
            print(f"Error copying file from {src_path} to {dest_path}: {e}")
            return False
    
    def get_file_size(self, path: str) -> Optional[int]:
        """
        Get the size of a file in bytes.
        
        Args:
            path (str): Path to file relative to base_path
        
        Returns:
            Optional[int]: File size in bytes, or None if file doesn't exist
        
        Example:
            size = storage.get_file_size("test/image.png")
            print(f"File size: {size} bytes")
        """
        try:
            file_path = self._resolve_path(path)
            if file_path.exists():
                return file_path.stat().st_size
            return None
        except Exception:
            return None

