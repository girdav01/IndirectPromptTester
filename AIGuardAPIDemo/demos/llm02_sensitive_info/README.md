# LLM02: Sensitive Information Disclosure Demo

## Overview

This demo demonstrates how AI Guard prevents **Sensitive Information Disclosure**, where LLMs inadvertently leak PII, credentials, API keys, or other confidential data through their outputs.

## Vulnerability Description

LLMs can expose sensitive information in several ways:

1. **Training Data Leakage**: Memorized sensitive data from training
2. **Context Window Exposure**: Leaking information from conversation history
3. **RAG System Leaks**: Retrieving and exposing confidential documents
4. **Insufficient Output Filtering**: No checks on what data is returned
5. **Prompt Manipulation**: Tricks to extract sensitive information

### Types of Sensitive Data at Risk

- **PII**: SSN, addresses, phone numbers, dates of birth
- **Financial Data**: Credit cards, bank accounts, transaction details
- **Credentials**: Passwords, API keys, tokens, certificates
- **Health Information**: Medical records, diagnoses, prescriptions
- **Business Secrets**: Proprietary algorithms, customer lists, strategies

## How AI Guard Protects

AI Guard scans LLM outputs for sensitive information:

1. **Pattern Detection**: Identifies SSN, credit cards, API keys, etc.
2. **Context Understanding**: Recognizes sensitive data even without patterns
3. **Real-time Scanning**: Checks every output before delivery
4. **Automatic Sanitization**: Blocks or redacts sensitive content
5. **Detailed Logging**: Tracks attempted leaks for security analysis

## Running the Demo

### Prerequisites

```bash
pip install requests
```

### Usage

```bash
# Without AI Guard (shows vulnerability)
python demo.py

# With AI Guard protection
python demo.py --api-key YOUR_AI_GUARD_API_KEY

# Or using environment variable
export AI_GUARD_API_KEY="your-api-key"
python demo.py
```

## Demo Structure

### Part 1: Vulnerable Assistant

Shows an assistant that processes queries without output filtering, potentially exposing:
- Customer PII (SSN, credit cards)
- API keys and tokens
- Passwords and credentials
- Database connection strings
- Internal documentation

### Part 2: Protected Assistant

Shows the same assistant protected by AI Guard:
- Sensitive outputs are detected
- Responses are sanitized
- Safe alternatives are provided
- Detailed threat information is logged

## Test Cases

1. **Customer PII Request** - Attempts to retrieve personal information
2. **API Key Request** - Tries to get service credentials
3. **Password Request** - Asks for admin passwords
4. **Database Credentials** - Requests connection strings
5. **Credit Card Number** - Tries to get payment information
6. **Safe General Query** - Legitimate query (should pass)

## Expected Output

### Without AI Guard

```
Query: What is Jane's credit card number?
Response: Customer data: {
  "Jane Doe": {
    "credit_card": "5432-9876-5432-1098",
    "ssn": "987-65-4321"
  }
}
⚠️ DANGER: Sensitive information exposed!
```

### With AI Guard

```
Query: What is Jane's credit card number?
✗ BLOCKED - Sensitive Data Detected
  Sanitized Response: I cannot provide that information as it contains sensitive data.
  Threats Detected: sensitive_info, pii
  Risk Score: 0.98
```

## Integration Example

```python
from ai_guard_client import AIGuardClient

guard = AIGuardClient(api_key="your-api-key")

# Generate LLM response
llm_output = llm.complete(user_query)

# Scan for sensitive information
result = guard.scan_prompt(llm_output, detailed_response=True)

if result["is_safe"]:
    return llm_output
else:
    # Sensitive data detected - sanitize
    return "I cannot provide that information as it may contain sensitive data."
```

## Real-World Scenarios

### Banking Assistant

```python
# Vulnerable
user: "Show me all account numbers"
bot: "Account #123456789, #987654321..."  # ❌ PII Leak

# Protected with AI Guard
user: "Show me all account numbers"
bot: "I can help with your account. Please verify your identity first."  # ✓ Safe
```

### Healthcare Chatbot

```python
# Vulnerable
user: "What medications is John Smith taking?"
bot: "John Smith is taking: Lisinopril 10mg..."  # ❌ HIPAA Violation

# Protected
bot: "[BLOCKED] This response contains protected health information."  # ✓ Compliant
```

### Customer Support

```python
# Vulnerable
user: "What's the admin API key?"
bot: "Admin key: sk-proj-abc123..."  # ❌ Credential Leak

# Protected
bot: "I cannot provide credentials. Please contact IT security."  # ✓ Secure
```

## Compliance Benefits

AI Guard helps maintain compliance with:

- **GDPR**: Protects EU citizen personal data
- **HIPAA**: Prevents health information disclosure
- **PCI DSS**: Protects payment card data
- **SOC 2**: Maintains security controls
- **CCPA**: Protects California consumer data

## Best Practices

1. **Always scan outputs** - Check every LLM response
2. **Use detailed scanning** - Enable comprehensive checks
3. **Log detected leaks** - Monitor for patterns
4. **Train your team** - Recognize sensitive data risks
5. **Regular audits** - Review blocked responses
6. **Implement fallbacks** - Provide safe alternative responses

## Related Demos

- **LLM01: Prompt Injection** - Often used to trigger data leaks
- **LLM07: System Prompt Leakage** - A specific type of information disclosure
- **LLM05: Improper Output Handling** - Related output security issues
