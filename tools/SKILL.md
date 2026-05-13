# 项目规则

## 1. 项目定位

oscheckperf是为Vastbase、PostgreSQL、MySQL等数据库设计的系统级压测工具，采用单脚本集成设计，一键完成 CPU、内存、IO、网络、线程、互斥锁等全维度性能测试，逐渐丰富扩展功能，丰富细化硬件性能指标。

## 2. 核心代码规范

- **单脚本集成**：所有功能必须集成于单一脚本 `oscheckperf`，函数模块化设计
- **命名规范**：函数名下划线分隔小写（如 `run_cpu_test`）；配置参数大写加下划线（如 `DURATION`、`IO_TOOL`）
- **注释规范**：代码注释统一使用英文
- **参数处理**：支持短选项（`-c`/`-o`/`-d`/`-h`）和 `KEY=VALUE` 赋值，优先级：命令行参数 > 配置文件 > 默认值
- **严禁硬编码**： 单机和多机函数复用性，减少冗余代码
- **代码更新同步**：新增参数必须同步更新 `--help`、`parameter.conf`、`README.md`（中英文内容）

## 3. 文档更新规范

新功能必须同步更新 `README.md`，该文件包含中英文两部分内容，结构完全一致。涉及开发规范调整时同步更新 `SKILL.md`。

### README 同步内容

| 同步内容 | 说明 |
|---------|------|
| 项目结构/目录说明/文件类型 | 目录结构和文件描述表格 |
| 路径配置 | 环境变量和路径设置 |
| FAQ | 常见问题解答 |
| 最佳实践 | 使用指南 |
| 功能/参数说明 | 详细功能和参数说明表格 |

### README 格式规范

- **文件结构**：`README.md` 采用中英文混合格式，中文在前，英文在后，通过 `## English` 锚点分隔
- **顶部链接**：`中文 | [English](#english)` 便于快速切换
- **同步要求**：中文内容更新时，英文内容必须同步更新，保持结构和内容一致

## 4. 输出与报告规范

- **目录**：输出存 `output/`，临时文件存 `$BASE_DIR/tmp/`，IO 测试文件存 `io_test/`，路径支持 `BASE_DIR` 环境变量配置
- **三类文件**：
  - `data_*`：执行命令结果输出
  - `report_benchmark_*`：结果汇总对比，表格形式
  - `original_data_*`：完整原始日志数据

## 5. 开发流程与版本管理

- **标准流程**：需求分析 → 代码实现 → 测试验证（使用 `test-script` 和 `test-validate-logs` Skill）→ 文档更新 → Tag 发布（使用 `push-all` Skill）
- **Tag 格式**：`vX.X.X - 简短功能描述`，下方编号列出变更点，末尾补充验证结果，必须使用中文

## 6. Trae Skills 规范

项目使用 `.trae/skills/` 下的 Skill 替代原 `tools/` 脚本：
- `push-all`：代码提交、版本号更新、Tag 生成、多仓库推送，替代原 `oscheckperf_push_all.sh`
- `test-script`：自动化测试（语法/帮助/模块功能/参数覆盖），替代原 `oscheckperf_test.sh`
- `test-validate-logs`：日志错误分析（绿色通过/黄色警告/红色错误），替代原 `oscheckperf_validate_logs.sh`
- `cluster-deploy-test`：多服务器部署测试
- `cluster-benchmark-mcp`：集群性能基准测试

严禁使用原生 git 命令直接提交，统一通过 `push-all` Skill 提交。

## 7. 语言与最佳实践

- **语言规范**：中文文档（README.md、所有SKILL.md）用中文；README.md 包含中英文两部分，英文部分与中文内容结构一致；代码注释用英文；agent思考时必须使用中文。
- **严禁行为**：修改默认目录结构、代码变更后不同步文档

