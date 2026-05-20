# 硬件规格探测文档

## 一、文档说明

本文档定义硬件规格探测的完整指标体系，用于**判断压测结果是否符合硬件规格**。每个指标包含采集命令、替代命令（原生sysfs）、是否需要root权限。

---

## 二、CPU子系统

### 2.1 基础规格

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| CPU型号 | `grep 'model name' /proc/cpuinfo` | `cat /proc/cpuinfo` | 否 | 判断CPU基准性能代数 |
| 物理核心数 | `grep -c 'physical id' /proc/cpuinfo` | `ls /sys/devices/system/cpu/` | 否 | 计算理论并发能力 |
| 逻辑核心数 | `nproc` | `ls -d /sys/devices/system/cpu/cpu[0-9]* | wc -l` | 否 | 线程数配置参考 |
| CPU频率(MHz) | `grep 'cpu MHz' /proc/cpuinfo` | `cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq` | 否 | 计算基准性能 |

### 2.2 高级规格

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| **L1缓存大小** | `lscpu -C \| grep L1d` | `cat /sys/devices/system/cpu/cpu0/cache/index0/size` | 否 | 判断缓存性能影响 |
| **L2缓存大小** | `lscpu -C \| grep L2` | `cat /sys/devices/system/cpu/cpu0/cache/index1/size` | 否 | 判断缓存性能影响 |
| **L3缓存大小** | `lscpu -C \| grep L3` | `cat /sys/devices/system/cpu/cpu0/cache/index2/size` | 否 | 判断缓存性能影响 |
| **CPU特性(AVX/AVX2)** | `grep flags /proc/cpuinfo \| head -1` | 无 | 否 | 判断指令集支持能力 |
| **NUMA拓扑** | `lscpu -C` | `numactl --hardware` 或 `ls /sys/devices/system/node/` | 否 | 判断内存访问模式 |
| **调度器类型** | `cpufreq-info` | `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor` | 否 | 判断频率调度策略 |
| **CPU频率上下限** | `cpufreq-info` | `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq`<br>`cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq` | 否 | 判断频率限制 |

---

## 三、内存子系统

### 3.1 基础规格

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| 内存总量(MB) | `awk '/MemTotal/ {print $2}' /proc/meminfo` | `cat /proc/meminfo \| grep MemTotal` | 否 | 容量确认 |
| 内存可用量(MB) | `awk '/MemAvailable/ {print $2}' /proc/meminfo` | `cat /proc/meminfo \| grep MemAvailable` | 否 | 容量确认 |
| 内存使用率 | `free \| grep Mem` | 无 | 否 | 判断内存压力 |

### 3.2 高级规格

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| **内存类型(DDR4/DDR5)** | `dmidecode -t memory \| grep Type` | 无 | **是** | 确定理论带宽 |
| **内存频率** | `dmidecode -t memory \| grep Speed` | 无 | **是** | 计算理论带宽 |
| **内存通道数** | `dmidecode -t memory \| grep Channel` | `ls /sys/devices/system/node/ \| grep node` | 否 | 计算理论带宽 |
| **理论带宽计算** | 无 | 公式: 频率(MT/s) × 通道数 × 8B ÷ 1000 = GB/s | 否 | 压测结果对比基准 |
| **透明大页配置** | `cat /sys/kernel/mm/transparent_hugepage/enabled` | 无 | 否 | 性能影响因素 |
| **大页数量** | `cat /proc/sys/vm/nr_hugepages` | 无 | **是** | 内存分配优化 |

---

## 四、IO子系统

### 4.1 基础规格

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| 磁盘列表 | `lsblk -d -o NAME,SIZE,TYPE` | `ls /sys/block/` | 否 | 磁盘识别 |
| 磁盘类型(SSD/HDD) | `lsblk -d -o NAME,ROTA` | `cat /sys/block/sda/queue/rotational` | 否 | 0=SSD, 1=HDD |
| 磁盘容量 | `lsblk -d -o NAME,SIZE` | `cat /sys/block/sda/size` | 否 | 容量确认 |
| 文件系统类型 | `df -T \| grep -v tmpfs` | `cat /proc/mounts \| grep -v tmpfs` | 否 | 文件系统识别 |

