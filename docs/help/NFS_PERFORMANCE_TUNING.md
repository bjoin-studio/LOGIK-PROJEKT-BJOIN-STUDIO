# NFS Performance Tuning for QNAP 100GbE

## Current Performance
- **production-scratch** (NVMe RAID 0): 1.8 GB/s write, 1.7 GB/s read
- **job-folder-archive** (HDD mirrors): 1.8 GB/s write, 17.1 GB/s read (cached)

## Why NVMe RAID 0 Isn't Showing Full Speed

### Bottlenecks Identified
1. **NFS Synchronous Write Semantics** - Server must commit data before acknowledging
2. **Single TCP Stream** - dd/single process limited to one connection
3. **NFSv4.1 Protocol Overhead** - ~20-30% overhead for safety/consistency
4. **Round-trip Latency** - Each write requires server acknowledgment

### Expected vs Actual Performance

| Storage Type | Raw Capability | NFS Synchronous | NFS Async/Parallel |
|--------------|----------------|-----------------|---------------------|
| NVMe RAID 0 (12 drives) | 15+ GB/s | **1.8 GB/s** ✅ | 5-8 GB/s possible |
| HDD Mirror (8 vdevs) | 1-2 GB/s | **1.8 GB/s** ✅ | 1.5-2 GB/s |
| HDD Read (cached) | RAM speed | N/A | **17.1 GB/s** 🔥 |

**Key Insight:** For synchronous single-stream NFS writes, both volumes are performing at the **protocol limit**, not the storage limit.

## Ways to Unlock NVMe Performance

### 1. Use Multiple Parallel Streams
```bash
# Install parallel if not available
sudo dnf install -y parallel

# Parallel write test (4 streams)
seq 1 4 | parallel -j4 "dd if=/dev/zero of=/mnt/production-scratch/test_{}.dat bs=50M count=250 oflag=direct" 2>&1 | grep copied

# Expected: 4-6 GB/s aggregate
```

### 2. Use Applications with Multi-threaded I/O
VFX applications that help:
- **Flame** - Multi-threaded render/export
- **FFmpeg** - Use multiple `-threads` and parallel jobs
- **Rsync** - Use multiple processes
- **Nuke** - Parallel frame rendering

### 3. Tune NFS Mount Options (Advanced)

Edit `/etc/auto_nfs` to add:
```bash
# Experimental high-performance settings
/mnt/production-scratch -fstype=nfs,vers=4.1,rw,resvport,tcp,hard,rsize=1048576,wsize=1048576,noatime,nodiratime,actimeo=300,nconnect=16    10.10.10.11:/production-scratch
```

**New options:**
- `nconnect=16` - Use 16 TCP connections (Linux 5.3+, Rocky 9.5 supports this)
- `actimeo=300` - Increase attribute cache to 5 minutes

Then restart autofs:
```bash
sudo systemctl restart autofs
ls /mnt/production-scratch  # Remount
```

### 4. Server-Side Tuning (QNAP)

Check QNAP NFS server settings:
- **Export Options**: Should include `async` on server side
- **NFS threads**: Increase from default (usually 8) to 32-64
- **Network tuning**: Ensure jumbo frames enabled (MTU 9000)

### 5. Test with FIO for Realistic VFX Workload

```bash
# Install fio
sudo dnf install -y fio

# Test simulating 24fps 50MB EXR sequence (parallel writes)
fio --name=vfx_write_test \
    --directory=/mnt/production-scratch \
    --size=50M \
    --numjobs=24 \
    --bs=1M \
    --ioengine=libaio \
    --iodepth=32 \
    --rw=write \
    --direct=1 \
    --group_reporting \
    --time_based \
    --runtime=60

# Test random read (simulating scrubbing timeline)
fio --name=vfx_read_test \
    --directory=/mnt/production-scratch \
    --size=10G \
    --numjobs=8 \
    --bs=50M \
    --ioengine=libaio \
    --iodepth=32 \
    --rw=randread \
    --direct=1 \
    --group_reporting \
    --time_based \
    --runtime=60
```

### 6. Verify Network Configuration

```bash
# Check current MTU (should be 9000 for jumbo frames)
ip link show | grep mtu

# Check network interface statistics
ethtool -S <interface_name> | grep error

# Test network bandwidth directly (without NFS overhead)
# On QNAP, install iperf3, then on workstation:
iperf3 -c 10.10.10.11 -t 30 -P 8
```

## Real-World VFX Performance Expectations

### Single Stream (Current Method)
- ✅ **1.8 GB/s is excellent** for single-stream synchronous writes
- ✅ Sufficient for 24fps @ 75MB per frame
- ✅ Sufficient for 30fps @ 60MB per frame

### Multi-Stream (Flame Rendering)
With parallel operations, expect:
- 🎯 **4-6 GB/s aggregate** write speed (2-3x improvement)
- 🎯 **6-10 GB/s aggregate** read speed
- 🎯 Sufficient for 24fps @ 250MB per frame (8K workflows)

### Production vs Archive Strategy

| Use Case | Volume | Why |
|----------|--------|-----|
| **Active rendering/compositing** | production-scratch | Fast NVMe, low latency |
| **Timeline/preview playback** | production-scratch | Fast random access |
| **Completed project storage** | job-folder-archive | Massive capacity, fast reads |
| **Long-term archive** | job-folder-archive | Mirror redundancy, 100TB space |

## Verification Commands

```bash
# Check actual mount options in use
mount | grep production-scratch

# Monitor real-time I/O
iostat -x 1 /mnt/production-scratch

# Check NFS stats
nfsstat -m | grep production-scratch

# Watch network usage
watch -n1 'ifstat -i <interface>'
```

## Bottom Line

Your current **1.8 GB/s synchronous write speed is actually excellent** and represents the practical limit of single-stream NFS operations. The NVMe RAID 0's true advantage will show when:

1. **Flame renders multiple frames simultaneously** (parallel I/O)
2. **Multiple users/workstations access simultaneously** (concurrent operations)
3. **Random read/write patterns** (low latency advantage of NVMe)

For single-stream sequential writes with sync, both volumes will perform similarly because the **protocol is the bottleneck, not the storage**.
