"""
Campaign Brief Parser Module
Parses and validates JSON campaign briefs with type safety.
"""

import json
from typing import Dict, Any, List
from pathlib import Path
from .input_validator import InputValidator


class CampaignBrief:
    """Represents a validated campaign brief."""
    
    def __init__(
        self,
        campaign_name: str,
        products: List[Dict[str, str]],
        target_region: str,
        target_audience: str,
        campaign_message: str,
        target_languages: List[str] = None
    ):
        """
        Initialize campaign brief.
        
        Args:
            campaign_name: Name of the campaign
            products: List of product dictionaries
            target_region: Target region/market
            target_audience: Target audience description
            campaign_message: Campaign message text
            target_languages: List of target language codes (e.g., ['en', 'es', 'fr'])
        """
        self.campaign_name = campaign_name
        self.products = products
        self.target_region = target_region
        self.target_audience = target_audience
        self.campaign_message = campaign_message
        self.target_languages = target_languages if target_languages else ['en']
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert brief to dictionary."""
        return {
            'campaign_name': self.campaign_name,
            'products': self.products,
            'target_region': self.target_region,
            'target_audience': self.target_audience,
            'campaign_message': self.campaign_message,
            'target_languages': self.target_languages
        }
    
    def __repr__(self) -> str:
        return f"CampaignBrief(campaign='{self.campaign_name}', products={len(self.products)})"


class BriefParser:
    """Parses campaign briefs from JSON files."""
    
    @staticmethod
    def parse_file(brief_path: str) -> CampaignBrief:
        """
        Parse campaign brief from JSON file.
        
        Args:
            brief_path: Path to JSON brief file
            
        Returns:
            Validated CampaignBrief object
            
        Raises:
            FileNotFoundError: If brief file doesn't exist
            ValueError: If brief format is invalid
            json.JSONDecodeError: If JSON is malformed
        """
        brief_file = Path(brief_path)
        
        if not brief_file.exists():
            raise FileNotFoundError(f"Brief file not found: {brief_path}")
        
        # Read and parse JSON
        with open(brief_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        return BriefParser.parse_dict(raw_data)
    
    @staticmethod
    def parse_dict(data: Dict[str, Any]) -> CampaignBrief:
        """
        Parse campaign brief from dictionary.
        
        Args:
            data: Dictionary containing brief data
            
        Returns:
            Validated CampaignBrief object
            
        Raises:
            ValueError: If brief format is invalid
        """
        # Validate and sanitize using input validator
        validated_data = InputValidator.validate_campaign_brief(data)
        
        return CampaignBrief(
            campaign_name=validated_data['campaign_name'],
            products=validated_data['products'],
            target_region=validated_data['target_region'],
            target_audience=validated_data['target_audience'],
            campaign_message=validated_data['campaign_message'],
            target_languages=validated_data.get('target_languages', ['en'])
        )
    
    @staticmethod
    def validate_brief_structure(brief_path: str) -> bool:
        """
        Validate brief structure without full parsing.
        
        Args:
            brief_path: Path to JSON brief file
            
        Returns:
            True if structure is valid
        """
        try:
            BriefParser.parse_file(brief_path)
            return True
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            return False

