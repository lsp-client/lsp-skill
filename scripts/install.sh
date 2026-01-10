#!/bin/bash
set -e

REPO="lsp-client/lsp-skill"
SKILL_NAME="lsp-code-analysis"

# Cleanup function for temporary files
cleanup() {
    rm -f "$TMP_ZIP" 2>/dev/null || true
    rm -rf "$TMP_DIR" 2>/dev/null || true
}

# Set trap to ensure cleanup on exit, interrupt, or termination
trap cleanup EXIT INT TERM

# Show help
if [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]; then
    echo "LSP Skill Installer"
    echo ""
    echo "Usage: $0 <skill_directory>"
    echo ""
    echo "Arguments:"
    echo "  skill_directory  Path to the skill directory to update"
    echo "                   Must contain SKILL.md with name: lsp-code-analysis"
    echo ""
    echo "This script will:"
    echo "  1. Validate the skill directory"
    echo "  2. Check if the skill version is up to date"
    echo "  3. Download and install the latest version if needed"
    echo "  4. Detect, install, or upgrade lsp-cli"
    echo ""
    exit 0
fi

SKILL_DIR="$1"

# Validate skill directory exists
if [ ! -d "$SKILL_DIR" ]; then
    echo "Error: Directory '$SKILL_DIR' does not exist."
    exit 1
fi

# Validate SKILL.md exists
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "Error: SKILL.md not found in '$SKILL_DIR'."
    exit 1
fi

# Validate skill name is lsp-code-analysis
SKILL_NAME_FROM_FILE=$(grep "^name:" "$SKILL_DIR/SKILL.md" | sed 's/^name: *//' || true)
if [ "$SKILL_NAME_FROM_FILE" != "$SKILL_NAME" ]; then
    echo "Error: Skill name in SKILL.md is '$SKILL_NAME_FROM_FILE', expected '$SKILL_NAME'."
    exit 1
fi

# Get current version from SKILL.md
CURRENT_VERSION=$(grep "^version:" "$SKILL_DIR/SKILL.md" | sed 's/^version: *//' || echo "unknown")

echo "Checking for updates for $SKILL_NAME..."

# Fetch latest release info
RELEASE_DATA=$(curl -sSL "https://api.github.com/repos/$REPO/releases/latest" 2>/dev/null || echo "")
LATEST_VERSION=$(echo "$RELEASE_DATA" | grep '"tag_name":' | head -n 1 | sed -E 's/.*"tag_name": "([^"]+)".*/\1/' || echo "")

if [ -z "$LATEST_VERSION" ]; then
    echo "Warning: Could not determine latest version from GitHub."
    echo "Current version: $CURRENT_VERSION"
    echo "Skill is ready to use."
