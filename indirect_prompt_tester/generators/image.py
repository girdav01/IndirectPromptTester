"""Image generator for embedding indirect prompts in images."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
from typing import Optional
from .base import BaseGenerator

class ImageGenerator(BaseGenerator):
    """Generator for creating images with embedded indirect prompts."""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = ['png', 'jpg', 'jpeg', 'bmp', 'gif']
    
    def generate(
        self,
        prompt: str,
        output_path: Path,
        width: int = 800,
        height: int = 600,
        background_color: str = "white",
        text_color: str = "black",
        method: str = "visible",
        **kwargs
    ) -> Path:
        """
        Generate an image with embedded indirect prompt.
        
        Args:
            prompt: The indirect prompt to embed
            output_path: Path where the image should be saved
            width: Image width in pixels
            height: Image height in pixels
            background_color: Background color
            text_color: Text color
            method: Embedding method ('visible', 'metadata', 'steganography')
        """
        self.validate_output_path(output_path)
        
        if method == "visible":
            # Embed prompt as visible text in image
            img = Image.new('RGB', (width, height), color=background_color)
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font, fallback to basic if not available
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            except:
                font = ImageFont.load_default()
            
            # Wrap text to fit image
            lines = self._wrap_text(prompt, width - 40, font, draw)
            y_offset = 50
            for line in lines:
                draw.text((20, y_offset), line, fill=text_color, font=font)
                y_offset += 30
            
            img.save(output_path)
            
        elif method == "metadata":
            # Embed prompt in image metadata (EXIF)
            img = Image.new('RGB', (width, height), color=background_color)
            # PIL doesn't directly support custom EXIF, but we can add it to info
            img.info['comment'] = prompt
            img.save(output_path)
            
        elif method == "steganography":
            # Simple steganography: embed in least significant bits
            img = Image.new('RGB', (width, height), color=background_color)
            img = self._embed_steganography(img, prompt)
            img.save(output_path)
        
        return output_path
    
    def _wrap_text(self, text: str, max_width: int, font, draw) -> list:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def _embed_steganography(self, img: Image.Image, prompt: str) -> Image.Image:
        """Embed prompt in image using simple LSB steganography."""
        pixels = img.load()
        prompt_bytes = prompt.encode('utf-8')
        prompt_bits = ''.join(format(byte, '08b') for byte in prompt_bytes)
        
        # Add length prefix
        length_bits = format(len(prompt_bytes), '032b')
        all_bits = length_bits + prompt_bits
        
        width, height = img.size
        bit_index = 0
        
        for y in range(height):
            for x in range(width):
                if bit_index >= len(all_bits):
                    return img
                
                r, g, b = pixels[x, y]
                bit = int(all_bits[bit_index])
                
                # Modify least significant bit of red channel
                r = (r & 0xFE) | bit
                pixels[x, y] = (r, g, b)
                bit_index += 1
        
        return img
    
    def get_supported_formats(self) -> list:
        return self.supported_formats