### 4.2 高级规格

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| **调度器类型** | `lsblk -o NAME,SCHEDULER` | `cat /sys/block/sda/queue/scheduler` | 否 | 判断IO调度策略 |
| **队列深度** | 无 | `cat /sys/block/sda/queue/nr_requests` | 否 | IO调度优化参考 |
| **预读大小** | 无 | `cat /sys/block/sda/queue/read_ahead_kb` | 否 | 读取优化 |
| **写缓存状态** | `hdparm -W /dev/sda` | `cat /sys/block/sda/queue/write_cache` | 否 | 写入性能影响 |
| **最大段大小** | 无 | `cat /sys/block/sda/queue/max_sectors_kb` | 否 | IO大小限制 |
| **TRIM支持** | `hdparm -I /dev/sda \| grep TRIM` | `cat /sys/block/sda/queue/discard_max_bytes` | 否 | SSD优化 |
| **挂载选项** | `findmnt -T /path -o OPTIONS` | `cat /proc/mounts` | 否 | 文件系统优化参考 |

### 4.3 NVMe专用规格

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| NVMe设备列表 | `ls /dev/nvme*` | `ls /sys/block/nvme*` | 否 | NVMe识别 |
| NVMe型号 | `nvme list` | `cat /sys/block/nvme0n1/device/model` | 否 | 型号识别 |
| NVMe固件版本 | `nvme list` | `cat /sys/block/nvme0n1/device/revision` | 否 | 固件版本 |
| NVMe命名空间 | `nvme list-ns /dev/nvme0` | `ls /sys/block/nvme0n*` | 否 | 命名空间 |

---

## 五、网络子系统

### 5.1 基础规格

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| 接口列表 | `ip link show` | `ls /sys/class/net/` | 否 | 接口识别 |
| IP地址 | `ip addr show` | `cat /sys/class/net/ens34/address` | 否 | 地址确认 |
| 接口状态 | `ip link show` | `cat /sys/class/net/ens34/operstate` | 否 | up/down |
| MTU | `ip link show` | `cat /sys/class/net/ens34/mtu` | 否 | 网络包大小 |
| **网卡标称速度** | `ethtool ens34 \| grep Speed` | `cat /sys/class/net/ens34/speed` | 否 | 理论带宽基准 |
| 双工模式 | `ethtool ens34 \| grep Duplex` | `cat /sys/class/net/ens34/duplex` | 否 | 全双工/半双工 |

### 5.2 高级规格

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| **中断合并设置** | `ethtool -c ens34` | `cat /sys/class/net/ens34/coalesce/rx-usecs`<br>`cat /sys/class/net/ens34/coalesce/tx-usecs` | 否 | CPU利用率优化 |
| **Offload特性** | `ethtool -k ens34` | `ls /sys/class/net/ens34/features/`<br>`cat /sys/class/net/ens34/features/*` | 否 | 网络卸载优化 |
| 网卡驱动信息 | `ethtool -i ens34` | `cat /sys/class/net/ens34/device/uevent` | 否 | 驱动诊断 |
| 统计信息 | `ethtool -S ens34` | `cat /proc/net/dev` | 否 | 流量统计 |
| Bonding配置 | `cat /proc/net/bonding/bond0` | `ls /sys/class/net/bond0/bonding/` | 否 | 聚合配置 |

---

## 六、内核参数

### 6.1 内存参数

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| Swap倾向 | `cat /proc/sys/vm/swappiness` | 无 | **是** | Swap使用策略 |
| 脏页比例 | `cat /proc/sys/vm/dirty_ratio` | 无 | **是** | 写缓存策略 |
| 内存过载策略 | `cat /proc/sys/vm/overcommit_memory` | 无 | **是** | 内存分配策略 |
| 透明大页状态 | `cat /sys/kernel/mm/transparent_hugepage/enabled` | 无 | 否 | THP状态 |

