# T0257 PRD：immutable object/pack 与 segmented manifest store

## 输入与边界

负责 repository 的 immutable 数据层，不负责源端枚举、wire ACK、current-ref、retention policy 或 restore 物化。输入是文件数据、metadata records 和稳定 content-id domain。

## 实现范围

- whole-file objects、大文件 chunks、小文件 packs、sparse extent map 和 pack index。
- cryptographic content id 使用类型/版本 domain separator；existing object 校验 length/type/digest。
- manifest shard segments 和 bounded fan-out root tree，全部支持流式构建/读取和 checked `uint64_t` 计数。
- temp write、file sync、content-id rename、repository directory sync 的崩溃安全提交。

## 验收标准

- [ ] AC-1: object/chunk/pack/manifest 任一写入与 rename 崩溃点恢复后只出现完整 immutable item 或无 item，不接受截断/坏 digest。
- [ ] AC-2: 相同 content id 相同内容幂等成功，不同 type/length/content 冲突 fail-closed；并发 publish 不覆盖已有对象。
- [ ] AC-3: 100k/1M records 和超大单目录的 manifest 构建/遍历内存、FD 与 open runs 有界，不一次载入全部路径。
- [ ] AC-4: small-file pack index、large-file chunk list 和 sparse extent map 损坏均被检测，且可从权威数据安全重建的派生索引不参与发布判定。
- [ ] AC-5: global count、segment/object sequence 和 byte totals 使用 checked `uint64_t`，单 record/pack/frame 使用显式有界长度。
- [ ] AC-6: metadata-index on/off 生成完全相同语义的版本化 manifest；manifest 不依赖本地 SQLite/LMDB 文件即可流式构建、校验和读取。

## 声明的测试接缝

- seam: tests/tree_checkpoint_paged_benchmark.sh -> src/tree_checkpoint.cpp
- seam: tests/unit.cpp -> src/tree_checkpoint.cpp
