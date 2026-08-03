# T0208 PRD：btree 随机操作序列一致性属性测试（多 btree id）

## 背景

T0207 后 subvol 交付重点（AGENTS.md：btree 操作正确性、事务一致性、
崩溃/故障注入、属性测试验证）中的缺口：现有 proptest 仅覆盖
journal-reclaim（T0173）、split（T0174）、bucket/discard 模型
（T0188-0191）、并发交错（T0199）。**btree 随机操作序列本身**
（多 btree id 下的 put/delete/scan × 拓扑变更 × 崩溃重开）无属性
验证。engine 层 `BtreeId` 支持任意 id（0..BTREE_ID_NR=9，types.rs），
`verify_all` 遍历所有 live btree（engine.rs:807），但测试几乎只用
DEFAULT(0)——多 id 隔离性未验证。

## 目标

随机操作序列（跨多 btree id 的 put/delete）下，engine 可见状态与
shadow 有序模型逐 id 一致；拓扑变更（split/merge）与崩溃重开
（journal 重放）不破坏一致性。

## 验收标准（AC）

- [ ] **AC-1 多 id 隔离与扫描一致性**：proptest 随机序列
  `(id ∈ 0..8, kind ∈ {put, delete}, pos)` → 每步后逐 id 断言：
  `scan(id)` == shadow 有序内容、`get(id, pos)` == shadow 命中；
  对**非目标 id** 抽查 scan 不变（隔离性）。
- [ ] **AC-2 拓扑变更一致性**：同 id 高密度 put（触发 split，T0174
  阈值模式）与密集 delete（触发 merge，T0204）后：`verify_all` 通过、
  全部 id scan 与 shadow 一致、节点拓扑（bch2_btree_node_check_topology
  经 verify）无异常。
- [ ] **AC-3 崩溃重开一致性**：随机序列中随机点 drop（模拟崩溃）→
  `open_persistent` 重开（journal 重放，T0201 模式）→ 所有 id scan
  与 shadow 一致（已同步部分 + 已提交日志部分）；重开后继续追加
  随机操作仍一致。
- [ ] **AC-4 门禁**：全量 `cargo test --lib`（244+ 测试，<1min）+
  `cargo fmt --check` + diff gate 干净。

## 对齐依据（约束 1/3/10）

| 域内行为 | bcachefs 对应（本地源码） |
|---------|--------------------------|
| 每 btree 独立 root/扫描 | `bch2_btree_id_root`（types.rs bch_fs.btree_id_root，BTREE_ID_NR=9；engine verify 遍历 live btrees，engine.rs:807） |
| 扫描有序性 | `bch2_btree_iter` 顺序遍历（engine verify 已断言 windows(2) 有序） |
| put/delete 事务 | `bch2_btree_insert_trans` / `bch2_btree_iter_init`（update.c） |
| split | `bch2_btree_split`（interior.c，T0174/T0177 已对齐） |
| merge | `bch2_foreground_maybe_merge`（interior.c，T0204 已对齐） |
| 崩溃重开 | journal 重放（T0201 persistent-concurrency 已对齐 journal 持久化语义） |

btree id 编号方案为域内自有（约束 14 豁免）。

## 实现决策（草案）

- 复用既有模式：`prepared_bucket_engine`（engine.rs:2968）+ proptest
  （engine.rs:4216 配置：cases 16, max_shrink_iters 64）。
- shadow 模型：`Vec<BTreeMap<KeyPosition, Vec<u64>>>`（每 id 一个），
  逐操作同步（put=insert、delete=remove），语义即"最终状态"。
- 操作生成器：`prop::collection::vec((0u8..8, 0u8..2, 0u64..K), 1..=40)`；
  id 范围可选子集（如 0..4）控制测试时长。
- 隔离性：逐步仅比对非目标 id（快照成本高则改为每步前记录
  shadow 指纹，操作后比对未触及 id 指纹）。
- 拓扑变更触发：同 id 连续 put（pos 递增）超过 split 阈值；
  全部删除触发 merge（T0204 测试模式实测阈值）。
- 崩溃点：`ModelEngine` 加 `reopen`（已存在，engine.rs:4185）在
  随机步数处调用；同步点用 `put_sync` 保证已同步部分可恢复。
- 测试时长：单测试 <60s（约束 9），proptest cases 与序列长度
  按实测调参。

## 范围外

- 不新增 engine API / 不新增 btree 逻辑（仅测试）。
- 不覆盖 fs 层兼容（AGENTS.md 范围外）。
- io 层读盘/重写（T0206/07 已覆盖）不重复。

## 风险

- split/merge 触发阈值需实测（过高则测试不含拓扑变更，过低则时长
  失控）→ 用 debug 日志（`rewrite_log_debug!` "commit maybe_merge"、
  "btree node split"）确认触发。
- 崩溃重开后 `verify_all` 的 bucket 派生状态校验可能因 journal 截断
  报错 → 参照 T0201 崩溃矩阵的期望误差范围处理。
