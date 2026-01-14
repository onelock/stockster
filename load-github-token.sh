#!/bin/bash
# Load GitHub token from encrypted file or environment

TOKEN_FILE="$HOME/.config/github_token"

# Try to load from file
if [ -f "$TOKEN_FILE" ]; then
    export GITHUB_TOKEN=$(cat "$TOKEN_FILE")
    echo "✓ GitHub token loaded from $TOKEN_FILE"
elif [ -n "$GITHUB_TOKEN" ]; then
    echo "✓ GitHub token already set in environment"
else
    echo "Error: GitHub token not found"
    echo ""
    echo "To set up:"
    echo "  mkdir -p ~/.config"
    echo "  echo 'ghp_your_token_here' > ~/.config/github_token"
    echo "  chmod 600 ~/.config/github_token"
    exit 1
fi
