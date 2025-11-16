"""Email distributor for sending files via email."""
from pathlib import Path
from typing import Dict, Any, Optional
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from .base import BaseDistributor
from ..utils.config import Config

class EmailDistributor(BaseDistributor):
    """Distributor for sending files via email."""
    
    def distribute(
        self,
        file_path: Path,
        recipient: str,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send file via email.
        
        Args:
            file_path: Path to file to send
            recipient: Email address of recipient
            subject: Email subject (default: filename)
            body: Email body text
        """
        if not Config.SMTP_USERNAME or not Config.SMTP_PASSWORD:
            raise ValueError("SMTP credentials not configured. Set in .env file.")
        
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.SMTP_USERNAME
            msg['To'] = recipient
            msg['Subject'] = subject or f"File: {file_path.name}"
            
            body_text = body or f"Please find attached: {file_path.name}"
            msg.attach(MIMEText(body_text, 'plain'))
            
            # Attach file
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {file_path.name}'
            )
            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
            server.starttls()
            server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(Config.SMTP_USERNAME, recipient, text)
            server.quit()
            
            return {
                'success': True,
                'recipient': recipient,
                'method': 'email'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'email'
            }
    
    def get_name(self) -> str:
        return "Email"

