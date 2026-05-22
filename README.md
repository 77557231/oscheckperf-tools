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

## 项目结构

```
$HOME/oscheckperf/
├── oscheckperf              # 主入口脚本
├── sysbench-1.0.20/         # sysbench 源码编译目录（-i 参数自动下载编译）
├── sysbench-1.0.20.tar.gz   # sysbench 源码压缩包（自动下载）
├── output/                  # 测试结果输出目录（当前目录下）
│   ├── original_data_*_all_results.log  # 原始测试数据汇总
│   ├── data_*_all_results.log           # 解析后的测试结果
│   └── report_benchmark_*.log           # 最终性能报告
├── tmp/                     # 临时文件目录
│   ├── vb_fileio_*.txt      # sysbench fileio 测试输出
│   ├── fio_*.fio            # fio 配置文件
│   ├── fio_*_result_*.json  # fio JSON 结果
│   └── network_*.json       # 网络测试 JSON 结果
├── io_test/                 # IO测试数据目录
│   ├── test_file.*          # sysbench 创建的测试文件（测试后自动清理）
│   └── fio_test_file.*      # fio 创建的测试文件（保留）
├── tools/
│   └── skill.md             # 开发规范文档
├── parameter.conf           # 配置文件模板
└── README.md                # 中英文文档
```

### 文件类型说明

| 文件类型            | 存放位置                                        | 说明                   |
| --------------- | ------------------------------------------- | -------------------- |
| **原始测试数据**      | `./output/original_data_*`                  | 所有测试的原始输出汇总          |
| **解析结果**        | `./output/data_*`                           | 解析后的结构化测试结果          |
| **最终报告**        | `./output/report_benchmark_*`               | 格式化的性能报告             |
| **sysbench 输出** | `$HOME/oscheckperf/tmp/vb_fileio_*.txt`     | sysbench 文本输出（临时）    |
| **fio 配置**      | `$HOME/oscheckperf/tmp/fio_*.fio`           | fio 配置文件（临时）         |
| **fio JSON**    | `$HOME/oscheckperf/tmp/fio_*_result_*.json` | fio JSON 结果（临时）      |
| **网络 JSON**     | `$HOME/oscheckperf/tmp/network_*.json`      | 网络测试结果（临时）           |
| **IO测试文件**      | `$HOME/oscheckperf/io_test/`                | sysbench/fio 创建的测试文件 |

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
192.168.1.101:user1:secret456
192.168.1.102:user1:secret456
192.168.1.103:user1:secret456
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
| jq       | 推荐 | JSON 结果解析        |
| sshpass  | 可选 | 密码认证支持           |

## 执行流程

工具的执行流程如下：

```
┌─────────────────────────────────────────────────────────────┐
│                    oscheckperf 执行流程                      │
├─────────────────────────────────────────────────────────────┤
│  1. 参数解析 (parse_args)                                   │
│     └─ 命令行参数 → 配置文件 → 默认值                        │
│                                                             │
│  2. 系统检查 (check_all)                                    │
│     ├─ 参数验证 (validate_all_parameters)                   │
│     ├─ 依赖检查 (check_dependencies)                        │
│     ├─ 权限检查 (check_permissions)                         │
│     ├─ 磁盘空间检查 (check_disk_space)                      │
│     ├─ 网络连通性检查 (check_network)                       │
│     ├─ SSH 连接检查 (check_ssh)                            │
│     └─ 残留进程清理 (cleanup_residual_processes)            │
│                                                             │
│  3. 测试执行 (run_all_selected_tests)                       │
│     ├─ CPU 测试 (run_cpu_test)                             │
│     ├─ Memory 测试 (run_memory_test)                       │
│     ├─ IO 测试 (run_io_test → sysbench/fio)                │
│     ├─ Network 测试 (run_network_test)                     │
│     ├─ Threads 测试 (run_threads_test)                     │
│     └─ Mutex 测试 (run_mutex_test)                         │
│                                                             │
│  4. 结果处理                                                │
│     ├─ 原始数据保存 (original_data_*.log)                   │
│     ├─ 解析结果保存 (data_*.log)                           │
│     └─ 报告生成 (report_benchmark_*.log)                   │
└─────────────────────────────────────────────────────────────┘
```

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

### 测试策略

1. **基准测试**：部署新服务器后立即运行，建立性能基准线
2. **定期测试**：每周/每月定期运行，监控性能变化趋势
3. **变更后测试**：系统变更（内核升级、硬件更换、配置调整）后运行
4. **对比分析**：使用多服务器对比报告功能分析性能差异
5. **测试环境**：在独立测试环境运行，避免影响生产业务
6. **测试时长**：生产环境建议使用较长的测试时长（如 60 秒以上）

### 参数调优建议

