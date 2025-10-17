"""
AWS S3 Storage Implementation
==============================

Implementation of the StorageBase interface for Amazon Web Services S3.
This provider enables cloud-based storage with high availability, durability,
and scalability.

Features:
    - Highly durable (99.999999999% durability)
    - Globally accessible
    - Automatic redundancy
    - Pre-signed URL support
    - Versioning support (optional)
    - Encryption at rest

Requirements:
    - boto3 library
    - AWS credentials (access key ID and secret access key)
    - S3 bucket must be created beforehand

Configuration:
    - bucket: S3 bucket name
    - region: AWS region (e.g., 'us-east-1')
    - access_key_id: AWS access key (or use IAM roles)
    - secret_access_key: AWS secret key (or use IAM roles)
    - prefix: Optional prefix for all paths
"""

from typing import Union, BinaryIO, Optional, List
import io

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from .storage_base import StorageBase


class S3Storage(StorageBase):
    """
    AWS S3 storage implementation.
    
    This storage provider saves files to Amazon S3, providing cloud-based
    storage with high availability and durability.
    
    Configuration Example:
        {
            "provider": "s3",
            "s3": {
                "bucket": "my-campaign-assets",
                "region": "us-east-1",
                "access_key_id": "AKIAIOSFODNN7EXAMPLE",  # Or use IAM roles
                "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "prefix": "campaigns/"  # Optional: prefix for all paths
            }
        }
    
    Authentication:
        Option 1: Provide access_key_id and secret_access_key in config
        Option 2: Use IAM roles (recommended for EC2/ECS)
        Option 3: Use AWS CLI credentials (~/.aws/credentials)
    
    Security Best Practices:
        - Use IAM roles instead of hardcoded credentials when possible
        - Enable versioning on the bucket
        - Enable encryption at rest
        - Use VPC endpoints for private access
        - Enable CloudTrail logging for audit
    """
    
    def __init__(self, config: dict):
        """
        Initialize S3 storage provider.
        
        Args:
            config (dict): Configuration dictionary with S3 settings
        
        Raises:
            ImportError: If boto3 is not installed
            ValueError: If required configuration is missing
            NoCredentialsError: If AWS credentials are not found
        """
        super().__init__(config)
        self.provider_name = "s3"
        
        # Check if boto3 is available
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 library is required for S3 storage. "
                            "Install it with: pip install boto3")
        
        # Extract S3 configuration
        s3_config = config.get('s3', {})
        self.bucket = s3_config.get('bucket')
        self.region = s3_config.get('region', 'us-east-1')
        self.prefix = s3_config.get('prefix', '').strip('/')
        
        if not self.bucket:
            raise ValueError("S3 bucket name is required in configuration")
        
        # Initialize S3 client
        # Boto3 will automatically look for credentials in this order:
        # 1. Parameters passed to boto3.client()
        # 2. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        # 3. AWS credentials file (~/.aws/credentials)
        # 4. IAM role (if running on EC2/ECS/Lambda)
        session_kwargs = {'region_name': self.region}
        
        # Use provided credentials if available
        access_key = s3_config.get('access_key_id')
        secret_key = s3_config.get('secret_access_key')
        
        if access_key and secret_key:
            session_kwargs['aws_access_key_id'] = access_key
            session_kwargs['aws_secret_access_key'] = secret_key
        
        # Create S3 client
        self.s3_client = boto3.client('s3', **session_kwargs)
        
        # Verify bucket access by attempting to get bucket metadata
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise ValueError(f"S3 bucket '{self.bucket}' does not exist")
            elif error_code == '403':
                raise PermissionError(f"Access denied to S3 bucket '{self.bucket}'")
            else:
                raise
    
    def _get_full_key(self, path: str) -> str:
        """
        Get the full S3 key by combining prefix and path.
        
        Args:
            path (str): Relative path
        
        Returns:
            str: Full S3 key with prefix
        
        Example:
            If prefix is "campaigns/" and path is "test/file.png"
            Returns: "campaigns/test/file.png"
        """
        if self.prefix:
            # Ensure no double slashes
            return f"{self.prefix}/{path}".replace('//', '/')
        return path
    
    def save_file(self, data: Union[bytes, BinaryIO], path: str) -> bool:
        """
        Save binary data to S3.
        
        Args:
            data (Union[bytes, BinaryIO]): Binary data or file-like object
            path (str): Destination path in S3 (will be combined with prefix)
        
        Returns:
            bool: True if upload was successful
        
        Example:
            storage.save_file(b"Hello World", "test/hello.txt")
            # Uploads to s3://bucket/campaigns/test/hello.txt (if prefix is "campaigns")
        """
        try:
            key = self._get_full_key(path)
            
            # Convert bytes to file-like object if needed
            if isinstance(data, bytes):
                data = io.BytesIO(data)
            
            # Upload to S3
            self.s3_client.upload_fileobj(data, self.bucket, key)
            return True
            
        except ClientError as e:
            print(f"Error uploading to S3 {path}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error uploading to S3 {path}: {e}")
            return False
    
    def read_file(self, path: str) -> bytes:
        """
        Read binary data from S3.
        
        Args:
            path (str): Path to file in S3
        
        Returns:
            bytes: Binary content of the file
        
        Raises:
            FileNotFoundError: If file doesn't exist in S3
        """
        try:
            key = self._get_full_key(path)
            
            # Download file to bytes
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read()
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise FileNotFoundError(f"File not found in S3: {path}")
            else:
                raise
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists in S3.
        
        Uses head_object which is more efficient than listing objects.
        
        Args:
            path (str): Path to file in S3
        
        Returns:
            bool: True if file exists
        """
        try:
            key = self._get_full_key(path)
            self.s3_client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                return False
            else:
                # Re-raise other errors (permission issues, etc.)
                raise
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """
        List files in an S3 "directory".
        
        Note: S3 doesn't have true directories, but uses key prefixes.
        This method lists all objects with the specified prefix.
        
        Args:
            directory (str): Directory prefix
            pattern (str): Simple wildcard pattern (*, *.png, etc.)
        
        Returns:
            List[str]: List of file paths (keys) without the configured prefix
        """
        try:
            full_prefix = self._get_full_key(directory)
            if not full_prefix.endswith('/'):
                full_prefix += '/'
            
            # List objects with the prefix
            files = []
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=self.bucket, Prefix=full_prefix):
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    key = obj['Key']
                    
                    # Remove the configured prefix to get relative path
                    if self.prefix and key.startswith(self.prefix + '/'):
                        relative_key = key[len(self.prefix) + 1:]
                    else:
                        relative_key = key
                    
                    # Simple pattern matching (only supports basic wildcards)
                    if pattern == "*" or self._matches_pattern(relative_key, pattern):
                        files.append(relative_key)
            
            return sorted(files)
            
        except ClientError as e:
            print(f"Error listing files in S3 {directory}: {e}")
            return []
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """
        Simple pattern matching for S3 files.
        
        Supports basic wildcards:
        - *.png matches all .png files
        - **/*.png matches .png files in any subdirectory
        
        Args:
            path (str): File path
            pattern (str): Pattern to match
        
        Returns:
            bool: True if path matches pattern
        """
        import fnmatch
        return fnmatch.fnmatch(path, pattern)
    
    def delete_file(self, path: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            path (str): Path to file in S3
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            key = self._get_full_key(path)
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            return True
            
        except ClientError as e:
            print(f"Error deleting file from S3 {path}: {e}")
            return False
    
    def get_file_url(self, path: str, expiry: int = 3600) -> Optional[str]:
        """
        Generate a pre-signed URL for S3 object access.
        
        Pre-signed URLs allow temporary access to private S3 objects without
        requiring AWS credentials.
        
        Args:
            path (str): Path to file in S3
            expiry (int): URL expiry time in seconds (default: 3600 = 1 hour)
        
        Returns:
            Optional[str]: Pre-signed URL or None on error
        
        Example:
            url = storage.get_file_url("test/image.png", expiry=7200)
            # URL valid for 2 hours
        """
        try:
            key = self._get_full_key(path)
            
            # Generate pre-signed URL
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expiry
            )
            return url
            
        except ClientError as e:
            print(f"Error generating pre-signed URL for {path}: {e}")
            return None
    
    def create_directory(self, directory: str) -> bool:
        """
        Create a "directory" in S3.
        
        Note: S3 doesn't have true directories. This method creates a zero-byte
        object with a trailing slash to simulate a directory. This is optional
        in S3 as directories are created implicitly when you upload files.
        
        Args:
            directory (str): Directory path
        
        Returns:
            bool: Always returns True (S3 creates directories implicitly)
        """
        # S3 creates "directories" implicitly when you upload files
        # No need to explicitly create them
        return True
    
    def copy_file(self, src_path: str, dest_path: str) -> bool:
        """
        Copy a file within S3 (server-side copy).
        
        This performs a server-side copy which is more efficient than
        downloading and re-uploading.
        
        Args:
            src_path (str): Source file path
            dest_path (str): Destination file path
        
        Returns:
            bool: True if copy was successful
        """
        try:
            src_key = self._get_full_key(src_path)
            dest_key = self._get_full_key(dest_path)
            
            # Server-side copy
            copy_source = {'Bucket': self.bucket, 'Key': src_key}
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket,
                Key=dest_key
            )
            return True
            
        except ClientError as e:
            print(f"Error copying file in S3 from {src_path} to {dest_path}: {e}")
            return False

