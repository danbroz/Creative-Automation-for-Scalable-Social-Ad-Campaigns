"""
Tests for Translation Module
=============================

Unit tests for the translation system.
"""

import pytest
from unittest.mock import Mock, patch

from src.translation import Translator


class TestTranslator:
    """Test translator functionality."""
    
    @patch('src.translation.translator.OpenAI')
    def test_translator_initialization(self, mock_openai):
        """Test that translator initializes correctly."""
        translator = Translator()
        
        assert translator.model == 'gpt-4'
        assert 'en' in translator.supported_languages
        assert 'es' in translator.supported_languages
        assert len(translator.supported_languages) == 9  # Changed from 10 to 9
    
    def test_list_supported_languages(self):
        """Test listing supported languages."""
        translator = Translator()
        languages = translator.list_supported_languages()
        
        assert len(languages) > 0
        assert 'en' in languages
        assert 'es' in languages
        assert 'ja' in languages
    
    def test_get_language_info(self):
        """Test getting language information."""
        translator = Translator()
        
        en_info = translator.get_language_info('en')
        assert en_info is not None
        assert en_info['name'] == 'English'
        assert en_info['code'] == 'en'
        
        ja_info = translator.get_language_info('ja')
        assert ja_info is not None
        assert ja_info['name'] == 'Japanese'
        assert ja_info['requires_special_font'] == True
    
    def test_same_language_translation(self):
        """Test that translating to same language returns original."""
        translator = Translator()
        
        text = "Hello World"
        result = translator.translate(text, target_language='en', source_language='en')
        
        assert result == text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

