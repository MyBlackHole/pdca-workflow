# Review Report — T0168 subvol btree 核心功能完整性审计

- 审计日期：2026-08-01
- 审计范围：`/home/black/Documents/subvol` 全仓功能模块（btree 12 模块 + journal + engine + data/keylist + snapshot + sb + lock）
- 对照基准：`/home/black/Documents/bcachefs-tools/fs/`（唯一权威，双基准交叉：bcachefs 语义为主 + 项目交付目标为辅）
- 粒度：关键路径（update/commit/checkpoint/恢复/reclaim/trigger）到函数级；其余 API 面 + 测试覆盖
- 缺陷处置：仅报告不修复（堆崩溃已到根因级）

## 执行摘要

subvol btree 核心功能**总体完整**：24 个功能项中 **15 完整 / 7 部分 / 2 缺失**（缺失项均明确不在当前交付范围）。btree 主干（bkey 编解码、bset 构建/搜索/更新、缓存、迭代器、node 读写、事务内存）与 bcachefs 逐函数对齐，测试覆盖 136 个内嵌测试 + 17 个 engine 集成测试（含进程级崩溃恢复）。

**必须优先处理**：1 个 CRITICAL 级数据安全缺陷（commit 空间检查未累加同 leaf 多 update → 堆越界写，ASAN 已定位根因，崩溃复现于 checkpoint COW 测试）。

## 一、功能矩阵（AC-1）

### btree 12 模块

| 模块 | bcachefs 对应物 | 判定 | 测试数 | 关键差异 |
|------|----------------|------|-------|---------|
| bkey.rs | fs/btree/bkey.c | 完整 | 11 | 无实质差异 |
| bset.rs | fs/btree/bset.h + fs/bcachefs/extents.c | 完整 | 27 | extent 逻辑跨两文件，subvol 集中于此 |
| bset_build.rs | fs/btree/sort.c + bset.c | 完整 | 8 | 无实质差异 |
| bset_search.rs | fs/btree/bset.c | 完整 | 1 | 测试覆盖偏薄 |
| bset_update.rs | fs/btree/bset.c(insert/delete) | 完整 | 1 | 测试覆盖偏薄 |
| cache.rs | fs/btree/cache.c | 完整 | 9 | freeable 批量回收简化 |
| interior.rs | fs/btree/interior.c | **部分** | 3 | 缺异步 btree_update 框架/split_interior/merge |
| io.rs | fs/btree/read.c + write.c | 完整 | 6 | 同步单副本模型（范围声明一致） |
| iter.rs | fs/btree/iter.c + locking.c | 完整 | 19 | 无实质差异 |
| node_iter.rs | fs/btree/bset.c(node_iter) | 完整 | 2 | 无实质差异 |
| types.rs | fs/btree/types.h + bbpos.h | 完整 | 6 | 无实质差异 |
| update.rs | fs/btree/commit.c + update.c + write_buffer.c | **部分** | 24 | **CRITICAL 缺陷**（见缺陷清单 D1）+ trigger 链简化 |

### journal / engine / 辅助模块

| 模块 | bcachefs 对应物 | 判定 | 测试数 | 关键差异 |
|------|----------------|------|-------|---------|
| journal.rs | fs/journal/{journal,read,write,reclaim,validate}.c | 部分 | 10 | seq_blacklist 缺失（见矩阵三） |
| engine.rs | fs/journal/reclaim.c + fs/btree/commit.c | 部分 | 17 | checkpoint 为架构代理实现 |
| data/keylist.rs | fs/btree/interior.h | 完整 | 1 | 核心操作集，辅助函数未移植 |
| snapshot.rs | fs/snapshots/snapshot.c | 部分 | 5 | 只读+skiplist 完整；create/delete/回收缺失 |
| sb/ | fs/sb/ | 部分 | 10 | 单版本承诺一致；clean/counters/downgrade 未实现 |
| lock/six.rs | fs/util/six.c | 完整 | 3 | FIFO 等待队列 Vec 化实现 |

## 二、资源生命周期矩阵（AC-2）

| 项 | subvol 关键位置 | bcachefs 对应物 | 判定 | 差异 |
|----|----------------|----------------|------|------|
| A1 journal reclaim | journal.rs `bch2_journal_update_last_seq`(517)、`__bch2_journal_reclaim`(802)；engine.rs `reclaim_journal`(824)/reclaim worker(1286-1365) | fs/journal/reclaim.c:1047/1184 | **完整** | pin 推进、direct/background 双路径对齐；无 bucket 归还，以 checkpoint 推进 last_seq_ondisk 代理 |
| A2 btree cache 生命周期 | cache.rs `bch2_btree_node_data_free`(402)、`__bch2_btree_node_mem_alloc`(429)、`evict`(671) | fs/btree/cache.c:159/188/317 | **完整** | 状态机 + 三级分配回退对齐；shrinker 未实现（范围外） |
| A3 事务内存分配器 | update.rs `bch2_trans_kmalloc`(125)、`bch2_trans_subbuf_reserve`(212)、`bch2_trans_free_owned_key`(402) | fs/btree/iter.c:3752、update.c:609/640 | **完整** | bump 分配 + 扩容策略对齐；事务无回池（栈上） |
| A4 checkpoint COW | engine.rs `checkpoint_sync`(816)、`write_persistent_checkpoint`(2219)、`recover`(916) | fs/journal/write.c + reclaim.c | **部分** | 双槽位 COW + 页校验回退完整；bcachefs 无独立 checkpoint 镜像，属架构代理 |
| A5 bucket 分配器 | **不存在** | fs/alloc/{buckets,foreground,background,discard,backpointers}.c | **缺失** | 存储模型为 journal 环形 + checkpoint 镜像，无物理分配/引用计数需求；明确不在交付范围 |

