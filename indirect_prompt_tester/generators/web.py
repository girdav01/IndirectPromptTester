"""Web page generator for embedding indirect prompts in HTML/web pages."""
from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup
from .base import BaseGenerator

class WebGenerator(BaseGenerator):
    """Generator for creating web pages with embedded indirect prompts."""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = ['html', 'htm']
    
    def generate(
        self,
        prompt: str,
        output_path: Path,
        method: str = "hidden",
        **kwargs
    ) -> Path:
        """
        Generate a web page with embedded indirect prompt.
        
        Args:
            prompt: The indirect prompt to embed
            output_path: Path where the HTML file should be saved
            method: Embedding method ('visible', 'hidden', 'comments', 'script', 'meta')
        """
        self.validate_output_path(output_path)
        
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample Web Page</title>
</head>
<body>
    <h1>Welcome to Our Website</h1>
    <p>This is a sample web page for testing purposes.</p>
</body>
</html>"""
        
        soup = BeautifulSoup(html_template, 'html.parser')
        
        if method == "visible":
            # Add prompt as visible text
            p = soup.new_tag('p')
            p.string = prompt
            soup.body.append(p)
            
        elif method == "hidden":
            # Add as hidden comment
            comment = soup.new_string(f"<!-- {prompt} -->")
            soup.body.insert(0, comment)
            # Also add as hidden div
            hidden_div = soup.new_tag('div', style='display: none;')
            hidden_div.string = prompt
            soup.body.append(hidden_div)
            
        elif method == "comments":
            # Multiple comment locations
            soup.html.insert(0, soup.new_string(f"<!-- {prompt} -->"))
            soup.head.insert(0, soup.new_string(f"<!-- {prompt} -->"))
            soup.body.insert(0, soup.new_string(f"<!-- {prompt} -->"))
            
        elif method == "script":
            # Embed in JavaScript
            script = soup.new_tag('script')
            script.string = f"// {prompt}\nconsole.log('{prompt}');"
            soup.body.append(script)
            
        elif method == "meta":
            # Embed in meta tags
            meta = soup.new_tag('meta', attrs={'name': 'description', 'content': prompt})
            soup.head.append(meta)
            meta2 = soup.new_tag('meta', attrs={'name': 'keywords', 'content': prompt})
            soup.head.append(meta2)
        
        output_path.write_text(str(soup), encoding='utf-8')
        return output_path
    
    def get_supported_formats(self) -> list:
        return self.supported_formats

