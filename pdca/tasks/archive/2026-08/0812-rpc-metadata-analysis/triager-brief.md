# Triage Brief

## 分类

- category: enhancement
- scenario_type: research
- 请求类型：对现有实现进行代码分析并输出文档，不涉及代码修改。

## 查重

- 当前 `$PDCA_HOME/pdca/tasks/` 无已有活跃任务。
- 仓库已有 `rpc/README.md` 与 `rpc/tests/metadata.cpp`，但没有针对海量元数据管理机制的系统分析文档。

## 事实核验

- `rpc/rpc-metadata.c` 使用 LMDB 单库，以目录项复合键定位 `meta_value_t`。
- `meta_add_path` 按路径组件逐级查找/创建目录项；`meta_get_path`、`meta_path_to_inode` 按同样方式解析。
- `meta_read_directory_callback` 和 `meta_find_directory_entries` 使用 LMDB cursor 的范围定位与顺序扫描。
- inode 计数器从持久化的 `ROOT_INODE/inode` 记录加载，并在事务提交时回写。
- RPC 备份/恢复路径以 `META_MAX_SIZE`（当前为 `UINT64_MAX`）打开元数据库；这使容量策略成为海量场景的重点分析项。

## 信息缺口

- 需要明确说明实际空间占用不能仅由 `map_size` 推断，并评估键值布局、路径深度、目录扫描、事务粒度和异常恢复风险。
- 需要区分代码事实、性能推断和后续建议。

## 推荐下一步

按 Plan→Do→Check→Act→Archive 执行：完成范围与验收标准后，基于源代码和现有测试形成分析文档，做静态一致性复核，并记录结论与处置建议。
