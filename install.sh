#!/bin/bash
set -e

REPO="lsp-client/lsp-skill"
TOOL=${1:-claude}
DEST_BASE=$2

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "LSP Skill Installer"
    echo ""
    echo "Usage: $0 [tool_name] [install_path]"
    echo ""
    echo "Arguments:"
    echo "  tool_name     The AI tool to install for (default: claude)"
    echo "                Supported: claude, gemini, codex, opencode"
    echo "  install_path  Custom path to install skills (default: ~/.[tool_name]/skills)"
    echo ""
    exit 0
fi

# Determine installation path
if [ -z "$DEST_BASE" ]; then
    DEST_BASE="$HOME/.$TOOL/skills"
fi

SKILL_NAME="lsp-code-analysis"
TARGET_DIR="$DEST_BASE/$SKILL_NAME"

echo "Installing $SKILL_NAME for $TOOL into $TARGET_DIR..."

# Create target directory if it doesn't exist
mkdir -p "$DEST_BASE"

# Fetch latest release info from GitHub API
echo "Fetching latest release from $REPO..."
RELEASE_DATA=$(curl -s "https://api.github.com/repos/$REPO/releases/latest")
DOWNLOAD_URL=$(echo "$RELEASE_DATA" | grep "browser_download_url" | grep ".zip" | head -n 1 | cut -d '"' -f 4)

if [ -z "$DOWNLOAD_URL" ]; then
    # Fallback to source zip if no binary release is found
    DOWNLOAD_URL=$(echo "$RELEASE_DATA" | grep "zipball_url" | head -n 1 | cut -d '"' -f 4)
fi

if [ -z "$DOWNLOAD_URL" ]; then
    echo "Error: Could not find download URL for latest release."
    exit 1
fi

# Download and extract
TMP_ZIP=$(mktemp)
echo "Downloading $DOWNLOAD_URL..."
curl -L -o "$TMP_ZIP" "$DOWNLOAD_URL"

echo "Extracting to $TARGET_DIR..."
# Remove old version if it exists
rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"

# Extracting. If it's a source zipball, it might have a nested directory.
unzip -q "$TMP_ZIP" -d "$TARGET_DIR.tmp"
# Move content up if it's nested (GitHub zipball behavior)
INNER_DIR=$(ls -d "$TARGET_DIR.tmp"/*/)
if [ -n "$INNER_DIR" ]; then
    mv "$INNER_DIR"* "$TARGET_DIR/"
    rm -rf "$TARGET_DIR.tmp"
else
    mv "$TARGET_DIR.tmp"/* "$TARGET_DIR/"
    rm -rf "$TARGET_DIR.tmp"
fi

rm "$TMP_ZIP"

echo "Successfully installed/updated $SKILL_NAME."
