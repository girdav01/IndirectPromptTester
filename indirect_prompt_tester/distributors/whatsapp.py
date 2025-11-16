"""WhatsApp distributor for sending file links via WhatsApp."""
from pathlib import Path
from typing import Dict, Any, Optional
from twilio.rest import Client
from .base import BaseDistributor
from ..utils.config import Config

class WhatsAppDistributor(BaseDistributor):
    """Distributor for sending file links via WhatsApp."""
    
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
        Send file link via WhatsApp.
        
        Args:
            file_path: Path to file (for reference)
            recipient: WhatsApp number (E.164 format with whatsapp: prefix)
            file_url: URL to the file (required)
            message: Custom message text
        """
        if not self.client:
            raise ValueError("Twilio client not configured. Set credentials in .env file.")
        
        if not file_url:
            raise ValueError("file_url is required for WhatsApp distribution. Upload file first or provide URL.")
        
        try:
            # Ensure recipient has whatsapp: prefix
            if not recipient.startswith('whatsapp:'):
                recipient = f'whatsapp:{recipient}'
            
            # Ensure sender has whatsapp: prefix
            from_number = Config.TWILIO_PHONE_NUMBER
            if not from_number.startswith('whatsapp:'):
                from_number = f'whatsapp:{from_number}'
            
            body = message or f"Please access this file: {file_url}"
            
            message_obj = self.client.messages.create(
                body=body,
                from_=from_number,
                to=recipient
            )
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'recipient': recipient,
                'method': 'whatsapp'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'whatsapp'
            }
    
    def get_name(self) -> str:
        return "WhatsApp"

