# Linux发行版命令兼容性分析

## 一、命令兼容性分类

### 1.1 内核标准接口（100%兼容）

这些是Linux内核提供的标准接口，**所有Linux发行版通用**，包括国产操作系统：

| 接口路径 | 说明 | Ubuntu | CentOS/RHEL | 中标麒麟 | 银河麒麟 | 深度Linux |
|---------|------|--------|-------------|---------|---------|---------|
| `/proc/cpuinfo` | CPU信息 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/proc/meminfo` | 内存信息 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/proc/interrupts` | 中断信息 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/proc/softirqs` | 软中断信息 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/proc/mounts` | 挂载信息 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/proc/diskstats` | 磁盘统计 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/proc/net/dev` | 网络统计 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/sys/class/net/*` | 网络接口属性 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/sys/block/*` | 块设备属性 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/sys/devices/system/cpu/*` | CPU属性 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/sys/devices/system/node/*` | NUMA节点 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/sys/kernel/mm/transparent_hugepage/*` | THP配置 | ✓ | ✓ | ✓ | ✓ | ✓ |

### 1.2 标准系统工具（99%兼容）

这些属于基础系统工具包，**几乎所有发行版默认安装**：

| 命令 | 所属包 | Ubuntu | CentOS/RHEL | 中标麒麟 | 银河麒麟 | 深度Linux |
|------|--------|--------|-------------|---------|---------|---------|
| `lsblk` | util-linux | ✓ | ✓ | ✓ | ✓ | ✓ |
| `df` | coreutils | ✓ | ✓ | ✓ | ✓ | ✓ |
| `free` | procps | ✓ | ✓ | ✓ | ✓ | ✓ |
| `vmstat` | procps | ✓ | ✓ | ✓ | ✓ | ✓ |
| `uptime` | procps | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cat` | coreutils | ✓ | ✓ | ✓ | ✓ | ✓ |
| `grep` | grep | ✓ | ✓ | ✓ | ✓ | ✓ |
| `awk` | gawk | ✓ | ✓ | ✓ | ✓ | ✓ |
| `ip` | iproute2 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `hostname` | coreutils | ✓ | ✓ | ✓ | ✓ | ✓ |
| `nproc` | coreutils | ✓ | ✓ | ✓ | ✓ | ✓ |

**安装命令**（如缺失）：
```bash
# Debian/Ubuntu
sudo apt-get install util-linux procps iproute2

# RHEL/CentOS
sudo yum install util-linux procps-ng iproute

# 国产OS
sudo yum install util-linux procps-ng iproute
```

### 1.3 性能监控工具（95%兼容）

| 命令 | 所属包 | Ubuntu | CentOS/RHEL | 中标麒麟 | 银河麒麟 | 深度Linux |
|------|--------|--------|-------------|---------|---------|---------|
| `lscpu` | util-linux | ✓ | ✓ | ✓ | ✓ | ✓ |
| `iostat` | sysstat | ✓ | ✓ | ✓ | ✓ | ✓ |
| `mpstat` | sysstat | ✓ | ✓ | ✓ | ✓ | ✓ |
| `sar` | sysstat | ✓ | ✓ | ✓ | ✓ | ✓ |
| `nmon` | nmon | △需安装 | △需安装 | △需安装 | △需安装 | △需安装 |

**安装命令**：
```bash
# Debian/Ubuntu
sudo apt-get install sysstat

# RHEL/CentOS/中标麒麟
sudo yum install sysstat

# 银河麒麟/深度
sudo apt-get install sysstat
```

### 1.4 硬件探测工具（90%兼容）

| 命令 | 所属包 | Ubuntu | CentOS/RHEL | 中标麒麟 | 银河麒麟 | 深度Linux |
|------|--------|--------|-------------|---------|---------|---------|
| `dmidecode` | dmidecode | ✓ | ✓ | ✓ | ✓ | ✓ |
| `ethtool` | ethtool | ✓ | ✓ | ✓ | ✓ | ✓ |
| `hdparm` | hdparm | ✓ | ✓ | ✓ | ✓ | ✓ |
| `numactl` | numactl | △需安装 | △需安装 | △需安装 | △需安装 | △需安装 |
| `cpufreq-info` | cpufrequtils | △需安装 | △需安装 | △需安装 | △需安装 | △需安装 |
| `nvme` | nvme-cli | △需安装 | △需安装 | △需安装 | △需安装 | △需安装 |
| `lldpctl` | lldpd | △需安装 | △需安装 | △需安装 | △需安装 | △需安装 |

**安装命令**：
```bash
# Debian/Ubuntu/银河麒麟/深度
sudo apt-get install dmidecode ethtool hdparm numactl cpufrequtils nvme-cli lldpd

# RHEL/CentOS/中标麒麟
sudo yum install dmidecode ethtool hdparm numactl kernel-tools nvme-cli lldpd
```

---

## 二、国产操作系统兼容性说明

### 2.1 中标麒麟（NeoKylin）

**基于**：CentOS/RHEL

**兼容性**：⭐⭐⭐⭐⭐ 极高

**特点**：
- 系统工具与CentOS完全兼容
- 使用 yum/dnf 包管理器
- `/etc/redhat-release` 标识
- 支持大部分RedHat企业版特性

**注意事项**：
- 部分安全增强特性可能需要额外配置
- 虚拟化环境支持较好

### 2.2 银河麒麟（Kylin）

**基于**：Ubuntu/Debian（新版）或 CentOS（老版）

**兼容性**：⭐⭐⭐⭐ 高

**特点**：
- 新版基于Ubuntu，包管理器 `apt`
- 老版基于CentOS，包管理器 `yum`
- 支持国产处理器（龙芯、飞腾、鲲鹏）

**注意事项**：
- 需要确认具体版本和架构
- 部分商业版工具可能不同

### 2.3 深度Linux（Deepin）

**基于**：Debian

**兼容性**：⭐⭐⭐⭐ 高

**特点**：
- 完全兼容Debian生态
- 使用 `apt` 包管理器
- 桌面体验较好

**注意事项**：
- 主要面向桌面，服务器场景需确认
- 部分系统服务配置可能不同

### 2.4 统信UOS

**基于**：Debian/Ubuntu

**兼容性**：⭐⭐⭐⭐ 高

**特点**：
- 类似Deepin生态
- 商业版可能有定制化

**注意事项**：
- 确认具体版本和架构支持

### 2.5 华为欧拉（openEuler）

**基于**：CentOS/RHEL

**兼容性**：⭐⭐⭐⭐⭐ 极高

**特点**：
- 与CentOS完全兼容
- 针对鲲鹏处理器优化
- 企业级特性完善

---

## 三、兼容性检测脚本

### 3.1 自动检测可用命令

```bash
#!/bin/bash
# 命令可用性检测脚本
# 用途：自动检测当前系统支持哪些命令

echo "=== Command Compatibility Check ==="
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2)"
echo ""

# 定义命令列表
declare -A commands=(
    ["proc"]="cat nproc grep awk free vmstat uptime"
    ["sysfs"]="lsblk df ip hostname findmnt"
    ["monitoring"]="lscpu iostat mpstat sar"
    ["hardware"]="dmidecode ethtool hdparm numactl"
    ["advanced"]="cpufreq-info nvme lldpctl"
)

# 检测每个命令
for category in "${!commands[@]}"; do
    echo "--- $category ---"
    for cmd in ${commands[$category]}; do
        if command -v "$cmd" &> /dev/null; then
            echo "✓ $cmd"
        else
            echo "✗ $cmd (missing)"
        fi
    done
    echo ""
done

echo "=== Recommended Installation ==="
missing=""
for cmd in numactl cpufreq-info nvme; do
    if ! command -v "$cmd" &> /dev/null; then
        missing="$missing $cmd"
    fi
done

if [ -n "$missing" ]; then
    echo "Missing commands:$missing"
    echo ""
    echo "Install command:"
    if [ -f /etc/debian_version ]; then
        echo "  sudo apt-get install$missing"
    elif [ -f /etc/redhat-version ] || [ -f /etc/centos-release ]; then
        echo "  sudo yum install$missing"
    else
        echo "  Please install manually"
    fi
else
    echo "All recommended commands are available!"
fi
```

### 3.2 备选方案（命令缺失时）

```bash
#!/bin/bash
# 备选方案检测脚本
# 用途：当某些命令缺失时，使用备选方案

echo "=== Alternative Command Detection ==="

# numactl 备选
if ! command -v numactl &> /dev/null; then
    echo "numactl: not found"
    
    # 备选1: 读取NUMA信息
    if [ -d /sys/devices/system/node ]; then
        echo "  Alternative: /sys/devices/system/node/ (available)"
        ls /sys/devices/system/node/
    fi
    
    # 备选2: lscpu
    if command -v lscpu &> /dev/null; then
        echo "  Alternative: lscpu -C (available)"
    fi
fi

# cpufreq-info 备选
if ! command -v cpufreq-info &> /dev/null; then
    echo "cpufreq-info: not found"
    
    # 备选: 直接读取sysfs
    if [ -d /sys/devices/system/cpu/cpu0/cpufreq ]; then
        echo "  Alternative: /sys/devices/system/cpu/cpu0/cpufreq/ (available)"
        ls /sys/devices/system/cpu/cpu0/cpufreq/
    fi
fi

# nvme 备选
if ! command -v nvme &> /dev/null; then
    echo "nvme: not found"
    
    # 备选: sysfs
    if [ -d /sys/block/nvme* ]; then
        echo "  Alternative: /sys/block/nvme*/ (available)"
        ls /sys/block/ | grep nvme
    fi
