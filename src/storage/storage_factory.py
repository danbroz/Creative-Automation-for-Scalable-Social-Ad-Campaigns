"""
Storage Factory
===============

Factory pattern implementation for creating storage provider instances.
This module provides a centralized way to instantiate the correct storage
provider based on configuration.

Design Pattern: Factory Pattern
Purpose: Encapsulate storage provider instantiation logic
Benefits:
    - Centralized provider creation
    - Easy to add new providers
    - Configuration-driven selection
    - Simplified client code

Usage:
    from src.storage import get_storage
    
    # Uses configuration to determine provider
    storage = get_storage()
    
    # Or provide custom configuration
    storage = get_storage(config={'provider': 'local', 'local': {'base_path': 'data/'}})
"""

import json
from pathlib import Path
from typing import Optional, Dict

from .storage_base import StorageBase
from .local_storage import LocalStorage


# Default configuration file path
DEFAULT_CONFIG_PATH = "config/storage_config.json"


def load_storage_config(config_path: str = DEFAULT_CONFIG_PATH) -> Dict:
    """
    Load storage configuration from JSON file.
    
    The configuration file should specify which storage provider to use
    and the necessary credentials/settings for that provider.
    
    Args:
        config_path (str): Path to storage configuration JSON file
    
    Returns:
        Dict: Storage configuration dictionary
    
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        json.JSONDecodeError: If configuration file is invalid JSON
    
    Configuration File Format:
        {
            "provider": "local|s3|azure|gcs",
            "local": {
                "base_path": "output/"
            },
            "s3": {
                "bucket": "my-bucket",
                "region": "us-east-1",
                "access_key_id": "...",
                "secret_access_key": "..."
            },
            "azure": {
                "account_name": "...",
                "account_key": "...",
                "container": "..."
            },
            "gcs": {
                "bucket": "...",
                "project_id": "...",
                "credentials_path": "..."
            }
        }
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"Warning: Storage config file not found at {config_path}")
        print("Using default local storage configuration")
        return {
            "provider": "local",
            "local": {
                "base_path": "output/"
            }
        }
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in storage config file: {e}")
        print("Using default local storage configuration")
        return {
            "provider": "local",
            "local": {
                "base_path": "output/"
            }
        }


def get_storage(config: Optional[Dict] = None, config_path: str = DEFAULT_CONFIG_PATH) -> StorageBase:
    """
    Factory function to create and return a storage provider instance.
    
    This function implements the Factory pattern, creating the appropriate
    storage provider based on the configuration. It supports local filesystem,
    AWS S3, Azure Blob Storage, and Google Cloud Storage.
    
    Args:
        config (Optional[Dict]): Storage configuration dictionary.
                                If None, loads from config_path.
        config_path (str): Path to configuration file (used if config is None)
    
    Returns:
        StorageBase: Instance of a storage provider (LocalStorage, S3Storage, etc.)
    
    Raises:
        ValueError: If provider type is unsupported or configuration is invalid
        ImportError: If required library for cloud provider is not installed
    
    Example Usage:
        # Use default configuration from file
        storage = get_storage()
        
        # Use custom configuration
        custom_config = {
            "provider": "local",
            "local": {"base_path": "my_data/"}
        }
        storage = get_storage(config=custom_config)
        
        # Then use the storage
        storage.save_file(b"data", "test.txt")
    
    Supported Providers:
        - "local": Local filesystem storage
        - "s3": Amazon Web Services S3
        - "azure": Microsoft Azure Blob Storage
        - "gcs": Google Cloud Storage
    
    Adding New Providers:
        To add a new storage provider:
        1. Create a new class inheriting from StorageBase
        2. Implement all abstract methods
        3. Add import and elif clause below
        4. Update configuration documentation
    """
    # Load configuration if not provided
    if config is None:
        config = load_storage_config(config_path)
    
    # Get provider type from configuration
    provider = config.get('provider', 'local').lower()
    
    print(f"Initializing {provider} storage provider...")
    
    # Factory logic: Create the appropriate storage provider
    # Each provider is lazy-imported to avoid importing unnecessary dependencies
    
    if provider == 'local':
        # Local filesystem storage (always available)
        return LocalStorage(config)
    
    elif provider == 's3':
        # Amazon S3 storage
        try:
            from .s3_storage import S3Storage
            return S3Storage(config)
        except ImportError as e:
            raise ImportError(
                f"S3 storage requires boto3 library. Install it with: pip install boto3\n"
                f"Error: {e}"
            )
    
    elif provider == 'azure':
        # Microsoft Azure Blob Storage
        try:
            from .azure_storage import AzureStorage
            return AzureStorage(config)
        except ImportError as e:
            raise ImportError(
                f"Azure storage requires azure-storage-blob library. "
                f"Install it with: pip install azure-storage-blob\n"
                f"Error: {e}"
            )
    
    elif provider == 'gcs':
        # Google Cloud Storage
        try:
            from .gcs_storage import GCSStorage
            return GCSStorage(config)
        except ImportError as e:
            raise ImportError(
                f"GCS storage requires google-cloud-storage library. "
                f"Install it with: pip install google-cloud-storage\n"
                f"Error: {e}"
            )
    
    else:
        # Unknown provider
        raise ValueError(
            f"Unsupported storage provider: {provider}\n"
            f"Supported providers: local, s3, azure, gcs\n"
            f"Check your configuration in {config_path}"
        )


def get_available_providers() -> Dict[str, bool]:
    """
    Check which storage providers are available (have required libraries installed).
    
    This is useful for diagnostics and for dynamically adapting the application
    based on which cloud SDKs are installed.
    
    Returns:
        Dict[str, bool]: Dictionary mapping provider names to availability
    
    Example:
        providers = get_available_providers()
        if providers['s3']:
            print("AWS S3 is available")
        if not providers['azure']:
            print("Azure Blob Storage SDK not installed")
    """
    available = {
        'local': True  # Always available (uses standard library)
    }
    
    # Check if boto3 (AWS SDK) is available
    try:
        import boto3
        available['s3'] = True
    except ImportError:
        available['s3'] = False
    
    # Check if Azure SDK is available
    try:
        from azure.storage.blob import BlobServiceClient
        available['azure'] = True
    except ImportError:
        available['azure'] = False
    
    # Check if Google Cloud SDK is available
    try:
        from google.cloud import storage
        available['gcs'] = True
    except ImportError:
        available['gcs'] = False
    
    return available


def print_storage_info(storage: StorageBase) -> None:
    """
    Print information about the storage provider.
    
    This is a convenience function for debugging and logging purposes.
    It displays the provider type and sanitized configuration.
    
    Args:
        storage (StorageBase): Storage provider instance
    
    Example:
        storage = get_storage()
        print_storage_info(storage)
        # Output:
        # Storage Provider: local
        # Configuration:
        #   base_path: output/
    """
    info = storage.get_info()
    print(f"\nStorage Provider: {info['provider']}")
    print("Configuration:")
    for key, value in info['config'].items():
        print(f"  {key}: {value}")
    print()


# Example usage and testing
if __name__ == "__main__":
    """
    Demonstration of storage factory usage.
    
    This section runs when the module is executed directly (python -m src.storage.storage_factory)
    and demonstrates how to use the storage factory.
    """
    print("=" * 60)
    print("Storage Factory Demo")
    print("=" * 60)
    
    # Check available providers
    print("\nChecking available storage providers...")
    providers = get_available_providers()
    for provider, available in providers.items():
        status = "✓ Available" if available else "✗ Not installed"
        print(f"  {provider:10s}: {status}")
    
    # Create storage instance
    print("\nCreating storage instance from config...")
    try:
        storage = get_storage()
        print_storage_info(storage)
        
        # Test basic operations
        print("Testing storage operations...")
        
        # Test save
        test_data = b"Hello from storage factory!"
        test_path = "test/factory_test.txt"
        
        if storage.save_file(test_data, test_path):
            print(f"✓ Successfully saved: {test_path}")
        else:
            print(f"✗ Failed to save: {test_path}")
        
        # Test read
        if storage.file_exists(test_path):
            data = storage.read_file(test_path)
            print(f"✓ Successfully read: {len(data)} bytes")
        else:
            print(f"✗ File does not exist: {test_path}")
        
        # Test delete
        if storage.delete_file(test_path):
            print(f"✓ Successfully deleted: {test_path}")
        else:
            print(f"✗ Failed to delete: {test_path}")
        
        print("\n" + "=" * 60)
        print("Storage factory demo completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        print("\nMake sure you have a valid storage configuration file at:")
        print(f"  {DEFAULT_CONFIG_PATH}")

