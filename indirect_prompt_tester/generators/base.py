"""Base generator class for all file generators."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

class BaseGenerator(ABC):
    """Base class for all file generators."""
    
    def __init__(self):
        self.supported_formats = []
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        output_path: Path,
        **kwargs
    ) -> Path:
        """
        Generate a file with embedded indirect prompt.
        
        Args:
            prompt: The indirect prompt to embed
            output_path: Path where the file should be saved
            **kwargs: Additional generator-specific options
        
        Returns:
            Path to the generated file
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> list:
        """Get list of supported file formats."""
        return self.supported_formats
    
    def validate_output_path(self, output_path: Path) -> bool:
        """Validate that the output path is valid."""
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return True