```bash
# 根据 CPU 核心数调整线程数
# CPU_THREADS=0 表示自动（建议值）
# THREADS_NUM 默认值为 cores*4

# 对于高 IOPS 场景（如 SSD）
./oscheckperf io IO_TOOL=fio FIO_NUMJOBS=8 FIO_IODEPTH=64

# 对于高带宽场景（如 RAID）
./oscheckperf io IO_TOOL=fio FIO_BS=128K FIO_NUMJOBS=4

# 数据库场景推荐（混合读写，16K 块大小）
./oscheckperf DURATION=120 IO_TOOL=fio FIO_PROFILES="randrw" FIO_BS=16K

# 内存密集型场景
./oscheckperf mem MEMORY_TOTAL_SIZE=50G MEMORY_BLOCK_SIZE=16K

# CPU 密集型场景
./oscheckperf cpu CPU_MAX_PRIME=50000
```

### 结果解读

1. **重点关注 P95/P99 延迟**：而非仅看平均值，尾部延迟更能反映真实用户体验
2. **IO 测试路径**：使用实际业务数据所在的磁盘分区，结果更具参考价值
3. **网络测试**：关注带宽、重传次数和 RTT，反映网络稳定性
4. **线程公平性**：stddev 越小表示各线程负载分布越均匀

### 运行建议

1. **多机测试**：网络压测前配置好 SSH 免密登录或准备密码认证配置
2. **资源监控**：测试期间可配合 vmstat、iostat、mpstat 等工具监控系统资源
3. **结果保存**：定期保存报告用于历史趋势分析和问题追溯

## 许可证

本项目采用 GNU General Public License v3.0 许可证。

***

## English

# oscheckperf - System Performance Benchmark Tool

**oscheckperf** is a system-level performance benchmarking tool specifically designed for database scenarios, providing one-stop server hardware performance evaluation capabilities. By automatically testing six core dimensions - CPU, Memory, Disk IO, Network Throughput, Thread Scheduling, and Mutex Lock - it helps users quickly assess server performance boundaries and identify potential bottlenecks.

**Core Value**:

- One-stop server hardware performance testing with aggregated results, enabling quick identification of cluster performance differences for efficient troubleshooting
- Facilitates database server hardware performance validation (Vastbase, openGauss, PostgreSQL, MySQL)

## Core Features

### 🚀 Comprehensive Testing Capabilities

- **One-stop Performance Evaluation**: Covers six core dimensions - CPU, Memory, Disk IO, Network Throughput, Thread Scheduling, and Mutex Lock
- **Dual-Engine IO Testing**: Supports both sysbench and fio for comprehensive IO performance evaluation
- **Multi-dimensional Network Testing**: Supports serial and full matrix network testing modes for comprehensive cluster network assessment

### 📦 Multi-scenario Deployment

- **Automatic Dependency Distribution**: Automatically compiles and distributes sysbench, sshpass to remote servers, supports cross-architecture deployment
- **Flexible Authentication**: Supports both SSH passwordless login and password authentication for different operation scenarios
- **Multi-mode Configuration**: Supports command line parameters, parameter.conf configuration file, and hybrid usage of multiple configuration methods

### 📊 Result Aggregation

- **Structured Report Generation**: Automatically generates professional performance reports with system info, test configuration, and detailed metrics
- **Multi-dimensional Comparison**: Supports multi-server comparison reports for quick performance difference and bottleneck identification
- **Rich Metrics Output**: Covers IOPS, Throughput, Latency (P95/P99), Fairness and other key performance indicators

### 🔒 Security Assurance

- **Path Security Validation**: Automatically detects and blocks IO testing on non-physical disk paths like tmpfs
- **Resource Pre-check**: Automatically verifies disk space, dependencies, permissions before testing to prevent failures
- **Process Management**: Automatically cleans up residual processes to protect production environment stability

### 🛠️ User-friendly Design

- **One-click Automated Testing**: Single command to start full workflow testing without complex configuration
- **Debug & Preview**: Supports `--debug` mode and `--dry-run` command preview mode
- **Flexible Parameter Control**: Three parameter passing methods - command line, environment variables, and configuration files

## Project Structure

```
$HOME/oscheckperf/
├── oscheckperf              # Main entry script
├── sysbench-1.0.20/         # sysbench source code compilation directory (auto downloaded by -i flag)
├── sysbench-1.0.20.tar.gz   # sysbench source code archive (auto downloaded)
├── output/                   # Test results output directory (in current directory)
│   ├── original_data_*_all_results.log  # Raw test data summary
│   ├── data_*_all_results.log           # Parsed test results
│   └── report_benchmark_*.log           # Final performance report
├── tmp/                      # Temporary files directory
│   ├── vb_fileio_*.txt       # sysbench fileio test output
│   ├── fio_*.fio             # fio configuration files
│   ├── fio_*_result_*.json   # fio JSON test results
│   └── network_*.json        # Network test JSON results
├── io_test/                  # IO test data directory
│   ├── test_file.*           # Test files created by sysbench (auto cleaned)
│   └── fio_test_file.*       # Test files created by fio (retained)
├── tools/
│   └── skill.md              # Development documentation
├── parameter.conf            # Configuration file template
└── README.md                 # Documentation (Chinese/English)
```

