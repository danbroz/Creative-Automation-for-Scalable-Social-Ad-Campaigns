"""
Asset Manager Module
Manages existing assets and tracks which need generation.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class AssetManager:
    """Manages campaign assets with intelligent caching."""
    
    def __init__(self, assets_dir: str = "assets/products"):
        """
        Initialize asset manager.
        
        Args:
            assets_dir: Directory containing product assets
        """
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache metadata file
        self.metadata_file = self.assets_dir / "asset_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Dict]:
        """
        Load asset metadata from cache.
        
        Returns:
            Dictionary of asset metadata
        """
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self) -> None:
        """Save asset metadata to cache."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def check_asset_exists(self, product_name: str) -> bool:
        """
        Check if asset exists for product.
        
        Args:
            product_name: Name of the product
            
        Returns:
            True if asset exists
        """
        # Normalize product name to filename
        safe_name = self._normalize_product_name(product_name)
        
        # Check for common image formats
        for ext in ['.png', '.jpg', '.jpeg']:
            asset_path = self.assets_dir / f"{safe_name}{ext}"
            if asset_path.exists():
                return True
        
        return False
    
    def get_asset_path(self, product_name: str) -> Optional[Path]:
        """
        Get path to existing asset.
        
        Args:
            product_name: Name of the product
            
        Returns:
            Path to asset or None if not found
        """
        safe_name = self._normalize_product_name(product_name)
        
        for ext in ['.png', '.jpg', '.jpeg']:
            asset_path = self.assets_dir / f"{safe_name}{ext}"
            if asset_path.exists():
                return asset_path
        
        return None
    
    def register_asset(
        self,
        product_name: str,
        asset_path: Path,
        source: str = "generated",
        cost: float = 0.0
    ) -> None:
        """
        Register a new or updated asset.
        
        Args:
            product_name: Name of the product
            asset_path: Path to the asset file
            source: Source of asset ('generated' or 'existing')
            cost: Cost of generation if applicable
        """
        safe_name = self._normalize_product_name(product_name)
        
        # Update metadata
        if safe_name not in self.metadata:
            self.metadata[safe_name] = {
                'product_name': product_name,
                'created_at': datetime.now().isoformat(),
                'usage_count': 0
            }
        
        self.metadata[safe_name].update({
            'asset_path': str(asset_path),
            'source': source,
            'last_used': datetime.now().isoformat(),
            'usage_count': self.metadata[safe_name]['usage_count'] + 1
        })
        
        if source == 'generated':
            self.metadata[safe_name]['generation_cost'] = cost
        
        self._save_metadata()
    
    def get_asset_info(self, product_name: str) -> Optional[Dict]:
        """
        Get metadata for an asset.
        
        Args:
            product_name: Name of the product
            
        Returns:
            Metadata dictionary or None if not found
        """
        safe_name = self._normalize_product_name(product_name)
        return self.metadata.get(safe_name)
    
    def get_assets_summary(self) -> Dict[str, any]:
        """
        Get summary of all assets.
        
        Returns:
            Summary dictionary
        """
        total_assets = len(self.metadata)
        generated_assets = sum(
            1 for asset in self.metadata.values()
            if asset.get('source') == 'generated'
        )
        existing_assets = total_assets - generated_assets
        
        total_cost = sum(
            asset.get('generation_cost', 0)
            for asset in self.metadata.values()
        )
        
        return {
            'total_assets': total_assets,
            'generated': generated_assets,
            'existing': existing_assets,
            'total_generation_cost': round(total_cost, 4)
        }
    
    @staticmethod
    def _normalize_product_name(product_name: str) -> str:
        """
        Normalize product name to safe filename.
        
        Args:
            product_name: Product name
            
        Returns:
            Safe filename
        """
        # Convert to lowercase and replace spaces/special chars
        safe_name = product_name.lower()
        safe_name = safe_name.replace(' ', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')
        return safe_name

