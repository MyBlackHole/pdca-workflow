# T0210 PRD：btree 节点实体落盘（allocator 子集 + 节点写盘 + root 驱动恢复）

## 背景

T0201 系列确立 **journal-first 持久化**：磁盘上唯一持久数据是 journal
记录（键更新 + root 集），节点实体只在内存（mem_ptr 寻址），重开由
journal btree_keys 重放**从空重建树**。上轮缺口盘点因此判 node_scan
"结构上无场景"。用户决策：**对齐节点实体**——节点写独立扇区，恢复
切换为 root 驱动遍历（此后再引入 node_scan 才有场景，P3 后续任务）。

域内已有基础设施（T0201-T0202 期间建立）：
- **bucket 骨架**：alloc btree（域内 id 4）+ freespace btree（域内 id 5）
  + need_discard（id 6）；`allocate_bucket`（engine.rs，对应
  foreground.c free-bucket 候选规则：freespace 位 → alloc_v4 状态校验
  → 置 BCH_DATA_BTREE + 清 freespace 位）；`add_free_bucket` 测试设施；
  `bch2_btree_bit_mod`；`trigger_update_value`（alloc 触发器路径）；
  `open_buckets` 集合（bucket 打开跟踪）。
- **写盘/读盘链已存在（T0205）**：`__bch2_btree_node_write`
  （io.rs:395-431，写 ptr offset 扇区 + xxhash checksum + bset 头
  journal_seq，对齐 write.c:336-642）；`bch2_btree_node_read`
  （io.rs:514，sectors_written/bset 遍历/journal_seq max，对齐
  read.c）；flush pin 回调经 `bch2_btree_node_write_trans` 写盘
  （update.rs:877，对齐 commit.c:254）。
- **缺的正是上游"分配器→磁盘 ptr"这一环**：节点 key 无磁盘 ptr
  （mem_ptr 寻址），因此写盘/读盘链在持久化路径从未真实触发；
  恢复无 root 绑定与节点遍历。

## 目标

对齐上游"节点实体写独立扇区 + journal 记录键更新与 root + 恢复 root
驱动遍历"：节点从分配器拿到真实扇区（btree_ptr_v2），事务产生的脏
节点写盘，重开时从 journal root 绑定 + 磁盘读节点遍历加载。

## 上游对齐锚点（约束 1/3/10，实现前必须逐处重读）

| 功能 | 上游锚点 |
|---|---|
| 扇区分配请求 | `bch2_alloc_sectors_req`（fs/alloc/foreground.c:1466）：writepoint_find → bucket_alloc_set_writepoint/partial/trans（bch2_bucket_alloc_freelist，foreground.c:438，alloc btree 扫描 free bucket）→ 域内 `allocate_bucket` 已对应 |
| open_bucket 扇区记账 | `bch2_alloc_sectors_append_ptrs`/`_inlined`（foreground.c:1653）：bucket 内扇区递增（sector_offset）、sectors_free 扣减、btree ptr offset = bucket 起点 + 已用扇区；`bch2_alloc_sectors_done`（1664） |
| 节点分配 | `__bch2_btree_node_alloc`（fs/btree/interior.c:451）：reserve_cache 复用（485-503）→ `bch2_alloc_sectors_req` → `bkey_btree_ptr_v2_init` → `bch2_alloc_sectors_append_ptrs` → `bch2_open_bucket_get`；`bch2_btree_node_alloc`（525） |
| 节点写盘 | `__bch2_btree_node_write`（fs/btree/write.c:336）：bset 头 journal_seq（485）、写 ptr offset 扇区、sectors_written（605-642）→ 域内 io.rs 已有，需接入分配来的 ptr |
| 恢复 root 驱动 | `read_btree_roots`（fs/init/recovery.c:625）→ `bch2_btree_root_read`（643）：root 绑定 → 从磁盘读 root 节点 → 遍历加载 |
| 崩溃一致性 | 节点 bset 头 journal_seq（write.c:485）读时过滤：节点扇区 journal_seq 大于已重放 seq 时该节点数据作废（以 journal 为准） |

## 交付物（P1+P2 一个任务交付，P3 node_scan 排后续任务）

### P1 扇区级分配（allocator 子集）
1. **open_bucket 扇区记账**（对齐 append_ptrs_inlined）：在 `allocate_bucket`
   之上建立 open_bucket 状态（sectors_free/sector_offset），节点分配从
   bucket 内递增 offset，一个 bucket 可连续放多个节点；bucket 耗尽
   （sectors_free < 节点扇区数）时关闭回收。
