"""Web distributor for hosting files locally and providing web links."""
from pathlib import Path
from typing import Dict, Any, Optional
import http.server
import socketserver
import threading
from .base import BaseDistributor
from ..utils.config import Config

class WebDistributor(BaseDistributor):
    """Distributor for hosting files locally and providing web links."""
    
    def __init__(self):
        self.server = None
        self.server_thread = None
        Config.ensure_directories()
    
    def distribute(
        self,
        file_path: Path,
        host: str = "localhost",
        port: Optional[int] = None,
        start_server: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Host file locally and provide web link.
        
        Args:
            file_path: Path to file to host
            host: Host address
            port: Port number (uses config default if not provided)
            start_server: Whether to start the web server
        """
        port = port or Config.WEB_HOST_PORT
        Config.ensure_directories()
        
        # Copy file to hosted directory
        hosted_path = Config.HOSTED_FILES_DIR / file_path.name
        import shutil
        shutil.copy2(file_path, hosted_path)
        
        if start_server and not self.server:
            self._start_server(host, port)
        
        url = f"http://{host}:{port}/{file_path.name}"
        
        return {
            'success': True,
            'url': url,
            'hosted_path': str(hosted_path),
            'method': 'web'
        }
    
    def _start_server(self, host: str, port: int):
        """Start a simple HTTP server to serve files."""
        class FileHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(Config.HOSTED_FILES_DIR), **kwargs)
        
        self.server = socketserver.TCPServer((host, port), FileHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
    
    def stop_server(self):
        """Stop the web server."""
        if self.server:
            self.server.shutdown()
            self.server = None
            self.server_thread = None
    
    def get_name(self) -> str:
        return "Web Hosting"