### Directory Structure Description

| Directory  | Purpose                                                                    | Default Path                   |
| ---------- | -------------------------------------------------------------------------- | ------------------------------ |
| `output/`  | Final reports and logs (original\_data\_*, data\_*, report\_benchmark\_\*) | `./output` (current directory) |
| `tmp/`     | Temporary files (network test results, fio JSON, sysbench output)          | `$HOME/oscheckperf/tmp`        |
| `io_test/` | IO test data files (test files created by sysbench/fio)                    | `$HOME/oscheckperf/io_test`    |

### File Type Description

| File Type           | Location                                    | Description                         | Usage                               |
| ------------------- | ------------------------------------------- | ----------------------------------- | ----------------------------------- |
| **Raw test data**   | `./output/original_data_*`                  | Summary of all raw test output      | Troubleshooting, traceability       |
| **Parsed results**  | `./output/data_*`                           | Structured parsed test results      | Data processing, secondary analysis |
| **Final report**    | `./output/report_benchmark_*`               | Formatted performance report        | Direct viewing, sharing             |
| **sysbench output** | `$HOME/oscheckperf/tmp/vb_fileio_*.txt`     | sysbench text output (temporary)    | Debugging, detailed analysis        |
| **fio config**      | `$HOME/oscheckperf/tmp/fio_*.fio`           | fio configuration files (temporary) | Debugging configuration             |
| **fio JSON**        | `$HOME/oscheckperf/tmp/fio_*_result_*.json` | fio JSON results (temporary)        | Program parsing                     |
| **Network JSON**    | `$HOME/oscheckperf/tmp/network_*.json`      | Network test results (temporary)    | Program parsing                     |
| **IO test files**   | `$HOME/oscheckperf/io_test/`                | Test files created by sysbench/fio  | Testing purpose                     |

### Path Configuration

You can modify the base directory using the `BASE_DIR` environment variable:

```bash
# Modify the base directory for all paths
export BASE_DIR=/custom/path/to/oscheckperf
./oscheckperf
```

**Environment Variable Priority**:

- `BASE_DIR` > Default value `$HOME/oscheckperf`
- `IO_PATH` > Default value `$BASE_DIR/io_test`
- `OUTPUT_DIR` > Default value `./output`

## Quick Start

### 1. Install Dependencies

```bash
# CentOS/RHEL
sudo yum install -y sysbench iperf3 jq

# Ubuntu/Debian
sudo apt-get install -y sysbench iperf3 jq
```

**Optional Dependencies**:

````bash
# fio (professional IO testing tool, recommended)
sudo yum install -y fio        # CentOS/RHEL
sudo apt-get install -y fio    # Ubuntu/Debian

# sshpass (password authentication support)
sudo yum install -y sshpass    # CentOS/RHEL

**Compilation Installation Notes**:

Compilation dependencies only need to be installed on the **compiler machine**. Other target servers **do not require** compilation tools.

```bash
# CentOS/RHEL (compiler machine only)
sudo yum install -y automake autoconf libtool gcc make

# Ubuntu/Debian (compiler machine only)
sudo apt install -y automake autoconf libtool gcc make
```

**Supported Components for Compilation**:

```bash
# Install all components (sysbench, sshpass, fio, iperf3, numactl, ethtool, jq)
./oscheckperf -i all

# Install specific component
./oscheckperf -i sysbench   # Compile and install sysbench
./oscheckperf -i sshpass    # Compile and install sshpass
./oscheckperf -i fio        # Compile and install fio
./oscheckperf -i iperf3     # Compile and install iperf3
./oscheckperf -i numactl    # Compile and install numactl
./oscheckperf -i ethtool    # Compile and install ethtool
./oscheckperf -i jq         # Compile and install jq
```

> **Note**: Before compiling ethtool, manually install libmnl dependency:
> - CentOS/RHEL: `sudo yum install -y libmnl-devel`
> - Ubuntu/Debian: `sudo apt-get install -y libmnl-dev`


### 2. Run Tests

