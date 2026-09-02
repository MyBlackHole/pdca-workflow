---
schema: pdca.asset/v1
id: ontology:entity/bcachefs-transaction
type: entity
layer: Knowledge
status: active
summary: bcachefs Transaction 实体 — btree_trans bump 内存、six 三态锁（read/intent/write+seq 乐观）与 25 种 restart 重试及 journal 并发环
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:pattern/research-diagram-methodology
    - ontology:pattern/production-ontology-scientific-gate
    - ontology:pattern/scientific-research-methodology
attributes:
  - name: btree_trans_bump_and_restart
    desc: btree_trans bump allocator（restart 即作废）与 25 种 BCH_ERR_transaction_restart 子码及 for_each_btree_key 重试宏可测
    constraint: 覆盖 struct btree_trans { mem/mem_top/mem_bytes + sorted/nr_paths + restarted/restart_count + journal_res + srcu_idx } + errcode.h:209 25 restart 子码（relock/relock_path/intent/too_many_iters/lock_node_reused/fill_mem_alloc/commit/nested 等）+ for_each_btree_key/commit_do 重试环 + BCACHEFS_INJECT_TRANSACTION_RESTARTS 注入，经时序与状态机可一图建模
    testable_signal: "运行 grep -q 'struct btree_trans' /home/black/Documents/bcachefs-tools/fs/btree/types.h 且 grep -q 'BCH_ERR_transaction_restart' /home/black/Documents/bcachefs-tools/fs/errcode.h 且 grep -q 'for_each_btree_key' /home/black/Documents/bcachefs-tools/fs/btree/iter.h 且 grep -q 'transaction' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
  - name: six_lock_three_state_and_seq
    desc: six 共享/意图/独占三态锁与 seq 乐观重取及 btree_path 层级锁快照可测
    constraint: 覆盖 util/six.h 三态（read 与 intent 兼容但 intent 互斥，intent→write 防升级死锁）+ seq 在 write 加解锁递增 + six_relock_read 乐观重取 + btree_path { l[4]{b,iter,lock_seq} + locks_want/nodes_locked } 层级快照，经 C4 L3 与状态机可一图建模
    testable_signal: "运行 grep -q 'six_lock' /home/black/Documents/bcachefs-tools/fs/util/six.h 且 grep -q 'six_relock_read' /home/black/Documents/bcachefs-tools/fs/util/six.h 且 grep -q 'btree_path' /home/black/Documents/bcachefs-tools/fs/btree/types.h 且 grep -q 'transaction' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
  - name: journal_ring_concurrency_and_srcu
    desc: journal 预约环 4 槽并发与 SRCU 读侧无锁及 journal_entry_pin flush 协同可测
    constraint: 覆盖 JOURNAL_STATE_BUF_NR=4  ringbuf + journal_res_state { cur_entry_offset/idx/buf0-3_count } + commit hook 中 journal pin + srcu_idx + transaction restart 计数，经时序与决策树可一图建模
    testable_signal: "运行 grep -q 'JOURNAL_STATE_BUF_NR' /home/black/Documents/bcachefs-tools/fs/journal/types.h 且 grep -q 'journal_res_state' /home/black/Documents/bcachefs-tools/fs/journal/types.h 且 grep -q 'srcu_idx' /home/black/Documents/bcachefs-tools/fs/btree/types.h 且 grep -q 'transaction' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
---

# Bcachefs Transaction（事务/并发）

事务以 `btree_trans`（`fs/btree/types.h:645`）为载体：`mem/mem_top/mem_bytes` 为 `bump allocator`（restart 即作废），`srcu_idx` 读侧无锁，`six_lock` 三态 + `seq` 乐观并发，`for_each_btree_key/commit_do` 宏以 25 种 `BCH_ERR_transaction_restart` 子码驱动重试，`journal_res_state` 4 槽环并发预约。定位：`src/bcachefs.rs:263` → `wrappers` → `fs/btree/`（`types.h/iter.h/update.h/errcode.h`）→ `fs/util/six.h` → `fs/journal/types.h:18`。

## C4 L3 Component — btree_trans + six + journal 环

