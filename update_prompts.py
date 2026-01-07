#!/usr/bin/env python3
"""
Convenience wrapper for updating the prompt injection database.

This script can be run from the project root to initialize or update
the prompt injection database with the latest intelligence.

Usage:
    python update_prompts.py           # Update database
    python update_prompts.py --clear   # Clear and rebuild database
    python update_prompts.py --stats   # Show statistics after update
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    # Run the actual update script
    script_path = Path(__file__).parent / "scripts" / "update_prompt_database.py"

    # Forward all arguments
    args = [sys.executable, str(script_path)] + sys.argv[1:]

    result = subprocess.run(args)
    sys.exit(result.returncode)
