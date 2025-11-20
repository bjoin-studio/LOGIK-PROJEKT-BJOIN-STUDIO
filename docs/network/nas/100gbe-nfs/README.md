# 100GbE NFS Configuration for VFX Workflows

## Overview

This directory documents the high-performance NFS configuration for the bjoin-studio VFX workstation connected to QNAP NAS storage over 100 Gigabit Ethernet.

**Network Setup:**
- Workstation: Rocky Linux 9.5 (10.10.10.20)
- QNAP NAS: 100GbE connection (10.10.10.11)
- ASUSSTOR NAS: 10GbE connection (10.20.33.86)
- Protocol: NFS 4.1 with nconnect=16

## Storage Architecture

### QNAP 100GbE NAS (10.10.10.11)

#### production-scratch
- **Type**: NVMe RAID 0 (12 striped volumes)
- **Capacity**: 18TB (3.1TB used, 15TB free)
- **Mount Point**: `/mnt/production-scratch`
- **Symbolic Link**: `/PROJEKTS` → `/mnt/production-scratch/PROJEKTS`
- **Use Case**: Active VFX production, rendering, compositing

#### job-folder-archive
- **Type**: HDD mirrors (8 vdevs)
- **Capacity**: 100TB (empty)
- **Mount Point**: `/mnt/job-folder-archive`
- **Use Case**: Long-term project archive, completed jobs

### ASUSSTOR 10GbE NAS (10.20.33.86)
- **Type**: HDD RAID
- **Capacity**: 13TB (100% full)
- **Mount Point**: `/mnt/ASUSSTOR`
- **Use Case**: Legacy storage, being migrated to QNAP

## Performance Benchmarks

### Before Optimization (Single Stream, no nconnect)
| Volume | Write Speed | Read Speed |
|--------|-------------|------------|
| production-scratch | 1.8 GB/s | 1.7 GB/s |
| job-folder-archive | 1.8 GB/s | 17.1 GB/s* |

*Read speed extraordinarily high due to empty volume with all metadata cached in RAM

### After Optimization (nconnect=16)

#### 4 Parallel Streams
| Volume | Write Speed | Read Speed | Improvement |
|--------|-------------|------------|-------------|
| production-scratch | **4.01 GB/s** | **2.61 GB/s** | 2.2x write, 1.5x read |

#### 16 Parallel Streams (Maximum)
| Volume | Write Speed | Read Speed | Improvement |
|--------|-------------|------------|-------------|
| production-scratch | **5.13 GB/s** | **5.88 GB/s** | 2.8x write, 3.5x read |

## Key Optimization: nconnect=16

The critical performance breakthrough came from adding `nconnect=16` to the NFS mount options.

### What It Does
- Opens **16 TCP connections** instead of 1
- Allows parallel I/O operations
- Bypasses single-stream protocol bottlenecks
- Takes full advantage of 100GbE bandwidth

### Why It Matters for VFX
- **Flame multi-frame rendering**: 2.8x faster render output
- **8K workflows**: Can now handle 250MB/frame sequences
- **Timeline scrubbing**: 5.88 GB/s = 117 frames/sec @ 50MB/frame
- **Concurrent operations**: Multiple users/processes don't bottleneck

### Requirements
- Linux kernel 5.3+ (Rocky Linux 9.5 has 5.14+) ✅
- NFS 4.1 or later ✅
- High-speed network (10GbE or faster) ✅

## Configuration Files

- **Primary Config**: `/etc/auto_nfs` - Automount configuration
- **Master File**: `/etc/auto.master` - References auto_nfs
- **Documentation**: `docs/network/nas/100gbe-nfs/` - This directory
- **Backups**: `/etc/auto_nfs.backup.*` - Configuration backups

## Real-World VFX Performance

### Supported Workflows

#### ✅ HD/2K Compositing
- 50MB EXR @ 24fps = 1.2 GB/s required
- **Single stream**: 1.8 GB/s ✅ (1.5x headroom)
- **Multi-frame render**: 5.13 GB/s ✅ (4.3x headroom)