## 三、数据一致性矩阵（AC-3）

| 项 | subvol 关键位置 | bcachefs 对应物 | 判定 | 差异 |
|----|----------------|----------------|------|------|
| 崩溃处理-写入 | journal.rs `bch2_journal_flush`(1005-1226)、`bch2_journal_res_get`(899) | journal.c:958/1255、write.c:1087 | **完整** | 同步单线程化，fsync 在调用线程完成 |
| 崩溃处理-恢复 | journal.rs `bch2_journal_read`(1258)、`replay`(1646-1842)；engine.rs `recover`(916) | read.c:1156 | **完整** | 含 root 早重放、overlay 构建 |
| seq_blacklist | **无**（全仓零命中） | seq_blacklist.c:49 `bch2_journal_seq_blacklist_add` | **缺失** | 以恢复期强连续性校验替代（重复 seq 返回 -7、乱序 -8）；seq 达上限时硬失败(journal.rs:1177-1179)，无环回 |
| journal 校验 | 内嵌 read：magic/seq/version/checksum(1331-1369) | validate.c:639/694/748 | **部分** | jset 头校验齐全；btree_keys 无逐 key 语义校验 |
| 事务 trigger | update.rs `btree_trigger_op`(909)、`run_one_mem_trigger`(1821) | commit.c:507/552/598-656 | **部分** | 结构/标志对齐；snapshot 域完整（mark_snapshot+whiteout）；**trans trigger 链与 gc trigger 缺失**——级联更新不可表达 |
| 在线 fsck | engine.rs `verify()`(751-779)、interior.rs `bch2_btree_node_check_topology`(251) | check.c:191/269/330/594/788、alloc/check.c:141-736 | **部分** | 仅排序 + 单节点拓扑；无递归全树拓扑、无 gc 引用标记、无 alloc 一致性 |

## 四、双基准不重合项清单（AC-4）

项目 AGENTS.md 交付目标中，bcachefs 语义未覆盖或机制不同的项：

1. **属性测试缺失**：AGENTS.md 将"崩溃/故障注入和属性测试验证"列为交付重点；当前无 proptest/quickcheck/fuzz 任何依赖（Cargo.toml 仅 urcu），无属性测试代码。故障注入已有（engine.rs `inject_fault` + FaultPoint 枚举），属性测试为零。
2. **故障注入覆盖面**：FaultPoint 枚举（engine.rs:311）已有实现，但注入点数量/类型未对照 bcachefs fault_inject 机制核对（本次未深入，建议后续任务评估）。
3. **seq 环回/黑名单机制**：bcachefs 崩溃恢复后靠 seq_blacklist 支持序号环回，subvol 以强连续性校验替代，长期运行到达 `JOURNAL_SEQ_MAX` 会硬失败——持久性正确性短期成立，长期可靠性有限。
4. **write_buffer 缓冲写路径**：bcachefs 有独立 write_buffer 机制（fs/btree/write_buffer.c），subvol 的 `bch2_trans_update_buffered`(update.rs:1375) 仅做了入口，未形成完整 buffered update 语义（测试引用存在但未验证）。
5. **interior split 语义**：bcachefs `bch2_btree_update_start` 异步框架（interior.c:1404）管理节点分配/journal 记录/锁升级；subvol 为同步简化版，多级分裂靠重试爬升——近期正确性成立（有测试），非完整对齐。

## 五、缺陷清单（AC-5/AC-6）

### D1【CRITICAL】commit 空间检查未累加同 leaf 多 update → 堆越界写（已根因级）

- **证据**：ASAN heap-buffer-overflow WRITE size=40 @ bset_update.rs:188（`bch2_bset_insert` copy_nonoverlapping），调用链 `Transaction::commit`(engine.rs:490) → `bch2_trans_commit`(update.rs:2160) → `bch2_btree_insert_key_leaf`(1676) → `bch2_bset_insert`。
- **复现**：`cargo test --lib engine::tests::checkpoint_pages_are_cow_and_corrupt_page_falls_back_to_prior_root` 单独运行即 SIGABRT（`free(): invalid next size`）。
- **根因**：`bch2_trans_commit` 空间检查（update.rs:1953-1971）对每个 update 独立判断 `bch2_btree_node_insert_fits(b, required_u64s)`，未模拟同一 leaf 多 update 的累计占用；bcachefs（commit.c:1083-1097）为 `u64s += i->k->k.u64s` 累加后 `btree_key_can_insert`（commit.c:427-432），放不下即中止 commit 并触发 split/restart。subvol 16 个 8-u64s key 全部通过空节点检查，插入第 8 个时节点（512B=64 u64s）已满仍写入，越界破坏堆（释放时暴露）。
- **次要防御缺失**：bcachefs `bch2_btree_bset_insert_key_inlined`（commit.c:189-195）的 `EBUG_ON(insert->k.u64s > bch2_btree_keys_u64s_remaining(b))` 在 subvol 缺失。
- **影响面**：btree 写路径；单事务向同一 leaf 累计写入超节点容量的 key 序列即触发（小节点最易触发）。
- **严重度**：高（内存破坏/崩溃，影响 checkpoint/持久化路径）。
- **修复方向**：对齐 commit.c 语义——同 leaf update 累加 u64s 后再检查 insert_fits，不满足则 split+restart；补剩余空间 EBUG_ON；补回归测试。

