#!/bin/bash

echo "============================================"
echo "Push AIGuardAPIDemo to GitHub"
echo "============================================"
echo ""

# Check if repository exists
echo "Step 1: Checking repository status..."
git status
echo ""

# Show what will be pushed
echo "Step 2: Commit history..."
git log --oneline -5
echo ""

# Try to push
echo "Step 3: Attempting to push to AIGuardAPIDemo..."
echo "Branch: claude/trend-vision-ai-integrations-01VVfQWNxVBTB3SohJzpRKkC"
echo ""

# Method 1: Try with proxy
echo "Attempt 1: Using local proxy..."
git remote set-url origin http://local_proxy@127.0.0.1:61022/git/girdav01/AIGuardAPIDemo
if git push -u origin claude/trend-vision-ai-integrations-01VVfQWNxVBTB3SohJzpRKkC 2>&1; then
    echo "✅ Successfully pushed to AIGuardAPIDemo!"
    exit 0
fi

echo "❌ Proxy push failed"
echo ""

# Method 2: Try with HTTPS (requires manual authentication)
echo "Attempt 2: Using HTTPS..."
echo "This requires GitHub credentials or personal access token"
git remote set-url origin https://github.com/girdav01/AIGuardAPIDemo.git
echo ""
echo "Run: git push -u origin claude/trend-vision-ai-integrations-01VVfQWNxVBTB3SohJzpRKkC"
echo ""
echo "Or with token:"
echo "git push https://YOUR_TOKEN@github.com/girdav01/AIGuardAPIDemo.git claude/trend-vision-ai-integrations-01VVfQWNxVBTB3SohJzpRKkC"
echo ""

# Show files that will be pushed
echo "============================================"
echo "Files to be pushed:"
echo "============================================"
git ls-files | head -25
echo ""
echo "Total: $(git ls-files | wc -l) files"
echo ""

echo "============================================"
echo "IMPORTANT: Repository must exist first!"
echo "============================================"
echo "1. Go to: https://github.com/new"
echo "2. Repository name: AIGuardAPIDemo"
echo "3. Make it Public"
echo "4. DO NOT initialize with README"
echo "5. Click 'Create repository'"
echo "6. Then run this script again or push manually"
echo ""
