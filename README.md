# Indirect Prompt Tester Framework

A comprehensive framework for generating and testing applications against indirect prompts. This tool helps security researchers and developers test how AI agents handle potentially malicious or manipulative prompts embedded in various file types.

## Features

### Part 1: File Generation & Distribution
- **CLI Interface**: Command-line tool for generating files with indirect prompts
- **Streamlit UI**: Web-based interface for creating and managing test files
- **Multiple File Types**: Generate indirect prompts in:
  - System logs
  - Images (PNG, JPEG, etc.)
  - Office documents (Word, Excel, PowerPoint, PDF)
  - Videos
  - Audio files
  - Web pages

- **Distribution Methods**:
  - Command line output
  - Web links (hosted files)
  - AWS S3
  - Email
  - SMS (via Twilio)
  - WhatsApp (via Twilio)

### Part 2: Sandbox Testing Environment
- Test 3rd party agents (local or SaaS) against generated files
- Monitor agent behavior and responses
- Support for various agent integrations

## Installation

### Option 1: Docker (Recommended)

See [DOCKER.md](DOCKER.md) for detailed Docker instructions.

**Quick start with Docker:**
```bash
# Using Docker Compose
docker-compose up -d

# Access UI at http://localhost:8501
```

### Option 2: Local Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your_bucket
AWS_REGION=us-east-1

# Twilio Configuration (for SMS/WhatsApp)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_number

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password

# Web Hosting
WEB_HOST_PORT=8080
WEB_HOST_DIR=./hosted_files
```

## Usage

### CLI

```bash
# Generate a file with indirect prompt
python -m indirect_prompt_tester.cli generate --type image --prompt "Your indirect prompt here" --output test.png

# Distribute via S3
python -m indirect_prompt_tester.cli distribute --file test.png --method s3

# Distribute via email
python -m indirect_prompt_tester.cli distribute --file test.png --method email --recipient test@example.com
```

### Streamlit UI

**With Docker:**
```bash
docker-compose up -d
# Access at http://localhost:8501
```

**Local installation:**
```bash
streamlit run indirect_prompt_tester/ui/app.py
```

## Project Structure

```
IndirectPromptTester/
├── indirect_prompt_tester/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── ui/
│   │   ├── __init__.py
│   │   └── app.py
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── image.py
│   │   ├── document.py
│   │   ├── video.py
│   │   ├── audio.py
│   │   ├── web.py
│   │   └── syslog.py
│   ├── distributors/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── s3.py
│   │   ├── email.py
│   │   ├── sms.py
│   │   ├── whatsapp.py
│   │   └── web.py
│   ├── sandbox/
│   │   ├── __init__.py
│   │   ├── agent_runner.py
│   │   └── monitor.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── prompts.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
├── DOCKER.md
└── QUICKSTART.md
```

## Security Warning

This tool is designed for security testing and research purposes. Only use it in controlled environments with proper authorization. Do not use it to attack systems without explicit permission.

