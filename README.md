# oscheckperf - 系统性能基准测试工具

**oscheckperf** 是一款专为数据库场景设计的系统级性能基准测试工具，支持单机和多机，提供一站式的服务器硬件性能评估能力。通过测试 CPU、内存、磁盘 IO、网络吞吐、线程调度、互斥锁六大核心维度，帮助用户快速评估服务器性能边界，识别潜在瓶颈。

## 快速开始

### 1. 安装依赖

**方式一：直接安装依赖包**

#### CentOS 系统为例

```bash
# 基础安装包
yum install -y sysbench iperf3 fio jq

# 非免密环境需额外安装
yum install -y sshpass

# 扩展查看更多硬件资源安装
yum install ethtool numactl
```

**方式二：工具自动编译安装**

**编译安装说明**：

编译安装仅需在\*\*编译机（脚本所在服务器）上安装编译依赖，其它远程服务器无需安装编译工具，工具会自动推送到多机。

> **重要**：必须先手动安装编译依赖库：
>
> - CentOS/RHEL: `sudo yum install -y automake autoconf libtool gcc make libaio-devel pkg-config`
> - Ubuntu/Debian: `sudo apt-get install -y automake autoconf libtool libtool-bin gcc make libaio-dev pkg-config`

**编译安装组件**

```bash
# 单机时使用 -i 参数编译安装（使用本地离线安装包，无需联网）
# -i all: 删除旧目录并重新编译所有组件
./oscheckperf -i all

# -i oscheckperf: 仅更新 oscheckperf 脚本
./oscheckperf -i oscheckperf

# 多机时自动编译并分发到远程服务器（无需 root 权限）
./oscheckperf -i all -f server_list
./oscheckperf -i oscheckperf -f server_list
```

**编译包推送时发行版兼容策略**

默认情况下，工具采用宽松模式进行发行版兼容性检查，**直接检测包管理系统**：

- **RPM 系**：自动检测 `rpm`/`yum`/`dnf` 包管理器
- **DEB 系**：自动检测 `dpkg`/`apt` 包管理器

严格模式：要求远程服务器发行版与本地完全匹配，STRICT\_DISTRO\_CHECK=true

| 模式       | 参数值     | Centos→Kylin | CentOS→Ubuntu | Ubuntu→Debian |
| -------- | ------- | ------------ | ------------- | ------------- |
| 宽松模式（默认） | `false` | ✅ 允许         | ❌ 拒绝          | ✅ 允许          |
| 严格模式     | `true`  | ❌ 拒绝         | ❌ 拒绝          | ❌ 拒绝          |

### 2. 运行测试

```bash
#单机运行
# 等同于执行./oscheckperf all 根据默认值执行所有测试项（不包括网络）
./oscheckperf
# 单机运行，例如：
./oscheckperf cpu           # 仅 CPU 测试
./oscheckperf cpu mem io    #  MEM和IO 测试
./oscheckperf network       # 仅网络测试
# 参数和配置文件同时配置时，参数优先级大于配置文件
./oscheckperf -p parameter.conf cpu


#多机运行
# 检查模式配合调试
./oscheckperf check -f server_list 
# 使用配置文件
./oscheckperf  -p parameter.conf -f server_list 
# 指定子命令和参数
./oscheckperf io DURATION=60 IO_TOOL=fio -f server_list
# 网络测试指定服务器列表(相同选项中参数优先级大于配置文件)
./oscheckperf network -f server_list -p parameter.conf
```

### 3. 服务器认证方式

#### 方式一：SSH 免密登录（推荐）

**服务器列表文件格式**：

```bash
# server_list 文件内容
192.168.1.101
192.168.1.102
192.168.1.103
```

**运行测试**：

```bash
./oscheckperf network -f server_list
```

#### 方式二：密码认证

**服务器列表文件格式**：

```bash
# server_list 文件内容（格式：IP username password，支持多空格或 tab 分隔）
# 密码可以包含任意特殊字符（包括冒号）
192.168.1.101 username secret123 
192.168.1.102 username secret123 
192.168.1.103 username secret123
```

