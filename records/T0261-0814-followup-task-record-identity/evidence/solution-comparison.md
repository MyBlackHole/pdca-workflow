# Identity Repair Options and Candidate Draft

## 方案比较

| 方案 | 能解决 task ID 冲突 | 能解决 event identity 分裂 | 历史兼容 | 主要代价 |
|---|---:|---:|---:|---|
| A. 仅全局原子 task ID 分配器 | 是（所有入口接入时） | 否 | 不触碰历史 | 需要把 instruction-driven 创建统一收口到命令/API |
| B. 仅以不可变 record identity 为主键 | 否 | 是（创建时即分配且禁止 fallback 时） | 需定义旧事件映射 | task parent/dependency 和展示编号仍歧义 |
| C. A+B 组合（推荐） | 是 | 是 | 通过显式兼容 receipt 读取，不改写旧事件 | 改动面较大，但问题边界完整 |

## 推荐的 P0 边界

1. 新增唯一的 task 创建入口：在仓库级锁内执行 ID reservation、slug 检查、task + clarification + PRD 创建；triage、to-tickets、Act follow-up 和 promotion 全部调用它。
2. task 创建时同时分配不可变 `meta.record`，事件系统不再回退到 `task.id`；缺 record 时审计应记录到独立 quarantine/system stream 或只报告错误，不能制造第二个 record identity。
3. `pdca-doctor` / workflow validation 增加全局 task ID + slug 唯一性检查，以及 event path == payload record_id 检查。
4. 历史 5 条 mismatch 不重写。若必须聚合，新增带源/目标、原因、操作者、时间和事件 digest 列表的 immutable relocation/alias receipt；没有 receipt 的 mismatch 始终 fail closed。

## Paired test / development seam 草案

| 先写的测试 | 最小实现 seam |
|---|---|
| 50 个并发进程从所有任务创建入口申请 ID，结果唯一且连续/可解释 | `scripts/task_identity.py`：仓库锁 + reservation + create-only transaction |
| 新任务创建后立即存在不可变 `meta.record`；重复写不同值被拒绝 | task schema / creation service；`scripts/pdca_core.py` identity invariant |
| Do→Check 在缺 record 时不向 `records/<task-id>/flow-events` 写事件 | `scripts/flow_audit.py`：移除 task.id fallback，改为 fail-closed/quarantine |
| event path 与 payload 不一致时 projection 拒绝；有合法 relocation receipt 时按 receipt 读取但不改写源事件 | `scripts/flow_issues.py` + 新 relocation schema |
| promotion 既有并发测试继续通过 | `tests/test_flow_issues.py` 回归保护 |
| doctor 对当前 23 个冲突 ID、5 个 mismatch 给出机器可读诊断 | `scripts/pdca-doctor.py` / `scripts/validate-workflow.py` |

## 配对基线、成功阈值与观察窗

- 冻结基线：23 个冲突 task ID / 47 个不同 slug / 49 份物理 task；5 个 event path mismatch；当前全量 projection 因 mismatch 失败。
- 开发期阈值：所有创建入口的并发测试 0 重复；所有新任务出生即有 record；所有新事件 path invariant 100% 通过；旧 5 条 mismatch 只能由显式 receipt 解释，不能自动修复。
- 真实观察窗：改动上线后 14 天或至少 20 个真实新任务（取较晚者），按创建入口分层统计 duplicate ID、missing record、path mismatch、创建失败和人工恢复次数。
- 回滚条件：统一入口导致任务无法创建、锁产生不可接受阻塞、或历史兼容实现需要改写不可变事件。回滚代码时保留新增诊断和原始事件。

## Improvement Candidate 草案（不正式登记）

- 标题：统一 task/record identity 创建事务并取消 audit fallback
- 来源：T0261 真实并发复现、真实 transition 路径复现、T0252 历史 occurrence invariant
- 预期收益：消除新 task ID 冲突和 record 双身份，恢复 flow backlog 可投影性，使真实使用记录可被持续评估。
- 风险：跨入口迁移不完整会形成双轨；历史兼容规则过宽会掩盖篡改。
- 授权状态：draft only；进入开发前必须另建 PDCA task 并获得最终确认。
