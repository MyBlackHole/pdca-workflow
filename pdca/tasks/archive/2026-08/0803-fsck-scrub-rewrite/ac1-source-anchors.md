# T0206 上游锚点记录（AC-1）：fsck/scrub 自动触发 btree 节点重写

修改前逐段对照的本地 bcachefs-tools 源码（fs/btree/read.c、interior.c、
fs/data/move.c）与 subvol 域内差异判定。

## 1. 上游语义链（源码锚点）

| 组件 | 锚点 | 语义 |
|------|------|------|
| `btree_node_scrub_work` | read.c:1233-1252 | scrub 读盘校验失败 → `bch2_btree_node_rewrite_key(trans, btree, level - 1, key, 0)`（read.c:1243）。level-1：scrub 的 level 是指针键所在层，rewrite_key 的 level 是目标节点层（T0205 已对齐此差异） |
| `bch2_btree_node_scrub` | read.c:1264-1328 | 读节点原始字节（bounce alloc + bio 读）→ 调度 scrub_work；被 move.c:326 数据移动 scrub 路径调用 |
| `btree_node_scrub_check` | read.c:1169-1204 | 校验 magic + 逐 bset 校验 csum（`csum_vstruct` + `bch2_crc_cmp`）+ written 边界（`vstruct_sectors`） |
| `bch2_btree_node_read_done` | read.c:578-880 | 读盘节点后逐项校验：硬错误（bad magic/seq/btree_id/level/min_key/max_key/format/unsupported version/SEPARATE_WHITEOUTS）直接失败；可修复错误（FSCK_CAN_FIX）截断/删键后设置 need_rewrite 标志 |
| need_rewrite 设置点 1 | read.c:567-568 | 键损坏截断（`next_good_key` 逻辑）：`le16_add_cpu(&i->u64s, -next_good_key)` + `memmove_u64s_down` → `set_btree_node_need_rewrite` + `set_btree_node_need_rewrite_error` |
| need_rewrite 设置点 2 | read.c:844-845 | 键值校验失败（`fsck_delete_bkey`）：删键 → `set_btree_node_need_rewrite` + `set_btree_node_need_rewrite_error` |
| need_rewrite 设置点 3 | read.c:871-872 | `ptr_written == 0`（写盘时未记录 sectors_written）：`set_btree_node_need_rewrite` + `set_btree_node_need_rewrite_ptr_written_zero` |
| 读完成自动触发 | read.c:968 | 读完成 endio：`failed.nr || btree_node_need_rewrite(b)` 且非 `scan_for_btree_nodes` pass → `bch2_async_btree_op(c, b, ASYNC_BTREE_rewrite)` |
| async work | interior.c:3395-3415 | `ASYNC_BTREE_rewrite` → `bch2_btree_node_rewrite_key(trans, btree_id, level, key.k, 0)`（ENOENT/EROFS/no_btree_node_nofill 忽略，其余报错） |
| 错误分类基准 | read.c:177-192 btree_err 宏 + read.c:120-175 `__btree_err` | FSCK_CAN_FIX（可修复，fix=yes 时返回 fsck_fix 不 goto fsck_err）；type=0（硬错误，直接失败）；scan pass 内一律硬错误 |
| `bch2_validate_bset` | read.c:245-450 | bset 级校验：version 兼容性、BSET_OFFSET 对齐（FSCK_CAN_FIX）、SEPARATE_WHITEOUTS（硬）、bad_seq/bad_btree/bad_level/bad_min_key/bad_max_key/bad_format（硬） |
| `bch2_validate_bset_keys` | read.c:449-577 | 键级校验：key past end（FSCK_CAN_FIX 截断）、bad format/u64s（FSCK_CAN_FIX 删键）、乱序（FSCK_CAN_FIX 删键）、值校验失败 fsck_delete_bkey（删键 + need_rewrite） |

## 2. subvol 现状核查

- `bch2_btree_node_read`（io.rs:435-680）：**严格校验**，可修复错误
  与硬错误一律返回错误码（-5 bad magic、-6 past end、-7 csum type、
  -8 bad csum、-9 version、-10 SEPARATE_WHITEOUTS/BIG_ENDIAN/OFFSET、
  -11 seq、-12 id/level、-13 min/max、-14 format、-15 key u64s、
  -16 key pos 越界、-17 乱序、-18 ptr_v2 value 过短、-19 ptr_written
  不匹配、-20 bset 越界），**无 need_rewrite 设置语义**。
- 读完成点：`bch2_btree_node_get_noiter_unlocked`（io.rs:800-860）
  与 `bch2_btree_root_read`（io.rs:1003-1060）：读失败 →
  `set_btree_node_read_error` → 返回 null / 错误码，无自动重写调度。
