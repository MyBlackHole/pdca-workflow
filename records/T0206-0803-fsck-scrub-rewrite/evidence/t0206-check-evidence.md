# T0206 Check 阶段证据（部分完成 PDCA）

记录时点：2026-08-03，AC-1..AC-4 完成，AC-5 部分完成（测试已写，
暴露 root 分支 extent 缺陷未修复），AC-6 未开始。

## AC-2 证据：读路径 need_rewrite 设置（read.c:567/844/871 对齐）

- 设置点 1（键损坏截断）：io.rs:662-663 `set_btree_node_need_rewrite`
  + `set_btree_node_need_rewrite_error`（对齐 read.c:567-568）。
- 设置点 2（ptr_written==0）：io.rs:742-743 `set_btree_node_need_rewrite`
  + `set_btree_node_need_rewrite_ptr_written_zero`（对齐 read.c:871-872）。
- 硬错误（bad magic/seq/id/level/min/max/format）维持错误码返回
  （io.rs:482-503），可修复错误截断/删键后继续（FSCK_CAN_FIX 门控，
  对齐 read.c:177-192 btree_err 分类）。
- 测试：root_read_need_rewrite_triggers_sync_rewrite（损坏键 u64s
  5→4 → 截断修复 + need_rewrite → 重写）。

## AC-3 证据：读完成自动触发（read.c:968 + interior.c:3395-3462）

- `bch2_btree_node_need_rewrite_add`（interior.rs，入队，key 拷贝
  对齐 interior.c:3440-3448）+ `bch2_do_pending_node_rewrites`
  （interior.rs，drain 对齐 interior.c:3462，忽略 -2/-5 其余报错，
  对齐 interior.c:3409-3412 错误忽略集）。
- 触发点 1：`bch2_btree_node_get_noiter_unlocked` 读成功 + need_rewrite
  入队（io.rs，对齐 read.c:968 endio 排队语义）。
- 触发点 2：`bch2_btree_root_read` 解锁后入队 + 立即 drain（io.rs，
  root_read 上下文无外层路径锁）。
- engine 集成：EngineFsGuard::drop drain（engine.rs，操作边界执行，
  实测 get 路径内同步重写与外层路径锁互斥死锁——D1 证据）。
- 重写失败传播：rewrite_key 失败返回码传播，drain 仅忽略已对齐的
  上游忽略集（D7）。
- 测试（3 个，全部通过）：
  - root_read_need_rewrite_triggers_sync_rewrite（root 触发点 +
    seq 101→102 + 键重打包）
  - child_read_need_rewrite_triggers_sync_rewrite_via_iter（get 触发
    点 + 入队延迟语义）
  - corrupt_root_region_does_not_affect_journal_first_recovery
    （engine journal-first 无节点读盘契约，D8）

## AC-4 证据：fsck 修复模式触发（用户裁决：差异记录 + AC-5 验证）

- 用户裁决（question 确认，0803）：D9 判定——上游 fsck 节点修复 =
  遍历读 → read.c:968 读完成触发（AC-3 已实现）；显式磁盘 scrub
  （read.c:1169-1328）仅 move.c:326 数据移动路径调用，engine
  journal-first 下节点从不落盘（探针实测 10 键 + sync 后文件 0 个
  节点 magic 词）→ scrub 无对象。
- 域内 fsck 节点修复路径 = FixErrors::Yes 时遍历触发 AC-3 读完成
  重写 + verify_all 校验；FixErrors::No 只检查不重写（对齐 -n
  nochanges 不落盘语义）。
- AC-4 域内无新增代码；验证责任转交 AC-5。
- 产出：ac1-source-anchors.md D9 差异记录 + 第 6 节判定记录。

## AC-5 证据（部分完成）

- 已交付：rewritten_node_revalidates_on_reopen（io.rs）——损坏
  root → root_read 重写（覆盖写盘 @ 64，seq 101→102，slot.key
  更新）→ 模拟关闭重开（slot key 取新 key + mem_ptr 清零）→ 第二
  次 root_read 重新读盘校验 → 断言读解析通过 / 无 need_rewrite /
  seq 持久化 / 键集 / 拓扑校验。
- **失败（Check 时点）**：返回 -2——重写后 slot.key 无 extent ptr
  （interior.rs root 分支 child_ptr(n) 仅 mem_ptr 寻址）→ 第二次
  root_read 读盘 bch2_bkey_ptrs_c 空返回 -2（io.rs:454）。上游语义：
  重写 root 后 slot.key 保留原 extent ptr（覆盖写原位置）。
- 未交付：verify_all 通过（engine 层无节点重写场景）、崩溃注入收敛
  （fallback = io 层重开一致 + fsck 故障矩阵已有）。

## AC-6：未开始（全量测试/fmt/diff gate）

## 全量测试基线（Check 时点）

- `cargo test --lib`：243 passed, 1 failed（rewritten_node_
  revalidates_on_reopen，即 AC-5 未完成项），~10.5s。