**运行测试**：

```bash
./oscheckperf network -f server_list
```

### 4. 自定义 SSH 端口

```bash
# 方法一：配置文件里设置SSH_PORT=2222
./oscheckperf network -f server_list -p parameter.conf

# 方法二：直接使用参数
./oscheckperf network -f server_list SSH_PORT=2222
```

### 5. 干运行模式（预览底层运行的原始命令，不实际执行）

```bash
# 预览指定测试命令
./oscheckperf io --dry-run

# 预览网络测试命令
./oscheckperf network -f server_list --dry-run
```

<br />

```bash
# 查看最终性能报告
cat output/report_benchmark_*.log

# 查看解析后的测试数据
cat output/data_*_all_results.log

# 查看原始测试数据
cat output/original_data_*_all_results.log
```

## 输出指标说明

### CPU 测试

- **events/sec**：每秒执行事件数（越高越好）
- **Avg Latency**：平均延迟（越低越好）
- **Min Latency**：最小延迟（越低越好）
- **P95 Latency**：95 百分位延迟（越低越好）
- **P99 Latency**：99 百分位延迟（越低越好）
- **Max Latency**：最大延迟（越低越好）
- **Sum Latency**：累计延迟（越低越好）
- **Threads fairness (events)**：线程事件公平性（格式为 avg/stddev，stddev 越小表示分布越均匀）
- **Threads fairness (execution time)**：线程执行时间公平性

### 内存测试

- **Total operations**：总操作数
- **operations/sec**：每秒内存操作数（越高越好）
- **Transferred**：实际传输数据量（MiB）
- **throughput**：内存吞吐量 MiB/s（越高越好）
- **Avg Latency**：平均延迟（越低越好）
- **Min Latency**：最小延迟（越低越好）
- **Max Latency**：最大延迟（越低越好）
- **P95 Latency**：95 百分位延迟（越低越好）
- **Sum Latency**：累计延迟（越低越好）

### IO 测试（sysbench）

- **Read IOPS**：每秒读操作数（越高越好）
- **Write IOPS**：每秒写操作数（越高越好）
- **Total IOPS**：每秒总 IO 操作数（越高越好）
- **fsyncs/s**：每秒 fsync 操作数（衡量同步写入性能）
- **Read BW**：读吞吐量 MB/s（越高越好）
- **Write BW**：写吞吐量 MB/s（越高越好）
- **Total BW**：总吞吐量 MB/s（越高越好）
- **Avg Latency**：平均延迟（越低越好）
- **Min/Max Latency**：最小/最大延迟（越低越好）
- **P95/P99 Latency**：95/99 百分位延迟（越低越好）
- **Threads fairness**：线程公平性（events/execution time）

### IO 测试（fio）

- **Read/Write IOPS**：每秒读/写操作数（越高越好）
- **Read/Write BW**：读/写吞吐量 MB/s（越高越好）
- **Avg Latency**：平均延迟（越低越好）
- **Min/Max/P95/P99 Latency**：最小/最大/95/99 百分位延迟（越低越好）
- **Device utilization**：设备利用率（%）
- **CPU user/system**：CPU 用户态/系统态利用率（%）
- **bw\_min/bw\_max**：最小/最大带宽（反映带宽稳定性）
- **slat/clat**：提交延迟/完成延迟（slat 指 IO 提交到设备的时间，clat 指设备处理完成的时间）
- **ctx/majf/minf**：上下文切换/主要页错误/次要页错误（反映系统资源使用情况）
- **iodepth\_level**：IO 队列深度级别（反映 IO 并发程度）

### 网络测试

- **Bandwidth (MB/s)**：网络带宽（越高越好）
- **Retrans**：TCP 重传次数（越少越好）
- **RTT(ms)**：往返时间（格式：平均值 (Min: 最小值, Max: 最大值)）
- **CPU(%)**：发送端/接收端 CPU 利用率（格式：senderCPU%/receiverCPU%）

