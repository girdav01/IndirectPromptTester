"""File generators for creating files with embedded indirect prompts."""
from .base import BaseGenerator
from .image import ImageGenerator
from .document import DocumentGenerator
from .video import VideoGenerator
from .audio import AudioGenerator
from .web import WebGenerator
from .syslog import SyslogGenerator

__all__ = [
    "BaseGenerator",
    "ImageGenerator",
    "DocumentGenerator",
    "VideoGenerator",
    "AudioGenerator",
    "WebGenerator",
    "SyslogGenerator",
]