```bash
# Run all tests (default)
./oscheckperf

# Run specific test
./oscheckperf cpu           # CPU test only
./oscheckperf mem           # Memory test only
./oscheckperf io            # IO test only
./oscheckperf network       # Network test only
./oscheckperf threads       # Threads test only
./oscheckperf mutex         # Mutex test only

# Specify test duration (default 30 seconds)
./oscheckperf DURATION=60

# Use fio for IO test (default sysbench)
./oscheckperf io IO_TOOL=fio

# Skip certain tests
./oscheckperf NETWORK_ENABLED=false

# Use configuration file
./oscheckperf -c parameter.conf

# Dry-run mode (preview commands without execution)
./oscheckperf --dry-run
```

**Subcommands**:

```bash
# Run system checks (dependencies, permissions, disk space, network)
./oscheckperf check

# Show hardware information report (CPU, memory, disk, network)
./oscheckperf hardware

# Run all tests (default)
./oscheckperf all
```

**Combine Subcommands with Parameters**:

```bash
# Specify subcommand with parameters
./oscheckperf io DURATION=60 IO_TOOL=fio

# Network test with server list
./oscheckperf network -f server_list

# Check mode with debug
./oscheckperf check --debug
```

### 3. Server Authentication Methods

#### Method 1: SSH Passwordless Login (Recommended)

**Server List File Format**:

```bash
# server_list file content
192.168.1.101
192.168.1.102
192.168.1.103
```

**Run Test**:

```bash
./oscheckperf network -f server_list
```

#### Method 2: Password Authentication (Non-passwordless)

**Install Dependencies**:

```bash
# CentOS/RHEL
sudo yum install -y sshpass

# Ubuntu/Debian
apt-get install -y sshpass
```

**Server List File Format**:

```bash
# server_list file content (format: IP:username:password)
192.168.1.101:user1:secret456
192.168.1.102:user1:secret456
192.168.1.103:user1:secret456
```

**Run Test**:

```bash
./oscheckperf network -f server_list
```

**Notes**:

- Password authentication requires `sshpass` tool
- Passwords in server list are stored in plain text, please keep them secure
- Mixed mode is supported: server list can contain both passwordless and password authenticated servers

### 4. Custom SSH Port

```bash
# Method 1: Specify port in server list
echo "192.168.1.101:2222" > server_list

# Method 2: Use environment variable
export SSH_PORT=2222
./oscheckperf network -f server_list

# Method 3: Use parameter
./oscheckperf network -f server_list SSH_PORT=2222
```

### 5. Dry-run Mode (Preview Commands)

```bash
# Preview all test commands
./oscheckperf --dry-run

# Preview specific test commands
./oscheckperf io --dry-run

# Preview network test commands
./oscheckperf network -f server_list --dry-run
```

### 6. View Reports

After testing, reports are saved in `./output` directory by default:

```bash
# View final performance report
cat output/report_benchmark_*.log

# View parsed test data
cat output/data_*_all_results.log

# View raw test data
cat output/original_data_*_all_results.log
```

## Output Metrics

### CPU Test

- **events/sec**: Events per second (higher is better)
- **Avg Latency**: Average latency in ms (lower is better)
- **Min Latency**: Minimum latency in ms (lower is better)
- **P95 Latency**: 95th percentile latency in ms (lower is better)
- **P99 Latency**: 99th percentile latency in ms (lower is better)
- **Max Latency**: Maximum latency in ms (lower is better)
- **Sum Latency**: Cumulative latency in ms (lower is better)
- **Threads fairness (events)**: Thread events fairness (avg/stddev format, lower stddev means better distribution)
- **Threads fairness (execution time)**: Thread execution time fairness

### Memory Test

- **Total operations**: Total number of operations
- **operations/sec**: Memory operations per second (higher is better)
- **Transferred**: Actual transferred data size (MiB)
- **throughput**: Memory throughput in MiB/s (higher is better)
- **Avg Latency**: Average latency in ms (lower is better)
- **Min Latency**: Minimum latency in ms (lower is better)
- **Max Latency**: Maximum latency in ms (lower is better)
- **P95 Latency**: 95th percentile latency in ms (lower is better)
- **Sum Latency**: Cumulative latency in ms (lower is better)

### IO Test (sysbench)

- **Read IOPS**: Read operations per second (higher is better)
- **Write IOPS**: Write operations per second (higher is better)
- **Total IOPS**: Total IO operations per second (higher is better)
- **fsyncs/s**: Fsync operations per second (measures synchronous write performance)
- **Read BW**: Read bandwidth in MB/s (higher is better)
- **Write BW**: Write bandwidth in MB/s (higher is better)
- **Total BW**: Total bandwidth in MB/s (higher is better)
- **Avg Latency**: Average latency in ms (lower is better)
- **Min/Max Latency**: Minimum/Maximum latency in ms (lower is better)
- **P95/P99 Latency**: 95th/99th percentile latency in ms (lower is better)
- **Threads fairness**: Thread fairness (events/execution time)