### 线程测试

- **total number of events**：总事件数
- **total time**：总耗时（秒）
- **Events/sec**：每秒线程事件数（越高越好）
- **Avg Latency**：平均延迟（越低越好）
- **Min Latency**：最小延迟（越低越好）
- **Max Latency**：最大延迟（越低越好）
- **P95 Latency**：95 百分位延迟（越低越好）
- **Sum Latency**：累计延迟（越低越好）
- **Threads fairness (events)**：线程事件公平性（格式 avg/stddev）

### 互斥锁测试

- **total number of events**：总事件数
- **total time**：总耗时（秒）
- **Transactions**：事务数（越高越好）
- **TPS**：每秒事务数（越高越好）
- **Avg Latency**：平均延迟（越低越好）
- **Min Latency**：最小延迟（越低越好）
- **Max Latency**：最大延迟（越低越好）
- **P95 Latency**：95 百分位延迟（越低越好）
- **Sum Latency**：累计延迟（越低越好）

## 常用参数

#### sysbench 参数

| 参数                     | 默认值                       | 说明                                                        |
| ---------------------- | ------------------------- | --------------------------------------------------------- |
| `SYSBENCH_PROFILES`    | `seqrd seqwr rndrd rndwr` | sysbench 测试模式，空格分隔（seqwr/seqrewr/seqrd/rndrd/rndwr/rndrw） |
| `SYSBENCH_FILE_NUM`    | `4`                       | sysbench 测试文件数量                                           |
| `SYSBENCH_BLOCK_SIZE`  | `16K`                     | sysbench 块大小                                              |
| `SYSBENCH_IO_MODE`     | `sync`                    | sysbench IO 模式（sync/async）                                |
| `SYSBENCH_EXTRA_FLAGS` | `direct`                  | sysbench 额外标志（direct/sync）                                |
| `SYSBENCH_THREADS`     | `4`                       | sysbench 线程数（设置为0时自动使用CPU核心数）                             |
| `SYSBENCH_DURATION`    | `DURATION`                | sysbench IO 测试时长                                          |

#### fio 参数

| 参数             | 默认值                             | 说明                                                                             |
| -------------- | ------------------------------- | ------------------------------------------------------------------------------ |
| `FIO_PROFILES` | `read write randread randwrite` | fio 测试模式，空格分隔（read/write/randread/randwrite/rw/randrw/trim/randtrim/trimwrite） |
| `FIO_BS`       | `8K`                            | fio 块大小（适合8K页数据库场景）                                                            |
| `FIO_IODEPTH`  | `64`                            | fio I/O 深度                                                                     |
| `FIO_NUMJOBS`  | `4`                             | fio 工作线程数（设置为0时自动使用CPU核心数）                                                     |
| `FIO_DIRECT`   | `1`                             | fio 直接 I/O 模式                                                                  |
| `FIO_FILE_NUM` | `4`                             | fio 测试文件数量（模拟多数据文件场景）                                                          |
| `FIO_IOENGINE` | `libaio`                        | fio IO 引擎（libaio/sync/posixaio）                                                |
| `FIO_DURATION` | `DURATION`                      | fio 测试时长                                                                       |

#### Threads 参数

| 参数               | 默认值              | 说明                                  |
| ---------------- | ---------------- | ----------------------------------- |
| `THREADS_NUM`    | `auto (cores*4)` | 线程数（未设置时自动根据 CPU 核心数计算，公式：cores\*4） |
| `THREADS_YIELDS` | `100`            | 每个线程的 yield 次数                      |
| `THREADS_LOCKS`  | `4`              | 锁数量                                 |

#### Memory 参数

| 参数                  | 默认值          | 说明                               |
| ------------------- | ------------ | -------------------------------- |
| `MEMORY_THREADS`    | `0`          | 内存测试线程数，0=自动（与CPU核心数一致）          |
| `MEMORY_BLOCK_SIZE` | `8K`         | 内存测试块大小                          |
| `MEMORY_TOTAL_SIZE` | `0`          | 内存测试总大小（测试数据量），0=自动（使用系统总内存的60%） |
| `MEMORY_OPER`       | `read write` | 内存操作类型                           |