else
    echo "Current version: $CURRENT_VERSION"
    echo "Latest version: $LATEST_VERSION"
    
    # Strip leading 'v' from versions for comparison
    if [ "${LATEST_VERSION#v}" = "${CURRENT_VERSION#v}" ]; then
        echo "✓ $SKILL_NAME is already at the latest version."
    else
        echo "Updating $SKILL_NAME to $LATEST_VERSION..."
        
        # Download and extract
        DOWNLOAD_URL="https://github.com/$REPO/releases/latest/download/lsp-code-analysis.zip"
        
        TMP_ZIP=$(mktemp)
        echo "Downloading from GitHub releases..."
        
        if ! curl -sSL -f -o "$TMP_ZIP" "$DOWNLOAD_URL" 2>/dev/null; then
            echo "Warning: Failed to download from $DOWNLOAD_URL."
            echo "Trying alternative download URL..."
            DOWNLOAD_URL=$(echo "$RELEASE_DATA" | grep "browser_download_url" | grep ".zip" | head -n 1 | cut -d '"' -f 4)
            
            if [ -z "$DOWNLOAD_URL" ]; then
                DOWNLOAD_URL=$(echo "$RELEASE_DATA" | grep "zipball_url" | head -n 1 | cut -d '"' -f 4)
            fi
            
            if [ -z "$DOWNLOAD_URL" ]; then
                echo "Error: Could not find download URL for latest release."
                rm -f "$TMP_ZIP"
                exit 1
            fi
            
            curl -sSL -o "$TMP_ZIP" "$DOWNLOAD_URL"
        fi
        
        # Optional checksum verification for security-conscious users.
        # If LSP_SKILL_ZIP_SHA256 is set, verify the downloaded archive.
        if [ -n "$LSP_SKILL_ZIP_SHA256" ]; then
            if command -v sha256sum >/dev/null 2>&1; then
                echo "Verifying checksum for downloaded archive..."
                ACTUAL_SHA256=$(sha256sum "$TMP_ZIP" | awk '{print $1}')
                if [ "$ACTUAL_SHA256" != "$LSP_SKILL_ZIP_SHA256" ]; then
                    echo "Error: Checksum verification failed for downloaded archive."
                    echo "Expected: $LSP_SKILL_ZIP_SHA256"
                    echo "Actual:   $ACTUAL_SHA256"
                    exit 1
                fi
                echo "✓ Checksum verified successfully."
            else
                echo "Warning: sha256sum not found; skipping checksum verification."
            fi
        fi
        
        echo "Extracting to $SKILL_DIR..."
        
        # Create temporary extraction directory
        TMP_DIR=$(mktemp -d)
        unzip -q "$TMP_ZIP" -d "$TMP_DIR"
        
        # Find where SKILL.md is and copy that directory's content
        SKILL_PATH=$(find "$TMP_DIR" -name "SKILL.md" -path "*/lsp-code-analysis/SKILL.md" | head -n 1)
        
        if [ -n "$SKILL_PATH" ]; then
            EXTRACTED_SKILL_DIR=$(dirname "$SKILL_PATH")
            # Remove old content (except hidden files like .version)
            if ! find "$SKILL_DIR" -mindepth 1 -not -name '.*' -exec rm -rf {} + 2>/dev/null; then
                echo "Error: Failed to clean existing skill directory '$SKILL_DIR'."
                exit 1
            fi
            # Copy new content (including hidden files)
            cp -r "$EXTRACTED_SKILL_DIR"/. "$SKILL_DIR/"
            echo "✓ Successfully updated $SKILL_NAME to $LATEST_VERSION."
        else
            echo "Error: Could not find SKILL.md in the downloaded archive."
            exit 1
        fi
        
        rm -rf "$TMP_DIR"
        rm -f "$TMP_ZIP"
    fi
fi

# Check for lsp-cli and install/upgrade
echo ""
echo "Checking lsp-cli installation..."

if command -v lsp >/dev/null 2>&1; then
    echo "✓ lsp-cli is installed."
    
    # Try to upgrade using uv tool
    if command -v uv >/dev/null 2>&1; then
        echo "Upgrading lsp-cli..."
        if uv tool upgrade lsp-cli 2>/dev/null; then
            echo "✓ lsp-cli upgraded successfully."
        else
            echo "Note: lsp-cli is already at the latest version or upgrade failed."
        fi
    else
        echo "Note: uv not found. To upgrade lsp-cli manually, run: uv tool upgrade lsp-cli"
    fi
else
    echo "⚠ lsp-cli is not installed."
    if command -v uv >/dev/null 2>&1; then
        echo "Installing lsp-cli..."
        if uv tool install --python 3.13 lsp-cli; then
            echo "✓ lsp-cli installed successfully."
        else
            echo "Error: Failed to install lsp-cli."
            exit 1
        fi
    else
        echo "Error: uv not found. Cannot install lsp-cli automatically."
        echo "Please install uv (https://astral.sh/uv) and then run:"
        echo "  uv tool install --python 3.13 lsp-cli"
        exit 1
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Setup complete! The lsp-code-analysis skill is ready."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