### 6.2 网络参数

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| TCP接收缓冲 | `cat /proc/sys/net/ipv4/tcp_rmem` | 无 | **是** | TCP优化 |
| TCP发送缓冲 | `cat /proc/sys/net/ipv4/tcp_wmem` | 无 | **是** | TCP优化 |
| 套接字最大缓冲 | `cat /proc/sys/net/core/rmem_max` | 无 | **是** | 套接字优化 |
| 网卡队列长度 | `cat /proc/sys/net/core/netdev_max_backlog` | 无 | **是** | 队列优化 |

### 6.3 文件系统参数

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| 最大文件句柄 | `cat /proc/sys/fs/file-max` | 无 | **是** | 句柄限制 |
| 单进程最大句柄 | `cat /proc/sys/fs/nr_open` | 无 | **是** | 进程限制 |

### 6.4 CPU调度参数

| 指标名称 | 采集命令 | 替代命令（原生sysfs） | 是否需要root | 用途说明 |
|---------|---------|---------------------|------------|---------|
| 调度周期 | `cat /proc/sys/kernel/sched_latency_ns` | 无 | **是** | 调度优化 |
| 最小时间片 | `cat /proc/sys/kernel/sched_min_granularity_ns` | 无 | **是** | 调度优化 |

---

## 七、硬件规格基准库

### 7.1 网络带宽预期

| 链路速度 | 理论带宽 | 正常达成率 | 备注 |
|---------|---------|-----------|------|
| 1 Gbps | 125 MB/s | 70-95% | 考虑协议开销 |
| 10 Gbps | 1250 MB/s | 70-95% | 需要 jumbo frame 优化 |
| 25 Gbps | 3125 MB/s | 70-95% | 通常需要 SR-IOV |
| 40 Gbps | 5000 MB/s | 70-95% | 多通道聚合 |

### 7.2 磁盘IOPS预期

| 磁盘类型 | 随机读IOPS | 随机写IOPS | 备注 |
|---------|-----------|-----------|------|
| HDD 7200 RPM | 75-150 | 75-150 | 受寻道时间限制 |
| HDD 10K RPM | 125-200 | 125-200 | 企业级 |
| SATA SSD | 30K-100K | 20K-80K | 取决于型号 |
| NVMe SSD | 200K-1000K | 150K-800K | 取决于型号 |

### 7.3 内存带宽预期

| 内存规格 | 单通道带宽 | 双通道带宽 | 四通道带宽 |
|---------|-----------|-----------|-----------|
| DDR4-2400 | 19.2 GB/s | 38.4 GB/s | 76.8 GB/s |
| DDR4-3200 | 25.6 GB/s | 51.2 GB/s | 102.4 GB/s |
| DDR5-4800 | 38.4 GB/s | 76.8 GB/s | 153.6 GB/s |

---

## 八、脚本实现示例

### 8.1 CPU规格采集脚本

```bash
#!/bin/bash
# CPU规格采集脚本
# 用途：采集CPU硬件规格信息

echo "=== CPU Hardware Spec ==="
echo "Model: $(grep 'model name' /proc/cpuinfo | head -1 | cut -d: -f2 | tr -d ' ')"
echo "Physical Cores: $(grep -c 'physical id' /proc/cpuinfo)"
echo "Logical Cores: $(nproc)"
echo "CPU Frequency (MHz): $(grep 'cpu MHz' /proc/cpuinfo | head -1 | cut -d: -f2 | tr -d ' ')"

# L1/L2/L3缓存 (如支持)
for level in 0 1 2; do
    cache_size=$(cat /sys/devices/system/cpu/cpu0/cache/index${level}/size 2>/dev/null)
    cache_type=$(cat /sys/devices/system/cpu/cpu0/cache/index${level}/level 2>/dev/null)
    echo "L${level} Cache: ${cache_size:-N/A}"
done

# CPU特性
echo "CPU Features: $(grep flags /proc/cpuinfo | head -1 | tr ' ' '\n' | grep -E '^lm|avx|sse' | tr '\n' ', ')"
```

### 8.2 内存规格采集脚本

