# Future NFS Optimization Ideas

## Proven Optimizations (Implemented ✅)

### 1. nconnect=16 (CRITICAL)
- **Status**: ✅ Implemented
- **Impact**: 2.8x write, 3.5x read improvement
- **Benefit**: Enables parallel I/O, bypasses single-stream bottleneck
- **Risk**: None - widely supported in modern kernels

---

## High Priority (Ready to Test)

### 2. Jumbo Frames (MTU 9000)
- **Status**: ⏳ Not verified
- **Expected Impact**: 10-20% improvement
- **Implementation**:
  ```bash
  # Check current MTU
  ip link show | grep mtu
  
  # Set MTU to 9000 (both workstation and QNAP)
  sudo ip link set <interface> mtu 9000
  
  # Make permanent in network config
  ```
- **Benefit**: Reduces packet overhead, fewer interrupts
- **Risk**: Low - may require network switch support
- **Testing**: `ping -s 8972 -M do 10.10.10.11` should work

### 3. Increase nconnect Beyond 16
- **Status**: 📝 Idea
- **Expected Impact**: 5-15% improvement (diminishing returns)
- **Implementation**:
  ```bash
  # Test with nconnect=24
  /mnt/production-scratch -fstype=nfs,vers=4.1,...,nconnect=24
  
  # Or nconnect=32
  /mnt/production-scratch -fstype=nfs,vers=4.1,...,nconnect=32
  ```
- **Benefit**: May saturate 100GbE more fully
- **Risk**: Minimal - just more connections
- **Testing**: Repeat benchmark with 24 and 32 parallel streams

### 4. NFSv4.2 (If Available)
- **Status**: 📝 Idea
- **Expected Impact**: 10-30% improvement
- **Implementation**:
  ```bash
  # Check if QNAP supports NFSv4.2
  showmount -e 10.10.10.11
  
  # Update mount to use 4.2
  /mnt/production-scratch -fstype=nfs,vers=4.2,...
  ```
- **Benefit**: 
  - Server-side copy (offload copy operations)
  - Sparse file support
  - Better parallel writes
  - AIO improvements
- **Risk**: Low - fallback to 4.1 if not supported
- **Testing**: Check QNAP firmware for NFSv4.2 support

### 5. Increase rsize/wsize
- **Status**: 📝 Idea
- **Current**: 1048576 (1MB)
- **Expected Impact**: 5-10% improvement (maybe)
- **Implementation**:
  ```bash
  # Try 2MB buffers
  rsize=2097152,wsize=2097152
  
  # Or 4MB buffers
  rsize=4194304,wsize=4194304
  ```
- **Benefit**: Fewer NFS operations for large files
- **Risk**: Low - may use more memory
- **Testing**: Benchmark with 2MB and 4MB buffers

---

## Medium Priority (Requires QNAP Access)

### 6. QNAP NFS Server Tuning
- **Status**: 📝 Idea (requires QNAP admin access)
- **Expected Impact**: 20-40% improvement
- **Implementation**:
  
  **A. Increase NFS threads**:
  - Default: 8 threads
  - Recommended: 32-64 threads
  - Location: QNAP Admin → NFS → Advanced Settings
  
  **B. Enable async exports** (if not already):
  - Makes server not wait for disk sync on every write
  - Significant performance boost
  - Trade-off: Small data loss risk on power failure
  - Location: QNAP share export options
  
  **C. Tune kernel parameters** (via SSH to QNAP):
  ```bash
  # Increase NFS server read-ahead
  echo 16384 > /proc/sys/vm/vfs_cache_pressure
  
  # Increase dirty page cache
  echo 80 > /proc/sys/vm/dirty_ratio
  echo 50 > /proc/sys/vm/dirty_background_ratio
  ```

- **Benefit**: Unlocks more server-side performance
- **Risk**: Medium - need to understand QNAP OS
- **Testing**: Requires careful benchmarking before/after

### 7. RDMA/RoCE (Remote Direct Memory Access)
- **Status**: 🚀 Advanced (if network cards support it)
- **Expected Impact**: 50-100% improvement
- **Requirements**:
  - Network cards must support RDMA/RoCE
  - QNAP must support RDMA
  - Linux kernel with RDMA support
- **Implementation**: Complex, requires special NFS configuration
- **Benefit**: Bypass kernel networking stack entirely
- **Risk**: High - complex to configure
- **Testing**: Check if hardware supports RDMA first

---

## Low Priority (Diminishing Returns)

### 8. Tune TCP Window Sizes
- **Status**: 📝 Idea
- **Expected Impact**: 5-10% improvement
- **Implementation**:
  ```bash
  # Increase TCP window size
  sudo sysctl -w net.core.rmem_max=134217728
  sudo sysctl -w net.core.wmem_max=134217728
  sudo sysctl -w net.ipv4.tcp_rmem="4096 87380 67108864"
  sudo sysctl -w net.ipv4.tcp_wmem="4096 65536 67108864"
  ```
- **Benefit**: Better for high-latency networks (not our case)
- **Risk**: Low
- **Testing**: Benchmark before/after

### 9. Disable CPU Power Saving
- **Status**: 📝 Idea
- **Expected Impact**: 5% improvement (latency)
- **Implementation**:
  ```bash
  # Set CPU governor to performance
  sudo cpupower frequency-set -g performance
  ```
- **Benefit**: Lower latency, more consistent performance
- **Risk**: Higher power consumption
- **Testing**: Check if performance mode is already enabled

### 10. IRQ Affinity Tuning
- **Status**: 🎓 Expert level
- **Expected Impact**: 5-10% improvement
- **Implementation**:
  ```bash
  # Pin network card IRQs to specific CPUs
  # Prevent interrupt handling from bouncing between cores
  ```
