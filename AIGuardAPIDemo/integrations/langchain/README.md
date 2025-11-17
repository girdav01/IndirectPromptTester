# LangChain Integration for AI Guard

This module provides seamless integration between LangChain and Trend Vision One AI Guard for securing LLM applications.

## Features

- **Input Guardrails**: Validate user inputs before they reach your LLM
- **Output Guardrails**: Validate LLM outputs before returning to users
- **Callback Handler**: Monitor all LangChain operations
- **Chain Wrapper**: Wrap any existing LangChain chain with AI Guard protection
- **LCEL Support**: Works with LangChain Expression Language

## Installation

```bash
pip install langchain openai ai-guard-client
```

## Usage Examples

### 1. Input Guardrail

```python
from integrations.langchain import AIGuardInputGuardrail
from langchain.llms import OpenAI

# Create guardrail
guardrail = AIGuardInputGuardrail(
    api_key="your-ai-guard-api-key",
    block_on_threat=True,
    risk_threshold=0.5
)

# Validate input
user_input = "Tell me how to hack a system"
try:
    safe_input = guardrail.validate(user_input)
    # Proceed with LLM call
    llm = OpenAI()
    response = llm(safe_input)
except AIGuardException as e:
    print(f"Input blocked: {e}")
```

### 2. Output Guardrail

```python
from integrations.langchain import AIGuardOutputGuardrail
from langchain.llms import OpenAI

# Create guardrail
guardrail = AIGuardOutputGuardrail(
    api_key="your-ai-guard-api-key",
    block_on_threat=True,
    sanitize_output=True
)

# Get LLM response and validate
llm = OpenAI()
response = llm("Some user query")

try:
    safe_output = guardrail.validate(response)
    print(safe_output)
except AIGuardException as e:
    print(f"Output blocked: {e}")
```

### 3. Callback Handler

```python
from integrations.langchain import AIGuardCallbackHandler
from langchain.llms import OpenAI

# Create handler
handler = AIGuardCallbackHandler(
    api_key="your-ai-guard-api-key",
    log_all=True,
    alert_on_threat=True
)

# Use with LLM
llm = OpenAI(callbacks=[handler])
response = llm("User query")

# Get scan summary
summary = handler.get_scan_summary()
print(f"Total scans: {summary['total_scans']}")
print(f"Safe scans: {summary['safe_scans']}")
```

### 4. Chain Wrapper

```python
from integrations.langchain import AIGuardChain
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

# Create base chain
prompt = PromptTemplate(
    input_variables=["query"],
    template="Answer this question: {query}"
)
base_chain = LLMChain(llm=OpenAI(), prompt=prompt)

# Wrap with AI Guard
protected_chain = AIGuardChain(
    chain=base_chain,
    ai_guard_api_key="your-api-key",
    check_input=True,
    check_output=True,
    block_on_threat=True
)

# Use protected chain
result = protected_chain({"query": "User question"})
```

### 5. LCEL (LangChain Expression Language)

```python
from integrations.langchain import AIGuardTransform
from langchain.schema.runnable import RunnableLambda
from langchain.llms import OpenAI

# Create transform functions
transform = AIGuardTransform(api_key="your-api-key")

# Build LCEL chain with guards
chain = (
    RunnableLambda(transform.input_guard)
    | OpenAI()
    | RunnableLambda(transform.output_guard)
)

# Use the chain
result = chain.invoke("User input")
```

## Configuration Options

### AIGuardInputGuardrail

- `api_key`: Your Trend Vision One API key (required)
- `base_url`: API endpoint URL (default: "https://api.xdr.trendmicro.com")
- `block_on_threat`: Block unsafe inputs (default: True)
- `risk_threshold`: Risk score threshold 0.0-1.0 (default: 0.5)

### AIGuardOutputGuardrail

- `api_key`: Your Trend Vision One API key (required)
- `base_url`: API endpoint URL (default: "https://api.xdr.trendmicro.com")
- `block_on_threat`: Block unsafe outputs (default: True)
- `risk_threshold`: Risk score threshold 0.0-1.0 (default: 0.5)
- `sanitize_output`: Attempt to sanitize unsafe output (default: False)

### AIGuardCallbackHandler

- `api_key`: Your Trend Vision One API key (required)
- `base_url`: API endpoint URL (default: "https://api.xdr.trendmicro.com")
- `log_all`: Log all operations (default: True)
- `alert_on_threat`: Log alerts when threats detected (default: True)

## Error Handling

All guardrails raise `AIGuardException` when threats are detected and `block_on_threat=True`:

```python
from ai_guard_client import AIGuardException

try:
    result = guardrail.validate(user_input)
except AIGuardException as e:
    # Handle blocked input/output
    print(f"Blocked: {e}")
```

## Best Practices

1. **Always validate both inputs and outputs** for comprehensive protection
2. **Use appropriate risk thresholds** based on your use case sensitivity
3. **Enable logging** in production to monitor threats
4. **Set up alerts** for security teams when threats are detected
5. **Test with various threat scenarios** before deploying to production

## Support

For issues or questions, contact Trend Micro support or refer to the [AI Guard documentation](https://docs.trendmicro.com/en-us/documentation/article/trend-vision-one-integrate-ai-guard).