```bash
#!/bin/bash
# 内存规格采集脚本
# 用途：采集内存硬件规格信息

echo "=== Memory Hardware Spec ==="
echo "Total Memory (MB): $(awk '/MemTotal/ {printf "%.0f", $2/1024}' /proc/meminfo)"
echo "Available Memory (MB): $(awk '/MemAvailable/ {printf "%.0f", $2/1024}' /proc/meminfo)"

# 需root权限
if [ "$(id -u)" = "0" ]; then
    echo "Memory Type: $(dmidecode -t memory | grep -m 1 'Type:' | awk '{print $2}')"
    echo "Memory Speed: $(dmidecode -t memory | grep -m 1 'Speed:' | awk '{print $2}')"
    echo "Memory Channels: $(dmidecode -t memory | grep -c 'Channel')"
    
    # 理论带宽计算
    freq=$(dmidecode -t memory | grep -m 1 'Speed:' | awk '{print $2}' | grep -o '[0-9]*')
    channels=$(dmidecode -t memory | grep -c 'Channel')
    if [ -n "$freq" ] && [ -n "$channels" ]; then
        bandwidth=$(awk "BEGIN {printf \"%.2f\", $freq * $channels * 8 / 1000}")
        echo "Theoretical Bandwidth: ${bandwidth} GB/s"
    fi
else
    echo "Memory Type: N/A (requires root)"
    echo "Memory Speed: N/A (requires root)"
    echo "Memory Channels: N/A (requires root)"
fi

echo "Transparent Hugepage: $(cat /sys/kernel/mm/transparent_hugepage/enabled)"
```

### 8.3 网络规格采集脚本

```bash
#!/bin/bash
# 网络规格采集脚本
# 用途：采集网络硬件规格信息

INTERFACE="${1:-eth0}"
echo "=== Network Hardware Spec (${INTERFACE}) ==="

# 基础信息
echo "MAC Address: $(cat /sys/class/net/${INTERFACE}/address)"
echo "MTU: $(cat /sys/class/net/${INTERFACE}/mtu)"
echo "Status: $(cat /sys/class/net/${INTERFACE}/operstate)"

# 网卡速度 (可能为Unknown)
speed=$(cat /sys/class/net/${INTERFACE}/speed 2>/dev/null || echo "Unknown")
echo "Speed: ${speed} Mbps"

# 中断合并设置 (替代ethtool -c)
echo "--- Interrupt Coalescing ---"
if [ -d "/sys/class/net/${INTERFACE}/coalesce" ]; then
    for param in rx-usecs tx-usecs rx-frames tx-frames; do
        value=$(cat /sys/class/net/${INTERFACE}/coalesce/${param} 2>/dev/null || echo "N/A")
        echo "${param}: ${value}"
    done
else
    echo "Interrupt coalescing: N/A (driver not support)"
fi

# Offload特性 (替代ethtool -k)
echo "--- Offload Features ---"
if [ -d "/sys/class/net/${INTERFACE}/features" ]; then
    for feature in /sys/class/net/${INTERFACE}/features/*; do
        name=$(basename "$feature")
        value=$(cat "$feature" 2>/dev/null || echo "N/A")
        echo "${name}: ${value}"
    done
else
    echo "Offload features: N/A (driver not support)"
fi
```

---

## 九、备注

1. **ethtool -c (中断合并)替代方案**：
   - 路径：`/sys/class/net/<iface>/coalesce/`
   - 关键参数：`rx-usecs`, `tx-usecs`, `rx-frames`, `tx-frames`
   - 局限性：部分驱动不支持sysfs接口，需使用ethtool

2. **ethtool -k (Offload特性)替代方案**：
   - 路径：`/sys/class/net/<iface>/features/`
   - 关键参数：`tx-tcp-segmentation`, `rx-gro`, `tx-gso-robust`等
   - 局限性：部分驱动不支持sysfs接口，需使用ethtool

3. **root权限要求**：
   - 大部分sysfs信息普通用户可读
   - `dmidecode`需要root权限
   - 修改内核参数需要root权限
