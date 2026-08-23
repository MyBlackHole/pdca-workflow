---
schema: pdca.asset/v1
id: T0371-0823-evaluate-uplift-potential
phase: check
source_ids: [eval-report, evidence-manifest, convergence-map]
---

## 上下文

T0370 报告提出 9 条可迁移原则后，本任务评估其对本项目（pdca-workflow）的真实提升潜力。方法：11 个候选项逐项现状核实（file:line 级证据）→ 7 项五维评估（收益/成本/风险/依赖/验证方式）→ 四层路线图。

## 假设与结果

| 假设 | 结果 |
|------|------|
| H1 T0370 建议可直接实施 | **被推翻（部分）**：2 项 already-done、1 项 mostly-done，直接实施会重复建设 |
| H2 存在真实且值得立项的空白 | 成立：P3/P7/P8c 三项通过五维评估进入立即/短期层 |
| H3 实施成本可控 | 成立：路线图刻意绕开 flow-do 主文件与硬门禁，预算豁免各一次 |

## 分析（逐 AC 判定）

- **AC-1 核实表** ✅ 报告第1节：11 项全覆盖（超 PRD 要求的 9），每项附 already-done/partial/gap 标注与本项目 file:line；另产出预算基线偏差实测（flow-do 持平/4 文件超额靠豁免）。
- **AC-2 五维评估** ✅ 报告第2节：7 个 partial/gap 项全部完成收益/成本/风险/依赖/验证方式分析，每项含裁定。
- **AC-3 路线图** ✅ 报告第3节：立即 1（P3）/短期 2（P8c+P7 合并立项）/观察 4（均带量化触发条件）/不做 3（重复或低值）。
- **AC-4 总体判定** ✅ 报告第0/4节：**部分能提升**——判定标准（Q1 轮预定义"至少 2 个 gap 项进立即/短期"）满足；依据链三层（实证/机制/约束）。
- **AC-5 证据登记** ✅ eval-report 映射 AC-1~4、evidence-manifest 映射 AC-5、convergence-map 已登记且 validate-convergence 返回 valid:true。

## 结论可靠性自查

方法充分性（静态核实+量化预算实测）、来源遗漏（未跑配对实验但已为每项设计验证方式并声明属实施任务范围）、替代解释（"完全不能提升"被实证层排除——3 项真实空白经核实成立）三项均已 grill 并记录 round 2。

## 适用边界

- 评估基于今日仓库快照；若 flows/skills 在评估后被修改，核实表行号需复核。
- 收益判断为机制推理+历史任务模式归纳，预期幅度中仅 research 可复核率给了可测目标，其余留待实施任务按各自验证方式实测。
- 触发条件型观察项（记录率<50%、词条>60 等）的度量口径以触发时的重测为准。

## 失败原因

不适用（verdict 非 rejected）。

## 下一轮建议

1. 用户批准路线图后：P3 单独立 Improvement Task（development）；P8c+P7 合并一个 documentation 任务。
2. 观察层触发条件写入 journal 跟踪。
