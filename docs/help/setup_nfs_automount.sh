#!/bin/bash

# -------------------------------------------------------------------------- #
# Filename:     setup_nfs_automount.sh
# Purpose:      Configure NFS automounts on Rocky Linux 9.5
# Description:  Sets up autofs for ASUSSTOR and QNAP NAS mounts
# Usage:        sudo bash setup_nfs_automount.sh
# -------------------------------------------------------------------------- #

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${GREEN}=== NFS Automount Setup for Rocky Linux 9.5 ===${NC}\n"

# Step 1: Install required packages
echo -e "${YELLOW}Step 1: Installing autofs and nfs-utils...${NC}"
dnf install -y autofs nfs-utils
echo -e "${GREEN}✓ Packages installed${NC}\n"

# Step 2: Backup existing configurations
echo -e "${YELLOW}Step 2: Backing up existing configurations...${NC}"
if [ -f /etc/auto.master ]; then
    cp /etc/auto.master /etc/auto.master.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✓ Backed up /etc/auto.master${NC}"
fi

if [ -f /etc/auto.nfs ]; then
    cp /etc/auto.nfs /etc/auto.nfs.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✓ Backed up /etc/auto.nfs${NC}"
fi
echo ""

# Step 3: Configure /etc/auto.master
echo -e "${YELLOW}Step 3: Configuring /etc/auto.master...${NC}"
if ! grep -q "/mnt/nfs /etc/auto.nfs" /etc/auto.master; then
    echo "/mnt/nfs /etc/auto.nfs --timeout=600" >> /etc/auto.master
    echo -e "${GREEN}✓ Added NFS automount entry to /etc/auto.master${NC}"
else
    echo -e "${GREEN}✓ Entry already exists in /etc/auto.master${NC}"
fi
echo ""

# Step 4: Create /etc/auto.nfs
echo -e "${YELLOW}Step 4: Creating /etc/auto.nfs configuration...${NC}"
cat > /etc/auto.nfs << 'EOF'
# filename: /etc/auto.nfs
# modified: 2025-11-19
# Rocky Linux 9.5 NFS automount configuration

# ASUSSTOR 24 TB NAS on network 10.20.33.86
ASUSSTOR           -fstype=nfs,vers=4,rw,resvport      10.20.33.86:/volume1/BJOINFILMS_NAS

# QNAP on 100GbE network (10.10.10.11) - Optimized for high-speed
production-scratch -fstype=nfs,vers=4.1,rw,resvport,tcp,hard,intr,rsize=1048576,wsize=1048576,async,noatime,nodiratime,actimeo=120    10.10.10.11:/production-scratch
job-folder-archive -fstype=nfs,vers=4.1,rw,resvport,tcp,hard,intr,rsize=1048576,wsize=1048576,async,noatime,nodiratime,actimeo=120    10.10.10.11:/job-folder-archive
EOF

chmod 644 /etc/auto.nfs
echo -e "${GREEN}✓ Created /etc/auto.nfs${NC}\n"

# Step 5: Create mount point
echo -e "${YELLOW}Step 5: Creating mount point directory...${NC}"
mkdir -p /mnt/nfs
echo -e "${GREEN}✓ Created /mnt/nfs${NC}\n"

# Step 6: Enable and start autofs
echo -e "${YELLOW}Step 6: Enabling and starting autofs service...${NC}"
systemctl enable autofs
systemctl restart autofs
sleep 2
echo -e "${GREEN}✓ autofs service started${NC}\n"

# Step 7: Test connectivity
echo -e "${YELLOW}Step 7: Testing NFS connectivity...${NC}"
echo "Testing ASUSSTOR (10.20.33.86)..."
if timeout 5 showmount -e 10.20.33.86 &>/dev/null; then
    echo -e "${GREEN}✓ ASUSSTOR NFS server is reachable${NC}"
else
    echo -e "${YELLOW}⚠ ASUSSTOR NFS server not responding (may be offline or firewall issue)${NC}"
fi

echo "Testing QNAP (10.10.10.11)..."
if timeout 5 showmount -e 10.10.10.11 &>/dev/null; then
    echo -e "${GREEN}✓ QNAP NFS server is reachable${NC}"
else
    echo -e "${YELLOW}⚠ QNAP NFS server not responding (may be offline or firewall issue)${NC}"
fi
echo ""

# Step 8: Display status
echo -e "${YELLOW}Step 8: Checking autofs status...${NC}"
systemctl status autofs --no-pager | head -10
echo ""

# Final instructions
echo -e "${GREEN}=== Setup Complete! ===${NC}\n"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Test the mounts by accessing:"
echo "   ls /mnt/nfs/ASUSSTOR"
echo "   ls /mnt/nfs/production-scratch"
echo "   ls /mnt/nfs/job-folder-archive"
echo ""
echo "2. View mount status:"
echo "   mount | grep nfs"
echo "   df -h | grep nfs"
echo ""
echo "3. Monitor autofs logs:"
echo "   sudo journalctl -u autofs -f"
echo ""
echo -e "${YELLOW}Note:${NC} Mounts will appear automatically when you access them."
echo "They will unmount after 10 minutes of inactivity (timeout=600)."
echo ""
echo "Configuration files:"
echo "  /etc/auto.master"
echo "  /etc/auto.nfs"