#### Mutex 参数

| 参数              | 默认值    | 说明            |
| --------------- | ------ | ------------- |
| `MUTEX_THREADS` | `0`    | 互斥锁测试线程数，0=自动 |
| `MUTEX_NUM`     | `1024` | 互斥锁数量         |

#### 通用参数

| 参数                 | 默认值                         | 说明                                   |
| ------------------ | --------------------------- | ------------------------------------ |
| `IO_PATH`          | `$HOME/oscheckperf/io_test` | 测试文件目录，默认`$HOME/oscheckperf/io_test` |
| `IO_TOTAL_SIZE`    | `10G`                       | 测试文件总大小（sysbench 和 fio 通用）           |
| `IO_TOOL`          | `fio`                       | IO 测试工具（sysbench/fio）                |
| `EXEC_MODE`        | `parallel`                  | 执行模式（parallel/serial）                |
| `NETWORK_PROTOCOL` | `tcp`                       | 网络协议（tcp/udp）                        |

#### 网络测试参数

| 参数                 | 默认值      | 说明                        |
| ------------------ | -------- | ------------------------- |
| `NETWORK_PARALLEL` | `4`      | 网络测试并行连接数（iperf3 的 -P 参数） |
| `NETWORK_PORT`     | `25201`  | 网络测试端口                    |
| `NETWORK_MODE`     | `matrix` | 网络测试模式（serial/matrix）     |
| `NETWORK_DURATION` | `DURATION`| 网络测试时长（秒），未设置时使用全局DURATION |

#### 参数说明

**FIO\_FILE\_NUM 说明**：

- 设置测试文件数量，默认为 4
- 当配置 `FIO_FILE_NUM` 时，每个文件大小 = `IO_TOTAL_SIZE / FIO_FILE_NUM`
- 例如：`IO_TOTAL_SIZE=1G`，`FIO_FILE_NUM=4` → 每个文件 256M

### 网络测试

- **Bandwidth (MB/s)**：网络带宽（越高越好）
- **Retrans**：TCP 重传次数（越少越好）
- **RTT(ms)**：往返时间（格式：平均值 (Min: 最小值, Max: 最大值)）
- **CPU(%)**：发送端/接收端 CPU 利用率（格式：senderCPU%/receiverCPU%）

### 线程测试

- **events/sec**：每秒线程事件数（越高越好）
- **latency**：线程调度延迟（越低越好）

### 互斥锁测试

- **transactions**：事务数（越高越好）
- **TPS**：每秒事务数（越高越好）
- **latency**：锁等待延迟（越低越好）

### 输出文件说明（`output` 可通过参数修改）：

| 文件类型       | 路径                              | 说明          | 用途        |
| ---------- | ------------------------------- | ----------- | --------- |
| **原始测试数据** | `output/original_data_*.log`    | 所有测试的完整原始输出 | 问题排查、追溯   |
| **命令输出结果** | `output/data_*.log`             | 结构化的测试结果    | 数据处理、二次分析 |
| **最终报告**   | `output/report_benchmark_*.log` | 格式化的性能报告    | 直接查看、分享   |

## 实用场景示例

### IO场景测试

```bash
# Vastbase/openGauss 数据库场景（高IOPS要求）
./oscheckperf io IO_TOOL=fio FIO_PROFILES="randrw read" FIO_NUMJOBS=8 FIO_IODEPTH=64

# MySQL 场景（混合读写）
./oscheckperf io IO_TOOL=sysbench SYSBENCH_PROFILES="rndrw"

# PostgreSQL 场景（高吞吐量）
./oscheckperf io IO_TOOL=fio FIO_PROFILES="randrw" FIO_BS=16K FIO_NUMJOBS=16
```

### 多服务器网络测试

