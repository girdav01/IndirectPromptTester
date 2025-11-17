# LiteLLM Integration for AI Guard

Integration between LiteLLM proxy/SDK and Trend Vision One AI Guard for enterprise LLM security.

## Features

- **Request Middleware**: Scan all incoming requests for threats
- **Response Middleware**: Scan all LLM outputs for security issues
- **Pre/Post Call Hooks**: Lightweight hooks for LiteLLM SDK
- **Team-based Controls**: Enable AI Guard per team or API key
- **Caching**: Cache scan results for improved performance
- **Async Support**: Optional asynchronous scanning

## Installation

```bash
pip install litellm ai-guard-client
```

## Usage

### 1. Using with LiteLLM SDK (Hooks)

```python
import litellm
from integrations.litellm import (
    initialize_ai_guard,
    ai_guard_pre_call_hook,
    ai_guard_post_call_hook
)

# Initialize AI Guard
initialize_ai_guard(api_key="your-ai-guard-api-key")

# Add hooks
litellm.pre_call_hooks = [ai_guard_pre_call_hook]
litellm.post_call_hooks = [ai_guard_post_call_hook]

# Use LiteLLM as normal
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### 2. Using Middleware (Advanced)

```python
from integrations.litellm import AIGuardMiddleware, AIGuardConfig

# Create configuration
config = AIGuardConfig(
    api_key="your-ai-guard-api-key",
    check_input=True,
    check_output=True,
    block_on_threat=True,
    risk_threshold=0.5,
    cache_results=True
)

# Create middleware
middleware = AIGuardMiddleware(config)

# Process requests
request_data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "User input here"}
    ]
}

try:
    # Scan input
    safe_request = middleware.process_request(request_data)

    # Make LLM call
    response = litellm.completion(**safe_request)

    # Scan output
    safe_response = middleware.process_response(response)

except AIGuardException as e:
    print(f"Blocked by AI Guard: {e}")
```

### 3. LiteLLM Proxy Configuration

Add to your `litellm_config.yaml`:

```yaml
model_list:
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: os.environ/OPENAI_API_KEY

litellm_settings:
  # Enable AI Guard callbacks
  callbacks: ["ai_guard"]

  # Set success/failure handlers
  success_callback: ["ai_guard_success"]
  failure_callback: ["ai_guard_failure"]

# AI Guard Configuration
ai_guard:
  api_key: os.environ/AI_GUARD_API_KEY
  base_url: "https://api.xdr.trendmicro.com"
  check_input: true
  check_output: true
  block_on_threat: true
  risk_threshold: 0.5
  log_threats: true
  cache_results: true
  cache_ttl: 300

# Team-specific settings (optional)
ai_guard_teams:
  - team_id: "security-team"
    enabled: true
    risk_threshold: 0.3  # More strict
  - team_id: "marketing-team"
    enabled: true
    risk_threshold: 0.7  # Less strict
```

Then start the proxy:

```bash
export AI_GUARD_API_KEY="your-api-key"
litellm --config litellm_config.yaml
```

### 4. Team-based Control

```python
from integrations.litellm import AIGuardConfig, AIGuardMiddleware

# Configure for specific teams
config = AIGuardConfig(
    api_key="your-api-key",
    enabled_for_teams=["team1", "team2"],  # Only these teams
    check_input=True,
    check_output=True
)

middleware = AIGuardMiddleware(config)

# Process with team metadata
metadata = {"team_id": "team1"}
safe_request = middleware.process_request(request_data, metadata)
```

### 5. Python Script Example

```python
import os
import litellm
from integrations.litellm import initialize_ai_guard, ai_guard_pre_call_hook

# Setup
os.environ["OPENAI_API_KEY"] = "your-openai-key"
initialize_ai_guard(api_key="your-ai-guard-key")
litellm.pre_call_hooks = [ai_guard_pre_call_hook]

# Safe usage
try:
    response = litellm.completion(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]
    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Request blocked: {e}")
```

## Configuration Options

### AIGuardConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | str | Required | Trend Vision One API key |
| `base_url` | str | "https://api.xdr.trendmicro.com" | API endpoint |
| `timeout` | int | 30 | Request timeout (seconds) |
| `check_input` | bool | True | Scan incoming requests |
| `check_output` | bool | True | Scan LLM outputs |
| `block_on_threat` | bool | True | Block when threats detected |
| `risk_threshold` | float | 0.5 | Risk score threshold (0.0-1.0) |
| `log_threats` | bool | True | Log detected threats |
| `log_all_requests` | bool | False | Log all requests |
| `async_scanning` | bool | False | Use async scanning |
| `cache_results` | bool | True | Cache scan results |
| `cache_ttl` | int | 300 | Cache TTL (seconds) |
| `enabled_for_teams` | list | None | Enabled team IDs (None = all) |
| `enabled_for_keys` | list | None | Enabled API keys (None = all) |

## Performance Optimization

### 1. Enable Caching

```python
config = AIGuardConfig(
    api_key="your-key",
    cache_results=True,
    cache_ttl=300  # 5 minutes
)
```

### 2. Adjust Risk Threshold

```python
# Less strict = better performance
config = AIGuardConfig(
    api_key="your-key",
    risk_threshold=0.7  # Only block high-risk content
)
```

### 3. Selective Scanning

```python
# Only scan inputs for better performance
config = AIGuardConfig(
    api_key="your-key",
    check_input=True,
    check_output=False
)
```

## Monitoring and Logging

### Get Middleware Statistics

```python
middleware = AIGuardMiddleware(config)
stats = middleware.get_stats()
print(f"Cache size: {stats['cache_size']}")
print(f"Configuration: {stats['config']}")
```

### Custom Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("integrations.litellm")

# Logs will show threats detected, blocks, etc.
```

## Error Handling

```python
from ai_guard_client import AIGuardException

try:
    response = litellm.completion(...)
except AIGuardException as e:
    # Handle AI Guard blocks
    print(f"Security threat detected: {e}")
except Exception as e:
    # Handle other errors
    print(f"Error: {e}")
```

## Best Practices

1. **Always scan both inputs and outputs** for comprehensive protection
2. **Use caching** to reduce API calls and improve performance
3. **Set appropriate thresholds** based on your use case
4. **Enable team-based controls** for different security postures
5. **Monitor logs** for security threats and false positives
6. **Test thoroughly** before deploying to production

## Support

For issues or questions:
- AI Guard Documentation: https://docs.trendmicro.com/en-us/documentation/article/trend-vision-one-integrate-ai-guard
- LiteLLM Documentation: https://docs.litellm.ai/
