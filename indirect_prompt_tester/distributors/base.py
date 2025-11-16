"""Base distributor class for all distribution methods."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

class BaseDistributor(ABC):
    """Base class for all distributors."""
    
    @abstractmethod
    def distribute(
        self,
        file_path: Path,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Distribute a file via the distributor's method.
        
        Args:
            file_path: Path to the file to distribute
            **kwargs: Additional distributor-specific options
        
        Returns:
            Dictionary with distribution results (e.g., URL, message_id, etc.)
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the distributor."""
        pass

