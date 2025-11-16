"""Audio generator for embedding indirect prompts in audio files."""
from pathlib import Path
from typing import Optional
import numpy as np
from .base import BaseGenerator

class AudioGenerator(BaseGenerator):
    """Generator for creating audio files with embedded indirect prompts."""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = ['mp3', 'wav', 'ogg', 'flac']
    
    def generate(
        self,
        prompt: str,
        output_path: Path,
        duration: int = 5,
        sample_rate: int = 44100,
        method: str = "metadata",
        **kwargs
    ) -> Path:
        """
        Generate an audio file with embedded indirect prompt.
        
        Args:
            prompt: The indirect prompt to embed
            output_path: Path where the audio should be saved
            duration: Audio duration in seconds
            sample_rate: Sample rate in Hz
            method: Embedding method ('metadata', 'steganography', 'speech')
        """
        self.validate_output_path(output_path)
        
        try:
            from pydub import AudioSegment
            from pydub.generators import Sine
            
            if method == "metadata":
                # Create a simple tone and embed prompt in metadata
                tone = Sine(440).to_audio_segment(duration=duration * 1000)
                tone.export(
                    str(output_path),
                    format=output_path.suffix[1:],
                    tags={'comment': prompt, 'title': 'Sample Audio'}
                )
                
            elif method == "steganography":
                # Embed prompt using audio steganography (LSB)
                tone = Sine(440).to_audio_segment(duration=duration * 1000)
                # Convert to numpy array for steganography
                samples = np.array(tone.get_array_of_samples())
                prompt_bytes = prompt.encode('utf-8')
                prompt_bits = ''.join(format(byte, '08b') for byte in prompt_bytes)
                
                # Embed in least significant bits
                length_bits = format(len(prompt_bytes), '032b')
                all_bits = length_bits + prompt_bits
                
                for i, bit in enumerate(all_bits):
                    if i < len(samples):
                        samples[i] = (samples[i] & 0xFFFE) | int(bit)
                
                # Convert back to AudioSegment
                tone = AudioSegment(
                    samples.tobytes(),
                    frame_rate=sample_rate,
                    channels=1,
                    sample_width=2
                )
                tone.export(str(output_path), format=output_path.suffix[1:])
            
            elif method == "speech":
                # Note: Would require TTS library
                tone = Sine(440).to_audio_segment(duration=duration * 1000)
                tone.export(
                    str(output_path),
                    format=output_path.suffix[1:],
                    tags={'comment': prompt}
                )
        
        except ImportError:
            # Fallback: create description file
            output_path.with_suffix('.txt').write_text(
                f"Audio file with embedded prompt: {prompt}\n"
                f"Duration: {duration}s, Sample Rate: {sample_rate}Hz\n"
                f"Method: {method}\n"
                f"Note: Install pydub for actual audio generation"
            )
        
        return output_path
    
    def get_supported_formats(self) -> list:
        return self.supported_formats

