---
schema: pdca.asset/v1
id: T0267-0815-skills-structure-gotchas
phase: check
source_ids: [ac1-check-structure-script, ac2-fixture-rejection, ac3-all-pass-contract, ac3-structure-report, ac4-all-gotchas, ac5-core-references, ac6-source-audit, ac7-full-suite-green, convergence-map-v2]
---

## 上下文

T0267 是第三轮可证明增量（T0266 后）。第三轮网络调研（Anthropic 官方 best practices、Anthropic 内部经验、pedronauck/skills writing-skills 含 validate-metadata.py、claude-skills-collection、agentskills.io 生态）确认两个缺失机制：① 无 skill 结构规范检查器（既有 audit-skill-content 只管流程资产契约，不校验 frontmatter/体积/gotchas）；② 0/39 skill 含 Gotchas 段（Anthropic 判定 skill 中最高信号内容）。本轮落地"skill 本身质量规范"层：结构契约检查器 + 全量 gotchas 段机制。

## 假设与结果

| 假设 | 结果 |
|---|---|
| H1：skill 结构契约可脚本化全量断言（Anthropic checklist + agentskills.io 规范） | **supported**：`scripts/check-skill-structure.py` 实现硬错误（name 格式/长度、description 长度、XML 指令标记、文件行数、Windows 路径、gotchas 段缺失/过短）与软警告（人称词、触发词、完成准则启发式）；`--exit-code` 供 CI 强校验。全量 39 正式 skills error_count=0。 |
| H2：Gotchas 段可全量强制且核心 skill 可溯源 | **supported**：39 个正式 skill 各含非空 `## 已知坑`/`## Gotchas` 段；核心 9 个（triage-work/register-evidence/resolving-merge-conflicts/write-conclusion/advance-phase/write-journal/design-it-twice/to-tickets/wayfinding-work）的 gotchas 从历史任务真实失败点提取（convergence 逐字一致、git merge 返回码 1、SKILLS-INDEX 过期、register-evidence --file 唯一、check_confirmation response 等），来源引用抽检存在。 |
| H3：可证明性 = 违规 fixture 拒绝 + 全量通过 + 来源抽检 | **supported**：18 个新测试（test_skill_structure 14 + test_gotchas_contract 4）全绿；违规 fixture（坏 name/长 desc/长文件/XML/Windows 路径/缺段/空段）逐项报告并返回非 0；全量断言 39 无 error；核心 9 来源引用正则提取且目标目录存在。 |
| H4：全量无回归 | **supported**：全量 233 passed / 4 既有失败 / 13 subtests；4 个既有失败（2 harness + 2 doctor）与基线完全一致（round62-67 外部任务缺失）。SKILLS-INDEX.md 已重新生成（改 39 skill 后同步）。 |

## 分析

### PRD 验收

| AC | 证据 | 状态 |
|---|---|---|
| AC-1 check-skill-structure.py 存在且对全量执行契约检查 | ac1-check-structure-script（脚本 8962 字节，含 name/description/体积/引用深度/完成准则/gotchas 契约） | Passed |
| AC-2 违规 fixture 逐项报告并返回非 0 | ac2-fixture-rejection（14 测试含坏 name/长 desc/长文件/XML/Windows 路径/缺段/空段 fixture，test_error_exit_code 断言 rc=1） | Passed |
| AC-3 全量 39 skills 通过全部结构契约，违规为空 | ac3-all-pass-contract（全量断言 >=39 且 error_count=0）+ ac3-structure-report（--json 报告 error_count=0, warnings=40） | Passed |
| AC-4 全量 39 skills 各含非空 gotchas 段（双语段名） | ac4-all-gotchas（test_all_gotchas_headers_non_empty + test_all_gotchas_headers 无 GOTCHAS_MISSING/EMPTY） | Passed |
| AC-5 核心 9 个 skill 的 gotchas 从历史失败点提取 | ac5-core-references（CORE_SKILLS_SOURCES 映射 + 断言来源 token 在段内） | Passed |
| AC-6 核心 9 的来源引用抽检存在 | ac6-source-audit（正则提取 T0xxx，record 前缀匹配或归档 task.json id 匹配） | Passed |
| AC-7 新增测试通过 + 既有 4 失败非回归 | ac7-full-suite-green（全量 233 passed / 4 既有失败 / 13 subtests，与基线一致） | Passed |