- T0205 已交付：`rewrite_node_key`（engine.rs:1428，rewrite_key 语义，
  level=目标节点层）、`rewrite_node`（engine.rs:1414，rewrite_pos 语义）。
- fsck 框架：`fsck_image`（engine.rs:2662）+ FixErrors + verify_all +
  `repair_derived_indexes`（仅派生索引键，无节点级修复）。

## 3. subvol 域内差异判定

| # | bcachefs 设施 | subvol 对应 | 判定 |
|---|--------------|-------------|------|
| D1 | async_btree_op work 队列 + BCH_WRITE_REF 记账（interior.c:3395-3459） | 读完成入队 btree.node_rewrites + 无锁时机同步 drain | 域内无异步调度（T0205 D3 同款）。实测：读路径内同步执行重写会与外层路径锁互斥死锁（get 路径测试曾挂死 60s+），故读完成点仅入队（对齐上游 pending 列表 + `bch2_bkey_buf_copy(&a->key, &b->key)` 的 key 拷贝语义，interior.c:3440-3448，不持节点引用防 retire 悬垂）；`bch2_do_pending_node_rewrites`（对齐 interior.c:3462）在无锁时机执行：root_read 末尾（锁已释放）与 engine 操作边界（EngineFsGuard::drop，trans 已释放） |
| D2 | move.c 数据移动层 scrub 触发 | fsck_image 修复模式触发 | 域内无数据移动层；scrub 语义落点为 fsck 修复模式（T0195-T0200 框架） |
| D3 | 读路径容错语义（截断坏键/删键 + set need_rewrite，read.c:567/844/871） | `bch2_btree_node_read` 严格校验返回错误码 | 用户裁决（P2）：读路径按上游语义设置 need_rewrite 后继续（可修复错误），硬错误维持错误码；读完成检查 need_rewrite → 入队延迟触发重写（read.c:968 语义） |
| D4 | scrub level 语义（read.c:1243 用 level-1，scrub level=指针键所在层） | rewrite_node_key（level=目标节点层） | 域内 fsck 触发时直接以目标节点层调用（T0205 已对齐 rewrite_key 语义） |
| D5 | btree_err FSCK_CAN_FIX 门控（fix=yes 才修复） | FixErrors::Yes 门控 | fsck 修复模式内触发重写，FixErrors::No 只检查（verify_all） |
| D6 | read.c:968 排除 scan_for_btree_nodes pass | 域内无 scan pass | 触发条件简化为 need_rewrite 标志（读失败已由 read_error 表达） |
| D7 | 上游 async work 错误忽略集（interior.c:3409-3412：ENOENT/EROFS/no_btree_node_nofill） | 同步 drain 忽略 -2（ENOENT）/ -5（no_btree_node_nofill） | 域内错误码：-2=定位节点 hash 不匹配、-5=节点不可达；其余错误记日志不中止（对齐上游仅报错） |
| D8 | engine 持久化模式与节点读盘的关系 | 无节点读盘 | journal-first 持久化（T0205）：节点 key 以 mem_ptr 寻址（interior.c:695-708 child_ptr 无 extent ptr），恢复期 disk_sb 无文件句柄 → journal.rs:1774 跳过 root_read → 树由 journal btree_keys 重建。AC-3 读完成触发仅在 io 层读路径（root_read / get）生效；engine 模式由 EngineFsGuard::drop drain 空转 |
| D9 | fsck 修复模式的节点 scrub（AC-4） | 域内无磁盘节点可 scrub | 用户裁决（0803）：差异记录 + AC-5 验证。上游 fsck 的节点修复 = 遍历读 → 读完成触发 rewrite（read.c:968，AC-3 已完整实现）；显式磁盘 scrub（read.c:1169-1328）仅在 move.c:326 数据移动路径调用，engine journal-first 下无节点扇区（实测 10 键 + sync 后文件 0 个节点 magic 词），scrub 无对象。域内 fsck_image 的节点级修复路径 = FixErrors::Yes 时遍历触发 AC-3 读完成重写 + verify_all 校验；FixErrors::No 只检查不重写（对齐 -n nochanges 不落盘语义） |

## 4. 测试设计锚点（草案）

| # | 场景 | 断言 |
|---|------|------|
| T1 | 读路径损坏节点（键 u64s 破坏 → 修复删键 + need_rewrite）→ 自动重写 | 读完成触发 rewrite、节点校验通过、scan 键集不变 |
| T2 | 硬错误（bad magic/seq/id/level/min/max/format） | 维持错误码，不触发重写 |
| T3 | fsck FixErrors::Yes 修复损坏节点 | 节点重写 + verify_all 通过；FixErrors::No 不改动 |
| T4 | 崩溃注入 | 重写提交后 drop 不 flush → 重开 → 键集一致、verify_all |
| T5 | 全量回归 <1min | 基线 --test-threads=4 |

