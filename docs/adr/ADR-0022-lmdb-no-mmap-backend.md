# ADR-0022：LMDB 使用显式 no-mmap 分支

## 状态

Proposed

## 背景

标准 LMDB 的核心读路径依赖文件 mmap；`MDB_NORDAHEAD` 只影响内核预读，不关闭映射。T0248 的 `madvise` 只能降低部分驻留页，不能满足 no-mmap 部署约束。

## 决策

LMDB backend 在 no-mmap 目标上必须由构建参数指向显式的 no-mmap header/library，并且 header 必须暴露 `MDB_VL32` 页管理能力。适配层不得调用标准 LMDB 映射信息或 `madvise` API；事务、键值编码和持久化由 no-mmap 分支提供的兼容 C API 承担。

## 后果

- 普通系统 LMDB 不得被静默当作 no-mmap 实现。
- no-mmap 的吞吐可能低于标准 mmap LMDB，必须以实测 RSS/吞吐做取舍。
- 构建环境需要显式安装并传入 no-mmap 分支的 include/library 路径。