2. **reserve_cache**（对齐 interior.c:485-503/650-653 语义）：节点预分配
   缓存（btree_alloc：key + open_bucket），`__bch2_btree_node_alloc`
   先查缓存，不足时走分配路径并回填。
3. **移植 `__bch2_btree_node_alloc`/`bch2_btree_node_alloc`**
   （interior.c:451-600）：节点 key 构造为 `btree_ptr_v2`
   （dev/offset/gen/sectors_written）——节点从 mem_ptr 寻址改为磁盘 ptr。

### P2 持久化接入 + 恢复切换
4. **节点写盘接入**：split/merge/update 产生的脏节点经既有写盘链
   （flush pin → write_trans → `__bch2_btree_node_write`）写 ptr 扇区；
   写序保证：journal 记录（含 root）先于节点扇区。
5. **恢复切换**：重开流程改为 replay（校正扇区键更新）→
   `read_btree_roots`（从 journal btree_root 条目绑定各 btree root）→
   `bch2_btree_node_read` 遍历加载，节点按 bset 头 journal_seq 过滤
   （扇区新于重放 seq 作废）。
6. **故障注入扩展**：节点扇区写失败、节点损坏读失败（为 P3 node_scan
   铺路；P3 本身不实现）。

## 验收标准

- [ ] **AC-1 分配语义**：节点分配产生真实扇区 ptr（dev/offset/gen），
  同一 bucket 内连续分配 offset 递增；bucket 耗尽后换新 bucket；分配后
  alloc_v4 状态与 freespace 位一致（对齐 foreground.c 候选规则）。
- [ ] **AC-2 写读往返**：事务提交后节点扇区可读回（xxhash 校验通过），
  sectors_written 正确；重写（split 后新节点）覆盖/追加扇区正确。
- [ ] **AC-3 恢复切换**：重开走 root 绑定 + 节点遍历加载（不再是纯
  btree_keys 重放重建）；重开后树内容与崩溃前一致（scan 与 shadow
  对比）；节点 bset 头 journal_seq 过滤正确（构造"扇区新于重放 seq"
  场景，节点数据以 journal 为准）。
- [ ] **AC-4 崩溃矩阵**：T0201 框架扩展——commit 前/后崩溃、节点写盘
  前/中/后崩溃，重开一致性与不变量保持（约束 9：测试 1 分钟内）。
- [ ] **AC-5 门禁**：全量 `cargo test --lib`（<1min）+ `cargo fmt --check`
  + diff gate 干净。

## 对齐依据（约束 1/3/6/8/10/12）

- 所有新增控制流来自上表锚点函数（foreground.c/interior.c/write.c/
  recovery.c）；分配重试、bucket 不足换桶、写失败恢复 dirty 标志等
  降级路径照搬，不简化（约束 6）。
- 不新增上游不存在的函数（约束 8）；reserve_cache、open_bucket 记账
  均为上游既有语义。
- 域内 btree id 编号保持自有（约束 14 豁免）：alloc=4、freespace=5、
  need_discard=6 沿用既有骨架，不因本任务改动。

## 边界

- 单设备（s_bdev_file 模拟盘），bucket_size/block_size 沿用 sb 配置。
- 不做 allocator 后台线程（上游 alloc.c 线程预填 open_bucket 是并发
  优化；域内同步按需分配，语义等价——若实现将单独对齐）。
- 不做 bucket 回收/GC、不做 fsck（上游 check.c alloc 一致性检查）。
- P3 node_scan（`bch2_scan_for_btree_nodes`，node_scan.c:373）+ 扇区
  损坏注入测试排后续任务。

## 风险

- **恢复路径切换推翻既有重开语义**：T0201/T0208 崩溃重开测试从
  "重放重建"改"root 遍历"，需逐处适配（scan 结果不变，机制变）。
- **mem_ptr → btree_ptr 波及面**：节点 key 构造（fake root、T0209 快照
  写路径、verify_all）都要过一遍。
- **崩溃一致性窗口**：写序（journal 先于节点扇区）+ bset 头 journal_seq
  过滤是本任务正确性核心，AC-3/AC-4 重点验证。
- 全量回归中既有测试若依赖"节点不落盘"的隐式行为，需要显式适配。
