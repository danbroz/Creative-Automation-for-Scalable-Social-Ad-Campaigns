"""
Azure Blob Storage Implementation
==================================

Implementation of the StorageBase interface for Microsoft Azure Blob Storage.
Provides cloud-based storage with high availability and integration with
Azure ecosystem.

Features:
    - Geo-redundant storage options
    - Integration with Azure Active Directory
    - Tiered storage (Hot, Cool, Archive)
    - CDN integration
    - Encryption at rest and in transit

Requirements:
    - azure-storage-blob library
    - Azure Storage account
    - Connection string or account key

Configuration:
    - account_name: Azure storage account name
    - account_key: Azure storage account key (or use connection_string)
    - connection_string: Full connection string (alternative to account_name/key)
    - container: Blob container name
    - prefix: Optional prefix for all paths
"""

from typing import Union, BinaryIO, Optional, List
import io

try:
    from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
    from azure.core.exceptions import ResourceNotFoundError, AzureError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from .storage_base import StorageBase


class AzureStorage(StorageBase):
    """
    Azure Blob Storage implementation.
    
    This storage provider saves files to Microsoft Azure Blob Storage,
    providing cloud-based storage with excellent integration into the
    Azure ecosystem.
    
    Configuration Example:
        {
            "provider": "azure",
            "azure": {
                "account_name": "myaccount",
                "account_key": "base64encodedkey==",
                "container": "campaign-assets",
                "prefix": "campaigns/"  # Optional
            }
        }
    
    Or using connection string:
        {
            "provider": "azure",
            "azure": {
                "connection_string": "DefaultEndpointsProtocol=https;AccountName=...",
                "container": "campaign-assets"
            }
        }
    
    Authentication Methods:
        1. Account name + account key
        2. Connection string
        3. Managed Identity (for Azure VMs/App Services)
        4. Azure AD authentication
    
    Security Best Practices:
        - Use Azure Key Vault for connection strings
        - Enable soft delete for blobs
        - Use HTTPS-only access
        - Enable Azure Defender for Storage
        - Use private endpoints for VNet integration
    """
    
    def __init__(self, config: dict):
        """
        Initialize Azure Blob Storage provider.
        
        Args:
            config (dict): Configuration dictionary with Azure settings
        
        Raises:
            ImportError: If azure-storage-blob is not installed
            ValueError: If required configuration is missing
        """
        super().__init__(config)
        self.provider_name = "azure"
        
        # Check if Azure SDK is available
        if not AZURE_AVAILABLE:
            raise ImportError("azure-storage-blob library is required for Azure storage. "
                            "Install it with: pip install azure-storage-blob")
        
        # Extract Azure configuration
        azure_config = config.get('azure', {})
        self.container_name = azure_config.get('container')
        self.prefix = azure_config.get('prefix', '').strip('/')
        
        if not self.container_name:
            raise ValueError("Azure container name is required in configuration")
        
        # Initialize BlobServiceClient
        # Method 1: Using connection string
        connection_string = azure_config.get('connection_string')
        if connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                connection_string
            )
        # Method 2: Using account name and key
        else:
            account_name = azure_config.get('account_name')
            account_key = azure_config.get('account_key')
            
            if not account_name or not account_key:
                raise ValueError("Azure account_name and account_key are required "
                               "if connection_string is not provided")
            
            account_url = f"https://{account_name}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=account_key
            )
        
        # Get container client
        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )
        
        # Verify container exists (or create it if it doesn't)
        try:
            self.container_client.get_container_properties()
        except ResourceNotFoundError:
            print(f"Container '{self.container_name}' not found. Creating...")
            self.container_client.create_container()
    
    def _get_full_blob_name(self, path: str) -> str:
        """
        Get the full blob name by combining prefix and path.
        
        Args:
            path (str): Relative path
        
        Returns:
            str: Full blob name with prefix
        """
        if self.prefix:
            return f"{self.prefix}/{path}".replace('//', '/')
        return path
    
    def save_file(self, data: Union[bytes, BinaryIO], path: str) -> bool:
        """
        Save binary data to Azure Blob Storage.
        
        Args:
            data (Union[bytes, BinaryIO]): Binary data or file-like object
            path (str): Destination path in blob storage
        
        Returns:
            bool: True if upload was successful
        
        Example:
            storage.save_file(b"Hello World", "test/hello.txt")
        """
        try:
            blob_name = self._get_full_blob_name(path)
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Upload data (handles both bytes and file-like objects)
            blob_client.upload_blob(data, overwrite=True)
            return True
            
        except AzureError as e:
            print(f"Error uploading to Azure Blob Storage {path}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error uploading to Azure {path}: {e}")
            return False
    
    def read_file(self, path: str) -> bytes:
        """
        Read binary data from Azure Blob Storage.
        
        Args:
            path (str): Path to blob
        
        Returns:
            bytes: Binary content of the blob
        
        Raises:
            FileNotFoundError: If blob doesn't exist
        """
        try:
            blob_name = self._get_full_blob_name(path)
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Download blob content
            download_stream = blob_client.download_blob()
            return download_stream.readall()
            
        except ResourceNotFoundError:
            raise FileNotFoundError(f"Blob not found in Azure Storage: {path}")
        except Exception as e:
            print(f"Error reading from Azure Blob Storage {path}: {e}")
            raise
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a blob exists in Azure Storage.
        
        Args:
            path (str): Path to blob
        
        Returns:
            bool: True if blob exists
        """
        try:
            blob_name = self._get_full_blob_name(path)
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            return blob_client.exists()
            
        except Exception:
            return False
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """
        List blobs in Azure Storage matching a pattern.
        
        Args:
            directory (str): Directory prefix
            pattern (str): Simple wildcard pattern
        
        Returns:
            List[str]: List of blob names (without configured prefix)
        """
        try:
            full_prefix = self._get_full_blob_name(directory)
            if full_prefix and not full_prefix.endswith('/'):
                full_prefix += '/'
            
            # List blobs with prefix
            blob_list = self.container_client.list_blobs(
                name_starts_with=full_prefix if full_prefix else None
            )
            
            files = []
            for blob in blob_list:
                blob_name = blob.name
                
                # Remove the configured prefix
                if self.prefix and blob_name.startswith(self.prefix + '/'):
                    relative_name = blob_name[len(self.prefix) + 1:]
                else:
                    relative_name = blob_name
                
                # Simple pattern matching
                if pattern == "*" or self._matches_pattern(relative_name, pattern):
                    files.append(relative_name)
            
            return sorted(files)
            
        except AzureError as e:
            print(f"Error listing blobs in Azure Storage {directory}: {e}")
            return []
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """
        Simple pattern matching for Azure blobs.
        
        Args:
            path (str): Blob name
            pattern (str): Pattern to match
        
        Returns:
            bool: True if path matches pattern
        """
        import fnmatch
        return fnmatch.fnmatch(path, pattern)
    
    def delete_file(self, path: str) -> bool:
        """
        Delete a blob from Azure Storage.
        
        Args:
            path (str): Path to blob
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            blob_name = self._get_full_blob_name(path)
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            return True
            
        except ResourceNotFoundError:
            print(f"Blob not found in Azure Storage: {path}")
            return False
        except AzureError as e:
            print(f"Error deleting blob from Azure Storage {path}: {e}")
            return False
    
    def get_file_url(self, path: str, expiry: int = 3600) -> Optional[str]:
        """
        Generate a SAS (Shared Access Signature) URL for blob access.
        
        SAS URLs provide temporary access to private blobs without requiring
        Azure credentials.
        
        Args:
            path (str): Path to blob
            expiry (int): URL expiry time in seconds
        
        Returns:
            Optional[str]: SAS URL or None on error
        """
        try:
            from datetime import datetime, timedelta
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions
            
            blob_name = self._get_full_blob_name(path)
            
            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.blob_service_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(seconds=expiry)
            )
            
            # Construct full URL
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            return f"{blob_client.url}?{sas_token}"
            
        except Exception as e:
            print(f"Error generating SAS URL for {path}: {e}")
            return None
    
    def create_directory(self, directory: str) -> bool:
        """
        Create a "directory" in Azure Blob Storage.
        
        Note: Azure Blob Storage doesn't have true directories. They are created
        implicitly when you upload blobs with "/" in their names.
        
        Args:
            directory (str): Directory path
        
        Returns:
            bool: Always returns True (Azure creates directories implicitly)
        """
        # Azure Blob Storage creates "directories" implicitly
        return True

