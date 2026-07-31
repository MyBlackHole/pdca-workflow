# T0142 双轴代码与删除审查

对比基点：`4e800db`  
规范来源：T0142 `prd.md`、`design.md`

## 标准轴

- Blocking：0。
- Warning：0。
- 初审发现 apply 仅信任 manifest、不会再次确认目标仍无效，以及 archive 根存在 `task.json` 时 active dry-run 可能产生不可应用目标；两项均在真实删除前修复并增加测试。
- active 路径只允许 `pdca/tasks/` 直接子目录；解析后越界、archive、保护目录和通配符均拒绝。
- apply 在删除前完成全部目标的路径、数量、recoverability、digest 和严格无效状态预检。

## 规范轴

- Blocking：0。
- manifest 精确包含 16 个当前无效活跃任务、49/49 Git 跟踪文件、0 个不可恢复目标。
- 实际 Git 删除文件 49 个，全部位于 manifest 目标内，范围外删除为 0。
- records、knowledge、journal、archive 和当前任务的删除前后摘要全部一致。
- 全库校验从 23 个任务/16 个无效变为 8 个任务/0 个无效。
- 38/38 单元测试、12/12 场景夹具、doctor、skill index 和 archive dry-run 均通过。
- 未增加旧格式解析或迁移逻辑。

结论：标准轴 0 Blocking / 0 Warning；规范轴 0 Blocking，清理结果满足进入 Check 条件。
