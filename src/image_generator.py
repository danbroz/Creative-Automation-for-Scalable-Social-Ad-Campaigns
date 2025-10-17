"""
Image Generator Module
Generates product images using OpenAI DALL-E API with retry logic.
"""

import os
import time
import json
import requests
from typing import Optional, Dict
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ImageGenerator:
    """Generates images using DALL-E API with prompt template management."""
    
    def __init__(
        self,
        prompts_config: str = "prompts/image_generation_prompts.json",
        model_config: str = "config/model_config.json"
    ):
        """
        Initialize image generator.
        
        Args:
            prompts_config: Path to prompts configuration file
            model_config: Path to model configuration file
        """
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        
        # Load configurations
        self.prompts = self._load_prompts(prompts_config)
        self.model_config = self._load_model_config(model_config)
        
        # Get model settings
        model_name = self.model_config.get('primary_model', 'dall-e-3')
        self.model_settings = self.model_config['model_settings'][model_name]
        self.model_name = model_name
    
    def _load_prompts(self, prompts_config: str) -> Dict:
        """Load prompt templates from configuration file."""
        prompts_file = Path(prompts_config)
        if not prompts_file.exists():
            raise FileNotFoundError(f"Prompts config not found: {prompts_config}")
        
        with open(prompts_file, 'r') as f:
            return json.load(f)
    
    def _load_model_config(self, model_config: str) -> Dict:
        """Load model configuration."""
        config_file = Path(model_config)
        if not config_file.exists():
            raise FileNotFoundError(f"Model config not found: {model_config}")
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def build_prompt(
        self,
        product_name: str,
        product_description: str = "",
        template_type: str = "product_hero"
    ) -> str:
        """
        Build image generation prompt from template.
        
        Args:
            product_name: Name of the product
            product_description: Description of the product
            template_type: Type of template to use
            
        Returns:
            Formatted prompt string
        """
        template = self.prompts['templates'].get(
            template_type,
            self.prompts['templates']['product_hero']
        )
        
        # Format the template
        prompt = template.format(
            product_name=product_name,
            product_description=product_description or f"high-quality {product_name}"
        )
        
        return prompt
    
    def generate_image(
        self,
        product_name: str,
        product_description: str = "",
        output_path: Optional[Path] = None
    ) -> tuple[Path, float, float]:
        """
        Generate image for product with retry logic.
        
        Args:
            product_name: Name of the product
            product_description: Description of the product
            output_path: Optional path to save image
            
        Returns:
            Tuple of (image_path, generation_time, cost)
            
        Raises:
            Exception: If generation fails after retries
        """
        prompt = self.build_prompt(product_name, product_description)
        
        max_retries = self.model_settings.get('max_retries', 3)
        retry_delay = self.model_settings.get('retry_delay', 2)
        
        last_error = None
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                # Call DALL-E API
                response = self.client.images.generate(
                    model=self.model_name,
                    prompt=prompt,
                    size=self.model_settings.get('size', '1024x1024'),
                    quality=self.model_settings.get('quality', 'standard'),
                    n=1
                )
                
                generation_time = time.time() - start_time
                
                # Get image URL
                image_url = response.data[0].url
                
                # Download image
                if output_path is None:
                    output_path = Path("assets/products") / f"{product_name.lower().replace(' ', '_')}.png"
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Download and save image
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    f.write(img_response.content)
                
                # Calculate cost
                cost = self._calculate_cost()
                
                return output_path, generation_time, cost
                
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    raise Exception(
                        f"Failed to generate image after {max_retries} attempts: {str(e)}"
                    ) from e
        
        raise Exception(f"Image generation failed: {last_error}")
    
    def _calculate_cost(self) -> float:
        """
        Calculate cost of image generation.
        
        Returns:
            Cost in USD
        """
        pricing = self.model_config.get('pricing', {})
        
        # Build pricing key
        quality = self.model_settings.get('quality', 'standard')
        size = self.model_settings.get('size', '1024x1024').replace('x', '')
        pricing_key = f"{self.model_name}_{quality}_{size}"
        
        return pricing.get(pricing_key, 0.040)  # Default to standard pricing
    
    def get_generation_stats(self) -> Dict[str, any]:
        """
        Get generation statistics.
        
        Returns:
            Dictionary with model and cost information
        """
        return {
            'model': self.model_name,
            'settings': self.model_settings,
            'cost_per_image': self._calculate_cost()
        }

