"""
Google Cloud Storage Implementation
====================================

Implementation of the StorageBase interface for Google Cloud Storage (GCS).
Provides cloud-based storage with tight integration into Google Cloud Platform.

Features:
    - Multi-regional replication
    - Strong consistency
    - Integration with Google Cloud services
    - Lifecycle management
    - Object versioning
    - IAM-based access control

Requirements:
    - google-cloud-storage library
    - GCS bucket
    - Service account credentials or Application Default Credentials

Configuration:
    - bucket: GCS bucket name
    - project_id: Google Cloud project ID
    - credentials_path: Path to service account JSON file (optional)
    - prefix: Optional prefix for all paths
"""

from typing import Union, BinaryIO, Optional, List
import io
from datetime import timedelta

try:
    from google.cloud import storage
    from google.cloud.exceptions import NotFound, GoogleCloudError
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

from .storage_base import StorageBase


class GCSStorage(StorageBase):
    """
    Google Cloud Storage implementation.
    
    This storage provider saves files to Google Cloud Storage, providing
    cloud-based storage with excellent integration into Google Cloud Platform.
    
    Configuration Example with service account:
        {
            "provider": "gcs",
            "gcs": {
                "bucket": "my-campaign-assets",
                "project_id": "my-project-12345",
                "credentials_path": "/path/to/service-account.json",
                "prefix": "campaigns/"  # Optional
            }
        }
    
    Configuration with Application Default Credentials:
        {
            "provider": "gcs",
            "gcs": {
                "bucket": "my-campaign-assets",
                "project_id": "my-project-12345"
            }
        }
    
    Authentication Methods:
        1. Service account JSON file (recommended for applications)
        2. Application Default Credentials (ADC) - for GCE, GKE, Cloud Run
        3. gcloud CLI credentials (for development)
    
    To use ADC, run: gcloud auth application-default login
    
    Security Best Practices:
        - Use service accounts with minimal permissions
        - Enable uniform bucket-level access
        - Use VPC Service Controls for sensitive data
        - Enable audit logging
        - Use customer-managed encryption keys (CMEK) for sensitive data
        - Set lifecycle policies to manage costs
    """
    
    def __init__(self, config: dict):
        """
        Initialize Google Cloud Storage provider.
        
        Args:
            config (dict): Configuration dictionary with GCS settings
        
        Raises:
            ImportError: If google-cloud-storage is not installed
            ValueError: If required configuration is missing
        """
        super().__init__(config)
        self.provider_name = "gcs"
        
        # Check if GCS SDK is available
        if not GCS_AVAILABLE:
            raise ImportError("google-cloud-storage library is required for GCS storage. "
                            "Install it with: pip install google-cloud-storage")
        
        # Extract GCS configuration
        gcs_config = config.get('gcs', {})
        self.bucket_name = gcs_config.get('bucket')
        self.project_id = gcs_config.get('project_id')
        self.prefix = gcs_config.get('prefix', '').strip('/')
        
        if not self.bucket_name:
            raise ValueError("GCS bucket name is required in configuration")
        
        # Initialize GCS client
        credentials_path = gcs_config.get('credentials_path')
        
        if credentials_path:
            # Use service account credentials
            self.storage_client = storage.Client.from_service_account_json(
                credentials_path,
                project=self.project_id
            )
        else:
            # Use Application Default Credentials (ADC)
            # This works on GCE, GKE, Cloud Run, or with gcloud CLI auth
            self.storage_client = storage.Client(project=self.project_id)
        
        # Get bucket
        try:
            self.bucket = self.storage_client.bucket(self.bucket_name)
            
            # Verify bucket exists
            if not self.bucket.exists():
                raise ValueError(f"GCS bucket '{self.bucket_name}' does not exist")
                
        except NotFound:
            raise ValueError(f"GCS bucket '{self.bucket_name}' not found")
        except Exception as e:
            raise ValueError(f"Error accessing GCS bucket: {e}")
    
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
        Save binary data to Google Cloud Storage.
        
        Args:
            data (Union[bytes, BinaryIO]): Binary data or file-like object
            path (str): Destination path in GCS
        
        Returns:
            bool: True if upload was successful
        
        Example:
            storage.save_file(b"Hello World", "test/hello.txt")
        """
        try:
            blob_name = self._get_full_blob_name(path)
            blob = self.bucket.blob(blob_name)
            
            # Upload data based on type
            if isinstance(data, bytes):
                blob.upload_from_string(data)
            else:
                # File-like object
                data.seek(0)  # Ensure we're at the start
                blob.upload_from_file(data)
            
            return True
            
        except GoogleCloudError as e:
            print(f"Error uploading to GCS {path}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error uploading to GCS {path}: {e}")
            return False
    
    def read_file(self, path: str) -> bytes:
        """
        Read binary data from Google Cloud Storage.
        
        Args:
            path (str): Path to blob
        
        Returns:
            bytes: Binary content of the blob
        
        Raises:
            FileNotFoundError: If blob doesn't exist
        """
        try:
            blob_name = self._get_full_blob_name(path)
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                raise FileNotFoundError(f"Blob not found in GCS: {path}")
            
            # Download blob content
            return blob.download_as_bytes()
            
        except NotFound:
            raise FileNotFoundError(f"Blob not found in GCS: {path}")
        except Exception as e:
            print(f"Error reading from GCS {path}: {e}")
            raise
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a blob exists in Google Cloud Storage.
        
        Args:
            path (str): Path to blob
        
        Returns:
            bool: True if blob exists
        """
        try:
            blob_name = self._get_full_blob_name(path)
            blob = self.bucket.blob(blob_name)
            return blob.exists()
        except Exception:
            return False
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """
        List blobs in GCS matching a pattern.
        
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
            blobs = self.storage_client.list_blobs(
                self.bucket_name,
                prefix=full_prefix if full_prefix else None
            )
            
            files = []
            for blob in blobs:
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
            
        except GoogleCloudError as e:
            print(f"Error listing blobs in GCS {directory}: {e}")
            return []
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """
        Simple pattern matching for GCS blobs.
        
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
        Delete a blob from Google Cloud Storage.
        
        Args:
            path (str): Path to blob
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            blob_name = self._get_full_blob_name(path)
            blob = self.bucket.blob(blob_name)
            
            if blob.exists():
                blob.delete()
                return True
            else:
                print(f"Blob not found in GCS: {path}")
                return False
                
        except GoogleCloudError as e:
            print(f"Error deleting blob from GCS {path}: {e}")
            return False
    
    def get_file_url(self, path: str, expiry: int = 3600) -> Optional[str]:
        """
        Generate a signed URL for GCS blob access.
        
        Signed URLs provide temporary access to private blobs without requiring
        Google Cloud credentials.
        
        Args:
            path (str): Path to blob
            expiry (int): URL expiry time in seconds
        
        Returns:
            Optional[str]: Signed URL or None on error
        
        Note:
            Generating signed URLs requires the storage client to have
            service account credentials. It won't work with ADC.
        """
        try:
            blob_name = self._get_full_blob_name(path)
            blob = self.bucket.blob(blob_name)
            
            # Generate signed URL
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(seconds=expiry),
                method="GET"
            )
            return url
            
        except Exception as e:
            print(f"Error generating signed URL for {path}: {e}")
            print("Note: Signed URLs require service account credentials")
            return None
    
    def create_directory(self, directory: str) -> bool:
        """
        Create a "directory" in Google Cloud Storage.
        
        Note: GCS doesn't have true directories. They are created implicitly
        when you upload blobs with "/" in their names.
        
        Args:
            directory (str): Directory path
        
        Returns:
            bool: Always returns True (GCS creates directories implicitly)
        """
        # GCS creates "directories" implicitly
        return True
    
    def copy_file(self, src_path: str, dest_path: str) -> bool:
        """
        Copy a blob within GCS (server-side copy).
        
        This performs a server-side copy which is more efficient than
        downloading and re-uploading.
        
        Args:
            src_path (str): Source blob path
            dest_path (str): Destination blob path
        
        Returns:
            bool: True if copy was successful
        """
        try:
            src_blob_name = self._get_full_blob_name(src_path)
            dest_blob_name = self._get_full_blob_name(dest_path)
            
            src_blob = self.bucket.blob(src_blob_name)
            
            if not src_blob.exists():
                print(f"Source blob not found in GCS: {src_path}")
                return False
            
            # Server-side copy
            self.bucket.copy_blob(src_blob, self.bucket, dest_blob_name)
            return True
            
        except GoogleCloudError as e:
            print(f"Error copying blob in GCS from {src_path} to {dest_path}: {e}")
            return False

