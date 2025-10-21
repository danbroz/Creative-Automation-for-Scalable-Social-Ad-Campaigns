"""
Image Processor Module
Resizes images to multiple aspect ratios and adds text overlays.
"""

import json
from typing import Dict, List, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class ImageProcessor:
    """Processes images for social media campaigns."""
    
    # Standard aspect ratios for social media
    ASPECT_RATIOS = {
        '1:1': (1080, 1080),      # Instagram square
        '9:16': (1080, 1920),     # Instagram/TikTok stories
        '16:9': (1920, 1080)      # Facebook/YouTube
    }
    
    def __init__(self, brand_guidelines: str = "config/brand_guidelines.json"):
        """
        Initialize image processor.
        
        Args:
            brand_guidelines: Path to brand guidelines configuration
        """
        self.brand_guidelines = self._load_brand_guidelines(brand_guidelines)
    
    def _load_brand_guidelines(self, guidelines_path: str) -> Dict:
        """Load brand guidelines from configuration file."""
        guidelines_file = Path(guidelines_path)
        if not guidelines_file.exists():
            # Use defaults if file doesn't exist
            return self._get_default_guidelines()
        
        with open(guidelines_file, 'r') as f:
            return json.load(f)
    
    def _get_default_guidelines(self) -> Dict:
        """Get default brand guidelines."""
        return {
            'brand_colors': {
                'primary': '#FF6B35',
                'text': '#2D3142'
            },
            'fonts': {
                'heading': 'Arial',
                'size_heading': 72,
                'size_body': 36
            },
            'text_overlay': {
                'position': 'bottom',
                'padding': 40,
                'max_width_percent': 80,
                'shadow': True
            }
        }
    
    def resize_image(
        self,
        input_path: Path,
        aspect_ratio: str,
        output_path: Path
    ) -> Path:
        """
        Resize image to specified aspect ratio.
        
        Args:
            input_path: Path to input image
            aspect_ratio: Target aspect ratio ('1:1', '9:16', or '16:9')
            output_path: Path to save resized image
            
        Returns:
            Path to resized image
        """
        if aspect_ratio not in self.ASPECT_RATIOS:
            raise ValueError(f"Invalid aspect ratio: {aspect_ratio}")
        
        target_size = self.ASPECT_RATIOS[aspect_ratio]
        
        # Open image
        img = Image.open(input_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Calculate scaling to cover the target size
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]
        
        if img_ratio > target_ratio:
            # Image is wider, scale by height
            new_height = target_size[1]
            new_width = int(img.width * (new_height / img.height))
        else:
            # Image is taller, scale by width
            new_width = target_size[0]
            new_height = int(img.height * (new_width / img.width))
        
        # Resize image
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center crop to target size
        left = (new_width - target_size[0]) // 2
        top = (new_height - target_size[1]) // 2
        right = left + target_size[0]
        bottom = top + target_size[1]
        
        img = img.crop((left, top, right, bottom))
        
        # Save resized image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, 'PNG', quality=95)
        
        return output_path
    
    def add_text_overlay(
        self,
        image_path: Path,
        text: str,
        output_path: Path,
        language: str = "en"
    ) -> Path:
        """
        Add text overlay to image following brand guidelines.
        
        Args:
            image_path: Path to input image
            text: Text to overlay
            output_path: Path to save image with overlay
            
        Returns:
            Path to image with text overlay
        """
        img = Image.open(image_path)
        
        # Create drawing context
        draw = ImageDraw.Draw(img)
        
        # Get brand guidelines
        text_config = self.brand_guidelines.get('text_overlay', {})
        font_config = self.brand_guidelines.get('fonts', {})
        colors = self.brand_guidelines.get('brand_colors', {})
        
        # Calculate text positioning
        padding = text_config.get('padding', 40)
        max_width = int(img.width * text_config.get('max_width_percent', 80) / 100)
        
        # Try to load language-specific font, fall back to default
        font_size = font_config.get('size_heading', 72)
        font = self._get_font_for_language(language, font_size)
        
        # Wrap text to fit width
        wrapped_text = self._wrap_text(text, font, max_width, draw)
        
        # Calculate text bounding box
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position text
        position = text_config.get('position', 'bottom')
        if position == 'bottom':
            x = (img.width - text_width) // 2
            y = img.height - text_height - padding
        elif position == 'top':
            x = (img.width - text_width) // 2
            y = padding
        else:  # center
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2
        
        # Draw shadow if enabled
        if text_config.get('shadow', True):
            shadow_offset = text_config.get('shadow_offset', 3)
            shadow_color = text_config.get('shadow_color', '#000000')
            draw.multiline_text(
                (x + shadow_offset, y + shadow_offset),
                wrapped_text,
                font=font,
                fill=shadow_color,
                align='center'
            )
        
        # Draw text
        text_color = colors.get('text', '#FFFFFF')
        draw.multiline_text(
            (x, y),
            wrapped_text,
            font=font,
            fill=text_color,
            align='center'
        )
        
        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, 'PNG', quality=95)
        
        return output_path
    
    def _wrap_text(self, text: str, font, max_width: int, draw) -> str:
        """
        Wrap text to fit within max width.
        
        Args:
            text: Text to wrap
            font: Font to use
            max_width: Maximum width in pixels
            draw: ImageDraw object
            
        Returns:
            Wrapped text with newlines
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def _get_font_for_language(self, language: str, font_size: int):
        """
        Get appropriate font for the given language.
        
        Args:
            language: Language code (e.g., 'en', 'zh', 'ja', 'ko')
            font_size: Font size
            
        Returns:
            PIL ImageFont object
        """
        # Load language configuration
        try:
            import json
            with open('config/languages.json', 'r', encoding='utf-8') as f:
                lang_config = json.load(f)
            lang_info = lang_config.get('supported_languages', {}).get(language, {})
        except:
            lang_info = {}
        
        # Get font family and fallbacks
        font_family = lang_info.get('font_family', 'Arial')
        font_fallbacks = lang_info.get('font_fallbacks', [])
        
        # Try primary font
        font_paths = [
            f"/System/Library/Fonts/{font_family}.ttf",  # macOS
            f"/System/Library/Fonts/Supplemental/{font_family}.ttf",  # macOS Supplemental
            f"/usr/share/fonts/truetype/{font_family.lower()}/{font_family}.ttf",  # Linux
            f"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux fallback
            "Arial.ttf",  # Windows
            "arial.ttf"   # Windows lowercase
        ]
        
        # Add fallback fonts
        for fallback in font_fallbacks:
            font_paths.extend([
                f"/System/Library/Fonts/{fallback}.ttf",
                f"/System/Library/Fonts/Supplemental/{fallback}.ttf",
                f"/usr/share/fonts/truetype/{fallback.lower()}/{fallback}.ttf",
                f"{fallback}.ttf"
            ])
        
        # Try each font path
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, font_size)
            except:
                continue
        
        # If all else fails, try to use a system font that supports Unicode
        try:
            # Try common Unicode fonts
            unicode_fonts = [
                "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",  # macOS (correct path)
                "/System/Library/Fonts/Arial Unicode MS.ttf",  # macOS alternative
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "/System/Library/Fonts/Supplemental/Arial.ttf"  # macOS Arial as last resort
            ]
            
            for unicode_font in unicode_fonts:
                try:
                    return ImageFont.truetype(unicode_font, font_size)
                except:
                    continue
        except:
            pass
        
        # Last resort: default font
        return ImageFont.load_default()
    
    def process_image(
        self,
        input_path: Path,
        text: str,
        output_dir: Path,
        product_name: str,
        language: str = "en"
    ) -> List[Path]:
        """
        Process image for all aspect ratios with text overlay.
        
        Args:
            input_path: Path to input image
            text: Text to overlay
            output_dir: Directory to save processed images
            product_name: Name of product (for file naming)
            
        Returns:
            List of paths to processed images
        """
        processed_images = []
        
        for ratio_name, ratio_size in self.ASPECT_RATIOS.items():
            # Create output directory
            ratio_dir = output_dir / ratio_name
            ratio_dir.mkdir(parents=True, exist_ok=True)
            
            # Resize image
            resized_path = ratio_dir / f"{product_name}_resized.png"
            self.resize_image(input_path, ratio_name, resized_path)
            
            # Add text overlay
            final_path = ratio_dir / f"{product_name}_final.png"
            self.add_text_overlay(resized_path, text, final_path, language)
            
            processed_images.append(final_path)
            
            # Clean up intermediate file
            if resized_path.exists() and resized_path != final_path:
                resized_path.unlink()
        
        return processed_images

