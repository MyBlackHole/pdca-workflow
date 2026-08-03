---
schema: pdca.asset/v1
id: T0206-0803-fsck-scrub-rewrite
phase: check
source_ids: [source-anchors, check-evidence, ac6-status]
---

## 上下文

T0206 目标：fsck/scrub 自动触发 btree 节点重写（need_rewrite 消费
路径），含读路径自动触发（用户 P2/D3 裁决）。AC-1..AC-6。

本次为**部分完成 PDCA**：AC-1..AC-4 完成，AC-5 部分完成（验证测试
已写，暴露 root 分支 extent 缺陷未修复），AC-6 未开始。

## 假设与结果

| 假设 | 结果 |
|------|------|
| AC-1 锚点记录完整（读完成触发/scrub/async work 语义链 + 差异判定） | ✓ 通过，ac1-source-anchors.md 含 D1-D9 逐项判定（本 Check 补 D9） |
| AC-2 读路径 need_rewrite 设置（read.c:567/844/871 对齐） | ✓ 通过，io.rs:662-663/742-743 设置点 + 硬错误维持错误码 |
| AC-3 读完成自动触发（read.c:968 + interior.c:3395-3462） | ✓ 通过，入队 + 无锁时机 drain（D1 死锁实测驱动）+ EngineFsGuard，3 测试全过 |
| AC-4 fsck 修复模式触发 | ✓ 通过（差异记录型）：用户裁决 D9——上游 fsck 节点修复=读完成触发（AC-3 已实现），显式磁盘 scrub（read.c:1169-1328）仅 move.c 数据移动路径调用，engine journal-first 无节点扇区可 scrub；域内 fsck 节点修复路径 = FixErrors::Yes 遍历触发 + verify_all / No 只检查 |
| AC-5 修复后验证 | ✗ 部分完成：rewritten_node_revalidates_on_reopen 测试已写但失败（-2）——重写后 slot.key 无 extent ptr（root 分支 child_ptr 仅 mem_ptr 寻址）→ 重开读盘 bch2_bkey_ptrs_c 空返回 -2（io.rs:454）；上游语义 slot.key 保留原 extent（覆盖写原位置）。verify_all / 崩溃注入收敛未交付 |
| AC-6 全量门禁 | ✗ 未开始（依赖 AC-5 修复） |

## 分析

1. **AC-3 死锁裁决验证成立**：get 路径读完成同步触发重写会与外层
   路径锁互斥死锁（实测 60s+ 挂死），入队 + 无锁时机 drain（root_read
   末尾 / EngineFsGuard::drop）为必要设计，对齐上游 pending 队列
   （interior.c:3440-3462）+ async work 解耦语义（D1/D7）。
2. **AC-4 差异裁决（D9）**：engine journal-first 下节点从不落盘
   （探针实测：10 键 + sync 后文件 0 个节点 magic 词），磁盘节点
   scrub 无对象；fsck 节点级修复 = AC-3 读完成机制 + FixErrors
   门控，域内无新增代码，验证责任转交 AC-5。
3. **AC-5 暴露的 root 分支 extent 缺陷**（本 Check 关键发现）：
   interior.rs root 分支 `child_ptr(n)` 生成的自身指针键仅 mem_ptr
   寻址、无 extent ptr（T0205 journal-first 域内模式），重写后
   slot.key 丢失磁盘位置 → 重开 root_read 读盘失败 -2。上游语义：
   set_root 后 root 记录保留原 extent（覆盖写原位置）。修复方向：
   root 分支 bkey_copy 前合并旧 extent ptr。

## 失败原因（partial）

AC-5/AC-6 未完成：AC-5 验证测试失败暴露 root 分支 extent 缺陷
（非预期行为，需修复）；AC-6 依赖 AC-5 修复后执行。已完成的
AC-1..AC-4 证据充分（收敛验证 valid:true）。

## 适用边界

- 已完成部分（AC-1..AC-4）结论可信：读完成触发链路（入队 + drain +
  错误忽略集）有 3 个专项测试 + 243 测试基线支撑。
- AC-5 缺陷影响面：仅 root 重写后重开的 io 层场景（slot.key 无
  extent）；engine journal-first 模式不受影响（不读盘）。
- 未完成部分不因本次 partial verdict 视为通过。

## 下一轮建议

1. 修复 root 分支 extent 保留（合并旧 extent ptr 到 child_ptr(n)
   生成的键，对齐上游 set_root 语义）→ 修复 rewritten_node_
   revalidates_on_reopen。
2. 补 AC-5 剩余：重写提交后 verify_all 通过、崩溃注入收敛（fallback
   = io 层重开一致 + fsck 故障矩阵已有）。
3. AC-6：全量 `cargo test --lib` + fmt + diff gate，单项 <1min。
4. 完成 AC-5/AC-6 后重新收敛验证并转 Check（本次 partial 需跟进任务
   关闭）。
