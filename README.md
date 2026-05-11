# 系统性能基准测试工具

一个系统级性能基准测试工具，支持全面的 CPU、内存、IO、网络、线程、互斥锁性能测试，帮助评估服务器硬件性能边界。适用于 Vastbase、openGauss、PostgreSQL、MySQL 等数据库及各类应用场景的上线前性能检查，助力发现系统潜在性能问题。

## 特性

- ✅ **一键执行**：自动化完成 CPU/内存/IO/网络/线程/锁测试，无需手动配置
- ✅ **最小依赖**：基础模式仅需 sysbench，其他工具（fio、iperf3）为可选
- ✅ **多工具支持**：IO 测试支持 sysbench 和 fio，可根据需要选择
- ✅ **多服务器支持**：网络压测支持多 IP 配置（支持免密和密码认证），可测试集群网络性能
- ✅ **密码认证**：支持服务器列表中配置用户名和密码，无需 SSH 免密登录
- ✅ **配置文件支持**：支持通过配置文件管理所有参数，便于批量配置和版本控制
- ✅ **详细报告**：生成结构化测试报告，包含系统信息、测试配置和详细指标
- ✅ **远程分发**：自动编译和分发 sysbench、sshpass 到远程服务器，支持跨架构部署
- ✅ **多种网络模式**：支持串行、并行和矩阵网络测试模式
- ✅ **结果分析**：生成多服务器对比报告，便于性能分析和问题定位
- ✅ **安全增强**：路径安全验证、磁盘空间检查、进程管理优化，保护生产环境
- ✅ **调试模式**：支持 `--debug` 和 `--dry-run` 模式，便于问题定位和命令预览

## 项目结构

```
$HOME/oscheckperf/
├── oscheckperf              # 主入口脚本
├── sysbench-1.0.20/         # sysbench 源码编译目录（-i 参数自动下载编译）
├── sysbench-1.0.20.tar.gz   # sysbench 源码压缩包（自动下载）
├── output/                   # 测试结果输出目录（当前目录下）
│   ├── original_data_*_all_results.log  # 原始测试数据汇总
│   ├── data_*_all_results.log           # 解析后的测试结果
│   └── report_benchmark_*.log           # 最终性能报告
├── tmp/                      # 临时文件目录
│   ├── vb_fileio_*.txt       # sysbench fileio 测试输出
│   ├── fio_*.fio             # fio 配置文件
│   ├── fio_*_result_*.json   # fio JSON 测试结果
│   └── network_*.json        # 网络测试 JSON 结果
├── io_test/                  # IO测试数据目录
│   ├── test_file.*           # sysbench 创建的测试文件（测试后自动清理）
│   └── fio_test_file.*       # fio 创建的测试文件（保留）
├── tools/
│   └── skill.md              # 开发规范文档
├── parameter.conf            # 配置文件模板
├── README.md                 # 中文文档（默认）
└── README.en.md              # 英文文档
```

### 目录结构说明

| 目录         | 用途                                                     | 默认路径                        |
| ---------- | ------------------------------------------------------ | --------------------------- |
| `output/`  | 最终报告和日志（original\_data\*, data\*, report\_benchmark\*） | `./output`（当前目录）            |
| `tmp/`     | 临时文件（网络测试结果、fio JSON、sysbench 输出）                      | `$HOME/oscheckperf/tmp`     |
| `io_test/` | IO测试数据文件（sysbench/fio 创建的测试文件）                         | `$HOME/oscheckperf/io_test` |

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

可以通过环境变量 `BASE_DIR` 统一修改基础目录：

```bash
# 修改所有路径的基础目录
export BASE_DIR=/custom/path/to/oscheckperf
./oscheckperf
```

**环境变量优先级**：

- `BASE_DIR` > 默认值 `$HOME/oscheckperf`
- `IO_PATH` > 默认值 `$BASE_DIR/io_test`
- `OUTPUT_DIR` > 默认值 `./output`

## 快速开始

### 1. 安装依赖

#### 方式一：原生命令安装

**基础依赖（必选）**：

```bash
# CentOS/RHEL
sudo yum install -y sysbench

# Ubuntu/Debian
sudo apt-get install -y sysbench
```

**完整依赖（推荐）**：

```bash
# CentOS/RHEL
sudo yum install -y sysbench fio iperf3 jq

# Ubuntu/Debian
sudo apt-get install -y sysbench fio iperf3 jq
```

