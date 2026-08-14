# Identity Reproduction Results

## R1：普通 scan→create 竞态（正例）

在隔离临时目录中，用两个线程同时调用当前 `_next_task_id()`，在读取后用 barrier 对齐，再分别创建不同 slug。观察结果：

```json
{"schema":"t0261.ordinary-scan-create/v1","created_ids":["T9001","T9001"],"creators":[{"chosen_id":"T9001","slug":"0814-concurrent-a"},{"chosen_id":"T9001","slug":"0814-concurrent-b"}],"duplicate_created":true}
```

独立 oracle 是两个实际创建出的不同目录及其 `task.json`；不是模型自评。首轮因测试进程缺少 `PYTHONPATH=scripts` 而报 `ModuleNotFoundError: pdca_core`，修正测试环境后复现成功；首轮错误不计产品证据。

## R2：promotion 并发保护（负对照）

运行仓库现有并发测试：

```text
python3 -m unittest tests.test_flow_issues.FlowIssueCliTest.test_concurrent_promotion_creates_one_task_even_with_different_requested_slugs
Ran 1 test in 1.621s
OK
```

该测试覆盖 `_promotion_lock()` 下的去重、task ID 分配和 `O_EXCL` 创建，只产生一个任务。它拒绝了“所有创建路径都必然冲突”的过宽假设，并提供可复用的安全实现对照。

## R3：真实 transition 路径的 record identity 分裂（正例）

在 `/tmp/t0261-identity-probe.mUinDo` 构造隔离 PDCA root，复制正式 schema 和 cutover receipt，通过仓库真实命令 `scripts/transition-phase.py --root <temp>` 对同一 Do task 执行两次 Do→Check：

1. `meta.record` 缺失：门禁以 `RECORD_MISSING` / `CONVERGENCE_MAP_MISSING` 拒绝，审计先写出 4 条 `records/T9002/flow-events/` 事件。
2. 仅补上 `meta.record=T9002-0814-identity-probe`：门禁以 evidence / convergence 缺失拒绝，审计又写出 4 条 `records/T9002-0814-identity-probe/flow-events/` 事件。

```json
{
  "schema": "t0261.real-transition-path/v1",
  "first_exit": 1,
  "second_exit": 1,
  "short_identity_events": 4,
  "full_identity_events": 4,
  "split_identity": true
}
```

独立 oracle 是两个 record 目录内的 8 个 schema-valid、create-only occurrence 文件。两次转换都退出 1，证明问题发生在非阻断 audit 写入阶段，并不要求门禁被绕过。

## R4：collision 与 mismatch 的负对照

- 23 个冲突 task ID 中，只有 `T0252` 出现 path mismatch。
- 另外 22 个冲突 ID 没有 mismatch。
- 因而 task ID collision 会让 task/parent/dependency 引用产生歧义，但它单独不能生成“目录 record 与载荷 record 不同”的事件。

## 假设判定

| 假设 | 结论 | 支持 / 反证 |
|---|---|---|
| H1 普通 Plan 创建缺少统一原子 ID 分配，并发会选择同一 next ID | supported（机制与可复现性）；历史每个冲突的具体操作者 inconclusive | R1 实际创建重复 ID；路径枚举未发现共享锁；R2 证明加锁路径不复现 |
| H2 promotion 路径是安全负对照 | supported | 仓库并发测试通过；锁覆盖 scan→create |
| H3 mismatch 源于 record 身份生命周期变化 / 事件写入后归并 | partial | R3 证明当前真实路径可将同一 task 的事件写入两个身份；T0252 时间序列一致；具体历史移动命令无 receipt，故该部分 inconclusive |
| H4 task ID collision 是放大器而非 mismatch 充分原因 | supported | 22/23 冲突 ID 无 mismatch |

## 记录机制有效性审查

本轮记录不是“白记录”：create-only 事件保存了原始 payload `record_id`，projection 的严格 path invariant 因而发现了 5 条历史异常；若只保留汇总计数或允许自动改写 payload，这个问题会消失在统计中。缺陷也同样明确：audit 在 record 未建立时采用可变 fallback identity，后续又缺乏显式 relocation receipt，使聚合器无法区分合法归并和篡改/误放。
