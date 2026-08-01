# T0176 验证 journal seq 溢出边界行为与 seq_blacklist 适用性

## 问题

T0168 review-report D2【中】声称：journal.rs:1177-1179 `JOURNAL_SEQ_MAX`
时返回 -2 硬失败，"bcachefs seq_blacklist.c 支持环回，长期运行可靠性受限"。

对照本地 bcachefs 源码（约束 1/2）后该描述与事实不符：

1. **溢出不是环回，是 emergency read-only**：
   - `JOURNAL_SEQ_MAX = (1ULL << 56) - 1`（journal/types.h:18）
   - journal.c:442 `journal_cur_seq(j) >= JOURNAL_SEQ_MAX` → 日志 + 
     `bch2_fs_emergency_read_only_locked()` + 返回 `journal_shutdown`
   - 项目 journal.rs:1184 `new_seq > JOURNAL_SEQ_MAX → -2` 与此语义
     **一致**（-2 即 shutdown 类错误，上层 engine 硬失败返回用户）
2. **seq_blacklist 与环回无关**：
   - seq_blacklist.c:13-38 注释阐明用途：崩溃后**忽略比最新成功 journal
     条目更新的 bset**（btree 节点先落盘、journal 未写时的乱序场景）
   - 项目为 write-ahead 顺序：journal 先落盘（engine.rs:731 注释）→
     checkpoint 才 flush btree pins（engine.rs:757）→ 才推进 last_seq
   - **bset 永不先于 journal 落盘 → blacklist 场景不存在**（约束 12：
     不为不存在的场景引入逻辑）

## 目标

验证型任务：
1. 补单测：seq 达 JOURNAL_SEQ_MAX 时 `bch2_journal_flush` 返回 -2
   （溢出边界行为锁定，对齐 journal.c:442 emergency read-only 语义）
2. 验证恢复路径对超上限 seq 的拒绝（journal.rs:1349 已有 -5 检查，
   补覆盖确认）
3. 结论文档化：D2 描述为误读；溢出硬失败是对齐行为；seq_blacklist
   因 write-ahead 顺序不适用（含 bcachefs 源码锚点）

## 用户故事

作为存储引擎开发者，我希望明确 journal seq 溢出与 blacklist 的真实
语义边界，以便：确认现有 -2 行为与 bcachefs 对齐（无需修改）、确认
无需引入 seq_blacklist 机制、并用单测锁定该边界防止未来回归。

## 方案

1. **单测 `flush_returns_shutdown_at_seq_overflow`**（journal.rs tests 模块）：
   - 构造 `journal::default()`，将 `j.seq` 置为 `JOURNAL_SEQ_MAX`
     （`(1<<56)-1`），同步 ring[idx].seq（1007 行 assert_eq 依赖）
   - 调用 `bch2_journal_flush` 断言返回 -2
   - 断言 seq 未推进（仍为 JOURNAL_SEQ_MAX，写入被拒绝）
2. **恢复路径覆盖**：journal.rs:1349 已有 `seq > JOURNAL_SEQ_MAX → -5`
   检查；查该分支是否有测试覆盖，无则补一行断言用例
3. **结论沉淀**：conclusion.md 记录 D2 纠误 + 源码锚点
   （journal.c:442、seq_blacklist.c:13-38、journal/types.h:18）

## 实现决策

| 决策 | 选择 | 依据 |
|------|------|------|
| 溢出行为 | 保持 -2，不实现环回 | journal.c:442 emergency read-only；约束 12 不引入自有逻辑 |
| seq_blacklist | 不实现，文档化不适用 | write-ahead 顺序下 bset 不先于 journal 落盘（seq_blacklist.c:13-38 前提不成立） |
| 单测构造 | 直接置 seq=JOURNAL_SEQ_MAX | default() 后改 seq + ring[idx].seq，disk_sb=null 走内存镜像路径，无文件依赖 |
| 约束 10 | 修改前已对照 bcachefs 源码 | journal.c:442/init.c:499/seq_blacklist.c 全文确认 |

## 验收标准

- [ ] AC-1: 单测验证 flush 在 seq=JOURNAL_SEQ_MAX 时返回 -2 且 seq 不推进
- [ ] AC-2: 恢复路径超上限 seq 拒绝（-5）有测试覆盖
- [ ] AC-3: conclusion 记录 D2 纠误 + 锚点（journal.c:442/seq_blacklist.c:13-38/types.h:18），明确 blacklist 不适用结论
- [ ] AC-4: 全量回归绿（lib 173+1 + 集成 10）+ fmt 干净
- [ ] AC-5: 与 bcachefs 语义对齐（溢出=emergency read-only，非环回）

## 范围外

- 实现 seq 环回机制（bcachefs 无此语义）
- 实现 seq_blacklist（write-ahead 顺序下无适用场景；若未来引入
  btree 先于 journal 落盘路径再评估）
- 其他 D 项（D3 trigger/D4 verify/D5/D6）

## 备注

- 提交：feature-commit-format（【F-T0176】…，0.1.0 -> 0.1.0）
- parent: T0168（D2 纠误）
- 纯测试 + 文档任务，无引擎行为修改（若验证发现行为与对齐不符
  则升级为 bugfix 任务）
