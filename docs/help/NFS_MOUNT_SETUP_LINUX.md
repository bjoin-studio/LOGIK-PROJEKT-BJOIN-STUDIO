# NFS Mount Setup for Rocky Linux 9.5

## Overview
This guide configures autofs to automatically mount NFS shares from ASUSSTOR and QNAP NAS devices.

## Configuration Files

### 1. `/etc/auto.master`
Add this line to enable NFS automounts:
```
/mnt/nfs /etc/auto.nfs --timeout=600
```

### 2. `/etc/auto.nfs`
Create this file with your NFS mount configurations (see below)

## Steps to Configure

### 1. Install autofs (if not already installed)
```bash
sudo dnf install -y autofs nfs-utils
```

### 2. Enable and start autofs service
```bash
sudo systemctl enable autofs
sudo systemctl start autofs
```

### 3. Edit /etc/auto.master
```bash
sudo nano /etc/auto.master
```
Add at the end:
```
/mnt/nfs /etc/auto.nfs --timeout=600
```

### 4. Create /etc/auto.nfs
```bash
sudo nano /etc/auto.nfs
```
Paste the configuration (see template below)

### 5. Reload autofs
```bash
sudo systemctl restart autofs
```

### 6. Test the mounts
```bash
# This will trigger automount
ls /mnt/nfs/ASUSSTOR
ls /mnt/nfs/production-scratch
ls /mnt/nfs/job-folder-archive
```

## Differences between macOS and Linux NFS options

| macOS Option | Linux Equivalent | Notes |
|--------------|------------------|-------|
| resvport | resvport | Same on both |
| nefsvers=4 | vers=4 or nfsvers=4 | Slightly different syntax |
| async | async | Same on both |
| noatime | noatime | Same on both |
| nodiratime | nodiratime | Same on both |
| actimeo=120 | actimeo=120 | Same on both |
| hard | hard | Same on both |
| intr | intr | Same on both |
| rsize | rsize | Same on both |
| wsize | wsize | Same on both |

## Troubleshooting

### Check autofs status
```bash
sudo systemctl status autofs
```

### View autofs logs
```bash
sudo journalctl -u autofs -f
```

### Test NFS connectivity
```bash
showmount -e 10.10.10.11
showmount -e 10.20.33.86
```

### Reload autofs after changes
```bash
sudo systemctl reload autofs
# or
sudo systemctl restart autofs
```

### Check mount status
```bash
mount | grep nfs
df -h | grep nfs
```

### Firewall configuration (if needed)
```bash
# Allow NFS through firewall
sudo firewall-cmd --permanent --add-service=nfs
sudo firewall-cmd --permanent --add-service=rpc-bind
sudo firewall-cmd --permanent --add-service=mountd
sudo firewall-cmd --reload
```
