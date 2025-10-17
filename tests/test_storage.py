"""
Tests for Storage Abstraction Layer
====================================

Unit tests for storage providers and factory.
"""

import pytest
from pathlib import Path
import json

from src.storage import get_storage, StorageBase
from src.storage.local_storage import LocalStorage


class TestLocalStorage:
    """Test local filesystem storage."""
    
    def test_local_storage_initialization(self):
        """Test that local storage initializes correctly."""
        config = {'local': {'base_path': 'test_output/'}}
        storage = LocalStorage(config)
        
        assert storage.provider_name == 'local'
        assert storage.base_path == Path('test_output/')
    
    def test_save_and_read_file(self):
        """Test saving and reading files."""
        config = {'local': {'base_path': 'test_output/'}}
        storage = LocalStorage(config)
        
        # Test data
        test_data = b"Hello, World!"
        test_path = "test/hello.txt"
        
        # Save file
        assert storage.save_file(test_data, test_path)
        
        # Check file exists
        assert storage.file_exists(test_path)
        
        # Read file
        read_data = storage.read_file(test_path)
        assert read_data == test_data
        
        # Cleanup
        storage.delete_file(test_path)
    
    def test_save_and_read_json(self):
        """Test saving and reading JSON files."""
        config = {'local': {'base_path': 'test_output/'}}
        storage = LocalStorage(config)
        
        # Test data
        test_data = {'name': 'test', 'value': 123}
        test_path = "test/data.json"
        
        # Save JSON
        assert storage.save_json(test_data, test_path)
        
        # Read JSON
        read_data = storage.read_json(test_path)
        assert read_data == test_data
        
        # Cleanup
        storage.delete_file(test_path)
    
    def test_list_files(self):
        """Test listing files in a directory."""
        config = {'local': {'base_path': 'test_output/'}}
        storage = LocalStorage(config)
        
        # Create test files
        storage.save_file(b"test1", "test_list/file1.txt")
        storage.save_file(b"test2", "test_list/file2.txt")
        storage.save_file(b"test3", "test_list/file3.json")
        
        # List all files
        files = storage.list_files("test_list", "**/*")
        assert len(files) >= 3
        
        # List only txt files
        txt_files = storage.list_files("test_list", "*.txt")
        assert len(txt_files) == 2
        
        # Cleanup
        for file in files:
            storage.delete_file(file)
    
    def test_file_exists(self):
        """Test checking if files exist."""
        config = {'local': {'base_path': 'test_output/'}}
        storage = LocalStorage(config)
        
        test_path = "test/exists.txt"
        
        # File shouldn't exist yet
        assert not storage.file_exists(test_path)
        
        # Create file
        storage.save_file(b"test", test_path)
        
        # Now it should exist
        assert storage.file_exists(test_path)
        
        # Cleanup
        storage.delete_file(test_path)
    
    def test_delete_file(self):
        """Test deleting files."""
        config = {'local': {'base_path': 'test_output/'}}
        storage = LocalStorage(config)
        
        test_path = "test/delete.txt"
        
        # Create file
        storage.save_file(b"test", test_path)
        assert storage.file_exists(test_path)
        
        # Delete file
        assert storage.delete_file(test_path)
        assert not storage.file_exists(test_path)


class TestStorageFactory:
    """Test storage factory."""
    
    def test_get_local_storage(self):
        """Test getting local storage from factory."""
        config = {
            'provider': 'local',
            'local': {'base_path': 'test_output/'}
        }
        
        storage = get_storage(config=config)
        
        assert isinstance(storage, LocalStorage)
        assert storage.provider_name == 'local'
    
    def test_invalid_provider(self):
        """Test that invalid provider raises error."""
        config = {'provider': 'invalid_provider'}
        
        with pytest.raises(ValueError):
            get_storage(config=config)


class TestStorageBase:
    """Test storage base class methods."""
    
    def test_get_info(self):
        """Test getting storage info."""
        config = {'local': {'base_path': 'test_output/'}}
        storage = LocalStorage(config)
        
        info = storage.get_info()
        
        assert 'provider' in info
        assert info['provider'] == 'local'
        assert 'config' in info


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

