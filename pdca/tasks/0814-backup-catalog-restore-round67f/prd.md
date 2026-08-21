# T0259 PRD：backup catalog 查询与可恢复 restore

## 输入与边界

依赖 T0258 发布的 immutable generation。负责仓库元数据查询、稳定分页和 restore，不修改 generation、对象或 retention policy。在线文件系统 `SYS_READDIR` 不是本任务的 catalog API。

## Catalog API

- `list-generations(repository, page_size, cursor)`。
- `stat-path(repository, generation, canonical_path_bytes, detail)`。
- `list-directory(repository, generation, directory_path_bytes, page_size, cursor)`，只返回直属 children；递归由调用方分页遍历。
- child name 按原始字节 unsigned lexicographic 排序，前缀较短者优先；不做 Unicode/locale/case 转换，不按类型分组。
- cursor 认证并绑定 repository、resolved generation/root digest、directory node、order version、last-key、limits 和 TTL lease。

## Restore API

- selector 支持 whole generation、directory subtree、single path。
- overwrite policy 支持 fail、skip、replace、rename；默认 fail。
- checkpoint 绑定 generation/root、selector、destination identity、policy 和 durable manifest position。
- 文件按 object/chunk 校验后同目录 rename，目录 metadata 最后应用；目标整树不宣称原子发布。

## 验收标准

- [ ] AC-1: 目录分页覆盖所有直属文件/目录且无重复遗漏；结果严格满足 unsigned byte lexicographic order，覆盖空字节以外的非 UTF-8、前缀、大小写和高位字节文件名。
- [ ] AC-2: current-ref 在翻页间切换仍读取首次解析 generation；cursor 篡改、跨目录/代/仓库复用、TTL/lease 过期明确失败。
- [ ] AC-3: page size 与 response bytes 有界，响应提供 raw name bytes、display escape、metadata summary、has_more 和 next cursor；1M 同目录遍历 RSS 有界。
- [ ] AC-4: stat/list 不读取 object payload或全量扫描 root manifest；目录 node range/index 损坏时 fail-closed。
- [ ] AC-5: whole/subtree/single restore 覆盖 regular/chunk/pack/sparse/hardlink/symlink/FIFO/xattr/ACL，并通过 digest 与 metadata 校验。
- [ ] AC-6: restore 在 object 写入、partial sync、rename、目录 metadata 和 checkpoint 各崩溃点可重试，不越过目标 confinement，不误覆盖 policy 外路径。
- [ ] AC-7: generation 被 retention/GC 删除时，新请求返回 not-found；活动 cursor/restore lease 在 TTL 内阻止依赖对象被 GC，过期后返回 stale 而非读取缺失数据。
- [ ] AC-8: repository/generation/path-prefix 授权在 cursor 和 object 解析前执行；未授权响应不泄露路径存在性，查询/restore 有主体级限额和结构化审计。
- [ ] AC-9: selective restore 的 hardlink anchor 不在 selector 时物化独立 regular file；完整 group selector 才恢复 hardlink，不得链接到 selector 或 destination 外。
- [ ] AC-10: metadata-index off generation 的 list/stat/pagination/restore 与 on 结果一致；查询直接读取 immutable directory nodes，不尝试打开本地 SQLite/LMDB 索引。

## 声明的测试接缝

- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/backupctl.cpp
- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/tree_checkpoint.cpp