### IO Test (fio)

- **Read/Write IOPS**: Read/write operations per second (higher is better)
- **Read/Write BW**: Read/write bandwidth in MB/s (higher is better)
- **Avg Latency**: Average latency in ms (lower is better)
- **Min/Max/P95/P99 Latency**: Latency percentiles in ms (lower is better)
- **Device utilization**: Device utilization (%)
- **CPU user/system**: CPU user/system utilization (%)
- **bw\_min/bw\_max**: Minimum/maximum bandwidth (reflects bandwidth stability)
- **slat/clat**: Submit latency/Completion latency (slat is time to submit IO to device, clat is time for device to complete)
- **ctx/majf/minf**: Context switches/Major page faults/Minor page faults (reflects system resource usage)
- **iodepth\_level**: IO queue depth level (reflects IO concurrency)

### Network Test

- **Bandwidth (MB/s)**: Network bandwidth (higher is better)
- **Retrans**: TCP retransmit count (lower is better)
- **RTT(ms)**: Round Trip Time (format: average (Min: min, Max: max))
- **CPU(%)**: Sender/receiver CPU utilization (format: senderCPU%/receiverCPU%)

### Threads Test

- **total number of events**: Total number of events
- **total time**: Total duration in seconds
- **Events/sec**: Thread events per second (higher is better)
- **Avg Latency**: Average latency in ms (lower is better)
- **Min Latency**: Minimum latency in ms (lower is better)
- **Max Latency**: Maximum latency in ms (lower is better)
- **P95 Latency**: 95th percentile latency in ms (lower is better)
- **Sum Latency**: Cumulative latency in ms (lower is better)
- **Threads fairness (events)**: Thread events fairness (avg/stddev format)
- **Threads fairness (execution time)**: Thread execution time fairness

### Mutex Test

- **total number of events**: Total number of events
- **total time**: Total duration in seconds
- **Transactions**: Number of transactions (higher is better)
- **TPS**: Transactions per second (higher is better)
- **Avg Latency**: Average latency in ms (lower is better)
- **Min Latency**: Minimum latency in ms (lower is better)
- **Max Latency**: Maximum latency in ms (lower is better)
- **P95 Latency**: 95th percentile latency in ms (lower is better)
- **Sum Latency**: Cumulative latency in ms (lower is better)

### IO Benchmark Detailed Description

#### Sysbench fileio Workflow

Sysbench fileio test consists of three phases:

1. **Prepare phase**: Create test files
   - Create test files in the directory specified by `IO_PATH`
   - Default file size is 1G (adjustable via `IO_TOTAL_SIZE`)
   - Default creates 1 file (adjustable via `SYSBENCH_FILE_NUM`)
2. **Run phase**: Execute actual benchmark
   - `DURATION` parameter only controls the execution time of this phase
   - Perform random read/write operations on files created in prepare phase
   - Default test mode is `rndrw` (random read/write), adjustable via `SYSBENCH_PROFILES`
3. **Cleanup phase**: Automatically clean up test files
   - Delete all test files created in prepare phase
   - The test directory itself is not deleted

#### FIO Workflow

FIO testing uses a different approach:

1. **Configuration generation**: Generate `.fio` configuration file based on parameters
2. **Test execution**: FIO automatically creates test files during runtime
3. **File handling**: FIO does not automatically delete files after testing; the script preserves result files

#### Important Notes

**IO\_PATH parameter**:

- Default test path is `$HOME/oscheckperf/io_test`
- **Do NOT use** **`/tmp`** **directory**: On some servers, `/tmp` is tmpfs (memory filesystem), which would result in inaccurate test results (testing memory instead of disk)
- It is recommended to use the disk partition where actual business data resides for more relevant results
- Ensure sufficient available space on the target partition (at least larger than `IO_TOTAL_SIZE`)

**Common Parameters**:

##### sysbench Parameters

| Parameter              | Default    | Description                                                                  |
| ---------------------- | ---------- | ---------------------------------------------------------------------------- |
| `SYSBENCH_PROFILES`    | `rndrw`    | sysbench test modes, space-separated (seqwr/seqrewr/seqrd/rndrd/rndwr/rndrw) |
| `SYSBENCH_FILE_NUM`    | `4`        | Number of sysbench test files                                                |
| `SYSBENCH_BLOCK_SIZE`  | `16K`      | sysbench block size                                                          |
| `SYSBENCH_IO_MODE`     | `sync`     | sysbench IO mode (sync/async)                                                |
| `SYSBENCH_EXTRA_FLAGS` | `direct`   | sysbench extra flags (direct/sync)                                           |
| `SYSBENCH_THREADS`     | `4`        | sysbench threads                                                             |
| `SYSBENCH_DURATION`    | `DURATION` | sysbench IO test duration                                                    |

