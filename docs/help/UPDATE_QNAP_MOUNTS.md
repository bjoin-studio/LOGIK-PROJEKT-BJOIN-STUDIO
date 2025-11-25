# Update QNAP NFS Mounts Guide

## Current Configuration
Your `/etc/auto_nfs` currently has:
```
/mnt/ASUSSTOR  -fstype=nfs,rw,resvport,nfsvers=4  10.20.33.86:/volume1/BJOINFILMS_NAS
/mnt/QNAP      -fstype=nfs,rw,hard,intr,vers=3,rsize=1048576,wsize=1048576  10.10.10.11:/QNAP
```

## Recommended Changes

Replace the single `/mnt/QNAP` mount with two specific shares optimized for your 100GbE network:

```
/mnt/production-scratch -fstype=nfs,vers=4.1,rw,resvport,tcp,hard,intr,rsize=1048576,wsize=1048576,async,noatime,nodiratime,actimeo=120    10.10.10.11:/production-scratch
/mnt/job-folder-archive -fstype=nfs,vers=4.1,rw,resvport,tcp,hard,intr,rsize=1048576,wsize=1048576,async,noatime,nodiratime,actimeo=120    10.10.10.11:/job-folder-archive
```

## Step-by-Step Instructions

### 1. Backup your current configuration
```bash
sudo cp /etc/auto_nfs /etc/auto_nfs.backup.$(date +%Y%m%d_%H%M%S)
```

### 2. Edit /etc/auto_nfs
```bash
sudo nano /etc/auto_nfs
```

### 3. Make these changes:
- Comment out the old QNAP line:
  ```
  #/mnt/QNAP -fstype=nfs,rw,hard,intr,vers=3,rsize=1048576,wsize=1048576 10.10.10.11:/QNAP
  ```

- Add the two new mount lines:
  ```
  /mnt/production-scratch -fstype=nfs,vers=4.1,rw,resvport,tcp,hard,intr,rsize=1048576,wsize=1048576,async,noatime,nodiratime,actimeo=120    10.10.10.11:/production-scratch
  /mnt/job-folder-archive -fstype=nfs,vers=4.1,rw,resvport,tcp,hard,intr,rsize=1048576,wsize=1048576,async,noatime,nodiratime,actimeo=120    10.10.10.11:/job-folder-archive
  ```

### 4. Create mount point directories
```bash
sudo mkdir -p /mnt/production-scratch
sudo mkdir -p /mnt/job-folder-archive
```

### 5. Reload autofs
```bash
sudo systemctl reload autofs
# or if reload doesn't work:
sudo systemctl restart autofs
```

### 6. Test the new mounts
```bash
# This will trigger automount
ls /mnt/production-scratch
ls /mnt/job-folder-archive

# Check mount status
mount | grep production-scratch
mount | grep job-folder-archive

# Verify performance
df -h | grep production-scratch
df -h | grep job-folder-archive
```

## Key Improvements

| Setting | Old | New | Benefit |
|---------|-----|-----|---------|
| NFS Version | vers=3 | vers=4.1 | Better performance, security, features |
| Protocol | (default) | tcp | More reliable for high-speed networks |
| Security | (none) | resvport | Use privileged source ports |
| Write mode | (sync default) | async | Better write performance |
| Access time | (updates) | noatime,nodiratime | Reduces metadata overhead |
| Attribute cache | (default 3-60s) | actimeo=120 | Better performance, less network traffic |

## Troubleshooting

### If mounts don't appear:
```bash
# Check autofs service
sudo systemctl status autofs

# View logs
sudo journalctl -u autofs -f

# Test NFS connectivity
showmount -e 10.10.10.11
```

### If you need to unmount:
```bash
sudo umount /mnt/production-scratch
sudo umount /mnt/job-folder-archive
sudo systemctl restart autofs
```

### Performance testing:
```bash
# Test write speed
time dd if=/dev/zero of=/mnt/production-scratch/test.dat bs=1M count=1024

# Test read speed  
time dd if=/mnt/production-scratch/test.dat of=/dev/null bs=1M

# Clean up
rm /mnt/production-scratch/test.dat
```

## Rollback Instructions

If you need to revert to the old configuration:
```bash
# Restore from backup
sudo cp /etc/auto_nfs.backup.YYYYMMDD_HHMMSS /etc/auto_nfs
sudo systemctl restart autofs
```

## Reference
- Recommended configuration: `docs/help/auto_nfs.recommended`
- Based on working macOS configuration from your Mac workstation
