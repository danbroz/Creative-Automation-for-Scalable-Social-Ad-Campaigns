"""
Storage Base Class
==================

Abstract base class defining the storage interface that all storage providers
must implement. This ensures consistent behavior across different storage backends.

Design Pattern: Strategy Pattern / Template Method
Purpose: Define a common interface for file storage operations
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, BinaryIO, Optional, List
import json


class StorageBase(ABC):
    """
    Abstract base class for storage providers.
    
    All storage implementations must inherit from this class and implement
    all abstract methods. This ensures a consistent API across different
    storage backends (local, S3, Azure, GCS, etc.).
    
    Attributes:
        config (dict): Configuration dictionary for the storage provider
        provider_name (str): Name of the storage provider (e.g., 'local', 's3')
    
    Methods:
        save_file: Save binary data to storage
        read_file: Read binary data from storage
        save_json: Save JSON data to storage
        read_json: Read JSON data from storage
        file_exists: Check if a file exists
        list_files: List files in a directory
        delete_file: Delete a file from storage
        get_file_url: Get a URL to access the file (if applicable)
        create_directory: Create a directory (if applicable)
    """
    
    def __init__(self, config: dict):
        """
        Initialize storage provider.
        
        Args:
            config (dict): Configuration dictionary specific to the storage provider.
                          Each provider may have different required configuration keys.
        """
        self.config = config
        self.provider_name = "base"
    
    @abstractmethod
    def save_file(self, data: Union[bytes, BinaryIO], path: str) -> bool:
        """
        Save binary data to storage.
        
        Args:
            data (Union[bytes, BinaryIO]): Binary data or file-like object to save
            path (str): Destination path in storage (e.g., 'campaigns/campaign1/image.png')
        
        Returns:
            bool: True if save was successful, False otherwise
        
        Raises:
            Exception: If save operation fails
        """
        pass
    
    @abstractmethod
    def read_file(self, path: str) -> bytes:
        """
        Read binary data from storage.
        
        Args:
            path (str): Path to file in storage
        
        Returns:
            bytes: Binary content of the file
        
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If read operation fails
        """
        pass
    
    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            path (str): Path to file in storage
        
        Returns:
            bool: True if file exists, False otherwise
        """
        pass
    
    @abstractmethod
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """
        List files in a directory.
        
        Args:
            directory (str): Directory path to list
            pattern (str): Glob pattern to filter files (default: "*" for all files)
        
        Returns:
            List[str]: List of file paths matching the pattern
        """
        pass
    
    @abstractmethod
    def delete_file(self, path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            path (str): Path to file to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_file_url(self, path: str, expiry: int = 3600) -> Optional[str]:
        """
        Get a URL to access the file (if supported by the storage provider).
        
        For cloud storage, this returns a pre-signed URL. For local storage,
        this may return a file:// URL or None.
        
        Args:
            path (str): Path to file in storage
            expiry (int): URL expiry time in seconds (default: 3600 = 1 hour)
        
        Returns:
            Optional[str]: URL to access the file, or None if not applicable
        """
        pass
    
    @abstractmethod
    def create_directory(self, directory: str) -> bool:
        """
        Create a directory in storage (if applicable).
        
        Some storage systems (like S3) don't have true directories, so this
        method may be a no-op for those providers.
        
        Args:
            directory (str): Directory path to create
        
        Returns:
            bool: True if directory was created or already exists
        """
        pass
    
    # Convenience methods with default implementations
    # These use the abstract methods above, so they work for all providers
    
    def save_json(self, data: dict, path: str) -> bool:
        """
        Save JSON data to storage.
        
        This is a convenience method that serializes a dictionary to JSON
        and saves it using the save_file method.
        
        Args:
            data (dict): Dictionary to save as JSON
            path (str): Destination path in storage
        
        Returns:
            bool: True if save was successful
        
        Example:
            storage.save_json({"name": "campaign1"}, "campaigns/campaign1/metadata.json")
        """
        try:
            json_bytes = json.dumps(data, indent=2).encode('utf-8')
            return self.save_file(json_bytes, path)
        except Exception as e:
            print(f"Error saving JSON to {path}: {e}")
            return False
    
    def read_json(self, path: str) -> dict:
        """
        Read JSON data from storage.
        
        This is a convenience method that reads binary data and deserializes
        it from JSON format.
        
        Args:
            path (str): Path to JSON file in storage
        
        Returns:
            dict: Deserialized JSON data
        
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        
        Example:
            data = storage.read_json("campaigns/campaign1/metadata.json")
        """
        try:
            json_bytes = self.read_file(path)
            return json.loads(json_bytes.decode('utf-8'))
        except Exception as e:
            print(f"Error reading JSON from {path}: {e}")
            raise
    
    def get_info(self) -> dict:
        """
        Get information about the storage provider.
        
        Returns:
            dict: Dictionary containing provider information including:
                  - provider: Name of the storage provider
                  - config: Sanitized configuration (no sensitive data)
        """
        return {
            'provider': self.provider_name,
            'config': self._sanitize_config()
        }
    
    def _sanitize_config(self) -> dict:
        """
        Sanitize configuration dictionary by removing sensitive information.
        
        This method removes keys that may contain sensitive data like API keys,
        access tokens, and passwords before returning configuration info.
        
        Returns:
            dict: Sanitized configuration dictionary
        """
        # List of sensitive keys to exclude from output
        sensitive_keys = ['api_key', 'secret_key', 'access_token', 'password', 
                         'access_key_id', 'secret_access_key', 'account_key']
        
        sanitized = {}
        for key, value in self.config.items():
            if key.lower() not in sensitive_keys:
                sanitized[key] = value
            else:
                sanitized[key] = '***REDACTED***'
        
        return sanitized