`btree_trans`（`types.h:645`）含 `mem/mem_top`（bump 区，`restarted:16` 标记时作废）、`sorted/nr_sorted/nr_paths`（`btree_path` 数组，每 path 含 `l[4]{b,iter,lock_seq} + locks_want`）、`journal_res/disk_res`（预约）、`srcu_idx`；`six_lock`（`util/six.h:1`）含 `read/intent/write + seq`；`journal_res_state`（`journal/types.h:142`）含 `cur_entry_offset:22/idx:2/buf0-3_count:10*4`。C4 L3 图以 `trans(bump+path[]) → six(read/intent/write) → journal ring(4) → SRCU` 四层呈现。

```mermaid
graph TD
    TR["btree_trans<br/>types.h:645<br/>mem/bump + path[4]<br/>+ journal_res + srcu"]
    TR --> PATH["btree_path<br/>types.h:462<br/>l[4]{b,iter,lock_seq}<br/>locks_want"]
    PATH --> SIX["six_lock<br/>util/six.h:1<br/>read/intent/write+seq"]
    TR --> JRES["journal_res_state<br/>journal/types.h:142<br/>offset22/idx2/count10*4"]
    JRES --> RING["ring[4]<br/>JOURNAL_STATE_BUF_NR=4"]
    SIX --> SRCU["srcu_idx<br/>读侧无锁"]
    %% Source: /home/black/Documents/bcachefs-tools/fs/btree/types.h:645 + fs/util/six.h:1 + fs/journal/types.h:142 + fs/journal/types.h:18
```

Source: `/home/black/Documents/bcachefs-tools/fs/btree/types.h:645`（`btree_trans { mem/mem_top/restarted/srcu_idx/journal_res }`）+ `/home/black/Documents/bcachefs-tools/fs/util/six.h:1`（`read/intent/write + seq`）+ `/home/black/Documents/bcachefs-tools/fs/journal/types.h:142`（`journal_res_state`）+ `/home/black/Documents/bcachefs-tools/fs/journal/types.h:18`（`JOURNAL_STATE_BUF_NR=4`）

## 时序 — for_each_btree_key 重试环与 six 升降级

`for_each_btree_key`（`iter.h:962`）展开为 `do { restart_count=begin(); _ret=do; } while(err_matches(restart))`：1) `bch2_trans_begin` 清 bump mem；2) `btree_path` 遍历持 `six read/intent`；3) 若并发冲突 `six` 抛 `BCH_ERR_transaction_restart_*`（25 子码），则解锁全部 + bump 作废 + `restart_count++`；4) 指数退避后重入；5) 成功则 `bch2_trans_commit` 经 `__bch2_trans_commit`（`update.h:273`）先触发器再 btree 写。`six` 升级路径 `read → intent → write` 防死锁，`six_relock_read` 以 `seq` 乐观验证。时序图以 `begin → six read/intent → conflict?restart → write → commit` 全链呈现。

```mermaid
sequenceDiagram
    participant T as trans begin
    participant P as btree_path
    participant S as six
    participant J as journal ring
    T->>P: begin() 清 bump
    P->>S: six read/intent
    S-->>P: ok 或 restart (25码)
    alt restart
        P->>T: 解锁全部 bump 作废
        T->>T: restart_count++ 退避重试
    else ok
        P->>S: intent→write (seq++)
        S->>J: journal_res_get (ring slot)
        J-->>T: commit hook → journal pin
        T->>T: commit done
    end
    %% Source: /home/black/Documents/bcachefs-tools/fs/btree/iter.h:962 + fs/btree/types.h:645 + fs/util/six.h:1 + fs/journal/types.h:142
```

Source: `/home/black/Documents/bcachefs-tools/fs/btree/iter.h:962`（`for_each_btree_key`）+ `/home/black/Documents/bcachefs-tools/fs/btree/types.h:645` + `/home/black/Documents/bcachefs-tools/fs/util/six.h:1` + `/home/black/Documents/bcachefs-tools/fs/journal/types.h:142`

## 状态机 — trans 重试与 six 三态

`trans` 三态 `begin → running → commit_or_restart`：`running` 中任 `six` 冲突即 `restart` 回 `begin`（bump 作废）。`six` 三态 `unlocked → read ↔ intent → write`：`read` 可重入共享，`intent` 互斥防升级死锁，`write` 独占且 `seq++`，`relock` 乐观 `seq` 验证。状态机图覆盖 `restart` 往返与 `intent` 栅栏。