##### fio Parameters

| Parameter      | Default    | Description                                                                                       |
| -------------- | ---------- | ------------------------------------------------------------------------------------------------- |
| `FIO_PROFILES` | `randrw`   | fio test modes, space-separated (read/write/randread/randwrite/rw/randrw/trim/randtrim/trimwrite) |
| `FIO_BS`       | `16K`      | fio block size (optimized for database scenarios)                                                 |
| `FIO_IODEPTH`  | `32`       | fio I/O depth                                                                                     |
| `FIO_NUMJOBS`  | `4`        | fio worker threads                                                                                |
| `FIO_DIRECT`   | `1`        | fio direct I/O mode                                                                               |
| `FIO_FILE_NUM` | `4`        | Number of fio test files (simulating multi-data file scenarios)                                   |
| `FIO_IOENGINE` | `libaio`   | fio IO engine (libaio/sync/posixaio)                                                              |
| `FIO_DURATION` | `DURATION` | fio test duration                                                                                 |

##### Threads Parameters

| Parameter        | Default          | Description                                                                            |
| ---------------- | ---------------- | -------------------------------------------------------------------------------------- |
| `THREADS_NUM`    | `auto (cores*4)` | Number of threads (auto-calculated based on CPU cores when not set, formula: cores\*4) |
| `THREADS_YIELDS` | `100`            | Number of yields per thread                                                            |
| `THREADS_LOCKS`  | `4`              | Number of locks                                                                        |

##### Memory Parameters

| Parameter           | Default | Description                                     |
| ------------------- | ------- | ----------------------------------------------- |
| `MEMORY_THREADS`    | `0`     | Memory test threads, 0=auto (same as CPU cores) |
| `MEMORY_BLOCK_SIZE` | `8K`    | Memory test block size                          |
| `MEMORY_TOTAL_SIZE` | `20G`   | Total memory test size                          |
| `MEMORY_OPER`       | `read`  | Memory operation type (read/write)              |

##### Mutex Parameters

| Parameter       | Default | Description                |
| --------------- | ------- | -------------------------- |
| `MUTEX_THREADS` | `0`     | Mutex test threads, 0=auto |
| `MUTEX_NUM`     | `1024`  | Number of mutex locks      |

##### Common Parameters

| Parameter       | Default                     | Description                                         |
| --------------- | --------------------------- | --------------------------------------------------- |
| `IO_PATH`       | `$HOME/oscheckperf/io_test` | Test file directory (alternative to IO\_TEST\_PATH) |
| `IO_TOTAL_SIZE` | `1G`                        | Total test file size (common for sysbench and fio)  |
| `IO_TOOL`       | `sysbench`                  | IO test tool (sysbench/fio)                         |

##### Parameter Description

**FIO\_FILE\_NUM**:

- Sets the number of test files, default is 4
- When `FIO_FILE_NUM` is configured, each file size = `IO_TOTAL_SIZE / FIO_FILE_NUM`
- Example: `IO_TOTAL_SIZE=1G`, `FIO_FILE_NUM=4` → 256M per file

**Examples**:

```bash
# Use sysbench for random read/write test
./oscheckperf io DURATION=60 IO_TOTAL_SIZE=2G

# Use fio for sequential read test
./oscheckperf io IO_TOOL=fio FIO_PROFILES=read FIO_DURATION=60

# Specify test path
./oscheckperf io IO_PATH=/data/test
```

### Network Test

- **Bandwidth (MB/s)**: Network bandwidth (higher is better)
- **Retrans**: TCP retransmit count (lower is better)
- **RTT(ms)**: Round Trip Time (format: average (Min: min, Max: max))
- **CPU(%)**: Sender/receiver CPU utilization (format: senderCPU%/receiverCPU%)

### Threads Test

- **events/sec**: Thread events per second (higher is better)
- **latency**: Thread scheduling latency (lower is better)

### Mutex Test

- **transactions**: Number of transactions (higher is better)
- **TPS**: Transactions per second (higher is better)
- **latency**: Lock wait latency (lower is better)

## Dependencies Description

| Tool     | Required    | Purpose                            |
| -------- | ----------- | ---------------------------------- |
| sysbench | Yes         | CPU/Memory/IO/Threads/Lock testing |
| fio      | Optional    | Professional IO benchmarking       |
| iperf3   | Optional    | Network throughput testing         |
| jq       | Recommended | JSON result parsing                |
| sshpass  | Optional    | Password authentication support    |

## Execution Flow

The execution flow of oscheckperf:

