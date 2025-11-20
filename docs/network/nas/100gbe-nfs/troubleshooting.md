# NFS Troubleshooting Guide

## Common Issues and Solutions

### Mount Not Appearing

**Symptom**: `/mnt/production-scratch` doesn't show any files or mount doesn't trigger

**Diagnosis**:
```bash
# Check autofs status
sudo systemctl status autofs

# Check if share is exported from NAS
showmount -e 10.10.10.11

# Check for mount errors in logs
sudo journalctl -u autofs -n 50
```

**Solutions**:
1. Restart autofs: `sudo systemctl restart autofs`
2. Manually trigger mount: `ls /mnt/production-scratch`
3. Check network connectivity: `ping 10.10.10.11`
4. Verify NAS is exporting share properly

---

### Slow Performance

**Symptom**: File operations are slower than expected

**Diagnosis**:
```bash
# Check if nconnect is active
mount | grep production-scratch | grep nconnect

# Check NFS statistics
nfsstat -m | grep production-scratch

# Monitor real-time I/O
iostat -x 5 /mnt/production-scratch

# Check for network errors
ethtool -S <interface> | grep error
```

**Solutions**:
1. Verify nconnect=16 is in mount options
2. If not, update /etc/auto_nfs and restart autofs
3. Check for network errors (packet loss, collisions)
4. Verify jumbo frames enabled (MTU 9000)
5. Check QNAP system load (CPU, memory, disk I/O)

---

### nconnect Not Working

**Symptom**: Mount options don't show `nconnect=16`

**Diagnosis**:
```bash
# Check kernel version (needs 5.3+)
uname -r

# Check if nconnect is in auto_nfs
cat /etc/auto_nfs | grep nconnect

# Check actual mount options
mount | grep production-scratch
```

**Solutions**:
1. Verify kernel is 5.3 or later (Rocky 9.5 has 5.14) ✅
2. Unmount and remount:
   ```bash
   sudo umount /mnt/production-scratch
   sudo systemctl restart autofs
   ls /mnt/production-scratch
   ```
3. Check for typos in /etc/auto_nfs
4. Ensure NFS version is 4.1 or later (nconnect requires NFSv4+)

---

### Stale File Handle

**Symptom**: Operations fail with "Stale NFS file handle" error

**Diagnosis**:
```bash
# Check mount status
mount | grep production-scratch

# Check NFS client status
nfsstat -c
```

**Solutions**:
1. Unmount and remount the share:
   ```bash
   sudo umount -f /mnt/production-scratch
   sudo systemctl restart autofs
   ls /mnt/production-scratch
   ```
2. If that fails, force unmount:
   ```bash
   sudo umount -l /mnt/production-scratch
   sudo systemctl restart autofs
   ```
3. Check if QNAP NFS service is running
4. Verify network stability

---

### Permission Denied

**Symptom**: Cannot read or write files despite mount appearing successful

**Diagnosis**:
```bash
# Check mount options
mount | grep production-scratch

# Check actual permissions
ls -la /mnt/production-scratch

# Check NFS ID mapping
nfsstat -m | grep production-scratch
```

**Solutions**:
1. Verify NAS export allows your IP (10.10.10.20)
2. Check user ID mapping on NAS
3. Verify `rw` (read-write) is in mount options
4. Check QNAP share permissions
5. Ensure `resvport` is being honored by NAS

---

### Auto-mount Not Working After Reboot

**Symptom**: Mounts don't appear automatically after system restart

**Diagnosis**:
```bash
# Check autofs service status
sudo systemctl status autofs

# Check if autofs is enabled
sudo systemctl is-enabled autofs

# Check auto.master configuration
cat /etc/auto.master | grep auto_nfs
```

**Solutions**:
1. Enable autofs on boot:
   ```bash
   sudo systemctl enable autofs
   sudo systemctl start autofs
   ```
2. Verify /etc/auto.master contains:
   ```
   /-  auto_nfs
   ```
3. Trigger mount: `ls /mnt/production-scratch`

---

### Network Performance Issues

**Symptom**: Not achieving expected speeds despite nconnect=16

**Diagnosis**:
```bash
# Test raw network performance
iperf3 -c 10.10.10.11 -P 16 -t 30

# Check network interface stats
ip -s link show <interface>

# Check MTU size
ip link show | grep mtu

# Monitor network utilization
iftop -i <interface>
```

**Solutions**:
1. **Enable Jumbo Frames** (if not already):
   ```bash
   # Check current MTU
   ip link show <interface> | grep mtu
   
   # Set MTU to 9000 (temporary)
   sudo ip link set <interface> mtu 9000
   
   # Make permanent in NetworkManager or /etc/sysconfig/network-scripts/
   ```

2. **Check for packet loss**:
   ```bash
   ping -c 100 -s 8972 10.10.10.11
   ```

