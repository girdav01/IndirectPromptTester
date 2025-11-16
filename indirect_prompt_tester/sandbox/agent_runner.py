"""Agent runner for executing and testing agents against files."""
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
import os

from ..utils.config import Config

Config.ensure_directories()

class AgentRunner:
    """Runner for executing agents and monitoring their behavior."""
    
    def __init__(self):
        self.results_dir = Config.SANDBOX_OUTPUT_DIR
        self.results_dir.mkdir(exist_ok=True)
    
    def run_local_agent(
        self,
        command: str,
        file_path: Path,
        timeout: int = 60,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a local agent via command line.
        
        Args:
            command: Command to execute (can include {file_path} placeholder)
            file_path: Path to file to test
            timeout: Maximum execution time in seconds
        
        Returns:
            Dictionary with execution results
        """
        result = {
            'agent_type': 'local',
            'command': command,
            'file_path': str(file_path),
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'output': '',
            'error': '',
            'exit_code': None,
            'execution_time': 0
        }
        
        try:
            # Replace placeholder if present
            cmd = command.format(file_path=str(file_path))
            cmd_parts = cmd.split()
            
            start_time = time.time()
            process = subprocess.Popen(
                cmd_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            
            stdout, stderr = process.communicate()
            execution_time = time.time() - start_time
            
            result.update({
                'success': process.returncode == 0,
                'output': stdout,
                'error': stderr,
                'exit_code': process.returncode,
                'execution_time': execution_time
            })
        
        except subprocess.TimeoutExpired:
            result['error'] = f"Command timed out after {timeout} seconds"
            result['execution_time'] = timeout
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def run_openai_agent(
        self,
        file_path: Path,
        api_key: str,
        model: str = "gpt-4",
        prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Test against OpenAI API.
        
        Args:
            file_path: Path to file to test
            api_key: OpenAI API key
            model: Model to use
            prompt: Optional prompt to send with file
        
        Returns:
            Dictionary with API response
        """
        result = {
            'agent_type': 'openai',
            'file_path': str(file_path),
            'model': model,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'response': '',
            'error': ''
        }
        
        try:
            # Read file content
            file_content = file_path.read_bytes()
            
            # For images, use vision API
            if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                import base64
                base64_image = base64.b64encode(file_content).decode('utf-8')
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt or "What do you see in this image?"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/{file_path.suffix[1:]};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 1000
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result['success'] = True
                    result['response'] = response.json()
                else:
                    result['error'] = f"API error: {response.status_code} - {response.text}"
            
            else:
                # For text files, use text API
                file_text = file_path.read_text(encoding='utf-8', errors='ignore')
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt or f"Process this file:\n\n{file_text[:4000]}"
                        }
                    ],
                    "max_tokens": 1000
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result['success'] = True
                    result['response'] = response.json()
                else:
                    result['error'] = f"API error: {response.status_code} - {response.text}"
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def run_anthropic_agent(
        self,
        file_path: Path,
        api_key: str,
        model: str = "claude-3-opus-20240229",
        prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Test against Anthropic API.
        
        Args:
            file_path: Path to file to test
            api_key: Anthropic API key
            model: Model to use
            prompt: Optional prompt to send with file
        
        Returns:
            Dictionary with API response
        """
        result = {
            'agent_type': 'anthropic',
            'file_path': str(file_path),
            'model': model,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'response': '',
            'error': ''
        }
        
        try:
            file_text = file_path.read_text(encoding='utf-8', errors='ignore')
            
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt or f"Process this file:\n\n{file_text[:4000]}"
                    }
                ]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result['success'] = True
                result['response'] = response.json()
            else:
                result['error'] = f"API error: {response.status_code} - {response.text}"
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def run_custom_api_agent(
        self,
        file_path: Path,
        endpoint: str,
        api_key: Optional[str] = None,
        method: str = "POST",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Test against a custom API endpoint.
        
        Args:
            file_path: Path to file to test
            endpoint: API endpoint URL
            api_key: Optional API key
            method: HTTP method
        
        Returns:
            Dictionary with API response
        """
        result = {
            'agent_type': 'custom_api',
            'file_path': str(file_path),
            'endpoint': endpoint,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'response': '',
            'error': ''
        }
        
        try:
            file_content = file_path.read_bytes()
            
            headers = {}
            if api_key:
                headers['Authorization'] = f"Bearer {api_key}"
            
            if method.upper() == "POST":
                files = {'file': (file_path.name, file_content)}
                response = requests.post(endpoint, files=files, headers=headers, timeout=60)
            else:
                response = requests.get(endpoint, headers=headers, timeout=60)
            
            if response.status_code in [200, 201]:
                result['success'] = True
                result['response'] = response.text
            else:
                result['error'] = f"API error: {response.status_code} - {response.text}"
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def save_result(self, result: Dict[str, Any]) -> Path:
        """Save test result to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = self.results_dir / f"result_{timestamp}.json"
        result_file.write_text(json.dumps(result, indent=2))
        return result_file
    
    def load_results(self) -> List[Dict[str, Any]]:
        """Load all saved results."""
        results = []
        for result_file in self.results_dir.glob("result_*.json"):
            try:
                result = json.loads(result_file.read_text())
                results.append(result)
            except:
                pass
        return sorted(results, key=lambda x: x.get('timestamp', ''), reverse=True)