```mermaid
stateDiagram-v2
    [*] --> Begin: bch2_trans_begin
    Begin --> Running: bump 清零 srcu
    Running --> SixRead: six read
    SixRead --> SixIntent: 需写提升
    SixIntent --> SixWrite: intent→write seq++
    SixWrite --> Commit: 无冲突
    Running --> Restart: BCH_ERR_restart (25码)
    Restart --> Begin: 解锁+bump作废+计数++
    Commit --> [*]
    SixRead --> SixRead: six_relock_read 乐观 seq==?
    %% Source: /home/black/Documents/bcachefs-tools/fs/btree/types.h:645 + fs/util/six.h:1 + fs/errcode.h:209
```

Source: `/home/black/Documents/bcachefs-tools/fs/btree/types.h:645` + `/home/black/Documents/bcachefs-tools/fs/util/six.h:1`（`DOC` 含 `intent→write` 防死锁）+ `/home/black/Documents/bcachefs-tools/fs/errcode.h:209`（25 restart 子码）

## 决策树

```mermaid
flowchart TD
    START(["bch2_trans_begin"]) --> Q1{"for_each 遍历<br/>six read/intent?"}
    Q1 -- 冲突 --> R["restart 25码<br/>relock/intent/too_many_iters<br/>commit/nested"]
    R --> Q2{"restart_count < 阈值?"}
    Q2 -- 是 --> START
    Q2 -- 否 --> E1["too_many_iters → 报错"]
    Q1 -- 成功 --> Q3{"需 commit?"}
    Q3 -- 否 --> OK1["只读 done"]
    Q3 -- 是 --> Q4{"journal 环有空槽?<br/>bufN_count < MAX"}
    Q4 -- 否 --> R
    Q4 -- 是 --> C["__bch2_trans_commit<br/>pin + accounting subbuf"]
    C --> OK2(["commit ok"])
    %% Source: /home/black/Documents/bcachefs-tools/fs/btree/iter.h:962 + fs/errcode.h:209 + fs/journal/types.h:142
```

Source: `/home/black/Documents/bcachefs-tools/fs/btree/iter.h:962` + `/home/black/Documents/bcachefs-tools/fs/errcode.h:209` + `/home/black/Documents/bcachefs-tools/fs/journal/types.h:142`

## 正例

```c
// 正例：for_each + commit 闭环，six 升降有序
for_each_btree_key(trans, iter, BTREE_ID_extents, pos, BTREE_ITER_slots, k, ret) {
    // 持有 six read/intent 遍历
    bch2_trans_update(trans, iter, &new_key);
}
ret = bch2_trans_commit(trans, NULL, NULL, BCH_TRANS_COMMIT_no_enospc);
// 验证：restart 时 bump 作废不泄漏，commit 时 journal ring 不溢出
```

命中：`restart` 与 `bump` 配对，`six intent→write` 有序，`journal_res_state` 不超 `COUNT_MAX`。

## 反例

```c
// 反例1：trans 间复用 bump 内存
// 错：restart 后仍用旧 mem 指针，UAF
// 正确：restart 即作废 mem/mem_top，begin 重新分配

// 反例2：跳过 intent 直接 write
// 错：read→write 升级与并发 read 死锁
// 正确：read→intent(互斥栅栏)→write
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' ontology/entity/bcachefs-transaction.md` ≥3
- **溯源门禁**：`grep -c 'Source:' ontology/entity/bcachefs-transaction.md` ≥3 且每图含 `Source: /home/black/Documents/bcachefs-tools/... file:line`
- **正文门禁**：`wc -l ontology/entity/bcachefs-transaction.md` ≥80 且含 `决策树` `正例` `反例` `门禁`
- **属性门禁**：`attributes` ≥3 且每条 `testable_signal` 含 `grep -q` 且双源可回归
- **本体校验**：`python3 scripts/ontology-validate.py` 0 issues 且 `islands:0`
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:entity/bcachefs-transaction --out /tmp/x.py` 可产
- **Gate 门禁**：`python3 scripts/production-ontology-gate.py --node ontology:entity/bcachefs-transaction` GATE OK

Source: `/home/black/Documents/bcachefs-tools/fs/btree/types.h:645` + `/home/black/Documents/bcachefs-tools/fs/util/six.h:1` + `/home/black/Documents/bcachefs-tools/fs/errcode.h:209`
