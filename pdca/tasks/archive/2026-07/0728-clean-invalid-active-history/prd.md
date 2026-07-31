# 清理旧格式活跃任务并恢复全库严格校验信号

## 问题陈述

- 当前 `validate-workflow --all` 检查 23 个任务，其中 16 个旧格式活跃任务因 `SCHEMA_INVALID` 固定失败。
- 固定噪声会掩盖新任务的真实错误，使全库校验不能作为 AI 的健康信号。
- 用户已明确不保留旧数据兼容规则，并批准清理历史数据。

## 已核验事实

- 目标数：16 个活跃任务直接子目录。
- 文件数：49；Git 跟踪数：49。
- Git 可恢复目标：16；不可恢复目标：0。
- `records/`、`knowledge/`、`pdca/journal/` 不在目标内。
- 现有 `audit-history.py` 只允许 archive scope，不能安全应用于当前目标。

## 解决方案

- 扩展现有历史审计工具，增加显式 active scope。
- dry-run 只选择 `pdca/tasks/` 的直接子目录中严格校验失败的任务，排除 archive 和当前有效任务。
- apply 阶段继续强制：禁止通配符、路径边界、目录存在、digest 未变化、确认数量完全一致。
- 未完全由 Git 跟踪的目标默认拒绝；本轮不使用不可恢复覆盖。
- 登记 dry-run manifest、删除结果和清理后全库验证结果。

## Seam 分析

### 测试接缝

- 目标解析 Seam：输入 scope 和路径，返回受限目录或稳定拒绝。
- dry-run CLI Seam：输入 active scope，输出带 digest、跟踪统计和恢复命令的 manifest。
- apply CLI Seam：输入 manifest 与确认数量，只删除全部预检通过的精确目标。
- 仓库结果 Seam：执行前后的保护资产摘要和 `validate-workflow --all` JSON。

### 验收可测性

- 使用临时 Git 仓库构造有效、无效、不可恢复、digest 漂移和越界目录。
- apply 必须先完成全部目标预检，再开始删除，确保任一目标失败时零删除。
- 真实清理以 manifest 固定目标集合，不使用 glob 或动态命令替换执行删除。

## 用户故事

1. 作为 AI 执行者，我希望全库校验没有固定旧错误，以便新失败能成为可信信号。
2. 作为维护者，我希望删除前得到精确、可恢复的 manifest，以免清理越界或误删证据资产。

## 实现决策

- `audit-history.py` 的 dry-run 增加必填 `--scope active|archive`。
- manifest 必须记录 scope；apply 从 manifest 读取 scope 并执行对应路径边界。
- active scope 只允许 `pdca/tasks/` 的直接子目录，显式拒绝 `archive`。
- archive scope 保持只允许 `pdca/tasks/archive/` 下的非根目录。
- 不接受缺 scope 的旧 manifest，不增加兼容分支。
- 删除仍通过现有 digest 和 Git recoverability 机制完成。

## 测试决策

- 扩充现有 operations 测试，验证 active dry-run、路径保护、确认数量、digest 漂移、不可恢复与精确删除。
- 复跑全部单元测试、12 个确定性夹具、doctor、skill index。

## 验收标准

- [ ] active dry-run 精确列出 16 个目标，且目标集合与当前 `validate-workflow --all` 的无效活跃任务一致。
- [ ] manifest 显示 16/16 目标 Git 可恢复、49/49 文件被跟踪。
- [ ] active scope 拒绝根目录、archive、records、knowledge、journal、通配符和任意越界路径。
- [ ] apply 在确认数量不等于 16 时拒绝且不删除任何目标。
- [ ] apply 在任一目录 digest 变化时拒绝且不删除任何目标。
- [ ] apply 默认拒绝任何 Git 不可恢复目标。
- [ ] 精确 manifest 应用后仅删除清单中的 16 个目录。
- [ ] `records/`、`knowledge/`、`pdca/journal/` 和严格任务的前后摘要一致。
- [ ] 清理后 `validate-workflow --all` 返回 valid 且 `invalid_count=0`。
- [ ] 现有及新增测试、12 个确定性夹具和 doctor 全部通过。

## 范围外

- 将旧任务迁移到新 schema。
- 增加任何旧格式兼容分支。
- 删除 records、knowledge、journal 或已归档严格任务。
- 修改旧任务内容后继续执行。
