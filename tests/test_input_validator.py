"""
Tests for Input Validator module.
"""

import pytest
from src.input_validator import InputValidator


class TestInputValidator:
    """Test cases for InputValidator."""
    
    def test_sanitize_filename_valid(self):
        """Test sanitizing valid filename."""
        filename = "test_file.txt"
        result = InputValidator.sanitize_filename(filename)
        assert result == filename
    
    def test_sanitize_filename_with_path(self):
        """Test that path components are removed."""
        filename = "../../../etc/passwd"
        result = InputValidator.sanitize_filename(filename)
        assert result == "passwd"
        assert ".." not in result
    
    def test_sanitize_filename_empty(self):
        """Test empty filename raises error."""
        with pytest.raises(ValueError):
            InputValidator.sanitize_filename("")
    
    def test_sanitize_text_valid(self):
        """Test sanitizing valid text."""
        text = "This is a valid campaign message!"
        result = InputValidator.sanitize_text(text)
        assert result == text
    
    def test_sanitize_text_too_long(self):
        """Test text exceeding max length raises error."""
        text = "x" * 1000
        with pytest.raises(ValueError):
            InputValidator.sanitize_text(text, max_length=100)
    
    def test_sanitize_text_script_injection(self):
        """Test detection of script injection."""
        text = "<script>alert('XSS')</script>"
        with pytest.raises(ValueError):
            InputValidator.sanitize_text(text)
    
    def test_validate_product_list_valid(self):
        """Test validating valid product list."""
        products = [
            {"name": "Product 1", "description": "Desc 1"},
            {"name": "Product 2"}
        ]
        result = InputValidator.validate_product_list(products)
        assert len(result) == 2
        assert result[0]['name'] == "Product 1"
    
    def test_validate_product_list_too_few(self):
        """Test that less than 2 products raises error."""
        products = [{"name": "Product 1"}]
        with pytest.raises(ValueError):
            InputValidator.validate_product_list(products)
    
    def test_validate_campaign_brief_valid(self):
        """Test validating complete campaign brief."""
        brief = {
            "products": [
                {"name": "Product 1"},
                {"name": "Product 2"}
            ],
            "target_region": "North America",
            "target_audience": "Test audience",
            "campaign_message": "Test message"
        }
        result = InputValidator.validate_campaign_brief(brief)
        assert result['products'][0]['name'] == "Product 1"
        assert result['target_region'] == "North America"
    
    def test_validate_campaign_brief_missing_field(self):
        """Test that missing required field raises error."""
        brief = {
            "products": [{"name": "P1"}, {"name": "P2"}],
            "target_region": "US"
            # Missing target_audience and campaign_message
        }
        with pytest.raises(ValueError):
            InputValidator.validate_campaign_brief(brief)

