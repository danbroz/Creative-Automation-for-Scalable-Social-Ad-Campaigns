"""
Storage Module
==============

This module provides a unified storage abstraction layer that supports multiple
storage backends including local filesystem, AWS S3, Azure Blob Storage, and
Google Cloud Storage.

The storage abstraction follows the Strategy pattern, allowing the application
to switch between different storage providers without changing the core logic.

Usage:
    from src.storage import get_storage
    
    storage = get_storage()  # Uses config to determine provider
    storage.save_file(data, "path/to/file.png")
    data = storage.read_file("path/to/file.png")

Components:
    - StorageBase: Abstract base class defining the storage interface
    - LocalStorage: Local filesystem implementation
    - S3Storage: AWS S3 implementation
    - AzureStorage: Azure Blob Storage implementation
    - GCSStorage: Google Cloud Storage implementation
    - get_storage: Factory function to create storage instances
"""

from .storage_factory import get_storage
from .storage_base import StorageBase

__all__ = ['get_storage', 'StorageBase']