- `serial`：串行模式，使用server\_list文件IP列表中第一个主机作为服务器，其余主机作为客户端依次测试
  - 支持本地和远程服务器（自动检测）
  - 第一个主机为本机时直接执行，无需SSH开销
- `matrix`：执行全矩阵交叉测试（每对服务器之间都进行测试）
  - **自动分批并行**：当主机数 > 3 时，自动启用分批并行执行（参考 gpcheckperf）
  - **并行度**：自动计算为 `floor(主机数 / 2)`，无需手动配置
  - **批次内**：多个主机对同时测试，无资源竞争
  - **批次间**：顺序执行，确保测试准确性
  - **端口偏移**：批次内不同主机对使用不同端口（NETWORK\_PORT + 序号）

| 主机数 | 并行度 | 总测试对 | 总批次数 | 所需端口数 |
| --- | --- | ---- | ---- | ----- |
| 2   | 1   | 1    | 1    | 1     |
| 3   | 1   | 3    | 3    | 1     |
| 4   | 2   | 6    | 3    | 2     |
| 6   | 3   | 15   | 5    | 3     |
| 8   | 4   | 28   | 7    | 4     |

### 硬件信息及检查

```bash
# 仅查看硬件信息
./oscheckperf hardware -f server_list

# 检查系统环境（依赖、权限、磁盘、网络）
./oscheckperf check -f server_list

```

## 常见问题

### Q1: 测试需要 root 权限吗？

非 root 用户运行时，硬件信息可能显示不完整（主要集中在dmidecode ），不影响测试功能。

### Q2: IO测试文件会自动清理吗？如何自定义测试路径？

**A**: IO压测写入指定 `IO_PATH` 参数目录（默认 `$HOME/oscheckperf/io_test`），测试完成后会自动清理。可通过参数自定义路径：`./oscheckperf io IO_PATH=/data`

### Q3: 需要哪些端口？

| 端口类型   | 参数名            | 默认值   | 用途         |
| ------ | -------------- | ----- | ---------- |
| SSH端口  | `SSH_PORT`     | 22    | 远程服务器SSH连接 |
| 网络测试端口 | `NETWORK_PORT` | 25201 | iperf3网络测试 |

串行模式下，只需要25201端口

矩阵模式下，当主机数 > 3 时会自动分配偏移端口（`NETWORK_PORT + 序号`），偏移量取决批次内主机个数，有防火墙时建议开发端口参考`matrix`部分所列端口数。

### Q4: 执行工具的用户（协调机）与 server\_list 中的用户必须一致吗？

需要保证一致性，路径等参数传递时依赖类似$HOME等参数

### Q5: IO 压测文件大小如何计算？

**A**: sysbench 和 fio 的文件大小计算方式不同：

#### sysbench 文件大小

```
每个文件大小 = IO_TOTAL_SIZE / SYSBENCH_FILE_NUM
```

例如：`IO_TOTAL_SIZE=1G`，`SYSBENCH_FILE_NUM=4` → 每个文件 256M

#### fio 文件大小

```
每个文件大小 = IO_TOTAL_SIZE / (FIO_FILE_NUM * FIO_NUMJOBS)
总计 = 每个文件大小 × FIO_FILE_NUM × FIO_NUMJOBS = IO_TOTAL_SIZE
```

例如：`IO_TOTAL_SIZE=1G`，`FIO_FILE_NUM=4`，`FIO_NUMJOBS=4` → 每个文件 64M

### Q6: IO\_TOTAL\_SIZE 和 DURATION 的关系？RAID 缓存有影响吗？

**A**:

- `IO_TOTAL_SIZE` 是测试文件总大小，`DURATION` 是测试持续时间，两者独立配置
- 当`IO_TOTAL_SIZE`较小时，`DURATION`内工具会反复读或写`IO_PATH`文件；sysbench 和 fio 都支持此机制
- `direct=1` 只绕过操作系统缓存，**无法绕过 RAID 卡缓存，**`IO_TOTAL_SIZE`和`DURATION`应合理设置大小，否则结果偏高。

