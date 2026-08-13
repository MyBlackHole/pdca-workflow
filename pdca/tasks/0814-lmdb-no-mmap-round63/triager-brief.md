# T0249 Triage Brief

## 分类

- category: enhancement
- scenario_type: development
- 来源：T0248 Check 阶段暴露 LMDB RSS 超过 SQLite 约 38%，用户明确要求改用关闭 mmap 的 LMDB 分支。

## 事实验证

- 当前 `/usr/include/lmdb.h` 是标准 LMDB API：没有 no-mmap 开关；`MDB_NORDAHEAD` 只关闭内核预读，不能关闭 mmap。
- 当前代码调用 `mdb_env_set_mapsize`、`mdb_env_info` 和 `madvise`，并链接系统 `/usr/lib/liblmdb.so`，因此当前不是 no-mmap backend。
- 目标分支以 `MDB_VL32` 头文件能力作为 feature probe；仅有显式 include/library 仍不足以把系统标准 LMDB 冒充为 no-mmap 实现。

## 去重

- T0248 已完成 TREE checkpoint 和标准 LMDB adapter；本任务只承接 no-mmap backend 选择、构建探测、运行验证和 RSS 复测。
- 未发现已有 active task 专门覆盖 no-mmap LMDB。

## 推荐下一步

增加显式 `LMDB_NO_MMAP` 构建配置和 no-mmap feature probe，禁止普通 LMDB 在该配置下通过；移除 mmap-only 调用，保留 MetadataStore procedural contract，完成 SQLite/LMDB/Make/CMake/TLS 矩阵与 100k benchmark。
