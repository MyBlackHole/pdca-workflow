# skills 二轮深挖：剩余提升点落地包 — PRD

## 来源

T0371 评估后 P3/P7/P8c 已由 T0372/T0373 落地。本轮对 mattpocock/skills 做二轮扫描，提取四项剩余可吸收点（结合 T0374-T0377 后的新认知）。

## 方案（documentation 场景，四个子项）

### W1 纠偏引导词（学 wait-what）
AGENTS.md 入口区新增一行引导：用户表达未理解/消息未传达时，AI 应 re-pitch——补上下文、用 CONTEXT.md 共享语言、简明英语。不建独立技能（三行以内的事不值得一个文件）。

### W2 生效信号段（学 docs 页 "It's working if"）
flows 四文件各追加"生效自检"节：2-3 条可观察成功信号。例 flow-check："每个 AC 判定行可 grep 到证据 ID"、"用户 verdict 均有 check_confirmation 留痕"。

### W3 路由防谎规则（学 ask-matt 维护规则）
AGENTS.md 补一句：新增/改名/删除技能时必须重新生成 SKILLS-INDEX 并核对 AGENTS.md 入口路由仍准确——"路由指向不存在或过时技能即说谎"。

### W5 必录清单固化（交互捕获降噪规则，承接 T0375 与用户咨询结论）
grilling SKILL 规则 7 追加必录三层清单：①用户元反馈原话 ②verdict 时自由文本修正 ③用户否决推荐答案的选择；常规 yes/no 确认与事实性问答不录。敏感内容沿用 Redact 原则。

### W4 P9 试点兑现：flow-do C/D 路径 Done when 化
C1 加完成判据（报告落盘+关键结论含验证途径）；D1/D2 加判据（文档覆盖需求全节+双轴审查双通过）。兑现 T0371 观察层承诺，试点结论决定是否扩散到其余路径。

## 验收标准

- [ ] AC-1: AGENTS.md 含纠偏引导词与路由防谎规则两处新增
- [ ] AC-2: flows 四文件各含生效自检节且每节 >=2 条可观察信号
- [ ] AC-3: flow-do C/D 路径每步含 Done when 判据；A/B/E/F 路径未被改动（试点边界保持）
- [ ] AC-4: baseline 豁免更新、audit 零 budget issue；evidence 齐备 convergence valid
- [ ] AC-5: grilling SKILL 含必录三层清单与 Redact 提示（W5）

## 范围外

- 不改 A/B/E/F 路径（P9 扩散等试点证据）
- 不新建独立技能文件（W1 以入口引导词形态存在）

## 备注

预计增量：AGENTS.md +约400B（无 baseline 管控）、flows 四文件合计 +约1200B 豁免。
