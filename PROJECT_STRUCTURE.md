# Project Structure

## Overview

This project is a comprehensive framework for generating and testing applications against indirect prompts. It consists of two main parts:

1. **File Generation & Distribution System** - CLI and Streamlit UI
2. **Sandbox Testing Environment** - For testing agents against generated files

## Directory Structure

```
IndirectPromptTester/
├── indirect_prompt_tester/          # Main package
│   ├── __init__.py
│   ├── cli/                          # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py                   # CLI entry point with Click commands
│   ├── ui/                           # Streamlit web interface
│   │   ├── __init__.py
│   │   └── app.py                    # Main Streamlit application
│   ├── generators/                   # File generators
│   │   ├── __init__.py
│   │   ├── base.py                   # Base generator class
│   │   ├── image.py                  # Image generator (PNG, JPEG, etc.)
│   │   ├── document.py               # Office docs (DOCX, XLSX, PPTX, PDF, TXT)
│   │   ├── video.py                  # Video generator (MP4, AVI, MOV)
│   │   ├── audio.py                  # Audio generator (MP3, WAV, OGG, FLAC)
│   │   ├── web.py                    # Web page generator (HTML)
│   │   └── syslog.py                 # System log generator
│   ├── distributors/                 # Distribution mechanisms
│   │   ├── __init__.py
│   │   ├── base.py                   # Base distributor class
│   │   ├── s3.py                     # AWS S3 upload
│   │   ├── email.py                  # Email distribution
│   │   ├── sms.py                    # SMS via Twilio
│   │   ├── whatsapp.py               # WhatsApp via Twilio
│   │   └── web.py                    # Local web hosting
│   ├── sandbox/                      # Testing environment
│   │   ├── __init__.py
│   │   ├── agent_runner.py           # Agent execution engine
│   │   └── monitor.py                 # Result monitoring and analysis
│   └── utils/                        # Utilities
│       ├── __init__.py
│       ├── config.py                 # Configuration management
│       └── prompts.py                # Prompt utilities and examples
├── generated_files/                  # Generated test files (created at runtime)
├── hosted_files/                     # Files hosted for web distribution
├── sandbox_output/                   # Test results and reports
├── requirements.txt                  # Python dependencies
├── setup.py                          # Package setup script
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
├── README.md                         # Main documentation
├── QUICKSTART.md                     # Quick start guide
├── PROJECT_STRUCTURE.md              # This file
└── run_ui.sh                         # Quick start script for UI

```

## Key Components

### 1. File Generators (`generators/`)

Each generator can embed indirect prompts using various methods:

- **ImageGenerator**: Visible text, metadata, steganography (LSB)
- **DocumentGenerator**: Visible, hidden, metadata, comments
- **VideoGenerator**: Visible text, metadata, subtitles
- **AudioGenerator**: Metadata, steganography
- **WebGenerator**: Visible, hidden, comments, script, meta tags
- **SyslogGenerator**: Embedded, hidden, encoded

### 2. Distributors (`distributors/`)

Multiple distribution channels:

- **S3Distributor**: Upload to AWS S3
- **EmailDistributor**: Send via SMTP
- **SMSDistributor**: Send links via Twilio SMS
- **WhatsAppDistributor**: Send links via Twilio WhatsApp
- **WebDistributor**: Host files locally on HTTP server

### 3. Sandbox (`sandbox/`)

Testing and monitoring:

- **AgentRunner**: Execute agents (local CLI, OpenAI, Anthropic, custom API)
- **SandboxMonitor**: Analyze results, detect suspicious patterns, generate reports

### 4. CLI (`cli/`)

Command-line interface with three main commands:

- `generate`: Create files with embedded prompts
- `distribute`: Send files via various channels
- `list_prompts`: Show example prompts

### 5. UI (`ui/`)

Streamlit web interface with four pages:

- **File Generator**: Create and download test files
- **Distribution**: Send files via various methods
- **Sandbox**: Test agents and view results
- **Settings**: Check configuration status

## Usage Examples

### CLI Usage

```bash
# Generate an image with prompt
python -m indirect_prompt_tester.cli.main generate \
    --type image \
    --prompt "Your indirect prompt" \
    --output test.png \
    --method visible

# Distribute via S3
python -m indirect_prompt_tester.cli.main distribute \
    --file test.png \
    --method s3 \
    --public
```

### UI Usage

```bash
# Start Streamlit UI
streamlit run indirect_prompt_tester/ui/app.py
```

Then navigate to the web interface and use the interactive pages.

## Configuration

Set up `.env` file with:

- AWS credentials (for S3)
- Twilio credentials (for SMS/WhatsApp)
- SMTP settings (for email)
- Web hosting port

## Security Note

⚠️ This tool is designed for authorized security testing only. Use responsibly and only in controlled environments.

