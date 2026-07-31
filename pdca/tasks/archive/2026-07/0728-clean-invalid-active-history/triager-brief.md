# T0142 Triage

- 分类：enhancement
- 场景：development
- 查重：T0136 清理过不兼容 archive；本任务处理尚未覆盖的 active direct children，不重复。
- Claim 核验：`validate-workflow --all` 返回 23 个任务、16 个无效，全部仅含 `SCHEMA_INVALID`；16 个目录的 49 个文件全部被 Git 跟踪。
- 风险：删除属于破坏性操作；必须先生成精确 manifest，再以目标数量、digest 和 Git 可恢复性三重确认执行。
- 推荐：扩展现有审计工具的路径边界，不使用直接 `rm`，不保留旧 schema 兼容逻辑。