#### 方式二：oscheckperf 自动安装

本工具支持自动编译和分发 sysbench、sshpass 到远程服务器，降低最小额外安装影响。

**单机安装**：

```bash
# 安装所有组件（sysbench + sshpass + oscheckperf）
./oscheckperf -i

# 安装指定组件
./oscheckperf -i sysbench    # 仅安装 sysbench
./oscheckperf -i sshpass     # 仅安装 sshpass
./oscheckperf -i all         # 安装所有组件（默认）
```

**多机器安装**：

```bash
# 从服务器列表文件安装
./oscheckperf -i -f all-servers

# 直接指定 IP 列表安装
./oscheckperf -i -f "192.168.1.101 192.168.1.102 192.168.1.103"
```

**安装逻辑**：

| 场景                               | 行为                  |
| -------------------------------- | ------------------- |
| 本机在 IP 列表中且无 `$HOME/oscheckperf` | 先编译，再分发             |
| 本机有 `$HOME/oscheckperf` 目录       | 跳过编译，直接打包分发         |
| 本机不在 IP 列表中                      | 所有服务器都需要分发（从本地已有目录） |
| SCP 分发                           | 自动排除本机器 IP          |

**优势**：

- 无需在远程服务器上安装编译工具和依赖
- 统一的 sysbench 版本，确保测试结果的一致性
- 降低对远程服务器的影响，无需修改系统配置
- 自动配置环境变量，使用方便

### 2. 运行测试

#### 方式一：不使用配置文件（直接运行）

**基本用法**：

```bash
# 运行所有测试（默认）
./oscheckperf
```

**命令行参数覆盖**：

```bash
# 覆盖测试时长
./oscheckperf DURATION=60

# 覆盖 CPU 最大素数
./oscheckperf CPU_MAX_PRIME=10000

# 禁用特定测试
./oscheckperf MEMORY_ENABLED=false NETWORK_ENABLED=false

# 使用 fio 进行 IO 测试
./oscheckperf IO_TOOL=fio
```

**运行特定测试（子命令）**：

```bash
# 运行 CPU 测试
./oscheckperf cpu

# 运行内存测试
./oscheckperf mem

# 运行 IO 测试
./oscheckperf io

# 运行网络测试（矩阵模式）
./oscheckperf network -f all-servers NETWORK_MODE=matrix

# 运行线程测试
./oscheckperf thread

# 运行互斥锁测试
./oscheckperf mutex

# 运行系统检查（依赖项、权限、磁盘空间、网络）
./oscheckperf check

# 运行所有测试（默认）
./oscheckperf all
```

**子命令与参数组合使用**：

```bash
# 运行 CPU 测试并指定参数
./oscheckperf cpu DURATION=20 CPU_MAX_PRIME=10000

# 运行 IO 测试并使用 fio
./oscheckperf io IO_TOOL=fio FIO_DURATION=30

# 运行网络测试并指定服务器列表
./oscheckperf network -f "192.168.1.101 192.168.1.102" NETWORK_MODE=parallel
```

#### 方式二：使用配置文件

**创建配置文件**（`parameter.conf`）：

```bash
# 通用参数
DURATION=60              # 测试时长（秒）
OUTPUT_DIR=./output      # 输出目录
IO_TOOL=sysbench         # IO测试工具（sysbench/fio）
SSH_PORT=22              # SSH连接端口

# 测试模块开关
CPU_ENABLED=true         # 启用CPU测试
MEMORY_ENABLED=true      # 启用内存测试
IO_ENABLED=true          # 启用IO测试
NETWORK_ENABLED=true     # 启用网络测试
THREADS_ENABLED=true     # 启用线程测试
MUTEX_ENABLED=true       # 启用互斥锁测试

# CPU测试参数
CPU_THREADS=0            # CPU线程数，0=自动
CPU_MAX_PRIME=20000      # CPU测试最大素数

# IO测试参数
IO_TOTAL_SIZE=1G         # IO测试文件总大小
IO_PATH=$HOME/oscheckperf/io_test  # IO测试路径

# 网络测试参数
NETWORK_MODE=matrix      # 网络测试模式（serial/parallel/matrix）
NETWORK_PARALLEL=1       # 并行连接数
```

**使用配置文件运行**：

