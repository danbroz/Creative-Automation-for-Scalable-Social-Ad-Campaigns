"""
Tests for Content Filter module.
"""

import pytest
from pathlib import Path
from src.content_filter import ContentFilter


class TestContentFilter:
    """Test cases for ContentFilter."""
    
    def test_scan_content_clean(self):
        """Test scanning clean content."""
        filter = ContentFilter()
        text = "Buy our premium product today"
        is_compliant, violations = filter.scan_content(text)
        
        assert is_compliant is True
        assert len(violations) == 0
    
    def test_scan_content_with_violation(self):
        """Test scanning content with prohibited word."""
        filter = ContentFilter()
        text = "This is the best product guaranteed to work"
        is_compliant, violations = filter.scan_content(text)
        
        assert is_compliant is False
        assert len(violations) > 0
    
    def test_get_suggestions(self):
        """Test getting suggestions for prohibited words."""
        filter = ContentFilter()
        suggestions = filter.get_suggestions("guaranteed")
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert "reliable" in suggestions or "trusted" in suggestions
    
    def test_filter_and_suggest(self):
        """Test complete filter and suggest workflow."""
        filter = ContentFilter()
        text = "The best miracle product"
        result = filter.filter_and_suggest(text)
        
        assert 'is_compliant' in result
        assert 'violations_count' in result
        assert 'violations' in result
        
        if not result['is_compliant']:
            assert result['violations_count'] > 0
            for violation in result['violations']:
                assert 'suggestions' in violation