```
┌─────────────────────────────────────────────────────────────┐
│                    oscheckperf Execution Flow               │
├─────────────────────────────────────────────────────────────┤
│  1. Parameter Parsing (parse_args)                          │
│     └─ Command line → Config file → Default values          │
│                                                             │
│  2. System Checks (check_all)                               │
│     ├─ Parameter validation                                 │
│     ├─ Dependency check                                    │
│     ├─ Permission check                                    │
│     ├─ Disk space check                                    │
│     ├─ Network connectivity check                          │
│     ├─ SSH connectivity check                              │
│     └─ Residual process cleanup                            │
│                                                             │
│  3. Test Execution (run_all_selected_tests)                │
│     ├─ CPU test                                            │
│     ├─ Memory test                                         │
│     ├─ IO test (sysbench/fio)                              │
│     ├─ Network test                                        │
│     ├─ Threads test                                        │
│     └─ Mutex test                                          │
│                                                             │
│  4. Result Processing                                      │
│     ├─ Raw data saving (original_data_*.log)               │
│     ├─ Parsed results saving (data_*.log)                  │
│     └─ Report generation (report_benchmark_*.log)          │
└─────────────────────────────────────────────────────────────┘
```

### Output Files Description

| File Type           | Path                            | Description                      | Usage                               |
| ------------------- | ------------------------------- | -------------------------------- | ----------------------------------- |
| **Raw test data**   | `output/original_data_*.log`    | Complete raw output of all tests | Troubleshooting, traceability       |
| **Parsed results**  | `output/data_*.log`             | Structured test results          | Data processing, secondary analysis |
| **Final report**    | `output/report_benchmark_*.log` | Formatted performance report     | Direct viewing, sharing             |
| **sysbench output** | `tmp/vb_fileio_*.txt`           | sysbench text output             | Debugging, detailed analysis        |
| **fio config**      | `tmp/fio_*.fio`                 | fio configuration files          | Debugging configuration             |
| **fio JSON**        | `tmp/fio_*_result_*.json`       | fio JSON results                 | Program parsing                     |
| **Network JSON**    | `tmp/network_*.json`            | Network test results             | Program parsing                     |

## Practical Usage Examples

### Production Environment Testing

```bash
# Complete production test (60 seconds, fio IO test)
./oscheckperf DURATION=60 IO_TOOL=fio IO_TOTAL_SIZE=10G

# Quick validation test (short duration)
./oscheckperf DURATION=10

# Run only critical tests (CPU, Memory, IO)
./oscheckperf NETWORK_ENABLED=false THREADS_ENABLED=false MUTEX_ENABLED=false
```

### Database Scenario Testing

```bash
# Vastbase/openGauss scenario (high IOPS requirement)
./oscheckperf io IO_TOOL=fio FIO_PROFILES="randrw read" FIO_NUMJOBS=8 FIO_IODEPTH=64

# MySQL scenario (mixed read/write)
./oscheckperf io IO_TOOL=sysbench SYSBENCH_PROFILES="rndrw"

# PostgreSQL scenario (high throughput)
./oscheckperf io IO_TOOL=fio FIO_PROFILES="randrw" FIO_BS=32K FIO_NUMJOBS=16
```

### Multi-server Network Testing

```bash
# Matrix mode - test all server pairs (auto batch parallel when hosts > 3)
./oscheckperf network -f all-servers NETWORK_MODE=matrix NETWORK_PARALLEL=4

# Serial mode - first host as server, others as clients (supports local/remote server)
./oscheckperf network -f all-servers NETWORK_MODE=serial
```

**Matrix Test Batch Parallel Explanation**:

- **Auto Batching**: When hosts > 3, matrix mode automatically enables batch parallel execution
- **Parallelism Calculation**: Auto-calculated as `floor(hosts / 2)`, no manual configuration needed
- **Perfect Matching Algorithm**: All hosts participate in each batch with no resource contention
- **Port Offset Mechanism**: Different host pairs in a batch use different ports (NETWORK_PORT + index)

| Hosts | Parallelism | Total Pairs | Total Batches |
|-------|-------------|-------------|---------------|
| 2 | 1 | 1 | 1 |
| 3 | 1 | 3 | 3 |
| 4 | 2 | 6 | 3 |
| 6 | 3 | 15 | 5 |
| 8 | 4 | 28 | 7 |

### Hardware Information Check

```bash
# Show hardware information only
./oscheckperf hardware

# Run system checks
./oscheckperf check

# Run checks with debug mode
./oscheckperf check --debug
```

## FAQ

### Q1: Does testing require root privileges?

**A**: Most tests do not require root privileges. The script supports running as a regular user, but `sudo` is recommended for:

- fio direct IO mode (enabled by default): requires bypassing OS cache for real disk testing
- Installing dependency packages
- It is recommended to run `./oscheckperf check` to verify system environment before testing

### Q2: Will testing delete data?

