---
schema: pdca.asset/v1
id: T3957-0825-dead-hs-protocol-defs-cleanup
phase: check
source_ids: [ac1-build, dmsbtex-session-test, libobk-session-test, rdbcomm-session-test, mixed-mtls-integration, ac3-grep-residual]
---

## 上下文

用户要求检查 `DM_HS_OK_TIME` 类似的多余代码。T3956 归一握手结果码后，dmsbtex/libobk 协议头暴露一批早期协议设计残留（规划了 magic/version/payload 帧字段但实现从未包含）。逐项 grep 全仓库（含 tests）验证后确认 16 项零引用死定义并清理（commit 4ce569e3）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 16 项死定义删除不影响任何编译单元与线上字节流 | 成立：全量构建通过、四模块回归+e2e 17/17 全过 |
| 被删符号在全仓库无隐藏引用 | 成立：逐符号 grep 零残留 |

## 分析

- **AC-1** ✅ 全量 xmake 构建通过，`set_warnings(all,error)` 下零新增警告（ac1-build）
- **AC-2** ✅ dmsbtex/rdbcomm session test ALL PASS、libobk session test exit=0（静默设计）、mixed_mtls_integration AC1-7 PASS；e2e 场景矩阵 17/17（dmsbtex-session-test、libobk-session-test、rdbcomm-session-test、mixed-mtls-integration）
- **AC-3** ✅ 被删 16 项符号 grep 全仓库零残留（ac3-grep-residual）

Grill 追问：
1. 是否存在动态拼接引用宏名的可能？→ C 无反射，宏必须源码级出现；全仓库文本搜索已覆盖。
2. tests 目录是否绕过？→ 搜索含 tests 目录，零引用。
3. OPT_NULL/OPT_MAXNUM 为何不删？→ 匿名 enum 内删除会引发后续成员值偏移（OPT_BACKUP/RESTORE 有引用），超出纯删除安全边界，已在 PRD 范围外声明。

## 适用边界

仅适用于"零引用且非 enum 值偏移敏感"的协议层定义清理；enum 成员清理须先确认无隐式值依赖。

## 下一轮建议

- libs/tests/rpc_handshake_test.c（引用已删除头文件的死测试）仍待独立清理任务。
- 可对全仓库做一次系统性死码扫描（如 DM_HS_OK_TIME 同类的零引用协议常量），本任务清单已覆盖握手层。

verdict: {"outcome": "confirmed", "reason": "三项 AC 证据齐备：构建/回归/零残留全部通过，纯删除无行为变更", "verdict_id": "T3957-check-v1", "at": "2026-08-25T14:08:00+08:00"}
