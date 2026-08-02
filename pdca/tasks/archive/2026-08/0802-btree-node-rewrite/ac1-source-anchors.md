# T0205 上游锚点记录（AC-1）：btree 节点重写（rewrite/格式化）

修改前逐段对照的本地 bcachefs-tools 源码（fs/btree/interior.c）与
subvol 域内差异判定。

## 1. bcachefs node rewrite 语义链（源码锚点）

| 组件 | 锚点 | 语义 |
|------|------|------|
| `bch2_btree_node_rewrite` | interior.c:3276-3343 | 主体：BUG_ON(fake) → update_start（锁升级+记账）→ `bch2_btree_node_lock_write(b)` → `bch2_btree_node_alloc_replacement` → `build_aux_trees(n)` → `bch2_path_get_unlocked_mut` + `btree_path_take_new_node`（路径换新）→ `bch2_btree_update_emit_new_node_key(as, n)` → parent 分支：`bch2_keylist_add(parent_keys, &n->key)` + `bch2_btree_insert_node`；root 分支：`bch2_btree_set_root` → `bch2_btree_interior_update_will_free_node(as, b)` → `bch2_btree_update_write_new_node(as, n)` → `bch2_btree_node_free_inmem(trans, path, b)` → `bch2_trans_node_add(trans, n)` → `bch2_trans_node_verify_not_in_iters(trans, b)` → `bch2_btree_update_done`（retire b）；失败 `bch2_btree_update_free`；结尾 `path_put(new_path)` + `trans_downgrade` |
| `bch2_btree_node_alloc_replacement` | interior.c:593-616 | 新节点（同 level）：`format = bch2_btree_calc_format(b)` → `!bch2_btree_node_format_fits(as->c, b, b->nr, &format)` 时 `format = b->format`（回退旧格式）→ `seq = 旧 seq + 1` → `min/max` 继承 → `bch2_btree_sort_into(c, n, b)` 全键搬移 → `btree_node_reset_sib_u64s(n)` |
| `bch2_btree_node_format_fits` | interior.c:346-361 | `u64s = btree_node_u64s_with_format(nr, b->format, new_f)`；`__vstruct_bytes < btree_buf_bytes(b)`（严格小于，interior.c:2843/3150 注释强调） |
| `bch2_btree_node_rewrite_key` | interior.c:3345-3359 | 按 `k->k.p` 遍历到节点（BTREE_MAX_DEPTH/level），`btree_ptr_hash_val(&b->key) == btree_ptr_hash_val(k)` 匹配才重写，否则 -ENOENT |
| `bch2_btree_node_rewrite_pos` | interior.c:3373-3388 | `BUG_ON(!level)`；traverse level+1 → 拿 level-1 层路径得到节点指针 b，重写 b（target 写目标参数） |
| async_btree_rewrite | interior.c:3400-3459 | work 队列：`ASYNC_BTREE_rewrite` → rewrite_key；`ASYNC_BTREE_merge[_no_read]` → node_merge_key（T0204 范围外同款）；BCH_WRITE_REF_node_rewrite 记账；recovery 前挂 pending 队列 |
| `bch2_btree_node_rewrite_key` 调用点 | read.c:1243 | scrub 修复：读出错节点触发重写 |
| 常量/结构 | interior.c:2075（set_root 实现）、check.c:1353（format_fits 边界注释） | |

## 2. 调用点（挂载对照）

| 调用点 | 锚点 | 语义 |
|--------|------|------|
| 显式重写 | rewrite_key/rewrite_pos | 本任务挂载到 subvol 引擎公共 API |
| fsck/scrub | read.c:1243（scrub 读错误重写） | 域内：fsck 修复路径（T0195-T0200 fix_errors 框架）不消费 rewrite，后续候选 |
| GC 触发 | 范围外 | 域内无 GC |
| async worker | interior.c:3400+ | 域内无异步调度（D3），同步 API 等价 |

## 3. subvol 域内差异判定

| # | bcachefs 设施 | subvol 对应 | 判定 |
|---|--------------|-------------|------|
| D1 | btree_update 对象（update_start/update_done/update_free） | pending_interior 提交设施（update.rs:2219 `bch2_trans_commit_pending_interior`）+ 同步内存修改 | 域内差异：commit 全程持 fs 锁 + 单写者（同 T0204 D6），无 update 记账对象；parent/root 更新语义用 split/merge 已验证模式 |
| D2 | write_new_node 异步写队列 | journal-first `__bch2_btree_node_write`（io.rs:283）+ set_dirty 机制 | T0204 已论证设计替代：新节点 written==0 时事务内写盘（trans_commit_pending_interior 首段同款）；本任务走 split 模式（transition_state CLEAN + set_dirty + 写盘机制） |
| D3 | async_btree_rewrite work 队列 + BCH_WRITE_REF 记账 | 同步 API | 域内无异步调度；同步暴露 rewrite_key/rewrite_pos |
| D4 | `bch2_btree_node_format_fits` | 需移植：`btree_node_u64s_with_format`（interior.rs:1432 已有）+ `btree_buf_bytes`（interior.rs:5 已有）组合实现 | 严格小于语义保留 |
| D5 | rewrite_pos `BUG_ON(!level)` | 保留同断言 | root 重写走 rewrite 主体 parent==null 分支 |
| D6 | `bch2_btree_set_root`（interior.c:2075，含 journal 记账） | `bch2_btree_set_root_for_read`（interior.rs:223）+ root.key = child_ptr 自指针（split root 分支 interior.rs:800-850 已验证模式） | root 分支照 split root 分支同构 |
| D7 | `bch2_path_get_unlocked_mut` + `btree_path_take_new_node` | 同签名已有（split 用，interior.rs:740-750） | 照搬 |
| D8 | rewrite 不 restart（take_new_node 直接换新） | 同语义：rewrite 返回 0 不触发事务 restart（区别于 split 的 -4） | 照搬 |
| D9 | `bch2_btree_node_lock_write(b)` 前无额外锁升级（update_start 已做） | `bch2_btree_path_upgrade`（interior.rs:1688，T0204 引入） | rewrite 主体开头先升级路径锁（与 merge 同款） |
| D10 | emit_new_node_key + insert_node/set_root 分离 | parent/root 分支直接修改（merge 的 parent 键替换模式 interior.rs:1845-1920） | parent 分支：定位旧键（b 的 max_key）+ bch2_bset_insert 新键 + set_dirty(parent)；root 分支：child_ptr 自指针 + set_root_for_read |

## 4. 测试设计锚点

| # | 场景 | 断言 |
|---|------|------|
| T1 | 叶节点重写（rewrite_pos） | 键集不变、scan == 重写前、format/seq+1 断言、parent pivot 指向新节点（max_key 同） |
| T2 | 内部节点重写 | 子树访问正常（rewrite 后遍历全部叶键）、topology 校验通过 |
| T3 | root 重写（无 parent 分支） | set_root 生效、root.key 自指针、深遍历一致 |
| T4 | rewrite_key hash 不匹配 | -ENOENT、原节点不动 |
| T5 | 失败注入（alloc/锁冲突） | 原节点不动、无悬挂路径 |
| T6 | 崩溃恢复 | 重写提交后 drop 不 flush → 重开 → 键集一致、verify_all |
| T7 | 属性 | 随机 put/delete + 随机重写 → 模型一致 |