### 关键实现决策

- **失败驱动实现**：先写检查器 + 测试（全量断言红，46 errors 全为 GOTCHAS_MISSING），补完 39 个 gotchas 段后全绿。
- **WINDOWS_PATH 误报修复**：初版检测"含反斜杠"误报 6 个 shell 续行符（`python3 ... \` 多行命令）；改为盘符正则 `[A-Za-z]:[\\/]`，续行符不再误报。
- **DESC_XML 误报修复**：`<record-id>` 是占位符非 XML；description 的 XML 检测收紧为指令标签集合（thinking/instructions/system 等），name 的 XML 检测保持严格。
- **连接字符脚本调用**：`check-skill-structure.py` 含连字符无法 `import`，测试沿用 out-of-scope 先例用 subprocess 真实调用（CLI 契约即测试面）。
- **来源抽检口径**：record id 为 `T0266-0815-skills-round3` 全名非 `T0266`，抽检用前缀匹配 records/ + 归档 task.json 的 id 字段匹配。
- **39 vs 40 口径**：`skills/drafts/` 为草稿区（2 个未激活草稿），非正式 skill；检查器按 `skills/*/SKILL.md` 存在性扫描为 39，drafts 排除（test_drafts_excluded_from_scan 断言）。
- **ask-matt 人称修复**：description 含"你的"（第一/二人称），改为"用户"满足第三人称契约（软警告清零该项）。
- **触发词/完成准则为软警告**：18 个 description 缺触发词、多数无显式完成准则——设计为 warning 不阻塞 exit-code（避免超范围改写 18 个 description），`--exit-code` 供 CI 强校验时计入。

### 已知边界（非本任务引入）

- 4 个全量测试失败均为既有状态（2 harness + 2 doctor，round62-67 外部任务缺失），与 T0266 基线一致。
- LSP 静态告警（`arch_review`/`pdca_core` import 无法解析）不影响运行时。
- 触发词/完成准则为软警告：检查器报告但不阻塞默认 exit-code（退出码 1 仅 error，2 需 `--exit-code`）。
- gotchas 段真实性的抽检限于核心 9 个（有任务来源）；其余 30 个为领域通用失败模式，无记录级来源。
- drafts 草稿区不参与契约检查（未激活）。

## 失败原因（仅 rejected/partial）

无。本任务全部 AC 通过，无 rejected/partial 项。

## 适用边界

- 结构契约检查器适用于 SKILL.md 为主的 skill 仓库；硬契约（name/长度/XML/体积/Windows 路径/gotchas）为机器可判定的质量底线。
- Gotchas 段机制适用于"失败点积累"的运维型 skill 仓库；核心 skill 已有记录级溯源，其余 skill 的 gotchas 会随真实任务失败逐步替换为溯源版本。
- `--exit-code` 供 CI/门禁强校验；默认 exit-code 允许 warning 存在（渐进改进不阻塞）。

## 下一轮建议

1. 将触发词/完成准则从软警告升级为硬契约时，先批量改写 18 个缺触发词的 description（需逐条语义评审，非本轮范围）。
2. 为其余 30 个 skill 的 gotchas 逐步替换为记录级溯源版本（随真实失败积累）。
3. 将 `check-skill-structure.py` 接入 validate-gate.sh 门禁链（本轮按用户决策保持独立脚本）。
4. T0263（identity 观察）继续挂起等待观察窗，观察期满后出 effectiveness verdict。
