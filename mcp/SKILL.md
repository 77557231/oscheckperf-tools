---
name: "cluster-benchmark"
description: "使用oscheckperf进行集群系统性能基准测试"
tool_name: "oscheckperf"
---

# 集群系统压测技能

## 使用场景
- 需要对多节点服务器集群进行系统性能测试
- 需要评估服务器硬件性能边界
- 需要生成标准化性能报告
- 需要对比多服务器性能差异
- 需要快速获取服务器硬件信息

## 工具调用说明

### 工具定位
本技能通过**MCP协议**调用`oscheckperf`工具：
- **工具名称**: oscheckperf
- **调用方式**: MCP协议
- **执行位置**: MCP Server所在服务器
- **工具发现**: MCP自动查找并发现功能

### MCP自动发现机制
MCP Server启动时会自动：
1. 在系统PATH中查找oscheckperf可执行文件
2. 如果未找到，检查配置文件中指定的路径
3. 执行`oscheckperf --help`解析可用命令和参数
4. 将工具能力注册到Trae平台

## 操作流程
1. Agent识别用户需求（如"测试服务器性能"）
2. Agent读取本Skill，了解使用场景和参数要求
3. Agent构建工具调用请求，通过MCP协议发送给MCP Server
4. MCP Server执行oscheckperf命令
5. MCP Server返回测试结果给Agent
6. Agent整理结果并回复用户

## 可用命令
| 命令 | 说明 |
|------|------|
| cpu | CPU性能测试 |
| mem | 内存性能测试 |
| io | IO性能测试 |
| network | 网络性能测试 |
| thread | 线程测试 |
| mutex | 互斥锁测试 |
| all | 所有测试（默认） |
| check | 系统环境检查 |
| hardware | 硬件信息报告 |

## 可用参数
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| servers | array | - | 服务器IP地址列表，**必填** |
| command | string | all | 测试命令 |
| duration | integer | 60 | 测试时长（秒） |
| io_tool | string | sysbench | IO测试工具（sysbench/fio） |
| output_dir | string | ./output | 输出目录路径 |

## 调用示例

### 示例1：集群CPU测试
```yaml
工具调用: oscheckperf
参数:
  servers: ["192.168.1.101", "192.168.1.102", "192.168.1.103"]
  command: "cpu"
  duration: 60
```

### 示例2：集群IO测试（使用fio）
```yaml
工具调用: oscheckperf
参数:
  servers: ["192.168.1.101", "192.168.1.102"]
  command: "io"
  duration: 120
  io_tool: "fio"
```

### 示例3：单服务器硬件信息
```yaml
工具调用: oscheckperf
参数:
  servers: ["192.168.1.101"]
  command: "hardware"
```

### 示例4：运行所有测试
```yaml
工具调用: oscheckperf
参数:
  servers: ["192.168.1.101"]
  command: "all"
  duration: 60
```

## 输出结果格式

测试完成后，MCP Server返回的结果包含：
- `success`: 布尔值，测试是否成功
- `command`: 实际执行的命令
- `report_path`: 测试报告文件路径
- `stdout`: 命令标准输出（可选）
- `stderr`: 命令错误输出（可选）
- `error`: 错误信息（仅失败时）

## 注意事项
- **SSH认证**: 确保目标服务器已配置SSH免密登录或MCP Server已配置认证信息
- **依赖安装**: 确保目标服务器已安装oscheckperf所需依赖
- **执行时机**: 建议在业务低峰期执行测试，避免影响业务
- **网络可达**: 确保MCP Server能够访问所有目标服务器

## 技能与MCP的关系

| 组件 | 角色 | 说明 |
|------|------|------|
| **Skill（本文件）** | 说明书 | 告诉Agent"什么时候用"和"怎么用" |
| **MCP Server** | 执行者 | 实际调用oscheckperf并返回结果 |
| **oscheckperf** | 工具 | 执行具体的性能测试 |

**重要**: 本技能必须通过MCP调用，不能单独使用。Skill定义了调用方式和参数，MCP负责实际执行。