# T0261 Research Report

## 结论摘要

发现了可提升空间，而且本轮自我审查有效：记录层的严格 invariant 从真实历史中发现 5 条不可投影事件；随后真实命令复现证明当前 audit 的可变 fallback identity 能稳定制造同类身份分裂。与此同时，普通任务创建路径没有统一原子分配器，隔离并发实验证明两个创建者可以实际写出相同 next ID。

推荐结论是 `partial` 而不是 `confirmed`：H1、H2、H4 已有独立 oracle；H3 的“当前机制可制造分裂”已证实，但历史 T0252 的具体搬移动作没有 receipt，不能声称已定位具体操作者/命令。

## 根因链

```text
instruction-driven task creation
  -> scan max ID without shared lock
  -> concurrent sessions may create distinct slugs with same task ID
  -> parent/dependency/record discovery becomes ambiguous

Do audit before meta.record exists
  -> flow_audit falls back to task.id and writes create-only events
  -> meta.record is added later
  -> subsequent audit writes under full record identity
  -> any later directory consolidation leaves payload/path mismatch
  -> strict projection rejects the dataset
```

两条链相关但不等价：collision 是引用歧义放大器；record fallback 才是已复现的 event identity 分裂直接机制。

## 真实性边界

- 真实历史：23 个 collision ID、47 个不同 slug、5 条 mismatch、T0252 前后两种 payload identity、Git first-add 状态。
- 可执行复现：普通 scan→create 产生重复 ID；真实 transition 命令产生两个 record 目录；promotion 并发负对照通过。
- 未知：23 个历史 collision 各自由哪个会话/命令生成；T0252 的 5 个文件由哪个命令归并进完整 record 目录。
- 因此未知部分标记 inconclusive，不用推测补齐。

## 建议

下一周期实施组合方案：统一原子 task 创建入口 + task 出生时不可变 record identity + audit 取消 task.id fallback + 只用显式 relocation receipt 兼容历史。先写并发、身份不可变、路径一致性测试，再开发最小 seam；真实观察 14 天或 20 个任务后才能判定改进有效。

不应在本 research task 中直接修改实现，也不应重写任何历史 task、record 或 occurrence。
