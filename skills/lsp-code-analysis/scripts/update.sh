#!/bin/bash
set -e

REPO="lsp-client/lsp-skill"
SKILL_NAME="lsp-code-analysis"

# Cleanup function for temporary files
cleanup() {
    rm -f "$TMP_ZIP" 2>/dev/null || true
    rm -rf "$TMP_DIR" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

# Automatically detect skill directory (parent of scripts/)
SKILL_DIR=$(cd "$(dirname "$0")/.." && pwd)
VERSION_FILE="$SKILL_DIR/.version"

# Validate SKILL.md exists
[ -f "$SKILL_DIR/SKILL.md" ] || { echo "Error: SKILL.md not found in '$SKILL_DIR'."; exit 1; }

echo "Checking lsp-cli installation..."
uv tool install --python 3.13 lsp-cli@latest
LATEST_CLI_VERSION=$(uv tool list | grep "^lsp-cli " | awk '{print $2}' | sed 's/^v//')
CURRENT_CLI_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "unknown")

if [ "$LATEST_CLI_VERSION" = "$CURRENT_CLI_VERSION" ]; then
    echo "✓ $SKILL_NAME is already up to date (lsp-cli version $LATEST_CLI_VERSION)."
    exit 0
fi

echo "lsp-cli version mismatch ($CURRENT_CLI_VERSION -> $LATEST_CLI_VERSION). Proceeding with update..."

# Get current version from SKILL.md
CURRENT_VERSION=$(grep "^version:" "$SKILL_DIR/SKILL.md" | sed 's/^version: *//' || echo "unknown")

echo "Checking for updates for $SKILL_NAME..."

# Fetch latest release info
RELEASE_DATA=$(curl -sSL "https://api.github.com/repos/$REPO/releases/latest" 2>/dev/null || echo "")
LATEST_VERSION=$(echo "$RELEASE_DATA" | grep '"tag_name":' | head -n 1 | sed -E 's/.*"tag_name": "([^"]+)".*/\1/' || echo "")

if [ -z "$LATEST_VERSION" ]; then
    echo "Warning: Could not determine latest version from GitHub."
    echo "Current version: $CURRENT_VERSION"
else
    echo "Current version: $CURRENT_VERSION"
    echo "Latest version: $LATEST_VERSION"

    # Strip leading 'v' from versions for comparison
    if [ "${LATEST_VERSION#v}" = "${CURRENT_VERSION#v}" ]; then
        echo "✓ $SKILL_NAME files are already at the latest version."
    else
        echo "Updating $SKILL_NAME to $LATEST_VERSION..."

        # Download archive
        DOWNLOAD_URL="https://github.com/$REPO/releases/latest/download/lsp-code-analysis.zip"
        TMP_ZIP=$(mktemp)
        echo "Downloading from GitHub releases..."
        curl -sSL -f -o "$TMP_ZIP" "$DOWNLOAD_URL" || { echo "Error: Failed to download update."; exit 1; }

        echo "Extracting to $SKILL_DIR..."

        # Create temporary extraction directory
        TMP_DIR=$(mktemp -d)
        unzip -q "$TMP_ZIP" -d "$TMP_DIR"

        # Find where SKILL.md is and copy that directory's content
        SKILL_PATH=$(find "$TMP_DIR" -name "SKILL.md" -path "*/lsp-code-analysis/SKILL.md" | head -n 1)

        if [ -n "$SKILL_PATH" ]; then
            EXTRACTED_SKILL_DIR=$(dirname "$SKILL_PATH")
            # Remove old content (except hidden files and scripts directory)
            find "$SKILL_DIR" -mindepth 1 -not -name '.*' -not -name 'scripts' -exec rm -rf {} + 2>/dev/null || true
            # Copy new content (including hidden files)
            cp -r "$EXTRACTED_SKILL_DIR"/. "$SKILL_DIR/"
            echo "✓ Successfully updated $SKILL_NAME to $LATEST_VERSION."
        else
            echo "Error: Could not find SKILL.md in the downloaded archive."
            exit 1
        fi
    fi
fi

# Update .version file to match lsp-cli version
echo "$LATEST_CLI_VERSION" > "$VERSION_FILE"

echo "Setup complete! The lsp-code-analysis skill is ready."
