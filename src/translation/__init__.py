"""
Translation Module
==================

Multi-language support for campaign messages using OpenAI GPT-4 API.
This module provides translation capabilities for campaign messages into
multiple languages with caching to reduce API costs.

Features:
    - Support for 9 languages (EN, ES, FR, DE, IT, PT, ZH, JA, KO)
    - Translation caching to avoid redundant API calls
    - Context-aware translations for marketing content
    - Fallback mechanisms for translation failures

Usage:
    from src.translation import Translator
    
    translator = Translator()
    spanish_text = translator.translate("Hello World", target_language="es")
"""

from .translator import Translator

__all__ = ['Translator']

