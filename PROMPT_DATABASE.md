# Prompt Injection Database

The IndirectPromptTester framework now includes a comprehensive, curated database of prompt injection examples sourced from security research, OWASP guidelines, and real-world attacks.

## Overview

The prompt database contains **40+ categorized prompt injection examples** covering:
- Direct and Indirect injection attacks
- Multiple attack vectors (instruction override, code execution, RAG poisoning, etc.)
- Difficulty levels (beginner, intermediate, advanced)
- Metadata including sources, descriptions, and success rates

## Database Features

### Categories
- **direct_injection**: Direct prompt manipulation attempts
- **indirect_injection**: Attacks embedded in documents, emails, web pages, etc.

### Attack Vectors
- `instruction_override`: Override system instructions
- `code_execution`: Attempt to execute malicious code
- `information_disclosure`: Extract sensitive information
- `safety_bypass`: Circumvent safety guidelines
- `document_injection`: Hidden instructions in documents
- `web_injection`: Attacks via web content (HTML, metadata)
- `email_injection`: Malicious instructions in emails
- `rag_injection`: Poisoning RAG/knowledge base context
- `image_injection`: Text-in-image attacks for vision models
- `agent_manipulation`: Tool/agent behavior manipulation
- `obfuscation`: Unicode and encoding-based attacks

### Difficulty Levels
- **beginner**: Simple, straightforward attacks
- **intermediate**: More sophisticated techniques
- **advanced**: Complex, multi-stage attacks

## Using the Database

### 1. Initialize/Update the Database

First-time setup or to get the latest prompt intelligence:

```bash
python update_prompts.py --clear --stats
```

Update without clearing existing data:

```bash
python update_prompts.py --stats
```

### 2. CLI Usage

#### List All Prompts
```bash
ipt list-prompts
```

#### List with Filters
```bash
# Filter by category
ipt list-prompts --category direct_injection

# Filter by attack vector
ipt list-prompts --attack-vector instruction_override

# Filter by difficulty
ipt list-prompts --difficulty beginner

# Combine filters
ipt list-prompts --category indirect_injection --difficulty advanced

# Show detailed information
ipt list-prompts --detailed --limit 5
```

#### Database Statistics
```bash
ipt db-stats
```

#### View Available Filters
```bash
ipt db-info
```

#### Generate Files with Random Prompts
```bash
# Completely random prompt
ipt generate -t image -o test.png

# Random prompt with filters
ipt generate -t image -o test.png \
  --category direct_injection \
  --difficulty beginner

# Random RAG injection attack
ipt generate -t document -o malicious.docx \
  --attack-vector rag_injection \
  --difficulty advanced
```

### 3. UI Usage

The Streamlit UI includes a new **"Prompt Database"** page:

1. **Browse & Search**
   - Filter by category, attack vector, and difficulty
   - View detailed information for each prompt
   - See sources and descriptions
   - Export to CSV

2. **File Generator** (Enhanced)
   - **Random** option now includes filters:
     - Category (direct/indirect injection)
     - Attack vector (specific technique)
     - Difficulty level
   - **Select from Examples** also includes filters
   - Generate truly random attacks or target specific vectors

Launch the UI:
```bash
streamlit run indirect_prompt_tester/ui/app.py
```

### 4. Python API

```python
from indirect_prompt_tester.utils.prompts import (
    get_random_prompt,
    get_all_prompts,
    get_all_prompts_detailed,
    get_database_stats
)

# Get random prompt
prompt = get_random_prompt()

# Get random prompt with filters
prompt = get_random_prompt(
    category='indirect_injection',
    attack_vector='document_injection',
    difficulty='advanced'
)

# Get all prompts (text only)
prompts = get_all_prompts(category='direct_injection')

# Get all prompts with metadata
prompts_detailed = get_all_prompts_detailed(
    attack_vector='code_execution'
)

for p in prompts_detailed:
    print(f"[{p['difficulty']}] {p['prompt']}")
    print(f"Source: {p['source']}")
    print()

# Get statistics
stats = get_database_stats()
print(f"Total prompts: {stats['total_prompts']}")
```

## Data Sources

The database is populated from authoritative security research:

### Primary Sources
- **OWASP LLM01:2025** - Prompt Injection guidelines and examples
  - https://genai.owasp.org/llmrisk/llm01-prompt-injection/

- **Lakera AI Research** - Indirect prompt injection analysis
  - https://www.lakera.ai/blog/indirect-prompt-injection
  - https://www.lakera.ai/blog/guide-to-prompt-injection

