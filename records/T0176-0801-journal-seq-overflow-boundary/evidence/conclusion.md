# T0176 journal seq 溢出边界行为验证 — 结论

## 任务

T0168 review-report D2【中】声称 seq 达 `JOURNAL_SEQ_MAX` 硬失败、
"bcachefs seq_blacklist.c 支持环回，长期运行可靠性受限"。本任务对照
本地 bcachefs 源码验证真实语义边界，补单测锁定，并修正 D2 描述。

## 收敛结论

**结论：通过**（convergence valid=true，5/5 AC 全达标）

| AC | 结果 | 证据 |
|----|------|------|
| AC-1 flush 溢出返回 -2 且 seq 不推进 | 通过（新增单测 ok） | e1（diff:92 行）/ e2 |
| AC-2 恢复路径超上限 seq 拒绝（-5）有覆盖 | 通过（新增单测 ok） | e1 / e2 |
| AC-3 D2 纠误 + 锚点文档化 | 通过（本 conclusion） | e3（本文件） |
| AC-4 全量回归绿 + fmt | 通过（lib 175/175、集成 10/10、fmt 干净） | e1 / e2 |
| AC-5 bcachefs 语义对齐 | 通过（journal.c:442/types.h:18/seq_blacklist.c:13-38） | e2 |

## 验证记录

- 新增 `flush_returns_shutdown_at_seq_overflow`：seq=JOURNAL_SEQ_MAX 时
  flush 返回 -2、seq 不推进（同步 ring[1].seq 满足 old_buf 断言）
- 新增 `journal_read_rejects_seq_above_max`：设备 bucket 写 seq=
  JOURNAL_SEQ_MAX+1 记录，read 返回 -5、cur_seq 不推进
- lib 全量 175/175（原 173 + 新 2）；集成 10/10（105.18s）
- `cargo fmt --check -p subvol` 干净

## D2 纠误（关键结论）

1. **溢出不是环回，是 emergency read-only**：
   - `JOURNAL_SEQ_MAX = (1ULL << 56) - 1`（fs/journal/types.h:18），
     u64 空间下溢出几乎不可达（2^56 ≈ 7.2e16 条记录），仅防御性边界，
     永远无需环回
   - journal.c:442 `journal_cur_seq >= JOURNAL_SEQ_MAX` → 日志 +
     `bch2_fs_emergency_read_only_locked()` + 返回 `journal_shutdown`
   - 项目 journal.rs:1184 `new_seq > JOURNAL_SEQ_MAX → -2` 与此语义一致
     （-2 即 shutdown 类错误）——**现状正确，无需修改**
2. **seq_blacklist 与环回无关**：
   - seq_blacklist.c:13-38 用途：崩溃后**忽略比最新成功 journal 条目
     更新的 bset**（btree 节点先落盘、journal 未写时的乱序保护）
   - 项目为 write-ahead 顺序：journal 先落盘（engine.rs:731 注释）→
     checkpoint 才 flush btree pins（engine.rs:757）→ 才推进 last_seq
   - **bset 永不先于 journal 落盘 → blacklist 场景不存在**，不引入
     （约束 12：不为不存在的场景添加逻辑路径）
3. **review-report D2 描述修正**：原"seq 环回"表述为误读；实际为
   "溢出 → shutdown（对齐）+ blacklist 不适用（write-ahead 保证）"，
   长期运行可靠性不受限

## 语义锚点

- fs/journal/types.h:18（JOURNAL_SEQ_MAX 定义）
- fs/journal/journal.c:442（溢出 emergency read-only）、init.c:499
- fs/journal/seq_blacklist.c:13-38（blacklist 用途注释）
- 项目恢复拒绝超上限 seq：journal.rs:1349（与 bcachefs read.c 同条件）
- 约束 10：本任务修改前对照 bcachefs 源码（journal.c/init.c/
  seq_blacklist.c 全文确认），无凭记忆改动

## 备注

- 提交：8c75f24【F-T0176】engine: 新增 journal seq 溢出边界测试锁定
  shutdown 语义（D2 纠误）, 0.1.0 -> 0.1.0
- 纯测试 + 文档任务，无引擎行为修改；若未来引入 btree 先于 journal
  落盘路径（如独立 writeback），需重新评估 seq_blacklist
- 单一格式版本，无兼容性影响
