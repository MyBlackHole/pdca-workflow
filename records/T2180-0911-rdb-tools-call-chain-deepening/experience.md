---
schema: pdca.asset/v1
id: T2180-0911-rdb-tools-call-chain-deepening-experience
type: experience
source_record: T2180-0911-rdb-tools-call-chain-deepening
created_at: 2026-09-11T16:28:46+08:00
---

# T2180 经验：从工具百科纠偏到逐操作调用链

## 情境

`rdb-tools-design` 已有工具清单和若干入口信息，但用户认为不够详细。最初把“详细”理解为每个工具独立百科页；用户随后明确纠偏：“我需要的是调用链”，并指定 `rdb-feature-design` 为表达参照。

## 失效方向

- 以“23 个工具各建一页”为主目标，会增加文档数量，却不保证调用链深度。
- 通用栏目、工具简介和每工具强制配图不能替代真实分发分支、跨进程交接和返回路径。
- 仅写“命令 → 某函数 → 结果”的单行摘要，无法支持需求定位、协议核对或故障分析。

旧方向在实质产物形成前被中止并回滚，没有混入最终 skill。

## 有效做法

- 先读取用户指定的相邻 skill，提取其调用链颗粒度，再把它转换成当前仓库的可验证契约。
- 以外部可触发操作为最小单元，完整枚举 subcommand、method、opcode、ioctl 和 ABI 分支。
- 沿真实 `path:symbol` 展开“入口 → 请求/解析 → dispatch → 核心 → 边界/对端 → 返回/清理”。
- 跨进程协议按发送端和接收端双向核对；证据缺失时明确写“未闭合”。
- 保留现有 `SKILL.md + 00-index + 五份版本地图` 的渐进披露结构，避免为了页数而拆分信息。

## 证据摘要

- 23 个工具均可从总索引定位到逐操作调用链。
- 公开操作清单覆盖 fs-cli 21 个 method、fsbackup_tools 5 个命令、afs-cli 18 个 method、19 个 MT 请求、19 个 persistent opcode、XBSA 16 个 ABI、SBT2 11 个 API、DMSBT 13 个 ABI。
- 文档包含 138 个去重 `path:symbol` 锚点，53 个 Markdown 引用通过检查。
- `quick_validate.py`、工具索引、公开操作、协议双端、占位扫描与产品源码零变更检查全部通过。
- `afs-cli` 的 6 个网络 method 在当前基线没有找到接收端，保留“未闭合”状态。

证据清单见 `evidence/manifest.jsonl`；主要条目为 `t2180-call-chain-index-v1`、`t2180-fs-call-chains-v1`、`t2180-rpc-rdbcomm-call-chains-v1`、`t2180-s3-xbsa-call-chains-v1` 和 `t2180-validation-report-v1`。

## 可复用结论

当用户要求“调用链”时，完整性的衡量对象应是可触发操作及其真实分支，而不是工具数量或页面数量。结构设计只负责可发现性；链路质量必须由源码符号、协议双端、返回路径和明确边界共同证明。

## 适用边界

本轮是 6.2.0.0 静态源码级结论，不证明部署环境中的端口、权限、TLS、内核兼容或第三方数据库集成可用性。外部仓库和运行环境缺失时，不应把合理推测写成已闭合调用链。
