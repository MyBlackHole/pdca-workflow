# T0206 Triage Brief

## 输入

- T0205（btree 节点重写）归档后 conclusion「下一轮建议」首项：
  rewrite 的 fsck/scrub 自动触发路径（read.c:1243 语义），需先有
  fsck 修复调度框架（T0195-T0200 已建）。
- 用户裁决：PDCA 下一步方向 = fsck/scrub 自动触发 rewrite。

## 现状核查

- `BTREE_NODE_need_rewrite` 标志（types.rs:677）已有 set
  （root_alloc_fake interior.rs:177）、clear（journal.rs:3196/3270、
  update.rs:3267），消费点：`bch2_btree_node_insert_fits`
  （interior.rs:71）在 need_rewrite 时拒绝插入。**无自动触发
  消费路径**（T0205 范围外明确列出）。
- 读路径 `bch2_btree_node_read`（io.rs:435）严格校验
  （magic/seq/btree_id/level/min_key/max_key/format/csum/键序/
  ptr_written），失败返回错误码（-5..-19），**不设置 need_rewrite**。
- `bch2_btree_node_get_noiter_unlocked`（io.rs:842）读失败 →
  set_btree_node_read_error → 返回 null，无自动重写调度。
- T0205 已交付入口：`rewrite_node`（engine.rs:1414，rewrite_pos
  语义，level>=1 指针键所在层）、`rewrite_node_key`（engine.rs:1428，
  rewrite_key 语义，level=目标节点层，叶 level==0 合法）。
- fsck 框架（T0195-T0200）：`fsck_image`（engine.rs:2662）+
  FixErrors::No/Yes + `repair_derived_indexes`（派生索引键修复）+
  verify_all（拓扑/派生状态/bucket indexes/guard）+ 故障注入
  （FsckFaultPoint）。修复动作目前仅"删除/插入派生索引键"，
  **无节点级修复**。

## 上游对照

- `btree_node_scrub_work`（read.c:1233-1252）：scrub 校验失败 →
  `bch2_btree_node_rewrite_key(trans, btree, level - 1, key, 0)`
  （read.c:1243）。level-1 语义：scrub 的 level 是指针键所在层，
  rewrite_key 的 level 是目标节点层。
- `bch2_btree_node_scrub`（read.c:1264-1328）：读节点 →
  校验（magic/csum/written 边界，`btree_node_scrub_check`
  read.c:1169-1204）→ 失败调度 scrub work → rewrite_key。
- `bch2_async_btree_op(c, b, ASYNC_BTREE_rewrite)`（read.c:968）：
  读完成时 `failed.nr || need_rewrite(b)` 且非 scan pass →
  异步调度重写。
- `async_btree_node_rewrite_work`（interior.c:3395-3415）：
  ASYNC_BTREE_rewrite → `bch2_btree_node_rewrite_key(trans,
  btree_id, level, key.k, 0)`。
- need_rewrite 设置点：read.c:567/844/871（坏键截断、校验失败、
  ptr_written==0）。
- 触发方：move.c:326（scrub 数据移动）→ `bch2_btree_node_scrub`。

## 差异判定（草案）

- D1: async_btree_op work 队列 → 同步 API（域内无异步调度，
  T0205 D3 同款）。
- D2: move.c 数据移动层 scrub 触发 → 域内 fsck_image 修复模式
  触发（无数据移动层）。
- D3: 上游读取路径"校验失败 → 截断 → set need_rewrite"的容错
  读取语义 vs subvol 严格校验返回错误码——域内是否引入读失败
  自动重写，待 Grill 决策。
- D4: scrub 的 level 语义（read.c:1243 用 level-1，scrub
  level=指针键所在层）：域内 fsck 触发时直接以目标节点层调用
  rewrite_node_key（T0205 已对齐 rewrite_key 语义）。

## 查重

T0205 disposition task_only、范围外明确"fsck/scrub 调度集成、
need_rewrite 自动触发机制"；T0195-T0200 fsck 系列仅覆盖索引键
修复。无同范围活动任务。

## 推荐

立项：feature/development，parent=T0205。方案 = fsck_image
修复模式扩展节点级 scrub 校验：遍历 btree 各节点 → 校验
（对齐 btree_node_scrub_check 的 magic/csum/written 检查）→
校验失败 → 自动 `rewrite_node_key` 重写该节点（对齐
read.c:1243）→ 重写后重新校验通过。范围外：读取路径自动
触发（read.c:968）、GC 触发、async worker。
