---
schema: pdca.asset/v1
id: ontology:domain/rdb-config-optim-roadmap
type: domain
layer: Knowledge
status: active
summary: rdb config 优化路线图（T0386）
domain:
- ontology:domain/rdb-config
relations:
  specializes:
  - ontology:domain/rdb-config
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# rdb config 优化路线图（T0386）

> 来源：T0386 分析结论（confirmed）。本文件为可复用知识，沉淀 rdb config 当前架构状态与后续优化候选。

## 当前架构状态（可复用基线）
- C 侧 rdb config 已完成「注册表化」重构（T3978/T3979 集中 schema + T0361/T3981 严格解析 fail-closed）。
- 生产代码 100% 经 `sec_get_*` 注册表 API；`sec_resolve_*` 散点调用为 0；`config_get_*` 仅测试使用。
- 常量/env 名单一来源（`libs/cfg_path.h`、`rdb-config.h`）。
- Go(oss) `chooseStr=cli>env>file>def` 与 C 4 层模型语义一致（F1 已对齐）。

## 优化候选（按优先级）
| 优先级 | 项 | 根因 | 方案要点 |
|--------|----|------|----------|
| 高 | F9 证书路径校验 | `sec_walk_str` 直接返回未校验 `getenv` 指针（`RPC_TLS_CERT_DIR`）→ 证书路径注入 | **经决策不实施**：部署假设环境变量可信（与 T0369 F9 原结论一致），维持现状；若未来威胁模型变化（env 不可信）再立项 |
| 中 | fail-closed 一致性 | `mtls_enabled` 直接赋值无 `<0` 校验，与 audit/auth 启动期硬失败不一致 | **已实施（D2/T0388）**：rdbcommd-main 新增 mtls 硬失败，与 audit/auth 一致 |
| 中 | F7 配置源统一 | dmsbtex 仍读 `sbt-config.conf`，与 `rdb.conf` 并存 | 合并到 `rdb.conf` 统一源（跨模块专项，保留旧部署过渡） |
| 低 | 注册表覆盖度扩展 | 无 INT 型注册参数，端口/超时/并发等结构类参数各模块自读 | 按模块增量纳入并复用严格解析（防重演 atoi/截断类隐患） |
| 低 | 显式初始化入口 | `rdb_auto_init` constructor 无法禁用/指定路径/错误处理 | **已实施（D2/T0388）**：移除 constructor，改为 10 处最外层入口显式 `init_config`（fail-closed） |
| 否决 | 性能缓存 | 热路径读已解析的 `server_opts` 字段，不重复调用 `sec_get_*` | 无证据需缓存，不优化 |

## 复用指引
- 后续 rdb config 相关任务（配置增删、跨语言一致性、安全专项）先查本路线图与 `audit-findings.md`。
- 红线：跨语言 4 层模型一致性（env > 工具段 > 全局段 > 默认）；安全开关 fail-closed 必须正确处理非法 `-1`（维持开启或启动期硬失败，不得静默降级）。
- 结论：rdb config 当前无需紧急优化；上述为高/中/低增量项，建议后续 development 子任务立项。
