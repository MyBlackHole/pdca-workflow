# T0189 Review Report

## 审查范围

- 变更：`crates/subvol/src/engine.rs`（+405 行，仅 1 文件）。
- 意图：discard 边界与 open-bucket 回收保护（PRD AC-1..AC-6）。

## 标准轴发现

| 严重度 | 位置 | 发现 | 建议 |
|---|---|---|---|
| LOW | engine.rs:494 `rw_devs: BTreeSet::from([0])` | 初始 rw 设备硬编码 [0]，与设备几何耦合；engine 当前单设备（dev 0）语义下正确 | 未来多设备时按 sb 成员初始化 |
| LOW | `open_bucket`/`close_open_bucket` | 不校验位置合法性（可对无效位置 open）；bcachefs 中 open 只发生在分配流程 | 属性模型已限制 free 桶不 open；可保持现状 |
| 无 | 锁序 | reclaim/discard：fs → open_buckets → rw_devs；open/close/set 独立锁；无反向序，无死锁 | — |
| 无 | 错误码 | reclaim -16（live reference）、discard -11（未就绪轮转）、allocate -1（设备无效）与既有体系一致 | — |

Rust 清单：unsafe 无新增；Poisoned 全处理；测试为行为验证。

## 规范轴发现（对照 PRD AC）

- AC-2：open（-16/-11）+ 设备可写（-16/-11）+ journal boundary（既有 -11）+ need_discard 检查（既有）全部实现并有定向测试。
- AC-3：reclaim 同事务（基线）+ fault 注入（TransactionRestart 重试、JournalWrite 无半状态 + 恢复一致）测试。
- AC-4：worker 对 open/not_rw 桶轮转不阻塞就绪桶；EEXIST/EAGAIN 基线；process restart 属性 op。
- AC-5：属性模型（open 参与）：open 桶不转 free、need_discard 桶不消失、每 op 后 verify_bucket_indexes。
- AC-6：workspace lib 200/200 + 集成 10/10 + fmt 通过。

## 风险评级

- Blocking = 0。全部通过门禁。