fi

# ethtool 备选
if ! command -v ethtool &> /dev/null; then
    echo "ethtool: not found"
    
    # 备选: sysfs
    echo "  Alternative: /sys/class/net/ (available)"
    echo "  Note: Some features may not be available via sysfs"
fi
```

---

## 四、跨平台兼容策略

### 4.1 推荐实践

#### 方案1：优先使用sysfs（最通用）

```bash
# ✓ 推荐：使用内核标准接口
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
cat /sys/block/sda/queue/scheduler
cat /sys/class/net/eth0/speed

# △ 次选：使用发行版工具
lscpu
lsblk
ethtool
```

#### 方案2：自动降级

```bash
#!/bin/bash
# 获取CPU频率：优先使用cpufreq-info，降级到sysfs

get_cpu_freq() {
    # 方案1: cpufreq-info
    if command -v cpufreq-info &> /dev/null; then
        cpufreq-info -f 2>/dev/null
        return
    fi
    
    # 方案2: sysfs
    if [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq ]; then
        cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
        return
    fi
    
    # 方案3: /proc/cpuinfo
    grep 'cpu MHz' /proc/cpuinfo | head -1 | awk '{print $4}'
}

echo "CPU Frequency: $(get_cpu_freq) KHz"
```

### 4.2 检测脚本

```bash
#!/bin/bash
# 兼容性检测和适配脚本

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/redhat-release ]; then
        echo "rhel-like"
    elif [ -f /etc/debian_version ]; then
        echo "debian-like"
    else
        echo "unknown"
    fi
}

