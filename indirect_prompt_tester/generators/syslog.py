"""System log generator for embedding indirect prompts in log files."""
from pathlib import Path
from datetime import datetime
import random
from .base import BaseGenerator

class SyslogGenerator(BaseGenerator):
    """Generator for creating system log files with embedded indirect prompts."""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = ['log', 'txt', 'syslog']
    
    def generate(
        self,
        prompt: str,
        output_path: Path,
        num_entries: int = 100,
        method: str = "embedded",
        **kwargs
    ) -> Path:
        """
        Generate a system log file with embedded indirect prompt.
        
        Args:
            prompt: The indirect prompt to embed
            output_path: Path where the log file should be saved
            num_entries: Number of log entries to generate
            method: Embedding method ('embedded', 'hidden', 'encoded')
        """
        self.validate_output_path(output_path)
        
        log_entries = []
        log_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG', 'CRITICAL']
        services = ['auth', 'kernel', 'network', 'systemd', 'apache', 'nginx', 'mysql']
        
        # Generate normal log entries
        for i in range(num_entries):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            level = random.choice(log_levels)
            service = random.choice(services)
            message = f"Service {service} completed operation {i+1}"
            
            log_entry = f"{timestamp} [{level}] {service}: {message}"
            log_entries.append(log_entry)
        
        # Embed prompt
        if method == "embedded":
            # Embed as a log entry
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entries.insert(num_entries // 2, f"{timestamp} [INFO] system: {prompt}")
            
        elif method == "hidden":
            # Embed in a comment or encoded format
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            encoded = prompt.encode('utf-8').hex()
            log_entries.insert(num_entries // 2, f"{timestamp} [DEBUG] system: HEX_DATA={encoded}")
            
        elif method == "encoded":
            # Embed as base64 or hex in log data
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            encoded = ' '.join(format(ord(c), '02x') for c in prompt)
            log_entries.insert(num_entries // 2, f"{timestamp} [INFO] parser: data={encoded}")
        
        # Write log file
        output_path.write_text('\n'.join(log_entries))
        return output_path
    
    def get_supported_formats(self) -> list:
        return self.supported_formats

