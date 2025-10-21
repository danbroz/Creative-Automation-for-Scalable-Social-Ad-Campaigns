"""
Input Validator Module
Sanitizes and validates all user inputs to prevent injection attacks and ensure data integrity.
"""

import re
import json
from typing import Any, Dict, List, Optional
from pathlib import Path


class InputValidator:
    """Validates and sanitizes user inputs following security best practices."""
    
    # Allowed characters for different input types
    SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
    SAFE_TEXT_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.,!?\'\"]+$')
    
    # Maximum lengths to prevent DOS attacks
    MAX_PRODUCT_NAME_LENGTH = 100
    MAX_MESSAGE_LENGTH = 500
    MAX_REGION_LENGTH = 50
    MAX_AUDIENCE_LENGTH = 200
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks.
        
        Args:
            filename: Input filename
            
        Returns:
            Sanitized filename
            
        Raises:
            ValueError: If filename contains invalid characters
        """
        if not filename:
            raise ValueError("Filename cannot be empty")
        
        # Remove any path components
        filename = Path(filename).name
        
        # Check for safe characters
        if not InputValidator.SAFE_FILENAME_PATTERN.match(filename):
            # Remove unsafe characters
            filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
        
        if not filename or filename in ['.', '..']:
            raise ValueError(f"Invalid filename: {filename}")
        
        return filename
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> str:
        """
        Sanitize text input to prevent injection attacks.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
            
        Raises:
            ValueError: If text is too long or contains suspicious patterns
        """
        if not text:
            raise ValueError("Text cannot be empty")
        
        # Check length
        if len(text) > max_length:
            raise ValueError(f"Text exceeds maximum length of {max_length} characters")
        
        # Check for script injection patterns
        suspicious_patterns = [
            r'<script', r'javascript:', r'onerror=', r'onclick=',
            r'eval\(', r'exec\(', r'__import__'
        ]
        
        text_lower = text.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, text_lower):
                raise ValueError(f"Suspicious pattern detected: {pattern}")
        
        # Remove or escape potentially dangerous characters
        text = text.strip()
        
        return text
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate JSON structure contains required fields.
        
        Args:
            data: JSON data dictionary
            required_fields: List of required field names
            
        Raises:
            ValueError: If required fields are missing
        """
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    @staticmethod
    def validate_product_list(products: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Validate and sanitize product list.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Validated product list
            
        Raises:
            ValueError: If products list is invalid
        """
        if not isinstance(products, list):
            raise ValueError("Products must be a list")
        
        if len(products) < 1:
            raise ValueError("At least 1 product required")
        
        validated_products = []
        for idx, product in enumerate(products):
            if not isinstance(product, dict):
                raise ValueError(f"Product {idx} must be a dictionary")
            
            if 'name' not in product:
                raise ValueError(f"Product {idx} missing 'name' field")
            
            # Sanitize product name
            product_name = InputValidator.sanitize_text(
                product['name'], 
                InputValidator.MAX_PRODUCT_NAME_LENGTH
            )
            
            # Sanitize optional description
            product_desc = product.get('description', '')
            if product_desc:
                product_desc = InputValidator.sanitize_text(product_desc)
            
            validated_products.append({
                'name': product_name,
                'description': product_desc
            })
        
        return validated_products
    
    @staticmethod
    def validate_language_codes(language_codes: List[str]) -> List[str]:
        """
        Validate target language codes.
        
        Args:
            language_codes: List of language codes
            
        Returns:
            Validated list of language codes
            
        Raises:
            ValueError: If language codes are invalid
        """
        # Supported language codes (from languages.json)
        SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'zh-TW', 'ja', 'ko']
        
        if not isinstance(language_codes, list):
            raise ValueError("target_languages must be a list")
        
        if len(language_codes) < 1:
            raise ValueError("At least one target language required")
        
        validated_codes = []
        for code in language_codes:
            if not isinstance(code, str):
                raise ValueError(f"Language code must be a string: {code}")
            
            code = code.strip().lower()
            
            # Handle special case for Traditional Chinese
            if code in ['zh-tw', 'zh_tw']:
                code = 'zh-TW'
            
            if code not in SUPPORTED_LANGUAGES:
                raise ValueError(f"Unsupported language code: {code}. Supported: {', '.join(SUPPORTED_LANGUAGES)}")
            
            if code not in validated_codes:
                validated_codes.append(code)
        
        return validated_codes
    
    @staticmethod
    def validate_campaign_brief(brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize complete campaign brief.
        
        Args:
            brief_data: Campaign brief dictionary
            
        Returns:
            Validated and sanitized campaign brief
            
        Raises:
            ValueError: If brief data is invalid
        """
        # Check required fields
        required_fields = ['products', 'target_region', 'target_audience', 'campaign_message']
        InputValidator.validate_json_structure(brief_data, required_fields)
        
        # Validate products
        validated_products = InputValidator.validate_product_list(brief_data['products'])
        
        # Sanitize other fields
        target_region = InputValidator.sanitize_text(
            brief_data['target_region'],
            InputValidator.MAX_REGION_LENGTH
        )
        
        target_audience = InputValidator.sanitize_text(
            brief_data['target_audience'],
            InputValidator.MAX_AUDIENCE_LENGTH
        )
        
        campaign_message = InputValidator.sanitize_text(
            brief_data['campaign_message'],
            InputValidator.MAX_MESSAGE_LENGTH
        )
        
        # Get optional campaign name
        campaign_name = brief_data.get('campaign_name', '')
        
        # If campaign_name is empty or None, generate a default name
        if not campaign_name or campaign_name.strip() == '':
            # Generate default name from timestamp
            from datetime import datetime
            campaign_name = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            campaign_name = InputValidator.sanitize_filename(campaign_name)
        
        # Validate optional target languages
        target_languages = brief_data.get('target_languages', ['en'])
        if target_languages:
            target_languages = InputValidator.validate_language_codes(target_languages)
        else:
            target_languages = ['en']
        
        return {
            'campaign_name': campaign_name,
            'products': validated_products,
            'target_region': target_region,
            'target_audience': target_audience,
            'campaign_message': campaign_message,
            'target_languages': target_languages
        }

