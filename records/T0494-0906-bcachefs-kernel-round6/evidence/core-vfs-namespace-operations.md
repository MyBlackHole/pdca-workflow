---
schema: pdca.asset/v1
id: ontology:domain/core-vfs-namespace-operations
type: domain
layer: Knowledge
status: active
summary: SEEK双检 + splice直通 + fallocate四分支 + 配额迁移
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 文件空洞定位、零拷贝传输、空间预分配、跨卷改名、NFS导出场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/vfs/io.c 在仓库中存在且含 bch2_fallocate_dispatch 定义"
- name: constraints
  desc: 命名空间操作前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认脏页确认、配额迁移、代际校验三条前提在引用代码中有对应实现"
---

# VFS命名空间高级操作集

沉淀自 T0494（内核第六轮）。对照 bcachefs `fs/vfs/io.c`、
`fs/vfs/fs.c`、`fs/vfs/pagecache.c`。

## 核心概念

1. **SEEK_DATA/HOLE 双检**：仅两模式走定制；先查 extent 键再
   用页缓存修正；空洞须解锁后确认非全脏才停，否则继续搜，
   超尾钳位（`bch2_seek_data`、`bch2_seek_hole`）。
2. **splice/THP/remap 直通**：读/写/大页直通通用实现；重映射
   内做双 inode 锁 + 阻塞页缓存 + 等 DIO + 失效 + 配额预留 +
   扇区记账（`bch2_remap_file_range`）。
3. **fallocate 四分支**：防 EROFS 引用计数；加锁等 DIO 后按
   KEEP/ZERO→分配、PUNCH→打洞、INSERT/COLLAPSE→移位分发；
   退出清预留区间（`bch2_fallocate_dispatch`）。
4. **fsync 三段 + 延迟回写**：文件刷盘 + 元数据同步 + inode
   刷盘；EROFS 转 EIO；元数据脏经延迟 work 回写，驱逐时取消
   并断言配额已放（`bch2_fsync`、`bch2_vfs_writeback_fn`）。
5. **rename/link 配额迁移**：仅支持三模式；覆盖先刷盘；四锁 +
   只读检查后跨项目调配额迁移；whiteout 建字符节点；错误回
   滚（`bch2_rename2`）。
6. **NFS 导出 + 冻结只读**：fid 含代际，非目录带父；代际失配
   返 ESTALE；冻结加写锁转只读，紧急只读则空返
   （`bch2_encode_fh`、`freeze/unfreeze`）。

## 复用指南

- 空洞定位必须 extent 与页缓存双检，单检必误报。
- 重映射/fallocate 必须先阻塞页缓存 + 等 DIO，禁止带脏页改
  布局。
- 跨配额域改名必须迁移配额，禁止只改属主不结转。
