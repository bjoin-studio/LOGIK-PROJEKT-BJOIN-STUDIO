#!/bin/bash
# =============================================================================
# BJoin Studio Environment Setup Script
# =============================================================================
# This script sets up the BJoin Studio OCIO configuration and environment
# variables for use with Flame, Nuke, Resolve, Blender, and other DCC apps.
#
# Supports: macOS, Rocky Linux 9.x, CentOS, RHEL, Ubuntu
#
# Usage:
#   ./install/setup-bjoin-studio.sh [options]
#
# Options:
#   --user-only     Install to user directory only (no sudo required)
#   --system        Install to system directory (requires sudo)
#   --check         Check current installation status
#   --uninstall     Remove BJoin Studio OCIO setup
#   --help          Show this help message
#
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OCIO_SOURCE="$REPO_ROOT/resources/ocio/bjoin-studio-config.ocio"
ACES_SOURCE_DIR="$REPO_ROOT/resources/ocio/aces-1.3"

# System-wide install location
SYSTEM_OCIO_DIR="/opt/bjoin-studio/ocio"
SYSTEM_OCIO_CONFIG="$SYSTEM_OCIO_DIR/config.ocio"

# User install location
USER_OCIO_DIR="$HOME/.config/bjoin-studio/ocio"
USER_OCIO_CONFIG="$USER_OCIO_DIR/config.ocio"

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        SHELL_RC="$HOME/.zshrc"
        # Check if using bash instead
        if [[ "$SHELL" == *"bash"* ]]; then
            SHELL_RC="$HOME/.bash_profile"
        fi
    elif [[ -f /etc/rocky-release ]]; then
        OS="rocky"
        SHELL_RC="$HOME/.bashrc"
    elif [[ -f /etc/redhat-release ]]; then
        OS="rhel"
        SHELL_RC="$HOME/.bashrc"
    elif [[ -f /etc/debian_version ]]; then
        OS="debian"
        SHELL_RC="$HOME/.bashrc"
    else
        OS="linux"
        SHELL_RC="$HOME/.bashrc"
    fi
    
    # Override if zsh is detected
    if [[ "$SHELL" == *"zsh"* ]] && [[ "$OS" != "macos" ]]; then
        SHELL_RC="$HOME/.zshrc"
    fi
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  BJoin Studio Environment Setup${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}→${NC} $1"
}

# -----------------------------------------------------------------------------
# Installation Functions
# -----------------------------------------------------------------------------

check_prerequisites() {
    print_info "Checking prerequisites..."
    
    if [[ ! -f "$OCIO_SOURCE" ]]; then
        print_error "OCIO config not found at: $OCIO_SOURCE"
        print_error "Make sure you're running this from the LOGIK-PROJEKT repository"
        exit 1
    fi
    
    print_success "OCIO source config found"
    
    # Check for ACES 1.3 configs
    if [[ -d "$ACES_SOURCE_DIR" ]]; then
        print_success "ACES 1.3 reference configs found"
    else
        print_warning "ACES 1.3 reference configs not found (optional)"
    fi
}

