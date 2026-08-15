# 拒收统计（AC-6）

## 历史拒收留痕基线

`audit-gate-compliance.py` 扫描全量任务（154 个）显示历史 **rejected receipts 总量 = 0**：
- 原因：transition 拒绝留痕机制（T0270 新增）之前，transition-phase.py 拒绝时只打印 stderr，不落盘。
- 含义：门禁拦截在历史上有发生（第五轮 T0269 中多次被拒：convergence 空、clarifications 损坏、FINAL_CONFIRMATION_MISSING），但无持久记录。

## 机制后拒收可审计性

机制新增后，每次 transition 被拒都会写 `transition-receipts/rejected-<ns>-<to>.json`（schema `pdca.gate-rejection/v1`），
`audit-gate-compliance.py` 扫描的 `rejected_receipts_total` 即可计数拦截次数。

## 演示（测试证据）

`tests/test_gate_compliance.py::GateRejectionLeakTest` 验证两种拒绝路径均生成 rejected receipt：

| 场景 | 触发 | rejected receipt 内容 |
|---|---|---|
| 无 final_confirmation | gate_issues FINAL_CONFIRMATION_MISSING | task_id/from=plan/to=do/issues[FINAL_CONFIRMATION_MISSING]/at |
| 非邻接过渡 | NON_ADJACENT_TRANSITION | task_id/from=plan/to=check/error/at |

成功路径对照：`test_success_path_still_writes_success_receipt` 验证 plan→do 成功仍写成功 receipt 且无 rejected。

## 拒收率指标定义

拒收率 = rejected receipts / (成功 receipts + rejected receipts)。机制运行后可从 audit 扫描结果计算。