**A**: Test files are only written to the specified directory (default `$HOME/oscheckperf/io_test`) and can be automatically cleaned after testing

### Q3: How to customize IO test path?

**A**: Use the `IO_PATH` parameter: `./oscheckperf io IO_PATH=/data`

### Q4: What is the difference between NETWORK\_MODE and NETWORK\_PARALLEL?

**A**:

- **NETWORK\_MODE**: Controls the network test mode
  - `serial`: Serial mode, uses first host as server, other hosts as clients tested sequentially
    - Supports local and remote servers (auto-detected)
    - Direct execution when first host is local, no SSH overhead
  - `matrix`: Execute full matrix cross-testing (test between every pair of servers)
    - **Auto Batch Parallel**: When hosts > 3, automatically enables batch parallel execution (inspired by gpcheckperf)
    - **Parallelism**: Auto-calculated as `floor(hosts / 2)`, no manual configuration needed
    - **Intra-batch**: Multiple host pairs test simultaneously with no resource contention (perfect matching algorithm)
    - **Inter-batch**: Sequential execution to ensure test accuracy
    - **Port Offset**: Different host pairs in a batch use different ports (NETWORK_PORT + index)
- **NETWORK\_PARALLEL**: Controls the number of parallel connections for each iperf3 test, effective in all modes
  - Example: `NETWORK_PARALLEL=4` means each test uses 4 parallel connections

**Examples**:

```bash
# Serial mode with 4 parallel connections per test
./oscheckperf network -f all-servers NETWORK_MODE=serial NETWORK_PARALLEL=4

# Matrix mode with 4 parallel connections per test
./oscheckperf network -f all-servers NETWORK_MODE=matrix NETWORK_PARALLEL=4
```

## Best Practices

### Testing Strategy

1. **Baseline Testing**: Run immediately after deploying new servers to establish performance baseline
2. **Periodic Testing**: Run weekly/monthly to monitor performance trends
3. **Post-Change Testing**: Run after system changes (kernel upgrade, hardware change, configuration adjustment)
4. **Comparison Analysis**: Use multi-server comparison reports to analyze performance differences
5. **Test Environment**: Run in isolated test environment to avoid impacting production
6. **Test Duration**: Use longer duration (60+ seconds) for production environments

### Parameter Tuning Recommendations

```bash
# Adjust threads based on CPU cores
# CPU_THREADS=0 means auto (recommended)
# THREADS_NUM defaults to cores*4

# For high IOPS scenarios (e.g., SSD)
./oscheckperf io IO_TOOL=fio FIO_NUMJOBS=8 FIO_IODEPTH=64

# For high bandwidth scenarios (e.g., RAID)
./oscheckperf io IO_TOOL=fio FIO_BS=128K FIO_NUMJOBS=4

# Database scenario recommendation (mixed read/write, 16K block size)
./oscheckperf DURATION=120 IO_TOOL=fio FIO_PROFILES="randrw" FIO_BS=16K

# Memory-intensive scenarios
./oscheckperf mem MEMORY_TOTAL_SIZE=50G MEMORY_BLOCK_SIZE=16K

# CPU-intensive scenarios
./oscheckperf cpu CPU_MAX_PRIME=50000
```

### Result Interpretation

1. **Focus on P95/P99 latency**: Tail latency better reflects real user experience than average
2. **IO test path**: Use disk partition where actual business data resides for more relevant results
3. **Network test**: Focus on bandwidth, retransmit count, and RTT for network stability
4. **Thread fairness**: Lower stddev indicates better load distribution across threads

### Running Recommendations

1. **Multi-server testing**: Configure SSH passwordless login or prepare password authentication before network testing
2. **Resource monitoring**: Use vmstat, iostat, mpstat during testing to monitor system resources
3. **Result preservation**: Save reports regularly for historical trend analysis and issue tracking

## Installation Parameters

| Parameter           | Default   | Description                                  |
| ------------------- | --------- | -------------------------------------------- |
| `INSTALL_TARGET`    | Empty     | Installation target (sysbench/sshpass/fio/iperf3/numactl/ethtool/jq/oscheckperf/all) |
| `SERVERS_FILE`      | Empty     | Server list file path                        |

## Debug Parameters

| Parameter               | Default   | Description                                  |
| ----------------------- | --------- | -------------------------------------------- |
| `DEBUG`                 | `false`   | Debug mode (show detailed logs)              |
| `DRY_RUN`               | `false`   | Dry-run mode (preview commands, no execution) |
| `NO_CHECKS`             | `false`   | Skip pre-test checks                         |
| `CLEANUP`               | `true`    | Cleanup temporary files after testing        |
| `REPORT_HARDWARE_INFO`  | `true`    | Include hardware information in performance report |

## License

This project is licensed under the GNU General Public License v3.0.
````

