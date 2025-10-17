"""
Output Formatter Module
Standardizes output structure and generates metadata.
"""

import json
from typing import Dict, List
from pathlib import Path
from datetime import datetime


class OutputFormatter:
    """Formats and organizes pipeline outputs."""
    
    def __init__(self, base_output_dir: str = "output"):
        """
        Initialize output formatter.
        
        Args:
            base_output_dir: Base directory for outputs
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
    
    def create_campaign_directory(self, campaign_name: str) -> Path:
        """
        Create directory structure for campaign.
        
        Args:
            campaign_name: Name of the campaign
            
        Returns:
            Path to campaign directory
        """
        campaign_dir = self.base_output_dir / campaign_name
        campaign_dir.mkdir(parents=True, exist_ok=True)
        
        return campaign_dir
    
    def create_product_directory(self, campaign_dir: Path, product_name: str) -> Path:
        """
        Create directory for product within campaign.
        
        Args:
            campaign_dir: Campaign directory path
            product_name: Name of the product
            
        Returns:
            Path to product directory
        """
        # Normalize product name for directory
        safe_name = product_name.lower().replace(' ', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')
        
        product_dir = campaign_dir / safe_name
        product_dir.mkdir(parents=True, exist_ok=True)
        
        return product_dir
    
    def save_asset_metadata(
        self,
        asset_path: Path,
        metadata: Dict
    ) -> None:
        """
        Save metadata for an asset.
        
        Args:
            asset_path: Path to the asset
            metadata: Metadata dictionary
        """
        metadata_path = asset_path.parent / f"{asset_path.stem}_metadata.json"
        
        # Add standard fields
        full_metadata = {
            'asset_path': str(asset_path),
            'generated_at': datetime.now().isoformat(),
            **metadata
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(full_metadata, f, indent=2)
    
    def generate_campaign_summary(
        self,
        campaign_dir: Path,
        campaign_data: Dict
    ) -> Path:
        """
        Generate summary file for campaign.
        
        Args:
            campaign_dir: Campaign directory path
            campaign_data: Campaign data dictionary
            
        Returns:
            Path to summary file
        """
        summary_path = campaign_dir / "campaign_summary.json"
        
        summary = {
            'campaign_name': campaign_data.get('campaign_name', 'Unknown'),
            'generated_at': datetime.now().isoformat(),
            'products': campaign_data.get('products', []),
            'target_region': campaign_data.get('target_region', ''),
            'target_audience': campaign_data.get('target_audience', ''),
            'campaign_message': campaign_data.get('campaign_message', ''),
            'assets_generated': campaign_data.get('assets_generated', 0),
            'compliance_checks': campaign_data.get('compliance_checks', {}),
            'legal_checks': campaign_data.get('legal_checks', {})
        }
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary_path
    
    def get_output_structure(self, campaign_name: str) -> Dict[str, Path]:
        """
        Get standardized output directory structure.
        
        Args:
            campaign_name: Name of the campaign
            
        Returns:
            Dictionary mapping structure names to paths
        """
        campaign_dir = self.base_output_dir / campaign_name
        
        return {
            'campaign_root': campaign_dir,
            'assets': campaign_dir / 'assets',
            'reports': campaign_dir / 'reports',
            'metadata': campaign_dir / 'metadata'
        }

