# T0198 检查证据（check-evidence）

## AC-1：修改前逐段记录上游锚点

证据：`ac1-source-anchors.md`（实现前撰写）。
- fix_errors 门控：`fs/init/error.c:433-463` `bch2_fsck_err_opt`
  （FSCK_FIX_exit/yes/no/ask 分支，opts.h:132 枚举）；engine-local
  FixErrors::No/Yes 两值对齐 FSCK_FIX_no/yes。
- 修复动作：`fs/alloc/check.c:144-190` `bch2_check_alloc_key`（双向：
  need_discard 补键 175-179、freespace 补/删键 185-188）、
  `alloc/check.c:388-423` `bch2_check_discard_key`（删除）、
  `alloc/check.c:352-386` `delete_freespace_key`（每键单事务 commit）。
- CLI：`fsck.rs:32-46`（-y auto_repair / -n no_repair / -f force）、
  `fsck.rs:248-250`（-y → fix_errors=yes）、`fsck.rs:266-269`
  （-n → nochanges + fix_errors=no）、`fsck.rs:457-460`（fs.exit()
  关盘落盘）。
- engine-local：fsck_image（engine.rs:2424）、verify_bucket_indexes
  （engine.rs:618-668 expected 集）、set_need_discard_index
  （engine.rs:2674-2690 bit_mod+commit 模板）、rebuild_derived_state
  清除范围（engine.rs:2014-2019 只清 4/5/8 树，need_discard 树保留）。

## AC-2：库 API 修复模式，动作与上游一致，修复后 verify_all 通过

- `fsck_image(path, FixErrors)` 单入口（对齐 bch2_fs_fsck_errcode +
  fix_errors 选项）；`repair_derived_indexes` 双向修复：stale
  freespace/need_discard 键删除（对齐 delete_freespace_key /
  bch2_check_discard_key）+ 缺失键补齐（对齐 bch2_check_alloc_key
  alloc/check.c:175-188）；每键单事务 `bit_mod_sync`
  （-12 ENOMEM 重试，engine.rs:2674-2690 模板）。
- 修复后 `flush_journal` 落盘（对齐 fs.exit() fsck.rs:457-460，实测
  缺落盘时 reopen 后脏键复活）再 verify_all。
- 测试：`fsck_image_yes_mode_deletes_stale_need_discard_key`（脏键删除
  + reopen 后 verify_all Ok + 树中无脏键）、`fsck_image_yes_mode_
  restores_missing_need_discard_entry`（缺失补键 + reopen 验证树中
  有键）、`fsck_image_no_mode_leaves_image_unchanged`（No 不改镜像，
  两次报告同错，Yes 仍可修复）。

## AC-3：修复范围边界（守卫错误名不修复）

- 修复动作仅覆盖 alloc<->派生索引一致性（FreespaceSet /
  NeedDiscardSet，verify_bucket_indexes 报出的两类）。
- OpenBucketFree / NotRwBucketFree 为纯运行期内存不变量（open_buckets
  / rw_devs 不持久化，reopen 后 open 集为空），fsck 流程天然不会遇到；
  上游对 open 桶/not_rw 桶为 discard skip 语义（bch2_bucket_is_open_safe
  / bch2_dev_get_ioref 跳过），无 fsck 修复动作——修复函数不触碰，
  verify_all 对守卫检查行为不变（T0194 语义保留）。

## AC-4：CLI -y 修复模式

- `subvol-fsck -y`：健康镜像退出 0 + `OK (repaired)`（集成测试
  `fsck_cli_yes_mode_healthy_image_exits_zero_with_repair_output`）；
  打开失败仍退出 2（-y 同路径）；`-n` 与 `-y` 互斥退出 2（集成测试
  `fsck_cli_no_repair_and_yes_are_mutually_exclusive`）。
- 损坏（索引不一致）镜像的 CLI 级构造不可达：脏键注入需内部 bit_mod
  API（公开 API 无此手段），且 open_persistent 会重建 freespace 树
  （T0195 已澄清）——修复语义由库级 4 测试承担（实现期澄清 round 3
  已记录口径）。

## AC-5：修复原子性

- 每键独立事务（bit_mod_sync 单事务/键）；-12（ENOMEM）realloc 重试
  与既有事务路径一致；非索引错误（Io/事务）经 `?` 传播中止修复，
  不部分修复后假装成功（对齐上游 ret 传播）；修复前不预判、修复后
  verify_all 双保险。

## AC-6：workspace 全量测试、fmt、diff gate

- `cargo fmt` 通过；`cargo test --workspace` 全绿：220 lib + 10
  btree_proptest + 5 fsck_cli = 235；单项 ≤1min（btree_proptest
  44.04s）。
- 提交：subvol `5806e58`（4 files：engine.rs +278、bin +32、lib +4、
  fsck_cli +46）；fsck_image 签名变更 3 调用点同步。

## 结论

六项 AC 全部达成；修复模式实现"检查→修复→落盘→复验"闭环，need_discard
脏键（rebuild 不覆盖的树）为真实持久化修复场景；守卫错误名保持只读
校验语义（skip 对齐）。