## 5. AC-3 实现记录（同步触发）

- 交付：`btree::interior::bch2_btree_node_rewrite_key`（interior.rs:2209，
  AC-1 读完成触发与 engine rewrite_node_key 共用的实现，自建 trans +
  BTREE_ITER_intent + peek_node + `btree_ptr_hash_val` 匹配 → rewrite，
  不匹配 -2）+ `bch2_btree_node_need_rewrite_add`（入队，key 拷贝）+
  `bch2_do_pending_node_rewrites`（drain）。
- 触发点 1：`bch2_btree_node_get_noiter_unlocked`（io.rs，读成功、
  need_rewrite 时入队——上游 read.c:968 endio 排队语义）。
- 触发点 2：`bch2_btree_root_read`（io.rs，解锁后入队 + 立即 drain，
  root_read 上下文无外层路径锁，可安全执行）。
- engine 集成：`EngineFsGuard`（engine.rs）Drop 时 drain（= engine
  公开操作返回前，trans 与节点锁已释放）。
- engine 层 `rewrite_node_key_locked` 消重到 interior 助手（行为零变化）。
- 测试（全部 <1min 基线内）：
  - `root_read_need_rewrite_triggers_sync_rewrite`（io.rs）：root 即叶
    单节点 2 键，损坏键 2 u64s（5→4）→ root_read 后 root slot 被
    重写节点替换（seq 101→102）、幸存键重打包（keys.u64s==1、
    packed_keys==1）——验证 root 触发点 + 重写路径。
  - `child_read_need_rewrite_triggers_sync_rewrite_via_iter`（io.rs）：
    root level 1 + 损坏 child leaf → iter 遍历触发 get 路径读完成
    入队 → 手动 drain（等价 engine 操作边界）→ root 内 child 指针
    键 seq 101→102——验证 get 触发点 + 入队延迟语义（曾实测同步
    执行死锁，见 D1）。
  - `corrupt_root_region_does_not_affect_journal_first_recovery`
    （engine.rs）：journal-first 模式无节点读盘，破坏磁盘 root 区域
    不影响恢复——行为契约（D8）。
- 全量 `cargo test --lib`：243 passed, 0 failed（~10.6s）。

## 6. AC-4 判定记录（fsck 修复模式触发）

- 上游：fsck 不调用显式 scrub；节点修复 = 遍历读 → read.c:968 读完成
  触发 → async rewrite（FixErrors::No 时修复动作不落盘 = nochanges）。
  显式 `bch2_btree_node_scrub`（read.c:1264-1328，字节级 bio 读 +
  magic/csum/written 校验）仅由 move.c:326 数据移动路径调用。
- 域内判定（D9，用户裁决）：engine journal-first 下节点从不落盘
  （D8），磁盘节点 scrub 无对象；fsck 节点级修复 = AC-3 已实现的
  读完成触发机制（FixErrors::Yes 时 flush 持久化 / No 时不 flush）。
- AC-4 域内无新增代码；验证责任转交 AC-5（重写后重新校验通过 +
  重开一致 + verify_all）。

## 7. AC-5 实现记录（部分完成，Check 时点）

- 已交付：`rewritten_node_revalidates_on_reopen`（io.rs，AC-5 验证
  测试）：损坏 root → root_read 触发重写（覆盖写盘 @ 64，seq
  101→102，root 分支 set_root_for_read 更新 slot.key）→ 从 slot 取
  新 root key（mem_ptr 清零）模拟关闭重开 → 第二次 root_read 重新
  读盘校验 → 断言读解析通过 / 无 need_rewrite / seq 持久化 / 键集
  = 修复后内容 / 拓扑校验通过。
- **待修复（Check 时点失败）**：重写后 slot.key 无 extent ptr
  （interior.rs root 分支 child_ptr(n) 仅 mem_ptr 寻址，interior.c
  T0205 同款）→ 第二次 root_read 读盘 `bch2_bkey_ptrs_c` 空返回
  -2（io.rs:454）。上游语义：重写 root 后 slot.key 保留原 extent
  ptr（覆盖写原位置）。修复方向：root 分支 bkey_copy 前合并旧
  extent ptr（对齐上游 set_root 保留磁盘位置的语义）。
- 未交付（Check 时点）：重写提交后 verify_all 通过、崩溃注入收敛
  （engine 层无节点重写场景，fallback = io 层重开一致 + fsck 故障
  矩阵已有测试）；AC-6 全量门禁。
