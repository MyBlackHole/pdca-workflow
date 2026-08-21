# T0253 Triage Brief

## 分类

- category: enhancement
- scenario_type: development
- reason: 用户明确指出现有断点续传方案性能严重下降，并要求检索生产实现后重新选择架构。

## 查重与关系

- T0252 已完成 disk-backed TREE checkpoint 的 Do 实现，但尚未进入 Check/Act；本任务作为其后续架构审查与性能重构，不能把 T0252 的单次通过当作生产结论。
- T0248/T0250 涉及 LMDB 增量索引和 no-mmap 供应链；本任务不假设系统存在 `MDB_VL32`，仅复用已验证的 metadata 接口和实验结果。

## 已验证问题

1. `src/backupctl.cpp` 对每个扫描条目执行一次 checkpoint SQLite point lookup。
2. 当前 checkpoint flush 在远端 ACK 后执行 journal append、journal `fsync`、SQLite transaction 和 commit；扫描批次结束即可能触发该路径。
3. 现有合成基准只证明 RSS 降低，不能证明热路径吞吐没有严重回归，也没有报告 fsync 次数、CPU、I/O 等待和不同存储介质结果。
4. 当前真实 1M 文件测试受环境 inode 上限限制，不能替代生产级吞吐证据。

## 外部生产实现对比

- rsync 使用 partial/partial-dir 保留单文件临时结果，现代版本可原地更新 partial 文件；它不要求每个文件完成时同步一个全局数据库。
- restic 在中断后重新扫描源树，依靠已持久化的内容索引复用已上传 blob；索引周期更新，允许有限进度重做，而不是每个文件都做强同步。
- restic 的存储顺序是先写不可变 pack，再写索引，最后写 snapshot；崩溃时未被 snapshot 引用的 pack 是可清理的孤儿数据，不破坏已提交快照。
- Borg 使用周期性 checkpoint archive，恢复依靠重新执行并复用已存在的数据，而非要求每条扫描记录都同步提交。

## 推荐方向

优先采用两条明确分离的路径：

- 单文件：保留 `.partial`、源指纹、offset、最终校验和原子 rename；不要引入全局 TREE checkpoint lookup。
- 海量目录：改为批量/不可变 block ledger 或批量 manifest checkpoint；远端数据提交幂等，checkpoint 按时间或字节阈值落盘，允许声明范围内的重复发送。若继续使用 SQLite，只能作为批量索引/恢复工具，不能逐文件 `fsync`/COMMIT。

## 信息缺口

- 需要在 tmpfs、SSD、旋转盘或网络盘上分别测量当前方案与候选方案。
- 需要明确可接受的重复发送窗口和断电后最多重做的数据量。
- 需要注入 ACK 后、journal fsync 后、索引提交中断三类故障，验证 fail-closed 和幂等恢复。
