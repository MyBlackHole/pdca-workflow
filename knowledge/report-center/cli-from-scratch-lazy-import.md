# CLI 从零重写 + 惰性导入 + Keyset 分页（T0217 沉淀）

来源：T0217 cdm-data-cli（report-center 需求 140）。`records/T0217-0804-cdm-data-cli/conclusion.md`

## 背景

CDM 报表中心需要 collection-service 经既有 rpc 工具通道在 CDM 主机执行固定采集
命令（`cdm-data-cli`）输出 JSONL 入库。远端 `origin/feature/F-140-report-center`
存在历史实现，但用户 grill 决策**从零重写**——历史实现未达契约要求，参考成本高于
重写成本。重写采用「惰性导入 + 依赖注入 + 分层」架构，在无生产依赖（flask/aio）
的开发环境完成 69 项单测 + 冒烟全绿。

## 可复用模式

### 1. 惰性导入 + 构造器注入使核心层可测

- 生产依赖（flask、aio ORM 模型）仅在 `_load_models` 等入口惰性 import。
- 采集器经 `SourceReader` 抽象 + 构造器注入，测试环境注入内存 FakeReader。
- 效果：核心/编排/topic/cli 层零生产依赖，`pytest --noconftest` 直接跑，无需容器。
- 代价：生产字段/装配只能在 CDM 主机核对（登记为已知限制，不静默）。

### 2. Keyset（seek）分页替代 offset 深分页

- 用上一页末行 `{entity_key, task_run_key}` 作下一页起点，无 offset 全表扫描。
- task 增量按 `task_run_key >= cursor` 过滤（含等值，避免跳页），复合排序一次
  `order_by(*exprs)` 一次性传入（分开调用会互相覆盖，属隐蔽 bug）。
- page_size 固定不接收任意值（子方案契约：500/1000/500），防大页拖垮 rpc 通道。

### 3. ISO 时间解析的 3.6 兼容

- `datetime.fromisoformat` 在 3.6 对带 `+08:00` 后缀的字符串可能抛 ValueError，
  需要 `strptime` 回退：先 `fromisoformat`，失败再 `strptime(fmt, '%Y-%m-%dT%H:%M:%S%z')`。

### 4. 结构化错误码（stderr）替代裸退出

- 未知参数/非法值 → `RPC_ARGUMENT_INVALID`（对齐主方案 §6.4 第 3 类）。
- 未知 Topic → `TOPIC_UNSUPPORTED`；凭据失败 → `CLI_AUTH_FAILED`；
  未装配运行态 → `CLI_EXEC_FAILED`。CLI 侧尽量单进程、可管道解析、可脚本断言。

## 流程改进（供后续任务复用）

- do 阶段 task.json 被外部工具改回 `phase:plan` 时，用 `transition-receipts/` 的
  before/after digest 核对，补写 `states` 时间戳后重跑 `transition-phase --to do` 恢复。
- 确认/裁决记录必须用 `append-confirmation.py`（真实时钟 + schema 校验），
  手写 `at` 时间戳会被 schema 拒绝。
