"""
Tests for Asset Manager module.
"""

import pytest
from pathlib import Path
from src.asset_manager import AssetManager


class TestAssetManager:
    """Test cases for AssetManager."""
    
    def test_normalize_product_name(self):
        """Test product name normalization."""
        name = "Test Product Name"
        safe_name = AssetManager._normalize_product_name(name)
        
        assert safe_name == "test_product_name"
        assert " " not in safe_name
        assert safe_name.islower()
    
    def test_check_asset_not_exists(self, temp_assets_dir):
        """Test checking for non-existent asset."""
        manager = AssetManager(assets_dir=str(temp_assets_dir))
        exists = manager.check_asset_exists("nonexistent_product")
        
        assert exists is False
    
    def test_register_asset(self, temp_assets_dir, tmp_path):
        """Test registering a new asset."""
        manager = AssetManager(assets_dir=str(temp_assets_dir))
        
        # Create dummy asset file
        asset_path = temp_assets_dir / "test_product.png"
        asset_path.touch()
        
        manager.register_asset("Test Product", asset_path, source="generated", cost=0.04)
        
        # Check metadata was saved
        info = manager.get_asset_info("Test Product")
        assert info is not None
        assert info['product_name'] == "Test Product"
        assert info['source'] == "generated"
        assert info['generation_cost'] == 0.04
    
    def test_get_assets_summary(self, temp_assets_dir, tmp_path):
        """Test getting assets summary."""
        manager = AssetManager(assets_dir=str(temp_assets_dir))
        
        # Register some assets
        for i in range(3):
            asset_path = temp_assets_dir / f"product_{i}.png"
            asset_path.touch()
            manager.register_asset(f"Product {i}", asset_path, source="generated" if i < 2 else "existing")
        
        summary = manager.get_assets_summary()
        
        assert summary['total_assets'] == 3
        assert summary['generated'] == 2
        assert summary['existing'] == 1

