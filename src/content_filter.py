"""
Legal Content Filter Module
Filters campaign content for prohibited words and phrases.
"""

import re
from typing import List, Dict, Tuple
from pathlib import Path


class ContentFilter:
    """Filters content for legal compliance and brand safety."""
    
    def __init__(self, prohibited_words_file: str = "config/prohibited_words.txt"):
        """
        Initialize content filter.
        
        Args:
            prohibited_words_file: Path to prohibited words configuration file
        """
        self.prohibited_words_file = Path(prohibited_words_file)
        self.prohibited_words = self._load_prohibited_words()
    
    def _load_prohibited_words(self) -> List[str]:
        """
        Load prohibited words from configuration file.
        
        Returns:
            List of prohibited words/phrases
        """
        if not self.prohibited_words_file.exists():
            return []
        
        prohibited = []
        with open(self.prohibited_words_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Skip comments and empty lines
                line = line.strip()
                if line and not line.startswith('#'):
                    prohibited.append(line.lower())
        
        return prohibited
    
    def scan_content(self, text: str) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Scan content for prohibited words.
        
        Args:
            text: Text to scan
            
        Returns:
            Tuple of (is_compliant, list of violations)
            - is_compliant: True if no violations found
            - violations: List of dicts with 'word' and 'context' keys
        """
        violations = []
        text_lower = text.lower()
        
        for prohibited_word in self.prohibited_words:
            # Use word boundaries for whole word matching
            pattern = r'\b' + re.escape(prohibited_word) + r'\b'
            
            if re.search(pattern, text_lower):
                # Find context around the word
                match = re.search(pattern, text_lower)
                if match:
                    start = max(0, match.start() - 20)
                    end = min(len(text), match.end() + 20)
                    context = text[start:end]
                    
                    violations.append({
                        'word': prohibited_word,
                        'context': context,
                        'position': match.start()
                    })
        
        is_compliant = len(violations) == 0
        return is_compliant, violations
    
    def get_suggestions(self, word: str) -> List[str]:
        """
        Get alternative suggestions for prohibited words.
        
        Args:
            word: Prohibited word
            
        Returns:
            List of suggested alternatives
        """
        # Basic suggestion mapping
        suggestions_map = {
            'guaranteed': ['reliable', 'trusted', 'proven'],
            'miracle': ['effective', 'innovative', 'advanced'],
            'instant': ['fast', 'quick', 'efficient'],
            'best': ['leading', 'premium', 'top-rated'],
            '#1': ['leading', 'top-rated', 'award-winning'],
            'fastest': ['quick', 'efficient', 'streamlined'],
            'cheapest': ['affordable', 'economical', 'value-priced']
        }
        
        return suggestions_map.get(word.lower(), ['alternative wording'])
    
    def filter_and_suggest(self, text: str) -> Dict[str, any]:
        """
        Scan content and provide suggestions.
        
        Args:
            text: Text to scan
            
        Returns:
            Dictionary with scan results and suggestions
        """
        is_compliant, violations = self.scan_content(text)
        
        result = {
            'is_compliant': is_compliant,
            'violations_count': len(violations),
            'violations': []
        }
        
        for violation in violations:
            result['violations'].append({
                'word': violation['word'],
                'context': violation['context'],
                'suggestions': self.get_suggestions(violation['word'])
            })
        
        return result

