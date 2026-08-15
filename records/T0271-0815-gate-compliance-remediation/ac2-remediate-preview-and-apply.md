# 证据 ac2 — remediate 修复计划预览与执行

## 首次 apply 执行日志（修复前状态，9 项）

```
+ backfilled verdict V-T0207-001 -> T0207
+ backfilled verdict V-T0208-001 -> T0208
+ backfilled verdict V-T0209-001 -> T0209
+ marked exemption -> T0149
+ marked exemption -> T0200
+ deleted nested copy pdca/tasks/archive/0801-btree-split-proptest/0801-btree-split-proptest (1 files)
+ deleted nested copy pdca/tasks/archive/0801-trans-enomem-restart/0801-trans-enomem-restart (1 files)
+ removed active stale pdca/tasks/active/0804-cdm-report-center-analyse (13 files)
+ removed active stale pdca/tasks/active/T0215-0804-report-subscheme-docs (12 files)
```

补充：补 verdict 后 audit 复查发现 T0207/T0208/T0209 仍缺 final_confirmation/act-to-archive receipt，追加豁免 ×3（T0149/T0200 之外），总豁免 5 项。

## 幂等性（dry-run 重跑，全部 skip，无实际改动）

```
# 修复计划预览（dry-run）—— 共 12 项
- [skip] T0207: verdict already present
- [skip] T0208: verdict already present
- [skip] T0209: verdict already present
- [skip] T0149: exemption already present
- [skip] T0200: exemption already present
- [skip] T0207: exemption already present
- [skip] T0208: exemption already present
- [skip] T0209: exemption already present
- [skip] .../0801-btree-split-proptest: nested dir not found
- [skip] .../0801-trans-enomem-restart: nested dir not found
- [skip] .../0804-cdm-report-center-analyse: active dir not found
- [skip] .../T0215-0804-report-subscheme-docs: active dir not found
```

dry-run 预览不实际改动，apply 幂等（重复执行安全）。
