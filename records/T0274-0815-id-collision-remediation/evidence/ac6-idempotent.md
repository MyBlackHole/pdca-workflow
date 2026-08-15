# 幂等性与裁决表完整性验证（T0274）

## 幂等性

在临时工作区副本上执行 `apply_plan` 两次，对比 `pdca/tasks/` 全文件 SHA256 digest：
- 二次 apply 后文件实质变化数：**0**
- 判定：幂等 ✓

## 裁决表完整性

- `--check-cover`（apply 前）：doctor 23 组，裁决表覆盖 12 组可处置，11 组待办 → 全覆盖 ✓
- `--check-disposable`：12 组可处置组全部 archive ✓
- `--check-deferred`：11 组待办组全部含活跃任务 ✓

## 新 ID 唯一性

- 新分配 ID T0275-T0286 与既有全部 task.json id 及 records 目录名无冲突 ✓

## 目录重命名

- 5 个含旧 ID 前缀目录已同步更名：T0215-→T0278-、T0217-→T0279-、T0246-→T0283-、T0247-→T0284-、T0249-→T0285- ✓

## 记录重命名

- 12 组 records 目录全部重命名为 `Txxxx-slug` 新格式（含 3 个旧格式：R0142/R0244/裸T0225 → 规范格式）✓
