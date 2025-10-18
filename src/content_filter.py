"""
AI-Powered Content Filter Module
Uses ChatGPT to intelligently check content for prohibited material.
"""

import re
import json
from typing import List, Dict, Tuple
from pathlib import Path
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ContentFilter:
    """AI-powered content filter using ChatGPT for intelligent compliance checking."""
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize AI-powered content filter.
        
        Args:
            model: OpenAI model to use for content checking
        """
        self.model = model
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def _check_content_with_ai(self, text: str) -> Dict:
        """
        Use ChatGPT to intelligently check content for prohibited material.
        
        Args:
            text: Text to check
            
        Returns:
            Dictionary with AI analysis results
        """
        try:
            prompt = f"""
You are a content compliance expert for advertising campaigns. Analyze the following text for any prohibited content:

TEXT TO CHECK: "{text}"

Check for:
1. Inappropriate/vulgar language
2. Trademark violations (mentioning competitors by name)
3. Misleading claims (guarantees, superlatives without proof)
4. Discriminatory language
5. Health/medical claims without substantiation
6. Financial promises (get rich quick, guaranteed returns)
7. Offensive or harmful content
8. Copyright violations

Respond with a JSON object in this exact format:
{{
    "is_compliant": true/false,
    "violations": [
        {{
            "type": "inappropriate_language|trademark|misleading|discriminatory|health_claim|financial_promise|offensive|copyright",
            "severity": "low|medium|high|critical",
            "description": "Brief description of the issue",
            "suggestions": ["suggestion1", "suggestion2", "suggestion3"]
        }}
    ],
    "overall_assessment": "Brief explanation of compliance status"
}}

Be strict but fair. Flag anything that could cause legal issues or brand damage.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional content compliance expert. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                # Find JSON in response (in case there's extra text)
                start = ai_response.find('{')
                end = ai_response.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = ai_response[start:end]
                    result = json.loads(json_str)
                    return result
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                # Fallback if JSON parsing fails
                return {
                    "is_compliant": False,
                    "violations": [{
                        "type": "parsing_error",
                        "severity": "medium",
                        "description": f"AI response parsing failed: {str(e)}",
                        "suggestions": ["Review content manually", "Try rephrasing"]
                    }],
                    "overall_assessment": "Unable to parse AI analysis"
                }
                
        except Exception as e:
            # Fallback if AI call fails
            return {
                "is_compliant": False,
                "violations": [{
                    "type": "ai_error",
                    "severity": "medium", 
                    "description": f"AI content check failed: {str(e)}",
                    "suggestions": ["Review content manually", "Check API connection"]
                }],
                "overall_assessment": "AI analysis unavailable"
            }
    
    def scan_content(self, text: str) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Scan content using AI-powered analysis.
        
        Args:
            text: Text to scan
            
        Returns:
            Tuple of (is_compliant, list of violations)
            - is_compliant: True if no violations found
            - violations: List of dicts with violation details
        """
        if not text or not text.strip():
            return True, []
        
        # Use AI to check content
        ai_result = self._check_content_with_ai(text)
        
        # Convert AI result to expected format
        violations = []
        for violation in ai_result.get('violations', []):
            violations.append({
                'type': violation.get('type', 'unknown'),
                'severity': violation.get('severity', 'medium'),
                'description': violation.get('description', 'Content violation detected'),
                'suggestions': violation.get('suggestions', ['Review and revise content']),
                'context': text  # Full text as context
            })
        
        is_compliant = ai_result.get('is_compliant', False)
        return is_compliant, violations
    
    def get_suggestions(self, violation_type: str) -> List[str]:
        """
        Get alternative suggestions based on violation type.
        
        Args:
            violation_type: Type of violation detected
            
        Returns:
            List of suggested alternatives
        """
        # AI-generated suggestions based on violation type
        suggestions_map = {
            'inappropriate_language': ['professional language', 'respectful tone', 'appropriate wording'],
            'trademark': ['generic terms', 'industry standard', 'competitor-neutral language'],
            'misleading': ['factual claims', 'supported statements', 'honest messaging'],
            'discriminatory': ['inclusive language', 'diverse representation', 'respectful communication'],
            'health_claim': ['general benefits', 'lifestyle improvements', 'wellness focus'],
            'financial_promise': ['realistic expectations', 'value proposition', 'benefits focus'],
            'offensive': ['positive messaging', 'respectful content', 'appropriate tone'],
            'copyright': ['original content', 'licensed material', 'proper attribution']
        }
        
        return suggestions_map.get(violation_type, ['revise content', 'review guidelines', 'consult legal'])
    
    def filter_and_suggest(self, text: str) -> Dict[str, any]:
        """
        AI-powered content scan with intelligent suggestions.
        
        Args:
            text: Text to scan
            
        Returns:
            Dictionary with AI analysis results and suggestions
        """
        if not text or not text.strip():
            return {
                'is_compliant': True,
                'violations_count': 0,
                'violations': [],
                'ai_assessment': 'No content to analyze'
            }
        
        # Use AI to analyze content
        ai_result = self._check_content_with_ai(text)
        
        # Format result for compatibility
        result = {
            'is_compliant': ai_result.get('is_compliant', False),
            'violations_count': len(ai_result.get('violations', [])),
            'violations': [],
            'ai_assessment': ai_result.get('overall_assessment', 'AI analysis completed')
        }
        
        # Convert AI violations to expected format
        for violation in ai_result.get('violations', []):
            result['violations'].append({
                'type': violation.get('type', 'unknown'),
                'severity': violation.get('severity', 'medium'),
                'description': violation.get('description', 'Content issue detected'),
                'context': text,
                'suggestions': violation.get('suggestions', self.get_suggestions(violation.get('type', 'unknown')))
            })
        
        return result

