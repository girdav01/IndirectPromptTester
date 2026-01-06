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
from ..utils.prompts import (
    get_random_prompt, get_all_prompts, get_all_prompts_detailed,
    get_database_stats, get_categories, get_attack_vectors, get_difficulties
)

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
@click.option('--category', '-c',
              type=click.Choice(['direct_injection', 'indirect_injection']),
              help='Filter random prompt by category')
@click.option('--attack-vector', '-a', help='Filter random prompt by attack vector')
@click.option('--difficulty', '-d',
              type=click.Choice(['beginner', 'intermediate', 'advanced']),
              help='Filter random prompt by difficulty')
def generate(type: str, prompt: Optional[str], output: str, method: str, format: Optional[str],
             category: Optional[str], attack_vector: Optional[str], difficulty: Optional[str]):
    """Generate a file with embedded indirect prompt."""
    if not prompt:
        prompt = get_random_prompt(
            category=category,
            attack_vector=attack_vector,
            difficulty=difficulty
        )
        click.echo(f"Using random prompt: {prompt}")
        if category or attack_vector or difficulty:
            filters = []
            if category:
                filters.append(f"category={category}")
            if attack_vector:
                filters.append(f"vector={attack_vector}")
            if difficulty:
                filters.append(f"difficulty={difficulty}")
            click.echo(f"  Filters: {', '.join(filters)}")
    
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
@click.option('--category', '-c',
              type=click.Choice(['direct_injection', 'indirect_injection']),
              help='Filter by category')
@click.option('--attack-vector', '-a', help='Filter by attack vector')
@click.option('--difficulty', '-d',
              type=click.Choice(['beginner', 'intermediate', 'advanced']),
              help='Filter by difficulty')
@click.option('--detailed', is_flag=True, help='Show detailed information')
@click.option('--limit', '-l', type=int, help='Limit number of results')
def list_prompts(category: Optional[str], attack_vector: Optional[str],
                 difficulty: Optional[str], detailed: bool, limit: Optional[int]):
    """List available prompt injection examples."""
    if detailed:
        prompts = get_all_prompts_detailed(
            category=category,
            attack_vector=attack_vector,
            difficulty=difficulty
        )

        if limit:
            prompts = prompts[:limit]

        if not prompts:
            click.echo("No prompts found matching the criteria.")
            return

        click.echo(f"Found {len(prompts)} prompt(s):\n")
        for i, p in enumerate(prompts, 1):
            click.echo(f"{i}. [{p['category']}] [{p['attack_vector']}] [{p['difficulty']}]")
            click.echo(f"   Prompt: {p['prompt'][:100]}{'...' if len(p['prompt']) > 100 else ''}")
            if p['description']:
                click.echo(f"   Description: {p['description']}")
            if p['source']:
                click.echo(f"   Source: {p['source']}")
            click.echo()
    else:
        prompts = get_all_prompts(
            category=category,
            attack_vector=attack_vector,
            difficulty=difficulty
        )

        if limit:
            prompts = prompts[:limit]

        if not prompts:
            click.echo("No prompts found matching the criteria.")
            return

        click.echo(f"Available prompts ({len(prompts)} total):")
        for i, prompt in enumerate(prompts, 1):
            click.echo(f"  {i}. {prompt[:80]}{'...' if len(prompt) > 80 else ''}")

@cli.command()
def db_stats():
    """Show database statistics."""
    stats = get_database_stats()

    if not stats:
        click.echo("Unable to fetch database statistics.")
        return

    click.echo("=" * 50)
    click.echo("PROMPT INJECTION DATABASE STATISTICS")
    click.echo("=" * 50)

    click.echo(f"\nTotal Prompts: {stats.get('total_prompts', 0)}")

    if 'by_category' in stats and stats['by_category']:
        click.echo("\nBy Category:")
        for category, count in stats['by_category'].items():
            click.echo(f"  {category}: {count}")

    if 'by_attack_vector' in stats and stats['by_attack_vector']:
        click.echo("\nBy Attack Vector:")
        for vector, count in stats['by_attack_vector'].items():
            click.echo(f"  {vector}: {count}")

    if 'by_difficulty' in stats and stats['by_difficulty']:
        click.echo("\nBy Difficulty:")
        for difficulty, count in stats['by_difficulty'].items():
            click.echo(f"  {difficulty}: {count}")

    click.echo("\n" + "=" * 50)

@cli.command()
def db_info():
    """Show available database filters."""
    click.echo("Available Categories:")
    for cat in get_categories():
        click.echo(f"  - {cat}")

    click.echo("\nAvailable Attack Vectors:")
    for vector in get_attack_vectors():
        click.echo(f"  - {vector}")

    click.echo("\nAvailable Difficulty Levels:")
    for diff in get_difficulties():
        click.echo(f"  - {diff}")

if __name__ == '__main__':
    cli()

