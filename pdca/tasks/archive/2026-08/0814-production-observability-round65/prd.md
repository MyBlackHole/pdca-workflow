# T0251 Round 65：生产级结构化日志与海量备份可观测基线

## 问题陈述

海量文件增量和 TREE 断点续传已经有部分实现，但运行状态、跳过原因、checkpoint 恢复、失败阶段和提交结果散落在 `std::cerr` 文本中。生产环境无法稳定按 request/transfer/event 关联日志，也无法把日志写入轮转文件；直接替换输出又会破坏现有脚本和人工排障习惯。

## 目标

提供统一的线程安全日志模块，默认保持现有人类可读 stderr 语义，同时支持 JSON Lines 文件 sink、级别过滤、组件和事件字段；迁移 client/server 启停、传输结果、增量决策、checkpoint 批次和错误边界等关键事件。日志路径必须是可控开销、可禁用低级别事件且不泄露 token/路径内容以外的敏感数据。

## 方案

1. `src/log.hpp/.cpp` 提供 level、format、sink、timestamp、线程安全写入、JSON escape 和 bounded message handling。
2. `client_config_t` / `agent_config_t` 增加 `--log-level`、`--log-format text|json`、`--log-file`；默认 stderr + text，文件采用 append 与 size-based rotation。
3. 入口初始化/关闭 logger；优先迁移 backupctl/agent 的 lifecycle、transfer summary/error、metadata-cache、checkpoint flush/recovery 事件，保留业务 stdout 和既有关键 stderr 文本。
4. 用 unit 和 integration 验证 JSON 合法性、并发整行性、级别过滤、轮转、敏感字段不落盘、增量/续传事件可关联。

## Seam 分析

- 日志公共接口：`tests/unit.cpp` -> `src/log.cpp`
- CLI 配置：`tests/logging_integration.sh` -> `src/client_config.cpp` / `src/agent_config.cpp`
- transfer 事件：`tests/logging_integration.sh` -> `src/backupctl.cpp` / `src/backup_agent.cpp`
- checkpoint/incremental 事件：`tests/tls_tree_checkpoint_resume_integration.sh` -> `src/backupctl.cpp`

### 声明的测试接缝

- seam: tests/unit.cpp -> src/log.cpp
- seam: tests/logging_integration.sh -> src/client_config.cpp / src/agent_config.cpp
- seam: tests/logging_integration.sh -> src/backupctl.cpp / src/backup_agent.cpp
- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/backupctl.cpp

## 验收标准

- [ ] AC-1: Make/CMake TLS ON/OFF 构建包含日志模块，无新增 warning；默认 text stderr 与现有关键测试输出兼容。
- [ ] AC-2: `--log-level`、`--log-format`、`--log-file` 在 client/server 生效；JSONL 每行可解析，包含 timestamp、level、component、event、message。
- [ ] AC-3: 并发写入不产生交错行；文件 sink 支持原子 append、size rotation、关闭/重开和权限 `0600`；日志失败不阻塞备份主流程。
- [ ] AC-4: 增量扫描、跳过/发送决策、TREE checkpoint flush/recovery、提交成功/失败和错误阶段均有稳定 event 名称与关联字段；token 不得出现在日志中。
- [ ] AC-5: 100k 文件 metadata/incremental 与 TREE checkpoint 回归通过，日志开启时吞吐下降不超过 5%（同机三次中位数），并报告日志 bytes 与 CPU/RSS。
- [ ] AC-6: unit、logging integration、TLS/非 TLS tree/checkpoint regression、style check 和 CMake/Make 全量回归通过。

## 实现决策

- 默认 text 输出保护现有运维脚本；JSON 仅显式启用。
- 日志字段采用白名单 API，不接受任意格式化 token；路径只在 debug 或显式 event 中记录，认证 token 永不记录。
- 日志 I/O 使用独立 mutex 和短临界区；文件轮转在写入临界区内完成，失败降级到 stderr 并设置一次性内部告警。
- 本轮不重构 checkpoint 存储结构；其海量内存占用和真正可寻址恢复作为后续独立优化。

## 范围外

- 不改变 RSP/1 wire protocol、resume offset 语义或 metadata cache schema。
- 不把现有 ad-hoc metrics 一次性全部改成日志；本轮只迁移关键生命周期和诊断事件。
- 不将 no-mmap LMDB runtime 纳入本轮，继续由 T0250 跟进。
