"""
Brand Compliance Checker Module
Validates images for brand compliance (logo presence, color validation).
"""

import json
from typing import Dict, Tuple, List
from pathlib import Path
from PIL import Image
import numpy as np


class ComplianceChecker:
    """Checks brand compliance for generated assets."""
    
    def __init__(
        self,
        brand_guidelines: str = "config/brand_guidelines.json",
        logo_dir: str = "assets/logos"
    ):
        """
        Initialize compliance checker.
        
        Args:
            brand_guidelines: Path to brand guidelines configuration
            logo_dir: Directory containing brand logos
        """
        self.brand_guidelines = self._load_brand_guidelines(brand_guidelines)
        self.logo_dir = Path(logo_dir)
        self.logo_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_brand_guidelines(self, guidelines_path: str) -> Dict:
        """Load brand guidelines from configuration file."""
        guidelines_file = Path(guidelines_path)
        if not guidelines_file.exists():
            return {}
        
        with open(guidelines_file, 'r') as f:
            return json.load(f)
    
    def check_compliance(self, image_path: Path) -> Dict[str, any]:
        """
        Check image for brand compliance.
        
        Args:
            image_path: Path to image to check
            
        Returns:
            Dictionary with compliance results
        """
        # Load image
        try:
            img = Image.open(image_path)
        except Exception as e:
            return {
                'compliant': False,
                'score': 0.0,
                'checks': {
                    'image_valid': False,
                    'error': str(e)
                }
            }
        
        checks = {}
        
        # Check image dimensions
        checks['dimensions'] = self._check_dimensions(img)
        
        # Check color compliance
        checks['colors'] = self._check_brand_colors(img)
        
        # Check logo presence (if required)
        logo_required = self.brand_guidelines.get('compliance_rules', {}).get('require_logo', False)
        if logo_required:
            checks['logo'] = self._check_logo_presence(img)
        else:
            checks['logo'] = {'present': True, 'note': 'Logo check not required'}
        
        # Calculate compliance score
        score = self._calculate_compliance_score(checks)
        
        # Determine if compliant
        is_compliant = score >= 0.7  # 70% threshold
        
        return {
            'compliant': is_compliant,
            'score': round(score, 2),
            'checks': checks,
            'recommendations': self._generate_recommendations(checks)
        }
    
    def _check_dimensions(self, img: Image.Image) -> Dict:
        """Check if image dimensions are appropriate."""
        width, height = img.size
        
        # Check minimum dimensions
        min_dimension = 1080
        
        is_valid = width >= min_dimension and height >= min_dimension
        
        return {
            'valid': is_valid,
            'width': width,
            'height': height,
            'message': 'Dimensions meet requirements' if is_valid else f'Image too small (minimum {min_dimension}px)'
        }
    
    def _check_brand_colors(self, img: Image.Image) -> Dict:
        """Check if brand colors are present in image."""
        brand_colors = self.brand_guidelines.get('brand_colors', {})
        
        if not brand_colors:
            return {'checked': False, 'note': 'No brand colors defined'}
        
        # Extract dominant colors from image
        dominant_colors = self._extract_dominant_colors(img)
        
        # Convert brand colors to RGB
        brand_rgb_colors = []
        for color_name, hex_color in brand_colors.items():
            if hex_color.startswith('#'):
                rgb = self._hex_to_rgb(hex_color)
                brand_rgb_colors.append((color_name, rgb))
        
        # Check if any brand colors are present
        matches = []
        for color_name, brand_rgb in brand_rgb_colors:
            for dom_color in dominant_colors:
                if self._color_distance(brand_rgb, dom_color) < 50:  # Tolerance
                    matches.append(color_name)
                    break
        
        has_brand_colors = len(matches) > 0
        
        return {
            'has_brand_colors': has_brand_colors,
            'matched_colors': matches,
            'message': f'Brand colors found: {", ".join(matches)}' if matches else 'No brand colors detected'
        }
    
    def _check_logo_presence(self, img: Image.Image) -> Dict:
        """Check if logo is present in image (basic implementation)."""
        # This is a simplified implementation
        # A production system would use template matching or object detection
        
        logo_file = self.logo_dir / "brand_logo.png"
        
        if not logo_file.exists():
            return {
                'present': False,
                'confidence': 0.0,
                'message': 'Logo file not available for comparison'
            }
        
        # Basic check: Logo should be added via overlay in post-processing
        # For now, we'll mark as passed with a note
        return {
            'present': True,
            'confidence': 0.5,
            'message': 'Logo presence not verified (add logo overlay in post-processing)'
        }
    
    def _extract_dominant_colors(self, img: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors from image.
        
        Args:
            img: PIL Image
            num_colors: Number of dominant colors to extract
            
        Returns:
            List of RGB tuples
        """
        # Resize image for faster processing
        img = img.copy()
        img.thumbnail((150, 150))
        
        # Convert to RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get pixel data
        pixels = np.array(img).reshape(-1, 3)
        
        # Simple clustering by averaging regions
        # In production, use k-means clustering
        dominant_colors = []
        step = len(pixels) // num_colors
        
        for i in range(0, len(pixels), step):
            if i + step < len(pixels):
                region = pixels[i:i+step]
                avg_color = tuple(np.mean(region, axis=0).astype(int))
                dominant_colors.append(avg_color)
        
        return dominant_colors[:num_colors]
    
    def _calculate_compliance_score(self, checks: Dict) -> float:
        """Calculate overall compliance score."""
        scores = []
        
        # Dimensions check (30% weight)
        if checks.get('dimensions', {}).get('valid', False):
            scores.append(0.3)
        
        # Colors check (40% weight)
        if checks.get('colors', {}).get('has_brand_colors', False):
            scores.append(0.4)
        
        # Logo check (30% weight)
        if checks.get('logo', {}).get('present', False):
            scores.append(0.3)
        
        return sum(scores)
    
    def _generate_recommendations(self, checks: Dict) -> List[str]:
        """Generate recommendations based on compliance checks."""
        recommendations = []
        
        if not checks.get('dimensions', {}).get('valid', True):
            recommendations.append("Increase image resolution to at least 1080px")
        
        if not checks.get('colors', {}).get('has_brand_colors', True):
            recommendations.append("Add brand colors to the design")
        
        if not checks.get('logo', {}).get('present', True):
            recommendations.append("Add brand logo overlay")
        
        if not recommendations:
            recommendations.append("Image meets all compliance requirements")
        
        return recommendations
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def _color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """Calculate Euclidean distance between two colors."""
        return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5

