# T0190 discard worker in-flight 与重试恢复结论

## 结论

**通过（engine-local 范围）**。discard worker 的 in-flight 去重、EEXIST/EAGAIN 边界、
状态收束与 process-style restart 再发现已完成。

## 验证

- 重复 queue 返回 EEXIST 类 `-17`；
- boundary 未满足返回 EAGAIN 类 `-11` 且保留队列项；
- 成功 discard 后移除 in-flight 并保持派生索引一致；
- 重启从持久化 need_discard btree 重新发现未完成工作；
- workspace 191 测试通过，fmt/diff gate 通过。

## 边界

真实 block-device TRIM、完整 GC/LRU、stripe/EC 与 VFS 不属于本任务范围。
