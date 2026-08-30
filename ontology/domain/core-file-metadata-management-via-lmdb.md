---
schema: pdca.asset/v1
id: ontology:domain/core-file-metadata-management-via-lmdb
type: domain
layer: Knowledge
status: active
summary: 文件元信息的 LMDB 管理模型
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 由领域实践与测试验证
---

# 文件元信息的 LMDB 管理模型

适用于本仓库 `rpc/rpc-metadata.c` 当前实现的维护与评审。

## 核心模型

每个文件/目录对应一条 LMDB 记录：键由父目录 inode、名称和类型组成，值为 `meta_stat_t`。`meta_stat_t` 保存 inode、大小、UID、GID、权限/文件类型和修改时间。

## 生命周期

- 新增或更新：按路径逐级定位目录；新对象分配 inode，已存在对象保留 inode 并更新属性。
- 查询：按父 inode/名称查找，或从根 inode 开始逐级解析路径。
- 目录读取：按父 inode 范围使用 LMDB cursor 顺序读取。
- 删除：删除目录项，不回收 inode，也不递归删除子项。
- 持久化：写事务提交时回写下一个 inode；读取使用事务快照。

## 规模关注点

元信息数量增长会直接增加 LMDB 记录和页空间；路径查询随深度增加，单目录读取随条目数增加。容量应以实际名称长度、目录扇出和事务批量压测确定，不能把 `UINT64_MAX` map size 视为无限容量。

来源：`rpc/rpc-metadata.c`、`rpc/rpc-metadata.h`、`libs/lmdb_dict.c`。