#### ✅ 4K Compositing  
- 100MB EXR @ 24fps = 2.4 GB/s required
- **Single stream**: 1.8 GB/s ⚠️ (close to limit)
- **Multi-frame render**: 5.13 GB/s ✅ (2.1x headroom)

#### ⚠️ 8K Compositing
- 250MB EXR @ 24fps = 6 GB/s required
- **Single stream**: 1.8 GB/s ❌ (not sufficient)
- **Multi-frame render**: 5.13 GB/s ⚠️ (85% of requirement, very close)

#### ✅ Playback/Scrubbing
- 50MB frames @ 24fps = 1.2 GB/s required
- **Read performance**: 5.88 GB/s ✅ (4.9x headroom)
- **Smooth real-time playback** even with heavy footage

## Network Topology

```
┌─────────────────────────────────────────────────────┐
│ Rocky Linux 9.5 Workstation (10.10.10.20)          │
│ - Autodesk Flame 2026.1                             │
│ - LOGIK-PROJEKT VFX Pipeline                        │
│ - NFS 4.1 Client with nconnect=16                   │
└────────────┬──────────────────────┬─────────────────┘
             │ 100GbE               │ 10GbE
             │                      │
┌────────────▼──────────────┐  ┌───▼──────────────────┐
│ QNAP NAS (10.10.10.11)    │  │ ASUSSTOR             │
│                            │  │ (10.20.33.86)        │
│ Production Scratch:        │  │                      │
│ - NVMe RAID 0 (12 drives)  │  │ Legacy Storage:      │
│ - 18TB capacity            │  │ - HDD RAID           │
│ - 5.13 GB/s write          │  │ - 13TB (full)        │
│ - 5.88 GB/s read           │  │ - Being migrated     │
│                            │  │                      │
│ Job Archive:               │  └──────────────────────┘
│ - HDD mirrors (8 vdevs)    │
│ - 100TB capacity           │
│ - Long-term storage        │
└────────────────────────────┘
```

## Migration History

### November 19, 2025
1. **Updated NFS mounts** from single `/mnt/QNAP` to specific shares:
   - `/mnt/production-scratch` (NVMe RAID 0)
   - `/mnt/job-folder-archive` (HDD mirrors)

2. **Upgraded NFS version**: v3 → v4.1
   - Better performance
   - Enhanced security
   - Modern protocol features

3. **Added nconnect=16**: 
   - 2.8x write improvement (1.8 → 5.13 GB/s)
   - 3.5x read improvement (1.7 → 5.88 GB/s)

4. **Relinked /PROJEKTS symlink**:
   - Old: `/PROJEKTS` → `/mnt/ASUSSTOR/PROJEKTS`
   - New: `/PROJEKTS` → `/mnt/production-scratch/PROJEKTS`

## Related Documentation

- [NFS Mount Setup Guide](../../help/NFS_MOUNT_SETUP_LINUX.md)
- [NFS Performance Tuning](../../help/NFS_PERFORMANCE_TUNING.md)
- [QNAP Mount Update Guide](../../help/UPDATE_QNAP_MOUNTS.md)
- [Configuration Files](./config/)
- [Benchmark Results](./benchmarks/)
- [Troubleshooting](./troubleshooting.md)

## Quick Reference Commands

```bash
# Check mount status
mount | grep production-scratch

# View NFS statistics
nfsstat -m | grep production-scratch

# Test performance (single stream)
dd if=/dev/zero of=/mnt/production-scratch/test.dat bs=50M count=100 conv=fdatasync

# Restart autofs
sudo systemctl restart autofs

# List mounts
ls -la /mnt/
```

## Support & Troubleshooting

See [troubleshooting.md](./troubleshooting.md) for common issues and solutions.

---

**Last Updated**: November 19, 2025  
**Configuration Version**: 2.0 (with nconnect=16)  
**Status**: Production ✅