3. **Verify network card is using all queues**:
   ```bash
   ethtool -l <interface>
   ```

4. **Check interrupt distribution**:
   ```bash
   cat /proc/interrupts | grep <interface>
   ```

---

### QNAP NAS Issues

**Symptom**: NAS-side problems affecting performance

**Diagnosis** (on QNAP):
- Check NFS service status in QNAP admin panel
- Monitor CPU and memory usage
- Check disk health and RAID status
- Review NFS server logs

**Solutions**:
1. **Increase NFS threads** (QNAP admin):
   - Go to NFS settings
   - Increase thread count from 8 to 32-64

2. **Verify export options**:
   - Ensure share is exported with `async` on server side
   - Check client access list includes 10.10.10.20

3. **Check QNAP system resources**:
   - CPU usage should be < 80% during heavy I/O
   - Memory should have free cache for NFS operations
   - Disk I/O shouldn't be maxed out

---

### Flame-Specific Issues

**Symptom**: Flame has trouble accessing NFS mounts

**Diagnosis**:
```bash
# Check if Flame user can access mount
sudo -u flame ls /mnt/production-scratch

# Check Flame project paths
# In Flame, go to Project Settings → Paths

# Check symbolic link
ls -la /PROJEKTS
```

**Solutions**:
1. Verify /PROJEKTS symlink is correct:
   ```bash
   ls -la /PROJEKTS
   # Should show: /PROJEKTS -> /mnt/production-scratch/PROJEKTS
   ```

2. Ensure Flame has proper permissions
3. Check that project paths in Flame point to correct locations
4. Restart Flame after mount changes

---

### Testing Tools

#### Quick Performance Test
```bash
# Single stream (baseline)
dd if=/dev/zero of=/mnt/production-scratch/test.dat bs=50M count=100 conv=fdatasync
rm /mnt/production-scratch/test.dat

# Multi-stream (should be much faster with nconnect=16)
for i in {1..4}; do
  dd if=/dev/zero of=/mnt/production-scratch/test_$i.dat bs=50M count=25 &
done
wait
rm /mnt/production-scratch/test_*.dat
```

#### Network Bandwidth Test
```bash
# Install iperf3 on both workstation and QNAP
sudo dnf install -y iperf3

# On QNAP (or have it running as service):
iperf3 -s

# On workstation:
iperf3 -c 10.10.10.11 -P 16 -t 30
```

#### NFS Statistics
```bash
# Client-side statistics
nfsstat -c

# Mount-specific statistics  
nfsstat -m | grep production-scratch

# Watch statistics in real-time
watch -n 1 'nfsstat -c | head -20'
```

---

## Emergency Recovery

### Complete Mount Failure

If mounts are completely broken:

1. **Stop autofs**:
   ```bash
   sudo systemctl stop autofs
   ```

2. **Force unmount everything**:
   ```bash
   sudo umount -l /mnt/production-scratch
   sudo umount -l /mnt/job-folder-archive
   ```

3. **Restore backup configuration**:
   ```bash
   sudo cp /etc/auto_nfs.backup.<timestamp> /etc/auto_nfs
   ```

4. **Restart autofs**:
   ```bash
   sudo systemctl start autofs
   ls /mnt/production-scratch
   ```

### Rollback to Pre-nconnect Configuration

If nconnect is causing issues:

```bash
# Restore original config (without nconnect)
sudo cp /etc/auto_nfs.backup.pre-nconnect /etc/auto_nfs
sudo systemctl restart autofs
```

---

## Monitoring Commands

### Real-Time Monitoring

```bash
# Watch mount status
watch -n 2 'mount | grep production-scratch'

# Monitor NFS operations
nfsiostat 1

# Monitor disk I/O
iostat -x 1

# Monitor network
iftop -i <interface>

# System load
htop
```

### Log Monitoring

```bash
# Autofs logs
sudo journalctl -u autofs -f

# System logs for NFS
sudo journalctl -k | grep -i nfs

# Dmesg for mount errors
dmesg | grep -i nfs | tail -20
```

---

## Getting Help

### Information to Collect

When seeking help, gather this information:

```bash
# System info
uname -r
cat /etc/os-release

# Mount configuration
cat /etc/auto_nfs
cat /etc/auto.master

# Current mounts
mount | grep nfs

# NFS statistics
nfsstat -c

# Recent logs
sudo journalctl -u autofs -n 100 --no-pager

# Network config
ip addr show
ip route show
```

### Useful Links

- [Red Hat NFS Documentation](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/managing_file_systems/exporting-nfs-shares_managing-file-systems)
- [Linux NFS FAQ](http://nfs.sourceforge.net/)
- [QNAP NFS Documentation](https://www.qnap.com/en/how-to/faq/article/how-do-i-use-nfs)

---

**Last Updated**: November 19, 2025  
**Version**: 1.0
