# Manual Push Instructions for AIGuardAPIDemo

## Current Status
✅ Code is fully committed and ready
✅ Branch: claude/trend-vision-ai-integrations-01VVfQWNxVBTB3SohJzpRKkC
✅ 25 files with 3,828+ lines of code
❌ Unable to push via proxy (authorization error)

## Option 1: Push from this directory

If you have direct GitHub access from your machine:

```bash
cd /home/user/IndirectPromptTester/AIGuardAPIDemo

# Ensure repository exists on GitHub first:
# https://github.com/girdav01/AIGuardAPIDemo

# Then push:
git remote set-url origin https://github.com/girdav01/AIGuardAPIDemo.git
git push -u origin claude/trend-vision-ai-integrations-01VVfQWNxVBTB3SohJzpRKkC
```

## Option 2: Clone and Push Fresh

```bash
# Create the repository on GitHub first:
# https://github.com/new
# Name: AIGuardAPIDemo
# Don't initialize with README

# Then:
cd /home/user/IndirectPromptTester/AIGuardAPIDemo
git push https://YOUR_TOKEN@github.com/girdav01/AIGuardAPIDemo.git claude/trend-vision-ai-integrations-01VVfQWNxVBTB3SohJzpRKkC
```

## Option 3: Use GitHub CLI

```bash
# If gh CLI is available:
gh repo create girdav01/AIGuardAPIDemo --public --source=. --remote=origin --push
```

## What's Included

### Core Components:
- ai_guard_client/ - Full-featured Python client
- integrations/langchain/ - LangChain integration (5 files)
- integrations/litellm/ - LiteLLM integration (5 files)

### Demos:
- demos/llm01_prompt_injection/ - Prompt injection demo
- demos/llm02_sensitive_info/ - Sensitive data disclosure demo
- demos/llm06_excessive_agency/ - Excessive agency demo

### Infrastructure:
- README.md - Comprehensive documentation
- Dockerfile - Container setup
- docker-compose.yml - Multi-service orchestration
- requirements.txt - Python dependencies
- .env.example - Configuration template
- .gitignore - Git ignore rules

## Verify Before Push

```bash
git log --oneline  # Should show the commit
git branch         # Should show the claude/* branch
git remote -v      # Should show origin pointing to AIGuardAPIDemo
```
