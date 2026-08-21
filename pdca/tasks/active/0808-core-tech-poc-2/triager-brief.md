# Triage Brief — T0229 备份引擎核心原语实证（第二批）

## 需求来源
用户选定"新一批技术 POC"，延续 T0225（第一批 12-17：零拷贝/AEAD/哈希/布隆/帧复用/RS纠删）。

## 分类
- 类型：enhancement（POC 实证）
- scenario_type: development

## 查重
已覆盖场景（POC 仓库 scenarios/01-17）：
- 01-04 连接生命周期（FIN/EOF/重连/残留数据）
- 05-06 CDC 切块/滚动校验和
- 07 压缩加密顺序、08 并行切块、09 epoll、10 限流
- 12 零拷贝、13 AEAD、14 哈希选型、15 布隆去重、16 帧复用、17 RS(5,3)

**本批新场景（18-23）无重复**，聚焦存储层与恢复层原语。

## Claim 验证
已有系统库可用性已在 T0225 验证（OpenSSL/libsodium/libblake3/libxxhash/libzstd）；
zstd 的 `-lzstd` 需确认。其余为纯 C/系统调用实现，无外部依赖。

## 范围（6 场景）
1. **18-dedup-chunk-store**：去重块存储引擎（块写入/命中/索引，bloom 前置 + 指纹二次确认）
2. **19-streaming-crypto-chunk**：大文件流式分块 AEAD 加密（CEK 派生、nonce 管理、随机访问解密）
3. **20-compress-codec-bench**：压缩选型（zstd/lz4/gzip 压缩比 vs 吞吐权衡）
4. **21-dedup-refcount-gc**：去重块引用计数与 GC 回收（块释放、孤儿回收）
5. **22-integrity-verify**：全量校验（回读比对指纹、增量校验、损坏定位）
6. **23-wal-crash-recovery**：预写日志 + 崩溃恢复（半写块检测、截断恢复）
