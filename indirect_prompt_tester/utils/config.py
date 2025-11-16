"""Configuration management for the framework."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for managing environment variables and settings."""
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Email Configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    
    # Web Hosting Configuration
    WEB_HOST_PORT = int(os.getenv("WEB_HOST_PORT", "8080"))
    WEB_HOST_DIR = Path(os.getenv("WEB_HOST_DIR", "./hosted_files"))
    
    # Project Directories
    BASE_DIR = Path(__file__).parent.parent.parent
    GENERATED_FILES_DIR = BASE_DIR / "generated_files"
    HOSTED_FILES_DIR = BASE_DIR / "hosted_files"
    SANDBOX_OUTPUT_DIR = BASE_DIR / "sandbox_output"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        cls.GENERATED_FILES_DIR.mkdir(exist_ok=True)
        cls.HOSTED_FILES_DIR.mkdir(exist_ok=True)
        cls.SANDBOX_OUTPUT_DIR.mkdir(exist_ok=True)