OS_TYPE=$(detect_os)
echo "Detected OS: $OS_TYPE"

# 根据OS类型选择安装命令
case "$OS_TYPE" in
    ubuntu|debian|kylin)
        PKG_MANAGER="apt-get"
        ;;
    centos|rhel|neoKylin|openEuler)
        PKG_MANAGER="yum"
        ;;
    *)
        PKG_MANAGER="yum"  # 默认
        ;;
esac

echo "Package manager: $PKG_MANAGER"

# 检测并提示安装缺失命令
missing_cmds=""
for cmd in numactl cpufreq-info nvme; do
    if ! command -v "$cmd" &> /dev/null; then
        missing_cmds="$missing_cmds $cmd"
    fi
done

if [ -n "$missing_cmds" ]; then
    echo ""
    echo "Missing packages:$missing_cmds"
    echo "Install with: sudo $PKG_MANAGER install$missing_cmds"
fi
```

---

## 五、兼容性矩阵总结

### 5.1 命令依赖程度

| 依赖级别 | 说明 | 代表命令 | 兼容性 |
|---------|------|---------|--------|
| **L0** | 内核标准接口 | /proc/*, /sys/* | 100% |
| **L1** | 基础系统工具 | cat, grep, awk, free | 99% |
| **L2** | 标准工具包 | lsblk, df, ip, vmstat | 95% |
| **L3** | 扩展监控工具 | iostat, sar, mpstat | 95% |
| **L4** | 硬件探测工具 | dmidecode, ethtool | 90% |
| **L5** | 高级特性工具 | numactl, cpufreq-info | 85% |

### 5.2 国产OS特殊考虑

| 国产OS | 推荐的命令子集 | 需要注意的点 |
|--------|--------------|-------------|
| 中标麒麟 | L0-L4全部 | 使用yum包管理器 |
| 银河麒麟 | L0-L4全部 | 确认基于Debian还是CentOS |
| 深度Linux | L0-L4全部 | 主要是桌面场景验证 |
| 统信UOS | L0-L4全部 | 商业版可能有定制 |
| 华为欧拉 | L0-L4全部 | 对鲲鹏优化良好 |

### 5.3 最小依赖集

**压测工具最小依赖**（必须）：
```bash
# L0 + L1 + L2
cat grep awk free df ip hostname nproc
```

**硬件探测增强依赖**（推荐）：
```bash
# L3 + L4
lscpu iostat dmidecode ethtool lsblk
```

**高级诊断依赖**（可选）：
```bash
# L5
numactl cpufreq-info nvme lldpctl
```

---

## 六、最佳实践建议

1. **优先使用sysfs接口**：所有Linux内核提供，不依赖发行版
2. **提供备选方案**：每个功能至少有2种实现方式
3. **自动检测可用命令**：脚本运行时自动检测并适配
4. **明确告知缺失依赖**：运行时提示用户安装缺失工具
5. **兼容国产OS**：针对中标麒麟、银河麒麟等做专门适配
