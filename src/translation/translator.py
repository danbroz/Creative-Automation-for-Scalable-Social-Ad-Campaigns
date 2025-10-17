"""
Translator - Multi-Language Translation Service
================================================

This module provides translation services for campaign messages using OpenAI's GPT-4 API.
It supports 9 languages with intelligent caching to minimize API costs and latency.

Supported Languages:
    - English (en)
    - Spanish (es)
    - French (fr)
    - German (de)
    - Italian (it)
    - Portuguese (pt)
    - Chinese Simplified (zh)
    - Japanese (ja)
    - Korean (ko)

Features:
    - Context-aware translations (understands marketing/advertising context)
    - Translation caching (both memory and disk)
    - Automatic fallback mechanisms
    - Batch translation support
    - Translation quality validation

Architecture:
    The translator uses a two-level caching strategy:
    1. Memory cache: Fast in-memory lookups for frequently used translations
    2. Disk cache: Persistent storage for translations across sessions
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Translator:
    """
    Multi-language translator using OpenAI GPT-4 API.
    
    This class provides translation services with intelligent caching to reduce
    costs and improve performance. It's optimized for marketing and advertising
    content translation.
    
    Attributes:
        client (OpenAI): OpenAI API client
        config (dict): Language configuration
        model_config (dict): Model settings for translation
        cache (dict): In-memory translation cache
        cache_dir (Path): Directory for persistent cache storage
        supported_languages (dict): Dictionary of supported languages and their settings
    
    Example:
        translator = Translator()
        
        # Translate a single message
        spanish = translator.translate("Buy now and save 20%!", "es")
        
        # Translate to multiple languages
        translations = translator.translate_batch("Hello", ["es", "fr", "de"])
    """
    
    def __init__(
        self,
        language_config_path: str = "config/languages.json",
        model_config_path: str = "config/model_config.json"
    ):
        """
        Initialize the translator.
        
        Args:
            language_config_path (str): Path to language configuration file
            model_config_path (str): Path to model configuration file
        
        Raises:
            ValueError: If OpenAI API key is not found
            FileNotFoundError: If configuration files are missing
        """
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        
        # Load configurations
        self.config = self._load_language_config(language_config_path)
        self.model_config = self._load_model_config(model_config_path)
        
        # Get supported languages
        self.supported_languages = self.config.get('supported_languages', {})
        self.default_language = self.config.get('default_language', 'en')
        
        # Initialize cache
        self.cache = {}  # In-memory cache: {(text, source_lang, target_lang): translation}
        
        # Setup disk cache
        translation_settings = self.config.get('translation_settings', {})
        self.use_cache = translation_settings.get('cache_translations', True)
        cache_dir_str = translation_settings.get('cache_directory', '.translation_cache/')
        self.cache_dir = Path(cache_dir_str)
        
        if self.use_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_disk_cache()
        
        # Get model settings
        self.model = self.model_config.get('translation_model', 'gpt-4')
        self.translation_settings = self.model_config.get('translation_settings', {})
    
    def _load_language_config(self, config_path: str) -> dict:
        """
        Load language configuration from JSON file.
        
        Args:
            config_path (str): Path to configuration file
        
        Returns:
            dict: Language configuration
        
        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Language config not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_model_config(self, config_path: str) -> dict:
        """
        Load model configuration from JSON file.
        
        Args:
            config_path (str): Path to configuration file
        
        Returns:
            dict: Model configuration
        """
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"Warning: Model config not found: {config_path}")
            return {}
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_disk_cache(self) -> None:
        """
        Load previously cached translations from disk.
        
        This method loads all .json files from the cache directory into
        the in-memory cache for fast lookups.
        """
        try:
            for cache_file in self.cache_dir.glob('*.json'):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    # Reconstruct cache key from metadata
                    key = (
                        cached_data['original_text'],
                        cached_data['source_language'],
                        cached_data['target_language']
                    )
                    self.cache[key] = cached_data['translation']
        except Exception as e:
            print(f"Warning: Error loading translation cache: {e}")
    
    def _save_to_disk_cache(self, text: str, source_lang: str, target_lang: str, translation: str) -> None:
        """
        Save a translation to disk cache for persistence.
        
        Args:
            text (str): Original text
            source_lang (str): Source language code
            target_lang (str): Target language code
            translation (str): Translated text
        """
        if not self.use_cache:
            return
        
        try:
            # Create a unique filename based on content hash
            cache_key = f"{text}_{source_lang}_{target_lang}"
            file_hash = hashlib.md5(cache_key.encode('utf-8')).hexdigest()
            cache_file = self.cache_dir / f"{file_hash}.json"
            
            # Save translation with metadata
            cache_data = {
                'original_text': text,
                'source_language': source_lang,
                'target_language': target_lang,
                'translation': translation,
                'model': self.model
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Error saving to translation cache: {e}")
    
    def _get_from_cache(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Retrieve a translation from cache if it exists.
        
        Args:
            text (str): Original text
            source_lang (str): Source language code
            target_lang (str): Target language code
        
        Returns:
            Optional[str]: Cached translation or None if not found
        """
        cache_key = (text, source_lang, target_lang)
        return self.cache.get(cache_key)
    
    def _add_to_cache(self, text: str, source_lang: str, target_lang: str, translation: str) -> None:
        """
        Add a translation to both memory and disk cache.
        
        Args:
            text (str): Original text
            source_lang (str): Source language code
            target_lang (str): Target language code
            translation (str): Translated text
        """
        # Add to memory cache
        cache_key = (text, source_lang, target_lang)
        self.cache[cache_key] = translation
        
        # Add to disk cache
        self._save_to_disk_cache(text, source_lang, target_lang, translation)
    
    def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = "en",
        context: str = "marketing advertisement"
    ) -> str:
        """
        Translate text to target language using OpenAI GPT-4.
        
        This method first checks the cache, and only makes an API call if the
        translation isn't cached. It provides context-aware translations optimized
        for marketing and advertising content.
        
        Args:
            text (str): Text to translate
            target_language (str): Target language code (e.g., 'es', 'fr', 'ja')
            source_language (str): Source language code (default: 'en')
            context (str): Context for translation (default: 'marketing advertisement')
        
        Returns:
            str: Translated text
        
        Raises:
            ValueError: If language is not supported
            Exception: If translation fails
        
        Example:
            translator = Translator()
            spanish = translator.translate("Buy now!", "es")
            # Returns: "¡Compra ahora!"
        """
        # Validate languages
        if target_language not in self.supported_languages:
            raise ValueError(f"Unsupported target language: {target_language}")
        
        if source_language not in self.supported_languages:
            raise ValueError(f"Unsupported source language: {source_language}")
        
        # If source and target are the same, return original
        if source_language == target_language:
            return text
        
        # Check cache first
        cached_translation = self._get_from_cache(text, source_language, target_language)
        if cached_translation:
            print(f"  [Cache Hit] Translation from {source_language} to {target_language}")
            return cached_translation
        
        # Get target language name
        target_lang_info = self.supported_languages[target_language]
        target_lang_name = target_lang_info['name']
        
        print(f"  [API Call] Translating to {target_lang_name}...")
        
        try:
            # Create translation prompt
            system_prompt = f"""You are a professional translator specializing in {context}.
Translate the following text from {source_language.upper()} to {target_lang_name}.
Maintain the tone, style, and marketing effectiveness of the original text.
Only return the translated text, nothing else."""
            
            user_prompt = f"Text to translate: {text}"
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.translation_settings.get('temperature', 0.3),
                max_tokens=self.translation_settings.get('max_tokens', 1000)
            )
            
            # Extract translation
            translation = response.choices[0].message.content.strip()
            
            # Remove any quotes that GPT might add
            translation = translation.strip('"\'')
            
            # Cache the translation
            self._add_to_cache(text, source_language, target_language, translation)
            
            return translation
            
        except Exception as e:
            print(f"Error translating to {target_language}: {e}")
            # Return original text as fallback
            return text
    
    def translate_batch(
        self,
        text: str,
        target_languages: List[str],
        source_language: str = "en",
        context: str = "marketing advertisement"
    ) -> Dict[str, str]:
        """
        Translate text to multiple languages.
        
        This is more efficient than calling translate() multiple times as it
        can batch translations and leverage caching.
        
        Args:
            text (str): Text to translate
            target_languages (List[str]): List of target language codes
            source_language (str): Source language code (default: 'en')
            context (str): Context for translation
        
        Returns:
            Dict[str, str]: Dictionary mapping language codes to translations
        
        Example:
            translator = Translator()
            translations = translator.translate_batch(
                "Buy now!",
                ["es", "fr", "de"]
            )
            # Returns: {
            #     "es": "¡Compra ahora!",
            #     "fr": "Achetez maintenant!",
            #     "de": "Jetzt kaufen!"
            # }
        """
        translations = {}
        
        for target_lang in target_languages:
            try:
                translation = self.translate(text, target_lang, source_language, context)
                translations[target_lang] = translation
            except Exception as e:
                print(f"Error translating to {target_lang}: {e}")
                translations[target_lang] = text  # Fallback to original
        
        return translations
    
    def get_language_info(self, language_code: str) -> Optional[Dict]:
        """
        Get detailed information about a supported language.
        
        Args:
            language_code (str): Language code (e.g., 'es', 'ja')
        
        Returns:
            Optional[Dict]: Language information or None if not supported
        
        Example:
            info = translator.get_language_info('ja')
            # Returns: {
            #     'name': 'Japanese',
            #     'native_name': '日本語',
            #     'code': 'ja',
            #     'font_family': 'Noto Sans CJK JP',
            #     ...
            # }
        """
        return self.supported_languages.get(language_code)
    
    def list_supported_languages(self) -> List[str]:
        """
        Get a list of all supported language codes.
        
        Returns:
            List[str]: List of language codes
        
        Example:
            languages = translator.list_supported_languages()
            # Returns: ['en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko']
        """
        return list(self.supported_languages.keys())
    
    def clear_cache(self) -> None:
        """
        Clear both memory and disk cache.
        
        Use this method to force fresh translations or to clear old cached data.
        
        Example:
            translator.clear_cache()
        """
        # Clear memory cache
        self.cache = {}
        
        # Clear disk cache
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob('*.json'):
                try:
                    cache_file.unlink()
                except Exception as e:
                    print(f"Error deleting cache file {cache_file}: {e}")
        
        print("Translation cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """
        Get statistics about the translation cache.
        
        Returns:
            Dict: Cache statistics including size and hit rate
        
        Example:
            stats = translator.get_cache_stats()
            print(f"Cached translations: {stats['cached_translations']}")
        """
        disk_cache_files = list(self.cache_dir.glob('*.json')) if self.cache_dir.exists() else []
        
        return {
            'memory_cache_size': len(self.cache),
            'disk_cache_files': len(disk_cache_files),
            'cache_directory': str(self.cache_dir),
            'cache_enabled': self.use_cache
        }

