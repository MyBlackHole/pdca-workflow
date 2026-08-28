# T3993 结论文档（修订 v4）— 重新 squash 为 F-139 单需求提交并归一版本 +1

## 结论摘要

经多轮修正，最终将 `0bf741f8..fef11220` 的 11 个跨需求提交重新 squash 为**单个 F-139 单次需求提交** `9d1fcc69`：
- 提交结构：单一 F-139 提交，信息只概括 F-139 单次需求实现，不再把 T3985/B-3988 等子任务作为独立需求标签罗列（功能要点融入 F-139 描述）。
- 代码修复：仓库根 `xmake.lua` 中所有组件版本号归一为相对上一个提交 `fe9d4364` **仅递升一个版本**（+1），消除原始合并中 libobk 误跳版（1.0.0.0→1.0.1.7）、rpc(+8)、dmsbtex(+6)、rdbcomm(+7)、tls_keygen(+6) 等超幅变化。

## 验收判定（对照修订后产物）

- **AC-1** ✅ 证据 ev4-ac1-version-check：`libobk_version = "1.0.0.1"`，`verify_version.sh` 输出 PASS。
- **AC-2** ✅ 证据 ev4-ac23-commit-msg：合并提交信息首行为「【F-139】TLS 安全链路整合：TLS/mTLS 全栈实现、配置收口、mTLS fail-closed 与版本号归一」，含 F-139 需求单号概括。
- **AC-3** ✅ 证据 ev4-ac23-commit-msg：提交信息含「libobk 1.0.0.0 -> 1.0.0.1（+1）」「rpc 3.6.4.19 -> 3.6.4.20（+1）」等逐组件 +1 说明，且未罗列 T3985/B-3988 子任务标签。
- **AC-4** ✅ 证据 ev4-ac4-version-table：对比父 `fe9d4364` 版本变量表，差异全部为 +1（libobk/dmsbtex/rdbcomm/rpc/tls_keygen），oss 为新增首版 1.0.0.1；bwlimit/rpc_keygen/s3tools 与父一致未变。

## 关键证据引用

- `records/T3993-0828-fix-squash-commit-msg-version/evidence/ev4-ac1.txt`
- `records/T3993-0828-fix-squash-commit-msg-version/evidence/ev4-ac23.txt`
- `records/T3993-0828-fix-squash-commit-msg-version/evidence/ev4-ac4.txt`
- 收敛映射：`convergence-map4`（valid: true）

## 版本归一结果（相对 fe9d4364 均 +1）

| 组件 | 父 | 合并后 | Δ |
|------|-----|--------|---|
| libobk | 1.0.0.0 | 1.0.0.1 | +1 |
| rpc | 3.6.4.19 | 3.6.4.20 | +1 |
| dmsbtex | 1.1.0.1 | 1.1.0.2 | +1 |
| rdbcomm | 1.0.1.8 | 1.0.1.9 | +1 |
| tls_keygen | 1.0.0.0 | 1.0.0.1 | +1 |
| oss | 无 | 1.0.0.1 | 新增 |
| bwlimit/rpc_keygen/s3tools | 同父 | 不变 | 0 |

## 收敛

`meta.convergence[0]` 与 `converge4.json` item[0].text 逐字一致，已通过 `validate-convergence.py`。

## 范围外确认

未重排其他独立逻辑；仅本地操作，未推送 origin。

## Verdict

待用户确认（confirmed / rejected / partial）。
