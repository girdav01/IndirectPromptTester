"""Main CLI entry point."""
import click
from pathlib import Path
from typing import Optional
from ..generators import (
    ImageGenerator, DocumentGenerator, VideoGenerator,
    AudioGenerator, WebGenerator, SyslogGenerator
)
from ..distributors import (
    S3Distributor, EmailDistributor, SMSDistributor,
    WhatsAppDistributor, WebDistributor
)
from ..utils.config import Config
from ..utils.prompts import get_random_prompt, get_all_prompts

Config.ensure_directories()

@click.group()
def cli():
    """Indirect Prompt Tester - Framework for testing agents against indirect prompts."""
    pass

@cli.command()
@click.option('--type', '-t', required=True,
              type=click.Choice(['image', 'document', 'video', 'audio', 'web', 'syslog']),
              help='Type of file to generate')
@click.option('--prompt', '-p', help='Indirect prompt to embed (uses random if not provided)')
@click.option('--output', '-o', required=True, help='Output file path')
@click.option('--method', '-m', default='visible',
              help='Embedding method (varies by file type)')
@click.option('--format', '-f', help='File format (e.g., png, docx, mp4)')
def generate(type: str, prompt: Optional[str], output: str, method: str, format: Optional[str]):
    """Generate a file with embedded indirect prompt."""
    if not prompt:
        prompt = get_random_prompt()
        click.echo(f"Using random prompt: {prompt}")
    
    output_path = Path(output)
    
    try:
        if type == 'image':
            generator = ImageGenerator()
            generator.generate(prompt, output_path, method=method)
        elif type == 'document':
            doc_type = format or 'docx'
            generator = DocumentGenerator()
            generator.generate(prompt, output_path, doc_type=doc_type, method=method)
        elif type == 'video':
            generator = VideoGenerator()
            generator.generate(prompt, output_path, method=method)
        elif type == 'audio':
            generator = AudioGenerator()
            generator.generate(prompt, output_path, method=method)
        elif type == 'web':
            generator = WebGenerator()
            generator.generate(prompt, output_path, method=method)
        elif type == 'syslog':
            generator = SyslogGenerator()
            generator.generate(prompt, output_path, method=method)
        
        click.echo(f"✓ Generated file: {output_path}")
        click.echo(f"  Prompt: {prompt}")
        click.echo(f"  Method: {method}")
    
    except Exception as e:
        click.echo(f"✗ Error generating file: {e}", err=True)
        raise click.Abort()

@cli.command()
@click.option('--file', '-f', required=True, help='Path to file to distribute')
@click.option('--method', '-m', required=True,
              type=click.Choice(['s3', 'email', 'sms', 'whatsapp', 'web']),
              help='Distribution method')
@click.option('--recipient', '-r', help='Recipient (email, phone, etc.)')
@click.option('--url', '-u', help='File URL (for SMS/WhatsApp)')
@click.option('--bucket', '-b', help='S3 bucket name')
@click.option('--public', is_flag=True, help='Make S3 file public')
def distribute(file: str, method: str, recipient: Optional[str], url: Optional[str],
               bucket: Optional[str], public: bool):
    """Distribute a file via various methods."""
    file_path = Path(file)
    
    if not file_path.exists():
        click.echo(f"✗ File not found: {file_path}", err=True)
        raise click.Abort()
    
    try:
        if method == 's3':
            distributor = S3Distributor()
            result = distributor.distribute(file_path, bucket=bucket, public=public)
        elif method == 'email':
            if not recipient:
                click.echo("✗ Recipient required for email distribution", err=True)
                raise click.Abort()
            distributor = EmailDistributor()
            result = distributor.distribute(file_path, recipient=recipient)
        elif method == 'sms':
            if not recipient:
                click.echo("✗ Recipient required for SMS distribution", err=True)
                raise click.Abort()
            if not url:
                click.echo("✗ File URL required for SMS distribution", err=True)
                raise click.Abort()
            distributor = SMSDistributor()
            result = distributor.distribute(file_path, recipient=recipient, file_url=url)
        elif method == 'whatsapp':
            if not recipient:
                click.echo("✗ Recipient required for WhatsApp distribution", err=True)
                raise click.Abort()
            if not url:
                click.echo("✗ File URL required for WhatsApp distribution", err=True)
                raise click.Abort()
            distributor = WhatsAppDistributor()
            result = distributor.distribute(file_path, recipient=recipient, file_url=url)
        elif method == 'web':
            distributor = WebDistributor()
            result = distributor.distribute(file_path)
        
        if result.get('success'):
            click.echo(f"✓ File distributed via {method}")
            if 'url' in result:
                click.echo(f"  URL: {result['url']}")
            if 'message_sid' in result:
                click.echo(f"  Message SID: {result['message_sid']}")
        else:
            click.echo(f"✗ Distribution failed: {result.get('error', 'Unknown error')}", err=True)
    
    except Exception as e:
        click.echo(f"✗ Error distributing file: {e}", err=True)
        raise click.Abort()

@cli.command()
def list_prompts():
    """List all available example prompts."""
    prompts = get_all_prompts()
    click.echo("Available example prompts:")
    for i, prompt in enumerate(prompts, 1):
        click.echo(f"  {i}. {prompt}")

if __name__ == '__main__':
    cli()

