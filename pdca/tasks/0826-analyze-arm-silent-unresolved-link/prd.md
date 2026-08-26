# 分析 dmsbtex/xmake-arm.lua 遗留死文件问题并更正 T3975 审查结论

## 问题陈述

T3975 审查将 `dmsbtex/xmake-arm.lua` 判定为 CRITICAL（ARM 构建缺 TLS 依赖致加载失败）。用户指认该文件为**遗留多余**。经验证：全仓库零 includes 引用，真正 ARM 构建复用 `dmsbtex/xmake.lua`（依赖齐全）。需分析此文件的来龙去脉、死构建文件的误导机制，并更正审查结论。

## 已验证事实

1. `grep -rn "xmake-arm"` 全仓库（lua/sh/yml/md，排除 third_party/vendor）零命中——无任何文件 include 它。
2. 根 `xmake.lua:46-54`：`arch = os.arch()`，aarch64/arm64 → `"aarch64"`；`includes("dmsbtex")` 只引入 dmsbtex/xmake.lua。
3. `dmsbtex/xmake.lua:1`：`set_prefixdir("dm_ftp/" .. arch, ...)` ——aarch64 机器上直接构建即产出 `dm_ftp/aarch64/`，且 target 带 `add_deps("logger"/"tools"/"tls_cert")`。
4. 结论：xmake-arm.lua 不参与任何构建路径；T3975 CRITICAL#3 为误报。

## 分析维度（方案）

1. **历史考古**：`git log --follow --follow-patch -- dmsbtex/xmake-arm.lua` 厘清诞生时间点、最后一次同步修改、被 os.arch() 方案取代的提交——回答"为什么存在"。
2. **误导机制**：为什么它骗过了六路深审（grep 符号引用成立、x86/arm 对照差异成立）——死文件与活文件在静态检查下不可区分的根因；评估同类风险面（仓库内是否还有其他不被 include 的 *.lua / 构建入口残留）。
3. **处置方案**：删除步骤（含 git rm 与回归验证：删除后 xmake 配置解析无警告、全量 test 仍绿）；以及防止再次积累的机制建议（如 CI 死配置检测 or 约定）。
4. **T3975 更正**：在报告中出具显式更正声明（CRITICAL#3 撤销，Blocking 计数 4C→3C），并在 journal 留痕。

## Seam 分析

research 场景无代码测试产物；验证方式为报告内容断言。

### 声明的测试接缝

（无——纯调研分析）

## 范围外

不实际执行删除；不重审 T3975 其余 ~109 条发现。

## 验收标准

- [ ] AC-1: `records/T3976-0826-analyze-arm-silent-unresolved-link/analysis-report.md` 存在，含历史时间线章节（git log --follow 结论）
- [ ] AC-2: 报告含对 T3975 CRITICAL#3 的显式更正声明及更正后 Blocking 计数
- [ ] AC-3: 报告含同类风险面盘点结论（全仓库死构建配置扫描结果与数量）
- [ ] AC-4: 报告含处置建议（删除步骤 + 回归验证方式 + 防再积累机制）