install_system() {
    print_info "Installing OCIO config to system location..."
    print_info "Location: $SYSTEM_OCIO_DIR"
    
    # Create directory
    if ! sudo mkdir -p "$SYSTEM_OCIO_DIR" 2>/dev/null; then
        print_error "Failed to create directory. Do you have sudo access?"
        return 1
    fi
    
    # Copy main config
    sudo cp "$OCIO_SOURCE" "$SYSTEM_OCIO_CONFIG"
    sudo chmod 644 "$SYSTEM_OCIO_CONFIG"
    print_success "Installed config.ocio"
    
    # Copy ACES 1.3 reference configs if available
    if [[ -d "$ACES_SOURCE_DIR" ]]; then
        sudo mkdir -p "$SYSTEM_OCIO_DIR/aces-1.3"
        sudo cp "$ACES_SOURCE_DIR"/*.ocio "$SYSTEM_OCIO_DIR/aces-1.3/" 2>/dev/null || true
        sudo chmod 644 "$SYSTEM_OCIO_DIR/aces-1.3"/*.ocio 2>/dev/null || true
        print_success "Installed ACES 1.3 reference configs"
    fi
    
    # Set ownership
    sudo chown -R root:$(id -gn) "$SYSTEM_OCIO_DIR" 2>/dev/null || \
    sudo chown -R root:wheel "$SYSTEM_OCIO_DIR" 2>/dev/null || \
    sudo chown -R root:root "$SYSTEM_OCIO_DIR" 2>/dev/null || true
    
    INSTALLED_CONFIG="$SYSTEM_OCIO_CONFIG"
    print_success "System installation complete"
}

install_user() {
    print_info "Installing OCIO config to user location..."
    print_info "Location: $USER_OCIO_DIR"
    
    # Create directory
    mkdir -p "$USER_OCIO_DIR"
    
    # Copy main config
    cp "$OCIO_SOURCE" "$USER_OCIO_CONFIG"
    chmod 644 "$USER_OCIO_CONFIG"
    print_success "Installed config.ocio"
    
    # Copy ACES 1.3 reference configs if available
    if [[ -d "$ACES_SOURCE_DIR" ]]; then
        mkdir -p "$USER_OCIO_DIR/aces-1.3"
        cp "$ACES_SOURCE_DIR"/*.ocio "$USER_OCIO_DIR/aces-1.3/" 2>/dev/null || true
        print_success "Installed ACES 1.3 reference configs"
    fi
    
    INSTALLED_CONFIG="$USER_OCIO_CONFIG"
    print_success "User installation complete"
}

setup_environment() {
    local config_path="$1"
    
    print_info "Setting up environment variable..."
    print_info "Shell config: $SHELL_RC"
    
    # Create shell rc if it doesn't exist
    touch "$SHELL_RC"
    
    # Check if OCIO is already set
    if grep -q "^export OCIO=" "$SHELL_RC" 2>/dev/null; then
        # Update existing OCIO line
        if [[ "$OS" == "macos" ]]; then
            sed -i '' "s|^export OCIO=.*|export OCIO=\"$config_path\"|" "$SHELL_RC"
        else
            sed -i "s|^export OCIO=.*|export OCIO=\"$config_path\"|" "$SHELL_RC"
        fi
        print_success "Updated existing OCIO environment variable"
    else
        # Add new OCIO export
        echo "" >> "$SHELL_RC"
        echo "# BJoin Studio OCIO Configuration" >> "$SHELL_RC"
        echo "# Installed by setup-bjoin-studio.sh on $(date '+%Y-%m-%d')" >> "$SHELL_RC"
        echo "export OCIO=\"$config_path\"" >> "$SHELL_RC"
        print_success "Added OCIO environment variable to $SHELL_RC"
    fi
    
    # Export for current session
    export OCIO="$config_path"
}

check_installation() {
    print_header
    print_info "Checking BJoin Studio installation status..."
    echo ""
    
    # Check system install
    if [[ -f "$SYSTEM_OCIO_CONFIG" ]]; then
        print_success "System OCIO config: $SYSTEM_OCIO_CONFIG"
    else
        print_warning "System OCIO config not found"
    fi
    
    # Check user install
    if [[ -f "$USER_OCIO_CONFIG" ]]; then
        print_success "User OCIO config: $USER_OCIO_CONFIG"
    else
        print_warning "User OCIO config not found"
    fi
    
    # Check environment variable
    echo ""
    if [[ -n "$OCIO" ]]; then
        print_success "OCIO environment variable: $OCIO"
        if [[ -f "$OCIO" ]]; then
            print_success "OCIO config file exists"
        else
            print_error "OCIO config file does not exist!"
        fi
    else
        print_warning "OCIO environment variable not set in current session"
    fi
    
    # Check shell config
    echo ""
    if grep -q "OCIO=" "$SHELL_RC" 2>/dev/null; then
        print_success "OCIO configured in $SHELL_RC"
        grep "OCIO=" "$SHELL_RC" | head -1
    else
        print_warning "OCIO not configured in $SHELL_RC"
    fi
    
    echo ""
}

uninstall() {
    print_header
    print_info "Uninstalling BJoin Studio OCIO setup..."
    echo ""
    
    # Remove system install
    if [[ -d "$SYSTEM_OCIO_DIR" ]]; then
        print_info "Removing system installation..."
        sudo rm -rf "$SYSTEM_OCIO_DIR"
        print_success "Removed $SYSTEM_OCIO_DIR"
    fi
    
    # Remove user install
    if [[ -d "$USER_OCIO_DIR" ]]; then
        print_info "Removing user installation..."
        rm -rf "$USER_OCIO_DIR"
        print_success "Removed $USER_OCIO_DIR"
    fi
    
    # Remove from shell config
    if grep -q "BJoin Studio OCIO" "$SHELL_RC" 2>/dev/null; then
        print_info "Cleaning shell config..."
        if [[ "$OS" == "macos" ]]; then
            sed -i '' '/BJoin Studio OCIO/d' "$SHELL_RC"
            sed -i '' '/setup-bjoin-studio.sh/d' "$SHELL_RC"
            sed -i '' '/^export OCIO=.*bjoin-studio/d' "$SHELL_RC"
        else
            sed -i '/BJoin Studio OCIO/d' "$SHELL_RC"
            sed -i '/setup-bjoin-studio.sh/d' "$SHELL_RC"
            sed -i '/^export OCIO=.*bjoin-studio/d' "$SHELL_RC"
        fi
        print_success "Cleaned $SHELL_RC"
    fi
    
    echo ""
    print_success "Uninstallation complete"
    print_warning "Restart your terminal or run: unset OCIO"
}

show_help() {
    echo "BJoin Studio Environment Setup Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --user-only     Install to user directory only (no sudo required)"
    echo "  --system        Install to system directory (requires sudo)"
    echo "  --check         Check current installation status"
    echo "  --uninstall     Remove BJoin Studio OCIO setup"
    echo "  --help          Show this help message"
    echo ""
    echo "Default (no options): Interactive mode - prompts for install type"
    echo ""
    echo "Locations:"
    echo "  System:  $SYSTEM_OCIO_DIR"
    echo "  User:    $USER_OCIO_DIR"
    echo ""
    echo "Supported Applications:"
    echo "  - Autodesk Flame 2026+"
    echo "  - Foundry Nuke 15+/16+"
    echo "  - DaVinci Resolve"
    echo "  - Blender"
    echo "  - Any OCIO-compatible application"
}

show_post_install() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Installation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "OCIO Config: $INSTALLED_CONFIG"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    echo "1. Restart your terminal or run:"
    echo "   source $SHELL_RC"
    echo ""
    echo "2. Verify with:"
    echo "   echo \$OCIO"
    echo ""
    echo -e "${BLUE}Application Setup:${NC}"
    echo ""
    echo "• Flame: Should auto-detect. Or set in project settings."
    echo "• Nuke:  Auto-detects \$OCIO. Verify in Preferences > Color."
    echo "• Resolve: Preferences > Color > OCIO config path"
    echo "• Blender: Preferences > Rendering > OpenColorIO"
    echo ""
    echo -e "${BLUE}Color Pipeline:${NC}"
    echo "• Working Space: ACEScg"
    echo "• Grading Space: ACEScct"
    echo "• Output: ACES 1.0 SDR Video (Rec.709)"
    echo "• Cameras: RED, ARRI, Sony, Blackmagic supported"
    echo ""
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

main() {
    detect_os
    
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --check)
            check_installation
            exit 0
            ;;
        --uninstall)
            uninstall
            exit 0
            ;;
        --user-only)
            print_header
            check_prerequisites
            install_user
            setup_environment "$USER_OCIO_CONFIG"
            show_post_install
            ;;
        --system)
            print_header
            check_prerequisites
            install_system
            setup_environment "$SYSTEM_OCIO_CONFIG"
            show_post_install
            ;;
        "")
            # Interactive mode
            print_header
            detect_os
            echo "Detected OS: $OS"
            echo "Shell config: $SHELL_RC"
            echo ""
            echo "Installation Options:"
            echo "  1) System-wide (requires sudo) - Recommended"
            echo "     Location: $SYSTEM_OCIO_DIR"
            echo ""
            echo "  2) User only (no sudo required)"
            echo "     Location: $USER_OCIO_DIR"
            echo ""
            read -p "Choose installation type [1/2]: " choice
            
            check_prerequisites
            
            case "$choice" in
                1)
                    install_system
                    setup_environment "$SYSTEM_OCIO_CONFIG"
                    ;;
                2)
                    install_user
                    setup_environment "$USER_OCIO_CONFIG"
                    ;;
                *)
                    print_error "Invalid choice"
                    exit 1
                    ;;
            esac
            show_post_install
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