```bash
# 使用配置文件运行测试
./oscheckperf -p parameter.conf

# 命令行参数会覆盖配置文件中的值
./oscheckperf -p parameter.conf DURATION=30 IO_TOOL=fio
```

### 3. 服务器认证方式

#### 方式一：SSH 免密登录（推荐）

**配置步骤**：

```bash
# 生成 SSH 密钥（如果还没有）
ssh-keygen -t rsa -b 4096

# 将公钥分发到目标服务器
ssh-copy-id root@192.168.1.101
ssh-copy-id root@192.168.1.102
```

**服务器列表文件格式**：

```bash
# all-servers 文件内容
192.168.1.101
192.168.1.102
192.168.1.103
```

**运行测试**：

```bash
./oscheckperf network -f all-servers
```

#### 方式二：密码认证（非免密）

**安装依赖**：

```bash
# CentOS/RHEL
sudo yum install -y sshpass

# Ubuntu/Debian
sudo apt-get install -y sshpass
```

**服务器列表文件格式**：

```bash
# all-servers 文件内容（格式：IP:用户名:密码）
192.168.1.101:root:password123
192.168.1.102:admin:myp@ssword
192.168.1.103:user:secret456
```

**运行测试**：

```bash
./oscheckperf network -f all-servers
```

**注意事项**：

- 密码认证需要安装 `sshpass` 工具
- 服务器列表中的密码会以明文形式存储，请妥善保管
- 支持混合模式：服务器列表中可以同时包含免密和密码认证的服务器

### 4. 自定义 SSH 端口

**方式一：命令行参数**

```bash
# 指定SSH端口为2222
./oscheckperf -f servers.txt SSH_PORT=2222

# 网络测试指定SSH端口
./oscheckperf network -f servers.txt SSH_PORT=2222
```

**方式二：配置文件**

在 `parameter.conf` 中添加：

```bash
SSH_PORT=2222
```

**方式三：环境变量**

```bash
export SSH_PORT=2222
./oscheckperf -f servers.txt
```

**优先级**：命令行参数 > 配置文件 > 环境变量 > 默认值（22）

### 5. 干运行模式（预览命令）

```bash
# 使用 --dry-run 参数预览将要执行的命令
./oscheckperf --dry-run

# 配合其他参数使用
./oscheckperf io --dry-run IO_TOOL=fio FIO_PROFILES="read write"
```

### 6. 查看报告

```bash
ls -lh output/
cat output/report_benchmark_*.log
```

## 输出指标说明

### CPU 测试

- **events/sec**：每秒执行事件数（越高越好）
- **avg latency**：平均延迟（越低越好）
- **P95/P99 latency**：95/99 百分位延迟（越低越好）
- **Fairness (events)**：线程公平性指标，表示各线程间事件分布的均衡程度（格式为 avg/stddev，stddev 越小表示分布越均匀）

### 内存测试

- **operations/sec**：每秒内存操作数（越高越好）
- **throughput**：内存吞吐量 MB/s（越高越好）
- **avg latency**：平均延迟（越低越好）
- **P95 latency**：95 百分位延迟（越低越好）

### IO 测试

- **IOPS**：每秒 IO 操作数（越高越好）
- **Bandwidth**：吞吐量 MB/s（越高越好）
- **Latency**：延迟（越低越好）
- **fsyncs/s**：每秒 fsync 操作数（仅 sysbench，衡量同步写入性能）
- **Min/Max/P95/P99 latency**：最小/最大/95/99 百分位延迟（仅 fio）
- **Device utilization**：设备利用率（仅 fio）
- **CPU user/system**：CPU 用户态/系统态利用率（仅 fio）
- **bw\_min/bw\_max**：最小/最大带宽（仅 fio，反映带宽稳定性）
- **slat/clat**：提交延迟/完成延迟（仅 fio，slat 指 IO 提交到设备的时间，clat 指设备处理完成的时间）
- **ctx/majf/minf**：上下文切换/主要页错误/次要页错误（仅 fio，反映系统资源使用情况）
- **iodepth\_level**：IO 队列深度级别（仅 fio，反映 IO 并发程度）

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

### sysbench 参数

