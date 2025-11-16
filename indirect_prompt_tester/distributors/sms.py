"""SMS distributor for sending file links via SMS."""
from pathlib import Path
from typing import Dict, Any, Optional
from twilio.rest import Client
from .base import BaseDistributor
from ..utils.config import Config

class SMSDistributor(BaseDistributor):
    """Distributor for sending file links via SMS."""
    
    def __init__(self):
        self.client = None
        if Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN:
            self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
    
    def distribute(
        self,
        file_path: Path,
        recipient: str,
        file_url: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send file link via SMS.
        
        Args:
            file_path: Path to file (for reference)
            recipient: Phone number of recipient (E.164 format)
            file_url: URL to the file (required for SMS)
            message: Custom message text
        """
        if not self.client:
            raise ValueError("Twilio client not configured. Set credentials in .env file.")
        
        if not file_url:
            raise ValueError("file_url is required for SMS distribution. Upload file first or provide URL.")
        
        try:
            body = message or f"Please access this file: {file_url}"
            
            message_obj = self.client.messages.create(
                body=body,
                from_=Config.TWILIO_PHONE_NUMBER,
                to=recipient
            )
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'recipient': recipient,
                'method': 'sms'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'sms'
            }
    
    def get_name(self) -> str:
        return "SMS"

