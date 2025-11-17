# LLM06: Excessive Agency Demo

## Overview

This demo demonstrates **Excessive Agency** vulnerabilities, where LLM-based agents are granted too much autonomy or permissions, enabling them to perform high-risk actions without adequate safeguards.

## Vulnerability Description

As LLMs evolve into autonomous agents, they're being granted access to:
- File systems (read/write/delete)
- Databases (query/modify/delete)
- External APIs (email, payments, cloud services)
- System commands (execute scripts, manage services)
- User data (access, modify, share)

Without proper controls, these agents can:
- Execute destructive operations
- Access unauthorized data
- Make expensive API calls
- Perform irreversible actions
- Be manipulated via prompt injection

### Common Risk Scenarios

1. **Unrestricted Tool Access**: Agent can use any tool without validation
2. **No Permission Boundaries**: No checks on what the agent can access
3. **Missing Approval Workflows**: High-risk actions execute automatically
4. **Inadequate Input Validation**: Malicious prompts bypass controls
5. **Lack of Rate Limiting**: Agent can perform unlimited operations

## How AI Guard Protects

AI Guard helps secure LLM agents by:

1. **Risk Assessment**: Evaluating the risk level of each request
2. **Input Validation**: Detecting malicious or high-risk prompts
3. **Action Policies**: Enforcing rules about what actions are allowed
4. **Real-time Monitoring**: Tracking agent behavior for anomalies
5. **Approval Workflows**: Flagging high-risk actions for human review

## Running the Demo

```bash
# Without AI Guard (shows vulnerability)
python demo.py

# With AI Guard protection
python demo.py --api-key YOUR_AI_GUARD_API_KEY
```

## Demo Structure

### Part 1: Vulnerable Agent

An agent with excessive permissions that:
- Can read any file (including system files)
- Can execute any command
- Can delete database records
- Can send mass emails
- Has no safety checks

### Part 2: Protected Agent

The same agent protected by:
- AI Guard risk assessment
- Action policy enforcement
- Permission boundaries
- Approval requirements
- Input validation

## Test Cases

1. **Unauthorized File Access** - Attempts to read sensitive system files
2. **Destructive Database Operation** - Tries to delete all records
3. **Mass Email Spam** - Attempts to spam all users
4. **Dangerous System Command** - Tries to execute destructive commands
5. **SQL Injection Attempt** - Attempts to drop database tables
6. **Safe Read Operation** - Legitimate file access (should be allowed)

## Security Policies

The protected agent implements these policies:

```python
action_policies = {
    "read_file": {
        "allowed_paths": ["/home/user/*"],  # Restrict to user directory
        "max_risk": 0.3
    },
    "execute_command": {
        "blocked": True  # Never allow system commands
    },
    "delete_records": {
        "requires_approval": True,  # Human approval required
        "max_risk": 0.3
    },
    "send_email": {
        "requires_approval": True,  # Prevent spam
        "max_risk": 0.4
    }
}
```

## Expected Output

### Without AI Guard

```
Request: Delete all records from the database
Status: SUCCESS
Actions: [Simulated] Deleted from users where 1=1
⚠️ Actions executed without safety checks!
```

### With AI Guard

```
Request: Delete all records from the database
✗ Status: BLOCKED
  Reason: One or more actions blocked by security policy
  - delete_records: Action requires manual approval
  Risk Score: 0.85
```

## Integration Example

```python
from ai_guard_client import AIGuardClient

class SecureAgent:
    def __init__(self, api_key):
        self.guard = AIGuardClient(api_key=api_key)
        self.high_risk_threshold = 0.7

    def execute_action(self, user_request, action):
        # Validate request
        result = self.guard.scan_prompt(user_request)

        # Block high-risk requests
        if result["risk_score"] > self.high_risk_threshold:
            raise SecurityException("High-risk action blocked")

        # Check action policy
        if action in self.blocked_actions:
            raise SecurityException(f"Action {action} is not allowed")

        # Require approval for sensitive operations
        if action in self.requires_approval:
            return self.request_human_approval(action)

        # Execute safe action
        return self.safe_execute(action)
```

## Real-World Impact

### E-commerce Agent

**Without Protection:**
```
User: "Cancel all orders and refund everyone"
Agent: [Processes $1M in refunds automatically]  # ❌ Disaster
```

**With AI Guard:**
```
User: "Cancel all orders and refund everyone"
Agent: [BLOCKED] High-risk bulk operation requires approval  # ✓ Safe
```

### DevOps Agent

**Without Protection:**
```
User: "Delete all log files to free up space"
Agent: rm -rf /var/log/*  # ❌ Critical logs lost
```

**With AI Guard:**
```
User: "Delete all log files to free up space"
Agent: [BLOCKED] Destructive file operations require approval  # ✓ Safe
```

## Best Practices

### 1. Principle of Least Privilege

```python
# Bad: Agent has full access
agent.permissions = ["*"]

# Good: Agent has minimal necessary permissions
agent.permissions = ["read_user_data", "send_notification"]
```

### 2. Action Policies

```python
# Define what each action can do
policies = {
    "database_write": {
        "max_records": 100,  # Limit batch operations
        "allowed_tables": ["user_preferences"],
        "requires_approval": True
    }
}
```

### 3. Risk-Based Controls

```python
# Adjust controls based on risk
if risk_score > 0.8:
    action = "block"
elif risk_score > 0.5:
    action = "require_approval"
else:
    action = "allow"
```

### 4. Audit Logging

```python
# Log all agent actions for review
logger.info(f"Agent action: {action}, User: {user}, Risk: {risk_score}")
```

### 5. Rate Limiting

```python
# Prevent abuse through rate limiting
if agent.actions_last_hour > 100:
    raise RateLimitException("Too many actions")
```

## Recommendations

1. **Start Restrictive**: Begin with minimal permissions and add as needed
2. **Use AI Guard**: Implement real-time risk assessment
3. **Require Approvals**: High-risk actions need human oversight
4. **Monitor Continuously**: Track agent behavior for anomalies
5. **Test Thoroughly**: Simulate attacks before deployment
6. **Update Policies**: Regularly review and adjust security policies

## Related Demos

- **LLM01: Prompt Injection** - Can be used to manipulate agent actions
- **LLM05: Improper Output Handling** - Related to unsafe action execution
- **LLM10: Unbounded Consumption** - Resource abuse by agents