- **Benefit**: Lower latency, better cache utilization
- **Risk**: Complex - can hurt if done wrong
- **Testing**: Requires understanding of system topology

---

## Application-Level Optimizations

### 11. Flame Render Settings
- **Status**: 📝 Configuration
- **Expected Impact**: Utilize available bandwidth better
- **Implementation**:
  - Enable parallel frame rendering
  - Increase render chunk size
  - Configure write caching appropriately
- **Benefit**: Make better use of the 5.13 GB/s available
- **Risk**: None
- **Testing**: Monitor actual render speeds

### 12. Parallel Rsync
- **Status**: 📝 Script/workflow
- **Expected Impact**: 2-3x faster transfers
- **Implementation**:
  ```bash
  # Use parallel to spawn multiple rsync processes
  find /source -type f | parallel -j16 rsync -av {} /mnt/production-scratch/{}
  ```
- **Benefit**: Utilize nconnect=16 for large transfers
- **Risk**: None
- **Testing**: Compare with single rsync

### 13. FFmpeg Multi-Threading
- **Status**: 📝 Configuration
- **Expected Impact**: Better utilization of I/O bandwidth
- **Implementation**:
  ```bash
  # Use multiple threads for encoding/decoding
  ffmpeg -threads 16 -i input.mov -c:v prores output.mov
  ```
- **Benefit**: Faster transcoding with parallel I/O
- **Risk**: None
- **Testing**: Monitor I/O during transcode

---

## Monitoring & Validation

### 14. Continuous Performance Monitoring
- **Status**: 📝 Idea
- **Implementation**:
  - Set up Prometheus + Grafana
  - Monitor NFS stats over time
  - Track performance degradation
  - Alert on anomalies
- **Tools**:
  - `nfsiostat` for metrics
  - `node_exporter` for system metrics
  - Custom scripts for NFS statistics
- **Benefit**: Proactive performance management
- **Risk**: None - just monitoring

### 15. Automated Benchmark Suite
- **Status**: 📝 Idea
- **Implementation**:
  ```bash
  #!/bin/bash
  # benchmark-nfs.sh
  # Runs standardized tests and logs results
  
  # Single stream test
  # 4-stream parallel test
  # 16-stream parallel test
  # Random I/O test
  # Small file test
  # Large file test
  
  # Compare with baseline
  # Alert if performance drops below threshold
  ```
- **Benefit**: Track performance over time, detect regressions
- **Risk**: None

---

## Research Ideas (Experimental)

### 16. NFS over QUIC
- **Status**: 🔬 Research
- **Timeline**: Future (not yet standardized)
- **Expected Impact**: Unknown - potential 20-50% improvement
- **Details**: QUIC protocol for NFS (UDP-based, faster than TCP)
- **Risk**: Very experimental

### 17. Distributed Storage (Ceph/GlusterFS)
- **Status**: 🔬 Alternative approach
- **Expected Impact**: Different trade-offs (redundancy vs speed)
- **Details**: Replace NFS with distributed filesystem
- **Risk**: High - major architecture change
- **Benefit**: Potential for higher aggregate performance

### 18. Local NVMe Cache (bcache/dm-cache)
- **Status**: 🔬 Research
- **Expected Impact**: Dramatically better for hot data
- **Implementation**: Use local NVMe as write-through cache for NFS
- **Risk**: Medium - adds complexity
- **Benefit**: Near-local performance for frequently accessed files

---

## Testing Matrix

Priority order for testing:

1. ✅ **nconnect=16** (DONE - 2.8x improvement)
2. 🎯 **Verify/Enable Jumbo Frames** (Quick win, 10-20% expected)
3. 🎯 **Test nconnect=24 or 32** (Potential 5-15% more)
4. 🎯 **Check for NFSv4.2** (10-30% if available)
5. 🔧 **QNAP server tuning** (20-40% if can access)
6. 📊 **Set up monitoring** (Proactive management)
7. 🧪 **Test rsize/wsize increases** (5-10% maybe)

---

## Performance Goals

### Current Status (with nconnect=16)
- ✅ 5.13 GB/s write (16 streams)
- ✅ 5.88 GB/s read (16 streams)
- ✅ 85% of 8K @ 24fps capability

### Stretch Goals
- 🎯 7+ GB/s write (jumbo frames + NFSv4.2 + server tuning)
- 🎯 8+ GB/s read (full 8K @ 24fps support)
- 🎯 50% of 100GbE theoretical max (6.25 GB/s sustained)

### Ultimate Goal
- 🚀 10+ GB/s (requires RDMA/RoCE or major optimizations)
- 🚀 80% of 100GbE theoretical max (10 GB/s)

---

## Notes on Bottlenecks

### Current Bottleneck Analysis
With nconnect=16, we're now hitting:
1. **QNAP NAS CPU** - Processing 16 streams of NFS operations
2. **NFS protocol overhead** - Still ~50% overhead vs raw network
3. **Possible QNAP NIC saturation** - May need driver tuning

### What Won't Help
- ❌ Faster local disks (not the bottleneck)
- ❌ More RAM on workstation (not memory-limited)
- ❌ Client-side CPU (not CPU-bound)
- ❌ Increasing beyond nconnect=32 (diminishing returns)

### What Will Help Most
1. 🎯 QNAP server-side tuning (NFS threads, async exports)
2. 🎯 Network optimizations (jumbo frames, maybe RDMA)
3. 🎯 NFSv4.2 features (if available)

---

**Document Version**: 1.0  
**Last Updated**: November 19, 2025  
**Author**: nbjoin + GitHub Copilot  
**Status**: Living document - update as we test
