# oscheckperf MCP Server

为Trae平台提供集群系统性能基准测试能力的MCP Server。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Trae 平台                              │
│                                                          │
│  ┌───────────────────────────────────────────────────┐    │
│  │              Agent (AI执行主体)                    │    │
│  │                                                  │
│  │  ┌─────────────────────┐  ┌──────────────────┐   │    │
│  │  │     Skill           │  │     MCP Client   │   │    │
│  │  │ (操作指南/专业知识)  │  │   (工具调用协议) │   │    │
│  │  └──────────┬──────────┘  └────────┬─────────┘   │    │
│  └─────────────│───────────────────────│─────────────┘    │
│                │                       │                    │
│                ▼                       ▼                    │
│  ┌───────────────────────────────────────────────────┐    │
│  │         oscheckperf MCP Server                    │    │
│  │  ┌─────────────────────────────────────────┐     │    │
│  │  │ 1. 参数发现模块  2. 命令执行模块         │     │    │
│  │  │    (自动发现)     (调用oscheckperf)       │     │    │
│  │  └─────────────────────────────────────────┘     │    │
│  └───────────────────────────────────────────────────┘    │
│                                                          │
│  ┌───────────────────────────────────────────────────┐    │
│  │              oscheckperf (独立工具)               │    │
│  │    (可独立迭代升级，MCP自动识别新功能)            │    │
│  └───────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 特性

- ✅ 自动发现oscheckperf功能（通过解析--help）
- ✅ 支持集群多节点测试
- ✅ 与oscheckperf完全解耦
- ✅ 支持HTTP和标准MCP协议
- ✅ 支持自然语言交互

## 快速开始

### 方式一：HTTP协议（推荐用于调试）

```bash
cd /path/to/oscheckperf
python3 mcp/mcp_server_http.py
```

**在Trae中配置**：

```json
{
  "mcpServers": {
    "oscheckperf": {
      "url": "http://172.16.53.128:8080/mcp"
    }
  }
}
```

### 方式二：项目级配置（自动发现）

创建 `.trae/mcp.json` 文件：

```json
{
  "oscheckperf": {
    "command": "python3",
    "args": ["/home/vastbase/project/script/oscheckperf/mcp/mcp_server.py"]
  }
}
```

然后在Trae平台开启"启用项目级MCP"开关。

### 验证配置

```bash
# 检查健康状态（HTTP版本）
curl http://172.16.53.128:8080/mcp/health
# 预期输出: {"status": "healthy", "capabilities_loaded": true}

# 获取工具列表
curl http://172.16.53.128:8080/mcp/tools
# 预期输出: {"tools": [...]}
```

## 目录结构

```
mcp/
├── README.md         # 本文件
├── SKILL.md          # Trae Skill描述
├── mcp_server.py     # 标准MCP Server（stdio）
├── mcp_server_http.py # HTTP版本（用于调试）
├── discover.py       # 参数发现模块
├── executor.py       # 命令执行模块
└── config.py         # 配置
```

## API接口（HTTP版本）

### GET /mcp/health
健康检查

### GET /mcp/tools
返回可用工具列表（JSON格式）

### POST /mcp/invoke
调用工具执行测试（简化格式）

**请求示例**：
```json
{
  "tool": "oscheckperf",
  "args": {
    "servers": ["192.168.1.101", "192.168.1.102"],
    "command": "cpu",
    "duration": 60
  }
}
```

**响应示例**：
```json
{
  "success": true,
  "command": "./oscheckperf -f servers.txt cpu DURATION=60",
  "report_path": "./output/report_benchmark_xxx.log",
  "stdout": "测试输出..."
}
```

## 与oscheckperf的解耦设计

1. **调用方式解耦**：MCP通过命令行调用oscheckperf
2. **参数发现解耦**：通过--help动态发现，无需硬编码
3. **升级解耦**：oscheckperf独立升级，MCP自动适配
4. **错误隔离**：oscheckperf错误不影响MCP服务

## 支持的测试命令

| 命令 | 说明 |
|------|------|
| cpu | CPU性能测试 |
| mem | 内存性能测试 |
| io | IO性能测试 |
| network | 网络性能测试 |
| thread | 线程测试 |
| mutex | 互斥锁测试 |
| all | 所有测试 |
| check | 系统检查 |
| hardware | 硬件信息报告 |

## 支持的参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| servers | array | - | 服务器IP地址列表（必填） |
| command | string | all | 测试命令 |
| duration | integer | 60 | 测试时长（秒） |
| io_tool | string | sysbench | IO测试工具（sysbench/fio） |
| output_dir | string | ./output | 输出目录 |

## Skill导入说明

### Skill必须人工导入吗？

**是的，Skill需要手动导入**。原因如下：

| 组件 | 职责 | 是否自动导入 |
|------|------|--------------|
| **MCP Server** | 提供工具调用能力 | ✅ 通过配置自动连接 |
| **Skill (SKILL.md)** | 提供使用场景和操作指南 | ❌ 需要手动导入 |

### Skill导入步骤

1. 在Trae平台进入"技能管理"页面
2. 点击"导入技能"或"上传技能"
3. 选择 `mcp/SKILL.md` 文件
4. 完成导入

## 日志

日志文件位于 `./logs/mcp_server.log`

## 许可证

MIT License