- **Prompt.security** - Injection attack patterns
  - https://prompt.security/blog/prompt-injection-101

- **Microsoft Security Research** - Defense strategies (2025)
  - https://www.microsoft.com/en-us/msrc/blog/2025/07/how-microsoft-defends-against-indirect-prompt-injection-attacks

### Academic Research
- Cornell University: "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications"
- "Inject My PDF: Prompt Injection for your Resume" (Kai Greshake)

### Real-World Examples
- Car dealership chatbot manipulation (2023)
- Auto-GPT remote code execution (2023)
- HackAPrompt competition submissions

## Extending the Database

### Manual Additions

Edit `/home/user/IndirectPromptTester/scripts/update_prompt_database.py` and add to the appropriate section:

```python
new_prompts = [
    {
        "prompt": "Your injection text here",
        "difficulty": "intermediate",
        "description": "What this attack does",
        "source": "Source name",
        "source_url": "https://...",
        "tags": ["tag1", "tag2"]
    }
]

for item in new_prompts:
    db.add_prompt(
        prompt=item["prompt"],
        category="direct_injection",  # or indirect_injection
        attack_vector="instruction_override",  # see list above
        difficulty=item["difficulty"],
        description=item["description"],
        source=item["source"],
        source_url=item["source_url"],
        tags=item.get("tags", [])
    )
```

Then run:
```bash
python update_prompts.py --stats
```

### Programmatic Additions

```python
from indirect_prompt_tester.utils.prompt_database import PromptDatabase

db = PromptDatabase()

db.add_prompt(
    prompt="Your new prompt injection",
    category="direct_injection",
    attack_vector="safety_bypass",
    difficulty="beginner",
    description="Attempts to bypass safety filters",
    source="Custom Research",
    source_url="https://example.com",
    tags=["custom", "experimental"]
)

db.close()
```

## Database Schema

### Main Table: `prompt_injections`
- `id` - Unique identifier
- `prompt` - The actual injection text
- `category` - direct_injection or indirect_injection
- `attack_vector` - Technique used (instruction_override, code_execution, etc.)
- `difficulty` - beginner, intermediate, or advanced
- `description` - What the attack attempts to do
- `source` - Where the example came from
- `source_url` - Reference URL
- `success_rate` - Observed success rate (0.0 - 1.0)
- `created_at` - Timestamp
- `updated_at` - Last modified
- `enabled` - Active/inactive flag

### Tags Table: `prompt_tags`
- Flexible tagging system for additional categorization
- Many-to-many relationship with prompts

## Database Location

Default: `/home/user/IndirectPromptTester/prompt_injections.db`

SQLite database file - portable and requires no external dependencies.

## Best Practices

1. **Regular Updates**: Run the update script periodically to refresh intelligence
2. **Filter Testing**: Start with beginner prompts and progress to advanced
3. **Vector Targeting**: Test specific attack vectors relevant to your use case
4. **Track Success Rates**: Update success_rate field based on your testing results
5. **Document Findings**: Use the sandbox feature to record which prompts succeeded

## Statistics Example

After initialization, you should see:
```
Total Prompts: 40

By Category:
  direct_injection: 24
  indirect_injection: 16

By Attack Vector:
  instruction_override: 12
  code_execution: 4
  safety_bypass: 4
  information_disclosure: 3
  document_injection: 3
  email_injection: 3
  web_injection: 3
  rag_injection: 2
  agent_manipulation: 2
  image_injection: 2
  obfuscation: 2

By Difficulty:
  advanced: 15
  intermediate: 15
  beginner: 10
```

## Security Note

This database is for **authorized security testing only**:
- Penetration testing engagements
- CTF competitions
- Security research
- Defensive AI safety evaluation
- Educational purposes

Do **NOT** use for:
- Attacking production systems without authorization
- Malicious purposes
- Bypassing legitimate safety measures
- Harassment or abuse

## Troubleshooting

### Database Not Found
```bash
# Reinitialize the database
python update_prompts.py --clear --stats
```

### Empty Results
- Check your filters - they may be too restrictive
- Ensure database has been initialized
- Try querying without filters first

### Import Errors
Ensure you're running from the project root:
```bash
cd /home/user/IndirectPromptTester
python update_prompts.py --stats
```

## Future Enhancements

Planned features:
- Web scraper for automated updates from security advisories
- Success rate tracking based on sandbox results
- Collaborative database with community contributions
- Integration with CVE databases for real-world exploits
- LLM-based prompt mutation engine for variations
