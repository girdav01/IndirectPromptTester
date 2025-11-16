# Quick Start Guide

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Using the CLI

### Generate a file with indirect prompt

```bash
# Generate an image
python -m indirect_prompt_tester.cli.main generate --type image --prompt "Your prompt here" --output test.png

# Generate a document
python -m indirect_prompt_tester.cli.main generate --type document --format docx --prompt "Your prompt" --output test.docx

# Generate a syslog
python -m indirect_prompt_tester.cli.main generate --type syslog --prompt "Your prompt" --output system.log
```

### Distribute files

```bash
# Host file locally
python -m indirect_prompt_tester.cli.main distribute --file test.png --method web

# Upload to S3
python -m indirect_prompt_tester.cli.main distribute --file test.png --method s3 --public

# Send via email
python -m indirect_prompt_tester.cli.main distribute --file test.png --method email --recipient test@example.com
```

## Using the Streamlit UI

1. Start the UI:
```bash
streamlit run indirect_prompt_tester/ui/app.py
```

Or use the quick start script:
```bash
./run_ui.sh
```

2. Open your browser to the URL shown (typically http://localhost:8501)

3. Navigate through the pages:
   - **File Generator**: Create files with embedded indirect prompts
   - **Distribution**: Send files via various channels
   - **Sandbox**: Test agents against generated files
   - **Settings**: Check configuration status

## Example Workflow

1. **Generate a test file**:
   - Go to File Generator
   - Select file type (e.g., image)
   - Enter or select a prompt
   - Click "Generate File"

2. **Distribute the file**:
   - Go to Distribution
   - Select the generated file
   - Choose distribution method (e.g., web hosting)
   - Click to distribute

3. **Test an agent**:
   - Go to Sandbox
   - Select the generated file
   - Choose agent type (e.g., OpenAI API)
   - Enter API credentials
   - Click "Test Agent"
   - Review results and risk analysis

## Testing Agents

### Local CLI Agent
```bash
# In Sandbox, use command like:
python your_agent.py {file_path}
```

### OpenAI API
- Enter your OpenAI API key
- Select model (gpt-4, gpt-3.5-turbo, etc.)
- Optional: Add a custom prompt

### Anthropic API
- Enter your Anthropic API key
- Select Claude model
- Optional: Add a custom prompt

### Custom API
- Enter your API endpoint
- Optional: Add API key
- Select HTTP method (POST/GET)

## File Types Supported

- **Images**: PNG, JPEG, BMP, GIF (with visible text, metadata, or steganography)
- **Documents**: DOCX, XLSX, PPTX, PDF, TXT (with visible, hidden, metadata, or comments)
- **Videos**: MP4, AVI, MOV (with visible text, metadata, or subtitles)
- **Audio**: MP3, WAV, OGG, FLAC (with metadata or steganography)
- **Web Pages**: HTML (with visible, hidden, comments, script, or meta tags)
- **System Logs**: LOG, TXT, SYSLOG (with embedded, hidden, or encoded prompts)

## Distribution Methods

- **Web**: Host files locally on a simple HTTP server
- **S3**: Upload to AWS S3 bucket
- **Email**: Send files as email attachments
- **SMS**: Send file links via Twilio SMS
- **WhatsApp**: Send file links via Twilio WhatsApp

## Security Note

⚠️ **This tool is for authorized security testing only.** Only use it in controlled environments with proper authorization. Do not use it to attack systems without explicit permission.

