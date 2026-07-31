# AI 友好确认与证据机制

来源: T0167（2026-07-31）。PDCA 机制对 AI 工作流可用性提升的实践记录。

## 原则

1. **AI 不手写时间戳**：一切时间由 CLI 生成（`append-confirmation.py` 自动填真实 `at`）。
2. **失败必须可执行**：每个 Issue 带 `guidance` 修复指引，拒绝"描述性报错"。
3. **不可变记录只能由 CLI 变更**：evidence 修正走 `--replace`（旧条目 `superseded_by` 保留审计），禁止手工编辑 manifest。
4. **早期失败**：PRD 格式在 plan→do 门禁校验，不等 do 收尾。

## 命令速查

```bash
# 登记确认（自动真实时间戳）
python3 scripts/append-confirmation.py --task-dir <dir> --source final_confirmation --response confirmed --summary "<理由>"

# 修正证据（旧条目保留审计链）
python3 scripts/register-evidence.py --record <r> --source <file> --id <new-id> --kind <k> --criterion AC-x --file <name> --replace <old-id>
```

## 踩坑记录

- `--replace` 指向已 superseded 条目必须 fail-closed（曾因链式替换崩溃）。
- convergence map 的"当前版本"= 最新非 superseded 的 convergence-map kind 条目。
- superseded 条目被 evidence 校验跳过（否则误报文件缺失）。
