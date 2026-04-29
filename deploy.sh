#!/bin/bash
# Complete GitHub blog deployment
# Usage: ./deploy.sh <GITHUB_PAT>
#
# This script:
# 1. Creates the repo on GitHub
# 2. Pushes the blog
# 3. Enables GitHub Pages
#
# Prerequisites: Get a PAT from https://github.com/settings/tokens
# with 'repo' scope, then run this script.

set -e

PAT="${1:?Usage: $0 <GITHUB_PAT>}"
REPO="danmi-ai/danmi-ai.github.io"
PROXY="http://cmcproxy:WvUBhef4bQ@10.251.112.50:8128"
BLOG_DIR="/root/.openclaw/workspace/blog/danmi-ai.github.io"

echo "=== Step 1: Create repo ==="
STATUS=$(curl -s -o /tmp/gh_create.json -w '%{http_code}' \
    -x "$PROXY" \
    -H "Authorization: token $PAT" \
    -H "Accept: application/vnd.github+json" \
    -X POST https://api.github.com/user/repos \
    -d "{\"name\":\"danmi-ai.github.io\",\"description\":\"An AI assistant's perspective on LLM research, engineering, and the world.\",\"homepage\":\"https://danmi-ai.github.io\",\"public\":true,\"auto_init\":false}")

if [ "$STATUS" = "201" ]; then
    echo "  ✅ Repo created"
elif [ "$STATUS" = "422" ]; then
    echo "  ℹ️ Repo already exists"
else
    echo "  ❌ Failed (HTTP $STATUS):"
    cat /tmp/gh_create.json
    exit 1
fi

echo ""
echo "=== Step 2: Push blog ==="
cd "$BLOG_DIR"
git remote set-url origin "https://danmi-ai:${PAT}@github.com/${REPO}.git"
git config http.proxy "$PROXY"
git config https.proxy "$PROXY"
git push -u origin main
echo "  ✅ Pushed"

echo ""
echo "=== Step 3: Enable GitHub Pages ==="
# Enable Pages with GitHub Actions as source
curl -s -o /tmp/gh_pages.json -w '\n' \
    -x "$PROXY" \
    -H "Authorization: token $PAT" \
    -H "Accept: application/vnd.github+json" \
    -X POST "https://api.github.com/repos/${REPO}/pages" \
    -d '{"build_type":"workflow"}'
echo "  Pages configuration submitted"

echo ""
echo "=== Done! ==="
echo "Blog will be available at: https://danmi-ai.github.io"
echo "First deployment may take 1-2 minutes."
