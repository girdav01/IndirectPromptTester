# Docker Quick Start Guide

## 🚀 Quick Start (3 Steps)

### 1. Build and Start
```bash
docker-compose up -d
```

### 2. Access the UI
Open your browser: **http://localhost:8501**

### 3. Stop When Done
```bash
docker-compose down
```

## 📋 Common Commands

### Using Make (Easier)
```bash
make help          # Show all available commands
make build         # Build the image
make up            # Start the application
make logs          # View logs
make shell         # Open shell in container
make down          # Stop the application
```

### Using Docker Compose Directly
```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose build --no-cache
```

## 💡 Examples

### Example 1: Generate a Test File
```bash
# Using Make
make cli CMD="generate --type image --prompt 'Test prompt' --output test.png --method visible"

# Using Docker directly
docker-compose exec indirect-prompt-tester \
  python -m indirect_prompt_tester.cli.main \
  generate --type image --prompt "Test prompt" --output test.png
```

### Example 2: List Available Prompts
```bash
make cli CMD="list_prompts"
```

### Example 3: Distribute a File
```bash
make cli CMD="distribute --file generated_files/test.png --method web"
```

### Example 4: Run CLI in One Command
```bash
docker run -it --rm \
  -v $(pwd)/generated_files:/app/generated_files \
  indirect-prompt-tester \
  python -m indirect_prompt_tester.cli.main \
  generate --type document --format docx --prompt "Your prompt" --output test.docx
```

## 🔧 Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials (optional, only needed for S3, email, SMS features)

3. Restart the container:
   ```bash
   docker-compose restart
   ```

## 📁 Data Persistence

Generated files are saved in:
- `./generated_files/` - Your test files
- `./hosted_files/` - Files for web hosting
- `./sandbox_output/` - Test results

These directories are automatically created and persist between container restarts.

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml:
ports:
  - "9000:8501"  # Use port 9000 instead
```

### View Logs
```bash
docker-compose logs -f indirect-prompt-tester
```

### Rebuild Everything
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Check Container Status
```bash
docker-compose ps
```

## 📚 More Information

For detailed Docker documentation, see [DOCKER.md](DOCKER.md)

For general usage, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md)

