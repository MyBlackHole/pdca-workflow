# T0390 对话日志

## Plan 阶段
- 用户要求"下一个任务推荐"后，对"先前审查的问题都修复了吗"做实证复核（重新审查）。
- 发现原候选 #1（tls_cert.c `-Werror=stringop-truncation`）已过时：代码改 `safe_strcpy`，提交 `57fca54` 已修 xmake test 的 `-Werror` 阻断，重编干净。
- 实证确认真正现存的构建阻断是 #3：`libobk_protocol_test` 在 release（NDEBUG）下因 `assert` 被优化导致 `-Werror=unused-variable`/`uninitialized`。
- 创建 T0390（bugfix，parent T0389），写 PRD（方案：assert→真实错误检查）。

## Do 阶段
- `libobk/test/protocol_test.c`：`assert(...)` 改为 `if (...) { fprintf(stderr,...); return 1; }`，补 `#include <stdio.h>`；被测逻辑未改。
- release 与 debug 构建均 `build ok`，运行 `exit 0`，阻断消除。

## Check 阶段
- 登记证据：impl-diff / protocol_test_release / protocol_test_debug / convergence-map。
- 收敛校验通过（do→check 门禁 valid）。
- 写 `conclusion.md`，3 条 AC 全部 ✅。
- 用户 verdict=**confirmed**。

## Act 阶段
- 写 `meta.verdict`（confirmed）与 `meta.disposition`（projected）。
- 知识沉淀至 `knowledge/rdb-config/audit-findings.md`：新增"libobk_protocol_test 构建阻断（T0390 已修复）"小节；将 tls_cert.c 截断阻断条目标记为"已修正/作废"（重新审查实证）。
- 归档（phase→archive，任务目录移入 archive/）。
