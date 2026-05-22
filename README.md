vastbase@vastbase:~/project/script/oscheckperf$ cat README.md
中文 | [English](#english)

# oscheckperf - 系统性能基准测试工具

**oscheckperf** 是一款专为数据库场景设计的系统级性能基准测试工具，提供一站式的服务器硬件性能评估能力。通过自动化测试 CPU、内存、磁盘 IO、网络吞吐、线程调度、互斥锁六大核心维度，帮助用户快速评估服务器性能边界，识别潜在瓶颈。

**核心价值**：

- 一站式服务器硬件性能测试，结果汇总，快速分辨集群性能指标差异，便于问题定位
- 助力数据库（Vastbase、openGauss、PostgreSQL、MySQL）服务器硬件底层性能验证

## 核心特性

### 🚀 全面测试能力

- **一站式性能评估**：覆盖 CPU、内存、磁盘 IO、网络吞吐、线程调度、互斥锁六大核心维度
- **双引擎 IO 测试**：同时支持 sysbench 和 fio，满足不同场景下的 IO 性能评估需求
- **多维网络测试**：支持串行、全矩阵两种网络测试模式，全面评估集群网络性能
- **自动分发依赖包**：自动编译并分发 sysbench、sshpass 到远程服务器，支持跨架构部署
- **灵活认证方式**：同时支持 SSH 免密登录和密码认证，适应不同运维场景
- **灵活配置**：支持命令行参数、配置文件 parameter.conf、混合使用多种配置方式

### 📊 结果汇总

- **结构化报告生成**：自动生成包含系统信息、测试配置、详细指标的专业性能报告
- **多维度对比分析**：支持多服务器对比报告，快速定位性能差异和瓶颈
- **丰富指标输出**：涵盖 IOPS、吞吐量、延迟（P95/P99）、公平性等关键性能指标

### 🔒 安全保障

- **路径安全验证**：自动检测并阻止使用 tmpfs 等非真实磁盘路径进行 IO 测试
- **资源预检查**：测试前自动检查磁盘空间、依赖工具、权限等，避免测试失败
- **进程管理优化**：自动清理残留进程，保护生产环境稳定性

### 🛠️ 易用性设计

- **一键自动化测试**：单命令启动全流程测试，无需复杂配置
- **调试与预览**：支持 `--debug` 调试模式和 `--dry-run` 命令预览模式
- **灵活参数控制**：支持命令行参数、环境变量、配置文件三种参数传递方式


### 文件类型说明

| 文件类型            | 存放位置                                        | 说明                   |
| --------------- | ------------------------------------------- | -------------------- |
| **原始测试数据**      | `./output/original_data_*`                  | 所有测试的原始输出汇总          |
| **解析结果**        | `./output/data_*`                           | 解析后的结构化测试结果          |
| **最终报告**        | `./output/report_benchmark_*`               | 格式化的性能报告             |

### 路径配置

可以通过参数或配置文件 `BASE_DIR` 统一修改基础目录：

- `BASE_DIR` > 默认值 `$HOME/oscheckperf`
- `IO_PATH` > 默认值 `$BASE_DIR/io_test`
- `OUTPUT_DIR` > 默认值 `./output`

## 快速开始

### 1. 安装依赖

**方式一：直接安装依赖包**

```shellscript
# CentOS （fio可选、多IP压测非免密环境需安装sshpass）
sudo yum install -y sysbench iperf3 fio jq sshpass
```

**方式二：工具自动安装依赖**

**编译安装说明**：

编译安装仅需在**编译机（脚本所在服务器）上安装编译依赖，其它远程服务器**无需安装编译工具，工具会自动推送。

```bash
# CentOS/RHEL 系列（仅编译机需要）
sudo yum install -y automake autoconf libtool gcc make

# Ubuntu/Debian 系列（仅编译机需要）
sudo apt install -y automake autoconf libtool gcc make
```

**自动编译安装组件**

```bash
# 单机时安装-i 参数编译安装组件（使用本地离线安装包，无需联网）
./oscheckperf -i all

# 多机时自动编译并分发到远程服务器（无需root权限）
./oscheckperf -i -f server_list all

# 可以指定安装组件
./oscheckperf -i sysbench   # 编译安装 sysbench
./oscheckperf -i sshpass    # 编译安装 sshpass
./oscheckperf -i fio        # 编译安装 fio
./oscheckperf -i iperf3     # 编译安装 iperf3
./oscheckperf -i numactl    # 编译安装 numactl
./oscheckperf -i ethtool    # 编译安装 ethtool
./oscheckperf -i jq         # 编译安装 jq
```

> **注意**：编译 ethtool 前需手动安装 libmnl 依赖：
>
> - CentOS/RHEL: `sudo yum install -y libmnl-devel`
> - Ubuntu/Debian: `sudo apt-get install -y libmnl-dev`

### 2. 运行测试

```bash
# 单机运行所有测试（默认值）
./oscheckperf

# 单机运行
./oscheckperf cpu           # 仅 CPU 测试
./oscheckperf mem           # 仅内存测试
./oscheckperf io            # 仅 IO 测试
./oscheckperf network       # 仅网络测试

# 参数和配置文件同时配置时，参数优先级大于配置文件
./oscheckperf -p parameter.conf cpu

#多机运行
# 使用配置文件
./oscheckperf io IO_TOOL=sysbench -p parameter.conf -f server_list 
# 干运行模式（预览命令，不执行）
./oscheckperf all -f server_list all --dry-run
```

**命令与参数组合使用**：

```bash
# 指定子命令和参数
./oscheckperf io DURATION=60 IO_TOOL=fio

# 网络测试指定服务器列表
./oscheckperf network -f server_list

# 检查模式配合调试
./oscheckperf check --debug
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

#### 方式二：密码认证（非免密）

**服务器列表文件格式**：

```bash
# server_list 文件内容（格式：IP:username:password）
IP:username:password
IP:username:password
IP:username:password
```

**运行测试**：

```bash
./oscheckperf network -f server_list
```

**注意事项**：

- 密码认证需要安装 `sshpass` 工具，**参考安装依赖部分**
- 服务器列表中的密码以明文存储，请妥善保管
- 支持混合模式：服务器列表中可以同时包含免密和密码认证的服务器

### 4. 自定义 SSH 端口

```bash
# 方法一：配置文件里设置SSH_PORT=2222
./oscheckperf network -f server_list -p parameter.conf

# 方法二：使用环境变量
export SSH_PORT=2222
./oscheckperf network -f server_list

# 方法三：直接使用参数
./oscheckperf network -f server_list SSH_PORT=2222
```

### 5. 干运行模式（预览底层运行的原始命令）

```bash
# 预览所有测试命令
./oscheckperf --dry-run

# 预览指定测试命令
./oscheckperf io --dry-run

# 预览网络测试命令
./oscheckperf network -f server_list --dry-run
```

### 6. 查看报告

测试完成后，报告默认保存在 `./output` 目录：

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
- **Threads fairness (execution time)**：线程执行时间公平性

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

### IO 压测详细说明

#### Sysbench fileio 工作流程

Sysbench 的 fileio 测试分为三个阶段：

1. **prepare 阶段**：创建测试文件
   - 在 `IO_PATH` 指定的目录中创建测试文件
   - 默认文件大小为 1G（可通过 `IO_TOTAL_SIZE` 调整）
   - 默认创建 1 个文件（可通过 `SYSBENCH_FILE_NUM` 调整）
2. **run 阶段**：执行实际压测
   - `DURATION` 参数仅控制此阶段的执行时间
   - 对 prepare 阶段创建的文件进行随机读写操作
   - 测试模式默认为 `rndrw`（随机读写），可通过 `SYSBENCH_PROFILES` 调整
3. **cleanup 阶段**：自动清理测试文件
   - 删除 prepare 阶段创建的所有测试文件
   - 测试目录本身不会被删除

#### FIO 工作流程

FIO 测试采用不同的工作方式：

1. **配置生成**：根据参数生成 `.fio` 配置文件
2. **执行测试**：FIO 在运行时自动创建测试文件
3. **文件处理**：测试完成后 FIO 不会自动删除文件，脚本会保留结果文件

#### 重要注意事项

**IO\_PATH 参数说明**：

- 默认测试路径为 `$HOME/oscheckperf/io_test`
- **不要使用** **`/tmp`** **目录**：某些服务器的 `/tmp` 是 tmpfs（内存文件系统），会导致测试结果不准确（测试的是内存而非磁盘）
- 建议使用实际业务数据所在的磁盘分区，结果更具参考价值
- 确保目标分区有足够的可用空间（至少大于 `IO_TOTAL_SIZE`）

**常用参数**：

##### sysbench 参数

| 参数                     | 默认值        | 说明                                                        |
| ---------------------- | ---------- | --------------------------------------------------------- |
| `SYSBENCH_PROFILES`    | `rndrw`    | sysbench 测试模式，空格分隔（seqwr/seqrewr/seqrd/rndrd/rndwr/rndrw） |
| `SYSBENCH_FILE_NUM`    | `4`        | sysbench 测试文件数量                                           |
| `SYSBENCH_BLOCK_SIZE`  | `16K`      | sysbench 块大小                                              |
| `SYSBENCH_IO_MODE`     | `sync`     | sysbench IO 模式（sync/async）                                |
| `SYSBENCH_EXTRA_FLAGS` | `direct`   | sysbench 额外标志（direct/sync）                                |
| `SYSBENCH_THREADS`     | `4`        | sysbench 线程数                                              |
| `SYSBENCH_DURATION`    | `DURATION` | sysbench IO 测试时长                                          |

##### fio 参数

| 参数             | 默认值        | 说明                                                                             |
| -------------- | ---------- | ------------------------------------------------------------------------------ |
| `FIO_PROFILES` | `randrw`   | fio 测试模式，空格分隔（read/write/randread/randwrite/rw/randrw/trim/randtrim/trimwrite） |
| `FIO_BS`       | `16K`      | fio 块大小（优化后更适合数据库场景）                                                           |
| `FIO_IODEPTH`  | `32`       | fio I/O 深度                                                                     |
| `FIO_NUMJOBS`  | `4`        | fio 工作线程数                                                                      |
| `FIO_DIRECT`   | `1`        | fio 直接 I/O 模式                                                                  |
| `FIO_FILE_NUM` | `4`        | fio 测试文件数量（模拟多数据文件场景）                                                          |
| `FIO_IOENGINE` | `libaio`   | fio IO 引擎（libaio/sync/posixaio）                                                |
| `FIO_DURATION` | `DURATION` | fio 测试时长                                                                       |

##### Threads 参数

| 参数               | 默认值              | 说明                                  |
| ---------------- | ---------------- | ----------------------------------- |
| `THREADS_NUM`    | `auto (cores*4)` | 线程数（未设置时自动根据 CPU 核心数计算，公式：cores\*4） |
| `THREADS_YIELDS` | `100`            | 每个线程的 yield 次数                      |
| `THREADS_LOCKS`  | `4`              | 锁数量                                 |

##### Memory 参数

| 参数                  | 默认值    | 说明                      |
| ------------------- | ------ | ----------------------- |
| `MEMORY_THREADS`    | `0`    | 内存测试线程数，0=自动（与CPU核心数一致） |
| `MEMORY_BLOCK_SIZE` | `8K`   | 内存测试块大小                 |
| `MEMORY_TOTAL_SIZE` | `20G`  | 内存测试总大小（测试数据量）          |
| `MEMORY_OPER`       | `read` | 内存操作类型（read/write）      |

##### Mutex 参数

| 参数              | 默认值    | 说明            |
| --------------- | ------ | ------------- |
| `MUTEX_THREADS` | `0`    | 互斥锁测试线程数，0=自动 |
| `MUTEX_NUM`     | `1024` | 互斥锁数量         |

##### 通用参数

| 参数              | 默认值                         | 说明                         |
| --------------- | --------------------------- | -------------------------- |
| `IO_PATH`       | `$HOME/oscheckperf/io_test` | 测试文件目录（替代IO\_TEST\_PATH）   |
| `IO_TOTAL_SIZE` | `1G`                        | 测试文件总大小（sysbench 和 fio 通用） |
| `IO_TOOL`       | `sysbench`                  | IO 测试工具（sysbench/fio）      |

##### 参数说明

**FIO\_FILE\_NUM 说明**：

- 设置测试文件数量，默认为 4
- 当配置 `FIO_FILE_NUM` 时，每个文件大小 = `IO_TOTAL_SIZE / FIO_FILE_NUM`
- 例如：`IO_TOTAL_SIZE=1G`，`FIO_FILE_NUM=4` → 每个文件 256M

**示例**：

```bash
# 使用 sysbench 进行随机读写测试
./oscheckperf io DURATION=60 IO_TOTAL_SIZE=2G

# 使用 fio 进行顺序读测试
./oscheckperf io IO_TOOL=fio FIO_PROFILES=read FIO_DURATION=60

# 指定测试路径
./oscheckperf io IO_PATH=/data/test
```

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

## 依赖工具说明

| 工具       | 必选 | 用途               |
| -------- | -- | ---------------- |
| sysbench | 是  | CPU/内存/IO/线程/锁测试 |
| fio      | 可选 | 专业 IO 压测         |
| iperf3   | 可选 | 网络吞吐测试           |
| jq       | 是 | JSON 结果解析        |
| sshpass  | 可选 | 密码认证支持           |


### 输出文件说明

| 文件类型            | 路径                              | 说明            | 用途        |
| --------------- | ------------------------------- | ------------- | --------- |
| **原始测试数据**      | `output/original_data_*.log`    | 所有测试的完整原始输出   | 问题排查、追溯   |
| **解析结果**        | `output/data_*.log`             | 结构化的测试结果      | 数据处理、二次分析 |
| **最终报告**        | `output/report_benchmark_*.log` | 格式化的性能报告      | 直接查看、分享   |
| **sysbench 输出** | `tmp/vb_fileio_*.txt`           | sysbench 文本输出 | 调试、详细分析   |
| **fio 配置**      | `tmp/fio_*.fio`                 | fio 配置文件      | 调试配置      |
| **fio JSON**    | `tmp/fio_*_result_*.json`       | fio JSON 结果   | 程序解析      |
| **网络 JSON**     | `tmp/network_*.json`            | 网络测试结果        | 程序解析      |

## 实用场景示例

### 生产环境测试

```bash
# 生产环境完整测试（60秒，fio IO测试）
./oscheckperf DURATION=60 IO_TOOL=fio IO_TOTAL_SIZE=10G

# 快速验证测试（短时间）
./oscheckperf DURATION=10

# 仅运行关键测试（CPU、内存、IO）
./oscheckperf NETWORK_ENABLED=false THREADS_ENABLED=false MUTEX_ENABLED=false
```

### 数据库场景测试

```bash
# Vastbase/openGauss 数据库场景（高IOPS要求）
./oscheckperf io IO_TOOL=fio FIO_PROFILES="randrw read" FIO_NUMJOBS=8 FIO_IODEPTH=64

# MySQL 场景（混合读写）
./oscheckperf io IO_TOOL=sysbench SYSBENCH_PROFILES="rndrw"

# PostgreSQL 场景（高吞吐量）
./oscheckperf io IO_TOOL=fio FIO_PROFILES="randrw" FIO_BS=32K FIO_NUMJOBS=16
```

### 多服务器网络测试

```bash
# 矩阵模式测试所有服务器间网络（主机数>3时自动分批并行）
./oscheckperf network -f all-servers NETWORK_MODE=matrix NETWORK_PARALLEL=4

# 串行模式：第一个主机作为服务器，其余作为客户端（支持本地/远程服务器）
./oscheckperf network -f all-servers NETWORK_MODE=serial
```

**矩阵测试分批并行说明**：

- **自动分批**：当主机数 > 3 时，矩阵模式自动启用分批并行执行
- **并行度计算**：自动计算为 `floor(主机数 / 2)`，无需手动配置
- **完美匹配算法**：每批次内所有主机都参与测试且无资源竞争
- **端口偏移机制**：批次内不同主机对使用不同端口（NETWORK\_PORT + 序号）

| 主机数 | 并行度 | 总测试对 | 总批次数 |
| --- | --- | ---- | ---- |
| 2   | 1   | 1    | 1    |
| 3   | 1   | 3    | 3    |
| 4   | 2   | 6    | 3    |
| 6   | 3   | 15   | 5    |
| 8   | 4   | 28   | 7    |

### 硬件信息检查

```bash
# 仅查看硬件信息
./oscheckperf hardware

# 检查系统环境（依赖、权限、磁盘、网络）
./oscheckperf check

# 检查并启用调试模式
./oscheckperf check --debug
```

## 常见问题

### Q1: 测试需要 root 权限吗？

**A**: 大多数测试不需要 root 权限。脚本支持普通用户运行，但以下情况建议使用 `sudo`：

- fio direct IO 模式（默认启用）：需要绕过 OS 缓存进行真实磁盘测试
- 安装依赖包时需要 root 权限
- 建议在测试前使用 `./oscheckperf check` 检查系统环境

### Q2: 测试会删除数据吗？

**A**: 测试文件仅写入指定目录（默认 `$HOME/oscheckperf/io_test`），测试完成后可自动清理

### Q3: 如何自定义 IO 测试路径？

**A**: 使用 `IO_PATH` 参数：`./oscheckperf io IO_PATH=/data`

### Q4: NETWORK\_MODE 和 NETWORK\_PARALLEL 参数的区别是什么？

**A**:

- **NETWORK\_MODE**：控制网络测试的模式
  - `serial`：串行模式，使用第一个主机作为服务器，其余主机作为客户端依次测试
    - 支持本地和远程服务器（自动检测）
    - 第一个主机为本机时直接执行，无需SSH开销
  - `matrix`：执行全矩阵交叉测试（每对服务器之间都进行测试）
    - **自动分批并行**：当主机数 > 3 时，自动启用分批并行执行（参考 gpcheckperf）
    - **并行度**：自动计算为 `floor(主机数 / 2)`，无需手动配置
    - **批次内**：多个主机对同时测试，无资源竞争（完美匹配算法）
    - **批次间**：顺序执行，确保测试准确性
    - **端口偏移**：批次内不同主机对使用不同端口（NETWORK\_PORT + 序号）
- **NETWORK\_PARALLEL**：控制每个 iperf3 测试的并行连接数，在所有模式下都生效
  - 例如：`NETWORK_PARALLEL=4` 表示每个测试使用 4 个并行连接

**示例**：

```bash
# 串行模式，每个测试使用 4 个并行连接
./oscheckperf network -f all-servers NETWORK_MODE=serial NETWORK_PARALLEL=4

# 矩阵模式，每个测试使用 4 个并行连接
./oscheckperf network -f all-servers NETWORK_MODE=matrix NETWORK_PARALLEL=4
```

## 最佳实践
### 参数调优建议

```bash
# 根据 CPU 核心数调整线程数
# CPU_THREADS=0 表示自动（建议值）

# 对于高 IOPS 场景（如 SSD）
./oscheckperf io IO_TOOL=fio FIO_NUMJOBS=8 FIO_IODEPTH=64

# 对于高带宽场景（如 RAID）
./oscheckperf io IO_TOOL=fio FIO_BS=128K FIO_NUMJOBS=4

# 数据库场景推荐（混合读写，16K 块大小）
./oscheckperf DURATION=120 IO_TOOL=fio FIO_PROFILES="randrw" FIO_BS=16K

# 内存密集型场景
./oscheckperf mem MEMORY_TOTAL_SIZE=100G MEMORY_BLOCK_SIZE=16K

# CPU 密集型场景
./oscheckperf cpu CPU_MAX_PRIME=50000
```

***