| 参数                     | 默认值        | 说明                                                        |
| ---------------------- | ---------- | --------------------------------------------------------- |
| `SYSBENCH_PROFILES`    | `rndrw`    | sysbench 测试模式，空格分隔（seqwr/seqrewr/seqrd/rndrd/rndwr/rndrw） |
| `SYSBENCH_FILE_NUM`    | `4`        | sysbench 测试文件数量                                           |
| `SYSBENCH_BLOCK_SIZE`  | `16K`      | sysbench 块大小                                              |
| `SYSBENCH_IO_MODE`     | `sync`     | sysbench IO 模式（sync/async）                                |
| `SYSBENCH_EXTRA_FLAGS` | `direct`   | sysbench 额外标志（direct/sync）                                |
| `SYSBENCH_THREADS`     | `4`        | sysbench 线程数                                              |
| `SYSBENCH_DURATION`    | `DURATION` | sysbench IO 测试时长                                          |

### fio 参数

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

### Threads 参数

| 参数              | 默认值              | 说明                                    |
| --------------- | ---------------- | ------------------------------------- |
| `THREADS_NUM`   | `auto (cores*4)` | 线程数（未设置时自动根据 CPU 核心数计算，公式：cores*4） |
| `THREADS_YIELDS`| `100`            | 每个线程的 yield 次数                           |
| `THREADS_LOCKS` | `4`              | 锁数量                                    |

### 通用参数

| 参数              | 默认值                         | 说明                         |
| --------------- | --------------------------- | -------------------------- |
| `IO_PATH`       | `$HOME/oscheckperf/io_test` | 测试文件目录（替代IO\_TEST\_PATH）   |
| `IO_TOTAL_SIZE` | `1G`                        | 测试文件总大小（sysbench 和 fio 通用） |
| `IO_TOOL`       | `sysbench`                  | IO 测试工具（sysbench/fio）      |

### 参数说明

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
- **CPU(%)**：发送端/接收端 CPU 利用率（格式：发送端CPU%/接收端CPU%）

### 线程测试

- **events/sec**：每秒线程事件数（越高越好）
- **latency**：线程调度延迟（越低越好）

### 互斥锁测试

- **transactions**：事务数（越高越好）
- **TPS**：每秒事务数（越高越好）
- **latency**：锁等待延迟（越低越好）

### pgbench 测试

- **TPS**：每秒事务数（越高越好）
- **latency average**：平均延迟（越低越好）

## 依赖工具说明

| 工具       | 必选 | 用途               | 安装命令                      |
| -------- | -- | ---------------- | ------------------------- |
| sysbench | 是  | CPU/内存/IO/线程/锁测试 | `yum install -y sysbench` |
| fio      | 可选 | 专业 IO 压测         | `yum install -y fio`      |
| iperf3   | 可选 | 网络吞吐测试           | `yum install -y iperf3`   |
| jq       | 推荐 | JSON 结果解析        | `yum install -y jq`       |
| sshpass  | 可选 | 密码认证支持           | `yum install -y sshpass`  |

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

### Q4: NETWORK_MODE 和 NETWORK_PARALLEL 参数的区别是什么？

**A**:

- **NETWORK_MODE**：控制多个客户端测试的执行方式
  - `serial`：逐个执行客户端测试，一个完成后再开始下一个
  - `parallel`：同时执行所有客户端测试
  - `matrix`：执行全矩阵交叉测试（每对服务器之间都进行测试）
- **NETWORK_PARALLEL**：控制每个 iperf3 测试的并行连接数，在所有模式下都生效
  - 例如：`NETWORK_PARALLEL=4` 表示每个测试使用 4 个并行连接

**示例**：

```bash
# 串行执行，每个测试使用 4 个并行连接
./oscheckperf network -f all-servers NETWORK_MODE=serial NETWORK_PARALLEL=4

# 并行执行，每个测试使用 4 个并行连接
./oscheckperf network -f all-servers NETWORK_MODE=parallel NETWORK_PARALLEL=4
```

## 最佳实践

1. **测试环境**：在独立测试环境运行，避免影响生产业务
2. **测试时长**：生产环境建议使用较长的测试时长（如 60 秒以上）
3. **IO 测试路径**：使用实际业务数据所在的磁盘分区，结果更具参考价值
4. **历史对比**：定期运行测试，保存报告用于历史趋势分析
5. **多机测试**：网络压测前配置好 SSH 免密登录或准备密码认证配置
6. **结果解读**：重点关注 P95/P99 延迟，而非仅看平均值
7. **参数调整**：根据服务器配置调整测试参数，如线程数应与 CPU 核心数匹配

## 许可证

本项目采用 GNU General Public License v3.0 许可证。
