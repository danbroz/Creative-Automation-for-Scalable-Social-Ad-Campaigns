"""
Tests for Brief Parser module.
"""

import pytest
from src.brief_parser import BriefParser, CampaignBrief


class TestBriefParser:
    """Test cases for BriefParser."""
    
    def test_parse_file_valid(self, sample_brief_file):
        """Test parsing valid brief file."""
        brief = BriefParser.parse_file(str(sample_brief_file))
        
        assert isinstance(brief, CampaignBrief)
        assert brief.campaign_name == "test_campaign"
        assert len(brief.products) == 2
        assert brief.target_region == "Test Region"
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            BriefParser.parse_file("nonexistent.json")
    
    def test_parse_dict_valid(self, sample_brief_data):
        """Test parsing valid brief dictionary."""
        brief = BriefParser.parse_dict(sample_brief_data)
        
        assert brief.campaign_name == "test_campaign"
        assert len(brief.products) == 2
    
    def test_campaign_brief_to_dict(self, sample_brief_data):
        """Test converting campaign brief back to dict."""
        brief = BriefParser.parse_dict(sample_brief_data)
        result = brief.to_dict()
        
        assert result['campaign_name'] == "test_campaign"
        assert len(result['products']) == 2

