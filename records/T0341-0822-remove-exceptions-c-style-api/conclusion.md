---
schema: pdca.asset/v1
id: T0341-0822-remove-exceptions-c-style-api
phase: check
source_ids: [ev-ac1-syntax-scan, ev-ac2-prefix-scan, ev-ac3-namespace-scan, ev-ac4-boundary-purge, ev-ac5-make-build, ev-ac6-cmake-build, ev-ac7-style-rules, ev-ac8-build-graph, ev-ac9-tests-v2]
---

## 上下文

T0341 目标为移除 C++ 异常处理残留并统一 C 风格 API 调用（`::close` → `close`、拆 `namespace bs`）。Plan 阶段经两轮 Grill 与终审确认：整体删除异常边界、符号保现名全局化、style_check 作测试接缝。Do 阶段按 TDD 红→绿三切片实施，提交 de098a6（198 文件，+1289/−1876），版本 171.0.0 → 171.1.0。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 项目可达到源码零异常语法且删除全部异常编译豁免 | 成立（AC-1/AC-4 零命中） |
| libc 调用去 `::` 前缀后链接语义不变 | 成立（去前缀 1052 处，双通道构建绿 + 全量集成测试通过） |
| 拆除 namespace 后符号无撞名 | 成立（模块前缀命名习惯有效；全量链接与 120 项 ctest 无符号冲突） |
| style_check 全量通过 | **部分成立**——新增规则全部生效，但 4 处行数规则在 HEAD 即失配（存量） |
| 测试套件全部通过 | **部分成立**——可运行项全过；p1_closure/tree_small_metadata 存量失败（HEAD 复现） |

## 分析

**逐条 AC 判定**：
- AC-1 异常语法零命中 — PASS（ev-ac1-syntax-scan）
- AC-2 `::` 前缀零命中 — PASS（ev-ac2-prefix-scan）
- AC-3 namespace bs 零命中 — PASS（ev-ac3-namespace-scan）
- AC-4 exception_boundary 构建链零引用 — PASS（ev-ac4-boundary-purge）
- AC-5 make 构建 — PASS（ev-ac5-make-build）
- AC-6 cmake 构建无 -fexceptions — PASS（ev-ac6-cmake-build）
- AC-7 style_check 新规则生效 — PASS（规则存在且红→绿验证生效）；但脚本整体 exit=1 因 4 处存量行数违规（backup_agent 807/650 等，init 提交即失配）— 存量缺陷不阻塞本任务目标
- AC-8 build_graph 回归 — PASS（ev-ac8-build-graph，含新增"禁止任何 -fexceptions 编译"断言）
- AC-9 测试套件 — 可运行项全 PASS（单元 8 项 + 集成 30 余项 + TLS 变体 + ctest 117/120）；3 项 ctest 失败均为存量（ev-ac9-tests-v2）

**关键实施发现**（已解决）：
1. 去前缀暴露 10 处遮蔽变量（局部 `open`/`read` 与 libc 函数同名，原先靠 `::` 显式限定绕过遮蔽），重命名为 frame_open/work_read。
2. 批量替换正则需排除 `>` 前缀，否则破坏 `std::numeric_limits<size_t>::max()`。

**存量问题甄别方法**：git stash 回 HEAD 复跑对照，4 类失败均复现，排除为本任务引入。

## 适用边界

- 结论适用于本次提交 de098a6 的完整变更集；单步回滚需 revert 后手工摘除对应 hunk（四步实施相互独立）。
- 异常兜底语义为 std::terminate 的前提是"项目零异常源"——未来引入会抛异常的第三方库时必须重新评估。
- 符号全局化的撞名安全性依赖现有模块前缀命名惯例，新增模块应延续该惯例。

## 下一轮建议

1. 存量修复任务 A：style_check 行数分解规则与现实对齐（4 处 limit 失配，或拆分 backup_agent.cpp/backupctl.cpp）。
2. 存量修复任务 B：p1_closure_source_regression.sh 两个 grep 断言与当前源码格式同步。
3. 存量修复任务 C：tree_small_metadata_order_integration.sh 清理阶段对只读目录的 rm 处理。
4. Makefile test 目标清理：移除对 2 个不存在脚本的引用（session_pool/plain_session_elastic_pidfd）。

## verdict

```json
{
  "outcome": "confirmed",
  "reason": "9 条 AC 中 7 条 PASS；AC-7/AC-9 的字面'全部通过'受 4 类存量失败影响（HEAD 复现、与本任务无关），用户判定 confirmed:目标完全达成,存量失败不属本任务验收范围",
  "verdict_id": "T0341-check-v1",
  "at": "2026-08-22T07:50:00+08:00"
}
```
