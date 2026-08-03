# T0206 AC-6 状态记录（部分完成 PDCA）

## 状态：未开始（显式未覆盖）

Check 时点（2026-08-03）：AC-6（workspace 全量测试、fmt、diff gate
通过，单项不超过一分钟）尚未执行。

原因：AC-5 未完成（rewritten_node_revalidates_on_reopen 测试失败，
暴露 root 分支 extent 缺陷，见 check-evidence），AC-6 门禁须在
AC-5 修复后运行。

## 部分完成基线（Check 时点）

- `cargo test --lib`：243 passed, 1 failed（AC-5 未完成项），~10.5s。
- fmt / diff gate：未执行（等 AC-5 修复）。

## 部分完成 PDCA 意图

本次 Check 仅收敛已完成的 AC-1..AC-4（差异记录 D9 落文档 + 全部
通过测试基线）；AC-5 部分完成、AC-6 未开始，作为 partial verdict
进入 Act 阶段，创建跟进任务继续。
