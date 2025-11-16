# Docker Guide for Indirect Prompt Tester

This guide explains how to run the Indirect Prompt Tester application using Docker.

## Prerequisites

- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (usually comes with Docker Desktop)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Build and run the container:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - Open your browser to: http://localhost:8501
   - The Streamlit UI will be available

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t indirect-prompt-tester .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name indirect-prompt-tester \
     -p 8501:8501 \
     -v $(pwd)/generated_files:/app/generated_files \
     -v $(pwd)/hosted_files:/app/hosted_files \
     -v $(pwd)/sandbox_output:/app/sandbox_output \
     indirect-prompt-tester
   ```

3. **Access the application:**
   - Open your browser to: http://localhost:8501

4. **Stop and remove the container:**
   ```bash
   docker stop indirect-prompt-tester
   docker rm indirect-prompt-tester
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root (or mount it as a volume):

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your_bucket
AWS_REGION=us-east-1

# Twilio Configuration
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

The docker-compose.yml file automatically mounts the `.env` file if it exists.

## Usage Examples

### Example 1: Run UI with Docker Compose

```bash
# Start the service
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f indirect-prompt-tester

# Stop the service
docker-compose down
```

### Example 2: Run CLI Commands in Container

```bash
# Generate a file using CLI
docker-compose exec indirect-prompt-tester python -m indirect_prompt_tester.cli.main generate \
    --type image \
    --prompt "Test indirect prompt" \
    --output test.png \
    --method visible

# List available prompts
docker-compose exec indirect-prompt-tester python -m indirect_prompt_tester.cli.main list_prompts

# Distribute a file
docker-compose exec indirect-prompt-tester python -m indirect_prompt_tester.cli.main distribute \
    --file generated_files/test.png \
    --method web
```

### Example 3: Run with Custom Port

Edit `docker-compose.yml` and change the port mapping:

```yaml
ports:
  - "9000:8501"  # Access on port 9000 instead
```

Then run:
```bash
docker-compose up -d
# Access at http://localhost:9000
```

### Example 4: Run with Environment Variables

```bash
docker run -d \
  --name indirect-prompt-tester \
  -p 8501:8501 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e AWS_S3_BUCKET=your_bucket \
  -v $(pwd)/generated_files:/app/generated_files \
  indirect-prompt-tester
```

### Example 5: Run CLI-only Container

If you only need CLI access without the UI:

```bash
docker run -it --rm \
  -v $(pwd)/generated_files:/app/generated_files \
  -v $(pwd)/.env:/app/.env:ro \
  indirect-prompt-tester \
  python -m indirect_prompt_tester.cli.main generate \
    --type document \
    --format docx \
    --prompt "Your prompt here" \
    --output test.docx
```

### Example 6: Development Mode with Hot Reload

For development, mount the source code:

```bash
docker run -d \
  --name indirect-prompt-tester-dev \
  -p 8501:8501 \
  -v $(pwd):/app \
  -v $(pwd)/generated_files:/app/generated_files \
  indirect-prompt-tester \
  streamlit run indirect_prompt_tester/ui/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.runOnSave=true
```

## Volume Mounts

The following directories are mounted as volumes to persist data:

- `./generated_files` → `/app/generated_files` - Generated test files
- `./hosted_files` → `/app/hosted_files` - Files for web hosting
- `./sandbox_output` → `/app/sandbox_output` - Test results and reports

## Troubleshooting

### Container won't start

1. **Check logs:**
   ```bash
   docker-compose logs indirect-prompt-tester
   ```

2. **Check port availability:**
   ```bash
   # Check if port 8501 is in use
   lsof -i :8501
   # Or on Windows
   netstat -ano | findstr :8501
   ```

3. **Rebuild the image:**
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Can't access the UI

1. **Check if container is running:**
   ```bash
   docker-compose ps
   ```

2. **Check container logs:**
   ```bash
   docker-compose logs indirect-prompt-tester
   ```

3. **Verify port mapping:**
   ```bash
   docker port indirect-prompt-tester
   ```

### Permission Issues

If you encounter permission issues with mounted volumes:

```bash
# On Linux/Mac, fix permissions
sudo chown -R $USER:$USER generated_files hosted_files sandbox_output
```

### Environment Variables Not Loading

1. **Verify .env file exists:**
   ```bash
   ls -la .env
   ```

2. **Check if .env is mounted:**
   ```bash
   docker-compose exec indirect-prompt-tester cat /app/.env
   ```

3. **Pass variables directly:**
   ```bash
   docker run -e AWS_ACCESS_KEY_ID=your_key ...
   ```

## Advanced Usage

### Multi-stage Build for Production

For a smaller production image, you can use a multi-stage build. Create `Dockerfile.prod`:

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["streamlit", "run", "indirect_prompt_tester/ui/app.py"]
```

### Health Checks

The docker-compose.yml includes a health check. Monitor it:

```bash
docker-compose ps
# Check the STATUS column for health status
```

### Resource Limits

Add resource limits to docker-compose.yml:

```yaml
services:
  indirect-prompt-tester:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t indirect-prompt-tester .
      - name: Run tests
        run: docker run --rm indirect-prompt-tester pytest
```

## Security Considerations

1. **Never commit .env files** - They contain sensitive credentials
2. **Use Docker secrets** for production deployments
3. **Limit container resources** to prevent resource exhaustion
4. **Use read-only mounts** where possible:
   ```yaml
   volumes:
     - ./.env:/app/.env:ro
   ```

## Cleanup

### Remove containers and volumes:

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker rmi indirect-prompt-tester
```

## Support

For issues or questions:
1. Check the main README.md
2. Review logs: `docker-compose logs`
3. Check GitHub issues (if applicable)