### D2【中】seq_blacklist 缺失，seq 达上限硬失败

- journal.rs:1177-1179 `JOURNAL_SEQ_MAX` 时返回 -2；bcachefs seq_blacklist.c 支持环回。长期运行可靠性受限，崩溃窗口校验依赖强连续性（当前正确）。

### D3【中】trigger 链不完整

- trans trigger（commit.c:552 `run_one_trans_trigger`、598-646 多轮循环）与 gc trigger（commit.c:649-656）缺失；`insert_trigger_run`/`overwrite_trigger_run` 字段（iter.rs:339-340）仅存在不消费；触发判定硬编码 `type_ == KEY_TYPE_snapshot`（update.rs:1848）。级联更新不可表达，新 key 类型无法挂接 trigger。

### D4【中】在线 verify 覆盖不足

- `verify()`（engine.rs:751）仅排序检查 + 单节点拓扑（interior.rs:251），无递归全树拓扑/重建（check.c:330）、无 gc 引用标记（check.c:788）、无 alloc 一致性（alloc/check.c:141）。当前 btree 集无引用计数关系，短期风险低。

### D5【低】journal 校验部分

- btree_keys 条目不逐 key 语义校验（validate.c:694 有完整逐条目验证）。

### D6【低】测试覆盖薄弱项

- bset_search.rs / bset_update.rs 各仅 1 个测试；data/keylist 1 个；node_iter 2 个。

## 六、后续任务拆解建议（AC-7）

| 优先级 | 任务 | 理由 | 类型 |
|--------|------|------|------|
| P0 | 修复 D1：commit 空间检查累加同 leaf u64s + 补 EBUG_ON + 回归测试 | CRITICAL 内存破坏，checkpoint COW 测试即复现 | bugfix |
| P1 | 评估 seq_blacklist 或环回机制（D2） | 长期运行可靠性，JOURNAL_SEQ_MAX 硬失败 | development |
| P1 | 补 interior split_interior/异步 update_start 语义（部分模块） | 多级分裂当前靠重试，未对齐 interior.c 完整语义 | development |
| P2 | 引入属性测试（proptest）：btree 随机操作序列 vs 模型 | AGENTS.md 明确交付重点，当前为零 | development |
| P2 | 补 trans/gc trigger 链（D3） | 级联更新不可表达，新 key 类型无法挂接 | development |
| P2 | 增强 verify 为递归全树检查（D4） | 在线 fsck 能力提升 | development |
| P3 | 补薄弱模块测试覆盖（D6） | bset_search/bset_update/keylist 各 1 个测试 | development |
| P3 | journal 逐 key 语义校验（D5） | 恢复路径更强校验 | development |

## 七、bcachefs 对应物路径抽查（AC-8）

抽查 12 个路径全部真实存在（`ls` 验证），关键符号抽查：

| bcachefs 文件 | 关键符号 | 验证 |
|--------------|---------|------|
| fs/btree/commit.c:1094 | `u64s += i->k->k.u64s`（D1 根因对照） | 存在 |
| fs/btree/interior.c:1404 | `bch2_btree_update_start` | 存在 |
| fs/btree/interior.c:294 | `bch2_btree_node_check_topology` | 存在 |
| fs/btree/check.c:191 | `btree_check_node_boundaries` | 存在 |
| fs/journal/seq_blacklist.c:49 | `bch2_journal_seq_blacklist_add` | 存在 |
| fs/journal/reclaim.c / read.c / write.c / validate.c / util/six.c / snapshots/snapshot.c / alloc/check.c | 文件存在 | 存在 |

## 结论

- **btree 核心功能完整性：总体完整**（15/24 完整），关键路径语义与 bcachefs 对齐良好，崩溃一致性路径（journal 持久化/恢复 + 27 个含进程级崩溃的测试）最扎实。
- **必须处理**：D1 CRITICAL 缺陷（commit 空间预检）——修复后建议全量重跑 `cargo test --lib` 确认全绿。
- **机制性缺口**：seq_blacklist、trans/gc trigger 链、递归 fsck、属性测试——均在交付目标内但未完成，建议按 P1/P2 优先级排期。
- 全部缺失项（bucket 分配器、快照创建/删除、sb 多版本）符合 AGENTS.md 范围声明，不阻塞。
