#!/bin/bash

# OBPI Installation Script v0.7
# Advanced System Installation and Configuration Script
# Version: 0.7.0
# Last Updated: 2025-05-22 03:29:34
# Author: GI-Company

# Set strict error handling
set -euo pipefail
IFS=$'\n\t'

# Script Variables
TIMESTAMP="2025-05-22 03:29:34"
INSTALLER_VERSION="0.7.0"
CURRENT_USER="GI-Company"
LOG_FILE="/var/log/obpi-install.log"
TEMP_DIR="/tmp/obpi-install"
INSTALL_CONFIG="/etc/obpi/install.conf"

# Installation paths
BAREMETAL_PATH="/opt/obpi"
EXTERNAL_PATH=""
LIVE_PATH="/run/obpi"

# Required space (in GB)
MIN_SPACE=50
MIN_RAM=8

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logger function
log() {
    local level=$1
    local message=$2
    local timestamp=$(date -u +"%Y-%m-%d %H:%M:%S")
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

# System check function
check_system() {
    log "INFO" "Performing system checks..."
    
    # Check CPU
    local cpu_cores=$(nproc)
    if [ "$cpu_cores" -lt 4 ]; then
        log "WARNING" "System has less than 4 CPU cores (found: $cpu_cores)"
    fi

    # Check RAM
    local total_ram=$(awk '/MemTotal/ {print $2/1024/1024}' /proc/meminfo)
    if [ "${total_ram%.*}" -lt "$MIN_RAM" ]; then
        log "ERROR" "Insufficient RAM. Required: ${MIN_RAM}GB, Found: ${total_ram%.*}GB"
        exit 1
    fi

    # Check storage space
    local available_space=$(df -BG "$1" | awk 'NR==2 {print $4}' | tr -d 'G')
    if [ "${available_space%.*}" -lt "$MIN_SPACE" ]; then
        log "ERROR" "Insufficient space. Required: ${MIN_SPACE}GB, Found: ${available_space%.*}GB"
        exit 1
    fi
}

# Dependency check function
check_dependencies() {
    log "INFO" "Checking dependencies..."
    local deps=(
        "curl"
        "git"
        "parted"
        "rsync"
        "systemd"
        "cryptsetup"
    )

    for dep in "${deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            log "ERROR" "Missing dependency: $dep"
            exit 1
        fi
    }
}

# Partition setup function
setup_partitions() {
    local device=$1
    local type=$2

    log "INFO" "Setting up partitions on $device for $type installation"

    case "$type" in
        "baremetal")
            parted -s "$device" mklabel gpt
            parted -s "$device" mkpart primary fat32 1MiB 512MiB
            parted -s "$device" mkpart primary ext4 512MiB 100%
            parted -s "$device" set 1 boot on
            ;;
        "external")
            parted -s "$device" mklabel gpt
            parted -s "$device" mkpart primary fat32 1MiB 512MiB
            parted -s "$device" mkpart primary ext4 512MiB 95%
            parted -s "$device" mkpart primary linux-swap 95% 100%
            ;;
        "live")
            parted -s "$device" mklabel gpt
            parted -s "$device" mkpart primary fat32 1MiB 2GiB
            parted -s "$device" mkpart primary ext4 2GiB 100%
            ;;
    esac
}

# Filesystem setup function
setup_filesystems() {
    local device=$1
    local type=$2

    log "INFO" "Creating filesystems for $type installation"

    case "$type" in
        "baremetal"|"external")
            mkfs.fat -F32 "${device}1"
            mkfs.ext4 "${device}2"
            [ "$type" = "external" ] && mkswap "${device}3"
            ;;
        "live")
            mkfs.fat -F32 "${device}1"
            mkfs.ext4 "${device}2"
            ;;
    esac
}

# Core installation function
install_core() {
    local target=$1
    local type=$2

    log "INFO" "Installing OBPI core to $target"

    # Create directory structure
    mkdir -p "$target"/{bin,etc,lib,var,opt,usr}

    # Clone OBPI repository
    git clone https://github.com/gi-company/obpi.git "$TEMP_DIR/obpi"

    # Install core components
    rsync -av "$TEMP_DIR/obpi/core/" "$target/usr/lib/obpi/"
    
    # Configure system
    cat > "$target/etc/obpi/system.conf" <<EOF
OBPI_VERSION="$INSTALLER_VERSION"
INSTALL_TYPE="$type"
INSTALL_DATE="$TIMESTAMP"
INSTALL_USER="$CURRENT_USER"
EOF

    # Set up bootloader if needed
    if [ "$type" != "live" ]; then
        setup_bootloader "$target" "$type"
    fi
}

# Bootloader setup function
setup_bootloader() {
    local target=$1
    local type=$2

    log "INFO" "Setting up bootloader for $type installation"

    # Install GRUB
    if [ "$type" = "baremetal" ]; then
        grub-install --target=x86_64-efi --efi-directory="$target/boot/efi" --bootloader-id=OBPI
    elif [ "$type" = "external" ]; then
        grub-install --target=x86_64-efi --efi-directory="$target/boot/efi" --bootloader-id=OBPI --removable
    fi

    # Generate GRUB configuration
    grub-mkconfig -o "$target/boot/grub/grub.cfg"
}

# Main installation function
main() {
    echo -e "${BLUE}OBPI Installation Script v$INSTALLER_VERSION${NC}"
    echo -e "${BLUE}Current Time: $TIMESTAMP${NC}"
    echo -e "${BLUE}Current User: $CURRENT_USER${NC}\n"

    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"

    # Initialize log
    log "INFO" "Starting OBPI installation v$INSTALLER_VERSION"

    # Display installation options
    echo -e "${GREEN}Select installation type:${NC}"
    echo "1) Baremetal Installation"
    echo "2) External Drive Installation"
    echo "3) Live Boot Creation"
    read -p "Enter choice (1-3): " choice

    # Get target device
    read -p "Enter target device (e.g., /dev/sda): " target_device

    case "$choice" in
        1)
            check_system "$BAREMETAL_PATH"
            check_dependencies
            setup_partitions "$target_device" "baremetal"
            setup_filesystems "$target_device" "baremetal"
            install_core "$BAREMETAL_PATH" "baremetal"
            ;;
        2)
            check_system "$target_device"
            check_dependencies
            setup_partitions "$target_device" "external"
            setup_filesystems "$target_device" "external"
            EXTERNAL_PATH="/mnt/obpi-external"
            mkdir -p "$EXTERNAL_PATH"
            mount "${target_device}2" "$EXTERNAL_PATH"
            install_core "$EXTERNAL_PATH" "external"
            umount "$EXTERNAL_PATH"
            ;;
        3)
            check_system "$LIVE_PATH"
            check_dependencies
            setup_partitions "$target_device" "live"
            setup_filesystems "$target_device" "live"
            install_core "$LIVE_PATH" "live"
            ;;
        *)
            log "ERROR" "Invalid choice"
            exit 1
            ;;
    esac

    log "INFO" "Installation completed successfully"
    echo -e "${GREEN}OBPI installation completed successfully!${NC}"
}

# Run main function
main "$@"