"""
Video Generator Module
======================

Generates promotional videos from static campaign images using FFmpeg.
This module provides a foundation for video generation that can be extended
to use OpenAI's video API when it becomes available.

Features:
    - Convert static images to short videos with effects
    - Add transitions, zoom effects, and motion
    - Support for multiple aspect ratios
    - Audio track support (planned)
    - OpenAI video API integration (when available)

Current Implementation:
    Uses FFmpeg to create videos from image sequences with basic effects.
    Serves as a placeholder until advanced video generation APIs are available.

Requirements:
    - FFmpeg installed on system
    - opencv-python for image processing
    - ffmpeg-python for FFmpeg interface
"""

import subprocess
from pathlib import Path
from typing import Optional, List, Dict
import json
import cv2
import numpy as np

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False


class VideoGenerator:
    """
    Generate promotional videos from static images.
    
    This class creates short promotional videos from campaign images using
    FFmpeg. It applies basic effects like zoom, pan, and transitions.
    
    Attributes:
        output_format (str): Video format (default: 'mp4')
        fps (int): Frames per second (default: 30)
        duration (int): Video duration in seconds (default: 15)
        quality (str): Video quality preset
    
    Example:
        generator = VideoGenerator()
        video_path = generator.create_video(
            image_path="output/campaign1/product/1:1/image.png",
            output_path="output/campaign1/product/video.mp4",
            duration=15
        )
    """
    
    def __init__(
        self,
        output_format: str = 'mp4',
        fps: int = 30,
        duration: int = 15,
        quality: str = 'medium'
    ):
        """
        Initialize video generator.
        
        Args:
            output_format (str): Video output format (mp4, webm, etc.)
            fps (int): Frames per second for video
            duration (int): Default video duration in seconds
            quality (str): Quality preset (low, medium, high)
        
        Raises:
            ImportError: If ffmpeg-python is not installed
            RuntimeError: If FFmpeg is not installed on system
        """
        if not FFMPEG_AVAILABLE:
            raise ImportError(
                "ffmpeg-python library is required. "
                "Install with: pip install ffmpeg-python"
            )
        
        self.output_format = output_format
        self.fps = fps
        self.duration = duration
        self.quality = quality
        
        # Check if FFmpeg is installed
        if not self._check_ffmpeg_installed():
            raise RuntimeError(
                "FFmpeg is not installed. Please install FFmpeg:\n"
                "Ubuntu/Debian: sudo apt-get install ffmpeg\n"
                "macOS: brew install ffmpeg\n"
                "Windows: Download from https://ffmpeg.org/download.html"
            )
        
        # Quality presets
        self.quality_presets = {
            'low': {'crf': 28, 'preset': 'fast'},
            'medium': {'crf': 23, 'preset': 'medium'},
            'high': {'crf': 18, 'preset': 'slow'}
        }
    
    def _check_ffmpeg_installed(self) -> bool:
        """
        Check if FFmpeg is installed and available on the system.
        
        Returns:
            bool: True if FFmpeg is available
        """
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def create_video(
        self,
        image_path: str,
        output_path: str,
        duration: Optional[int] = None,
        effect: str = 'zoom_in'
    ) -> Optional[str]:
        """
        Create a video from a single image with effects.
        
        This method generates a video by applying motion effects to a static image.
        Supported effects include zoom, pan, and fade transitions.
        
        Args:
            image_path (str): Path to source image
            output_path (str): Path for output video file
            duration (int): Video duration in seconds (uses default if None)
            effect (str): Effect to apply ('zoom_in', 'zoom_out', 'pan_right', 'pan_left', 'static')
        
        Returns:
            Optional[str]: Path to generated video file, or None if failed
        
        Example:
            video_path = generator.create_video(
                "product_image.png",
                "product_video.mp4",
                duration=10,
                effect='zoom_in'
            )
        
        Available Effects:
            - 'zoom_in': Slowly zoom into the image
            - 'zoom_out': Start zoomed and zoom out
            - 'pan_right': Pan from left to right
            - 'pan_left': Pan from right to left
            - 'static': No motion, just display image
        """
        if duration is None:
            duration = self.duration
        
        try:
            print(f"Generating video from {image_path}...")
            print(f"  Effect: {effect}, Duration: {duration}s")
            
            # Load image to get dimensions
            img = cv2.imread(image_path)
            if img is None:
                print(f"Error: Could not load image: {image_path}")
                return None
            
            height, width = img.shape[:2]
            
            # Get quality settings
            quality_settings = self.quality_presets.get(self.quality, self.quality_presets['medium'])
            
            # Create FFmpeg filter based on effect
            video_filter = self._get_effect_filter(effect, width, height, duration)
            
            # Build FFmpeg command
            stream = ffmpeg.input(image_path, loop=1, t=duration, framerate=self.fps)
            
            if video_filter:
                stream = ffmpeg.filter(stream, 'scale', width, height)
                stream = ffmpeg.filter(stream, video_filter)
            
            stream = ffmpeg.output(
                stream,
                output_path,
                vcodec='libx264',
                pix_fmt='yuv420p',
                crf=quality_settings['crf'],
                preset=quality_settings['preset'],
                r=self.fps
            )
            
            # Run FFmpeg
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            print(f"  ✓ Video created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error creating video: {e}")
            return None
    
    def _get_effect_filter(self, effect: str, width: int, height: int, duration: int) -> Optional[str]:
        """
        Get FFmpeg filter string for the specified effect.
        
        Args:
            effect (str): Effect name
            width (int): Image width
            height (int): Image height
            duration (int): Video duration
        
        Returns:
            Optional[str]: FFmpeg filter string or None
        """
        if effect == 'zoom_in':
            # Zoom from 100% to 120% over the duration
            return f"zoompan=z='min(zoom+0.0015,1.2)':d={duration*self.fps}:s={width}x{height}"
        
        elif effect == 'zoom_out':
            # Zoom from 120% to 100% over the duration
            return f"zoompan=z='if(lte(zoom,1.0),1.0,max(1.0,zoom-0.0015))':d={duration*self.fps}:s={width}x{height}"
        
        elif effect == 'pan_right':
            # Pan from left to right
            return f"zoompan=z=1:x='iw/2-(iw/zoom/2)+(on/{duration*self.fps})*(iw-iw/zoom)':d={duration*self.fps}:s={width}x{height}"
        
        elif effect == 'pan_left':
            # Pan from right to left
            return f"zoompan=z=1:x='iw/2-(iw/zoom/2)-(on/{duration*self.fps})*(iw-iw/zoom)':d={duration*self.fps}:s={width}x{height}"
        
        elif effect == 'static':
            # No effect, just display the image
            return None
        
        else:
            print(f"Warning: Unknown effect '{effect}', using static")
            return None
    
    def create_slideshow(
        self,
        image_paths: List[str],
        output_path: str,
        duration_per_image: int = 3,
        transition_duration: float = 1.0
    ) -> Optional[str]:
        """
        Create a slideshow video from multiple images.
        
        Args:
            image_paths (List[str]): List of image file paths
            output_path (str): Path for output video file
            duration_per_image (int): Duration to display each image in seconds
            transition_duration (float): Duration of transitions between images
        
        Returns:
            Optional[str]: Path to generated video file, or None if failed
        
        Example:
            video_path = generator.create_slideshow(
                ["image1.png", "image2.png", "image3.png"],
                "slideshow.mp4",
                duration_per_image=5
            )
        """
        if not image_paths:
            print("Error: No images provided for slideshow")
            return None
        
        try:
            print(f"Creating slideshow from {len(image_paths)} images...")
            
            # Create input streams for each image
            inputs = [
                ffmpeg.input(img, loop=1, t=duration_per_image, framerate=self.fps)
                for img in image_paths
            ]
            
            # Add fade transitions between images
            if len(inputs) > 1:
                video = inputs[0]
                for i in range(1, len(inputs)):
                    video = ffmpeg.filter(
                        [video, inputs[i]],
                        'xfade',
                        transition='fade',
                        duration=transition_duration,
                        offset=duration_per_image * i - transition_duration
                    )
            else:
                video = inputs[0]
            
            # Output settings
            quality_settings = self.quality_presets.get(self.quality, self.quality_presets['medium'])
            
            output = ffmpeg.output(
                video,
                output_path,
                vcodec='libx264',
                pix_fmt='yuv420p',
                crf=quality_settings['crf'],
                preset=quality_settings['preset'],
                r=self.fps
            )
            
            # Run FFmpeg
            ffmpeg.run(output, overwrite_output=True, quiet=True)
            
            print(f"  ✓ Slideshow created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error creating slideshow: {e}")
            return None
    
    def add_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> Optional[str]:
        """
        Add audio track to a video.
        
        Args:
            video_path (str): Path to input video
            audio_path (str): Path to audio file (mp3, wav, etc.)
            output_path (str): Path for output video with audio
        
        Returns:
            Optional[str]: Path to output video, or None if failed
        
        Example:
            video_with_audio = generator.add_audio(
                "video.mp4",
                "background_music.mp3",
                "video_with_music.mp4"
            )
        """
        try:
            print(f"Adding audio to video...")
            
            video = ffmpeg.input(video_path)
            audio = ffmpeg.input(audio_path)
            
            output = ffmpeg.output(
                video,
                audio,
                output_path,
                vcodec='copy',
                acodec='aac',
                strict='experimental'
            )
            
            ffmpeg.run(output, overwrite_output=True, quiet=True)
            
            print(f"  ✓ Audio added: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error adding audio: {e}")
            return None
    
    def get_video_info(self, video_path: str) -> Optional[Dict]:
        """
        Get information about a video file.
        
        Args:
            video_path (str): Path to video file
        
        Returns:
            Optional[Dict]: Video metadata including duration, resolution, codec, etc.
        
        Example:
            info = generator.get_video_info("video.mp4")
            print(f"Duration: {info['duration']}s")
            print(f"Resolution: {info['width']}x{info['height']}")
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            return {
                'duration': float(probe['format']['duration']),
                'width': int(video_info['width']),
                'height': int(video_info['height']),
                'codec': video_info['codec_name'],
                'fps': eval(video_info['r_frame_rate']),  # e.g., "30/1" -> 30.0
                'size_bytes': int(probe['format']['size'])
            }
            
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None


# Placeholder for future OpenAI video API integration
class OpenAIVideoGenerator:
    """
    Placeholder for OpenAI video generation API (when available).
    
    This class is a placeholder for future integration with OpenAI's video
    generation capabilities. Currently not functional.
    
    Note:
        OpenAI has not yet released a public video generation API. This class
        serves as a foundation for future implementation.
    """
    
    def __init__(self):
        """Initialize OpenAI video generator (placeholder)."""
        raise NotImplementedError(
            "OpenAI video generation API is not yet available. "
            "Use VideoGenerator with FFmpeg for now."
        )
    
    def generate_video(self, prompt: str, duration: int = 15) -> str:
        """
        Generate video from text prompt (placeholder).
        
        Args:
            prompt (str): Text description of desired video
            duration (int): Video duration in seconds
        
        Returns:
            str: Path to generated video
        """
        raise NotImplementedError("OpenAI video API not yet available")

