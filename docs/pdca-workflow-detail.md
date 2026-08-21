# PDCA 工作流细节图集（v2 详细版）

本图集分四张阶段细节图展开 PDCA 全流程的操作级细节，每张图以
「动作 → 门禁 → 产物」为粒度。总览图见 `docs/pdca-workflow-full.md`。

## 图 0：五阶段总览（产物视角）

```mermaid
flowchart TD
    START((需求/想法)) --> P0["P0 Triage"]
    subgraph PL["Plan"]
        direction TB
        P0["P0 Triage<br/>task.json + triager-brief + prd 骨架"]
        P1["P1 澄清<br/>问题/目标/AC"]
        P2["P2 对齐 Grill<br/>clarifications.jsonl<br/>CONTEXT.md / ADR"]
        P3["P3 合成 PRD<br/>prd.md (SPEC 模板)"]
        P4["P4 拆解<br/>子 task.json (parent/children)"]
        P5["P5 知识注入<br/>implement.jsonl"]
        P6["P6 方案终审<br/>final_confirmation"]
        P7["P7 推进<br/>plan→do"]
        P0-->P1-->P2-->P3-->P4-->P5-->P6-->P7
    end
    subgraph DO2["Do"]
        direction TB
        D0["路径选择 A-F"]
        D1["Z1 register-evidence<br/>evidence/manifest.jsonl"]
        D2["Z2 convergence-map<br/>convergence.json"]
        D3["Z3 git commit (A/B/E)"]
        D4["Z4 推进 do→check"]
        D0-->D1-->D2-->D3-->D4
    end
    subgraph CK["Check"]
        direction TB
        C1["Ch1 回顾实验"]
        C2["Ch2 Grill 可靠性"]
        C3["Ch3 验证收敛"]
        C4["Ch4 conclusion.md + verdict"]
        C5["Ch5 用户判定"]
        C6["Ch6 推进 check→act"]
        C1-->C2-->C3-->C4-->C5-->C6
    end
    subgraph AC2["Act"]
        direction TB
        A0["Ac0 读 Verdict 分支"]
        A1["Ac1 Grill 知识 (confirmed)"]
        A2["Ac2 知识沉淀"]
        A3["Ac3 disposition"]
        A6["Ac6 journal"]
        A7["Ac7 git commit"]
        A8["Ac8 归档 archive/"]
        A0-->A1-->A2-->A3-->A6-->A7-->A8
    end
    P7-->D0
    D4-->C1
    C6-->A0
    A8-->END((归档完成))
```

> 图例：每阶段矩形节点右侧箭头指向下一阶段。详细操作见后续图 1-4。
## 图 1：Plan 阶段操作级细节（flow-plan）

```mermaid
flowchart TD
    START((需求/issue)) --> P0

    subgraph P["Plan 阶段：逐步骤操作 + 命令 + 产物 + 门禁"]
        P0["P0 Triage<br/>① 分类: scenario-boundary-check.py --judge<br/>② 查重: out-of-scope-manager.py check<br/>③ claim 验证: 代码/文档/可执行检查<br/>④ 建任务: task_identity.py create<br/>产物: task.json + prd骨架 + triager-brief"]
        P0 -->|"ready-to-plan"| P1
        P0 -->|"wontfix(重复/过时/越界)"| W["Wontfix<br/>surfacing 给用户<br/>记录到 out-of-scope 概念文件"]

        P1["P1 澄清<br/>读已有 prd/design/implement.md<br/>补齐: 问题陈述 + 目标 + 可测验收标准"]
        P1 --> P2

        P2["P2 对齐 Grill<br/>加载 grilling + domain-modeling-work<br/>按轮次批量询问决策(每问附推荐答案)<br/>① Q&A→clarifications.jsonl(source:grilling)<br/>② 模糊术语→CONTEXT.md<br/>③ 不可逆决策→ADR<br/>复杂任务(3+模块)→design.md+implement.md<br/>决策树闭合→请求方向确认<br/>→direction_confirm(非门禁,仅记录)"]
        P2 --> P3

        P3["P3 合成 PRD<br/>SPEC.md 模板<br/>问题/方案/用户故事/实现+测试决策/范围外/备注<br/>AC 必须: 可独立判定 pass/fail"]
        P3 -->|"dev/bugfix"| P35
        P3 -->|"research/doc/design/review"| P4

        P35["P3.5 测试接缝确认<br/>PRD '## Seam 分析' 下写<br/>'### 声明的测试接缝'<br/>格式: - seam: <测试文件> -> <被测模块><br/>向用户展示 seam 清单请求确认"]
        P35 --> P4

        P4["P4 拆解<br/>加载 to-tickets<br/>子任务 task_identity.py create --parent<br/>子PRD: 独立输入/边界/AC, 粒度≥1个PDCA周期<br/>父 task.json children 追加子ID<br/>依赖只存直接前置<br/>只创建不执行"]

        P5["P5 知识注入<br/>搜索 knowledge/, 只选影响决策的资产<br/>逐行追加 implement.jsonl<br/>: 文件+理由+动作+时间<br/>不为凑数加载全部历史"]
        P5 --> P6

        P6["P6 方案终审(唯一签审门禁)<br/>展示: 目标/范围/AC/设计/备选取舍/任务树<br/>遗漏→回 P2, 范围变化→回 P1/P2<br/>批准→append-confirmation.py<br/>--source final_confirmation --response confirmed --summary<br/>门禁: final_confirmation.response=confirmed<br/>dev/bugfix 额外: seam 子节缺失即拒<br/>+ seam_contract.py 校验"]
        P6 --> P7

        P7["P7 推进<br/>加载 advance-phase 执行转换<br/>transition-phase.py --to do<br/>门禁: plan→do 需 final_confirmation=confirmed<br/>PRD '## 验收标准' 必须 checkbox 格式<br/>'- [ ] AC-x:' ('### AC-x' 会被拒)"]
    end

    P7 --> DO["→ Do 阶段"]
```

> 图例：`→|"标签"|` 为分支；青色节点为门禁。执行器边界：**P6 前禁止
> agent.spawn 调度，P6 后才可用**；能力不可用由主 session 顺序执行。

## 图 2：Do 阶段操作级细节（flow-do）

```mermaid
flowchart TD
    IN["从 Plan 进入<br/>meta.phase=do"] --> RT["路由决策<br/>resolve-ai-friendliness-route.py<br/>--scenario <meta.scenario_type><br/>读 ai-friendliness-route-contract.json"]

    RT -->|"development"| DA["路径A 测试优先<br/>A1 原型验证(可选,技术风险高)<br/>A2 TDD切片: 确认Seam→先写失败测试→最小实现→跑定向测试<br/>A3 全量验证<br/>A4 双轴代码审查(code-review)<br/>A5 架构检查(可选,技术债重)"]
    RT -->|"bugfix"| DB["路径B 根因修复<br/>B1 根因诊断(diagnosing-bugs)<br/>B2 TDD回归: 确认回归Seam→复现失败测试→最小修复→跑定向回归<br/>B3 全量回归验证<br/>B4 双轴代码审查"]
    RT -->|"research"| DC["路径C 调研<br/>C1 调研+撰写报告(research)<br/>C2 对照PRD逐条检查完整性+引用格式"]
    RT -->|"documentation"| DD["路径D 文档<br/>D1 按SPEC模板写 design/spec/ADR<br/>D2 双轴审查(内容轴+格式轴,Mermaid可读)"]
    RT -->|"design"| DE["路径E 架构设计<br/>E1 方案(domain-modeling) design.md+ADR<br/>E2 设计评审: 逐条验证+备选trade-off<br/>E3 基线化: ADR+CONTEXT更新<br/>E4 基线代码提交 git commit"]
    RT -->|"review"| DF["路径F 审查<br/>F1 双轴审查(code-review)<br/>F2 写 review-report.md<br/>F3 架构检查(可选)"]

    DA --> Z1
    DB --> Z1
    DC --> Z1
    DD --> Z1
    DE --> Z1
    DF --> Z1

    Z1["Z1 登记证据<br/>register-evidence.py<br/>--record <id> --source <文件> --id <短ID><br/>--kind <类型> --criterion <AC><br/>要求: ≥1个AC, --file唯一, --source须存在<br/>immutable manifest.jsonl (digest+size+AC映射)<br/>修正用 --replace(新id+不同file)"]
    Z1 --> Z2["Z2 收敛映射<br/>convergence.json<br/>index唯一, text与task.meta.convergence逐字一致<br/>evidence_ids指向非map证据<br/>register-evidence --kind convergence-map<br/>validate-convergence.py --task-dir<br/>→ 必须 valid:true<br/>映射本身不能作为验收证据"]
    Z2 --> Z3["Z3 提交代码<br/>A/B 路径: git commit<br/>E 路径: 有基线才提交<br/>C/D/F: 无代码变更跳过"]
    Z3 --> Z4["Z4 推进<br/>transition-phase.py --to check<br/>门禁: do→check 需 PRD + 有效evidence<br/>(schema/文件/size/digest)"]
    Z4 --> OUT["→ Check 阶段"]

    RT -.->|"执行器容错<br/>agent.spawn 可用→Adapter调用<br/>不可用→主session顺序执行<br/>失败→记录failed-tasks.jsonl<br/>Blocking→主session接管<br/>非Blocking→跳过并注明"| Z1
```

> 图例：6 条路径最后汇聚到 Z1-Z4 通用收尾。执行器容错为 Do 阶段全程通用机制。
> Do 退出口：假设不成立/发现新信息 → 回 Plan 重新设计（meta.phase=plan）。

## 图 3：Check 阶段操作级细节（flow-check）

```mermaid
flowchart TD
    IN["从 Do 进入<br/>meta.phase=check"] --> C1

    subgraph CK["Check 阶段：逐步骤操作 + 门禁"]
        C1["Ch1 回顾实验<br/>读 task.json meta.scenario_type<br/>development/bugfix: 测试已跑吗? 新测试真实覆盖吗?<br/>research/doc/design/review: 对照PRD验收+产出物检查<br/>+ evidence/manifest.jsonl 证据清单核对"]
        C1 --> C2

        C2["Ch2 Grill 可靠性<br/>grilling 双轴追问(结论+证据)<br/>场景感知问题:<br/>  dev: 测试证明行为还是实现细节? 边界/并发/恢复?<br/>  research: 方法充分? 遗漏关键来源? 替代解释?<br/>模糊术语→更新 CONTEXT.md<br/>不清晰的继续 Grilling"]
        C2 --> C3

        C3["Ch3 验证收敛<br/>meta.convergence → AC → evidence 全覆盖<br/>AC 无证据→结论降级(标注部分成立)"]
        C3 --> C4

        C4["Ch4 结论文档 + 判定<br/>write-conclusion:<br/>records/<id>/conclusion.md<br/>章节: 上下文/假设与结果/分析<br/>/失败原因(rejected|partial)/适用边界<br/>/下一轮建议/已知坑<br/>+ task.json meta.verdict:<br/>outcome + reason + verdict_id + at<br/>verdict_id 唯一(历史 T<id>-confirmed-<date>)"]
        C4 --> C5

        C5["Ch5 用户判定<br/>展示结论摘要<br/>confirmed → Act 知识沉淀+归档<br/>rejected → Act 失败处置(不沉淀)<br/>partial → Act 提取有效部分+跟进<br/>判定后追加 clarifications.jsonl<br/>source: check_confirmation"]
        C5 -->|"confirmed / rejected / partial<br/>三者都进 Act, 不从 Check 退回"| C6

        C6["Ch6 推进<br/>advance-phase check→act<br/>meta.record 写入结论引用<br/>门禁: check→act 需 conclusion + verdict<br/>+ check_confirmation"]
    end

    C6 --> OUT["→ Act 阶段"]
```

> 图例：Ch1 按场景走不同检查清单；Ch5 三分支判定后**一律进入 Act**，
> 仅处置方式不同（沉淀/失败处置/部分跟进），不存在 Check 回退路径。

## 图 4：Act 阶段操作级细节（flow-act）

```mermaid
flowchart TD
    IN["从 Check 进入<br/>meta.phase=act"] --> A0

    subgraph AC2["Act 阶段：逐步骤操作 + 门禁"]
        A0["Ac0 读 Verdict<br/>读 task.json meta.verdict.outcome<br/>confirmed / rejected / partial 三分支"]
        A0 -->|"confirmed"| A1
        A0 -->|"rejected"| A2A
        A0 -->|"partial"| A2B

        A1["Ac1 Grill 知识(仅 confirmed)<br/>grilling 追问: 适用范围/限制?<br/>哪些可提炼复用? 流程有何改进?<br/>Q&A 追加 clarifications.jsonl(source:grilling)<br/>→ 产出知识沉淀决策"]
        A1 -->|"产出"| A2
        A1 -->|"不产出"| A3

        A2["Ac2 知识沉淀(仅 confirmed)<br/>写入 knowledge/<topic>/<slug>.md<br/>① clarifications.jsonl 追加 knowledge_decision<br/>  action: wrote|skipped + reason<br/>② knowledge/manifest.jsonl 追加<br/>  version/revision/at/knowledge/knowledge_digest<br/>  source_record/source_digest/reason"]
        A2 --> A3

        A2A["Ac2a 失败处置(仅 rejected)<br/>结论不成立, 不做知识沉淀<br/>从 conclusion.md 失败原因提取教训<br/>写入日志即可<br/>⛔ 跳过 Ac3-Ac5<br/>直接跳到 Ac6 日志"]
        A2A -.-> A6

        A2B["Ac2b 部分沉淀+跟进(仅 partial)<br/>⛔ 跳过 Ac1<br/>① 仅沉淀确凿可复用部分<br/>② 创建跟进任务(统一 identity 入口)<br/>task_identity.py create<br/>  --slug MMDD-followup-slug<br/>  --title '跟进:<未完成部分>' --parent <id><br/>  --scenario-type <继承> --meta.phase plan<br/>③ clarifications.jsonl 记录跟进 ID"]
        A2B --> A3

        A3["Ac3 记录处置<br/>task.json meta.disposition:<br/>outcome: projected|not_reusable|task_only<br/>reason + at<br/>⛔ 后续 Ac6 journal 前置依赖此项"]
        A3 --> A4

        A4["Ac4 架构改进<br/>结论涉及需改进的架构?<br/>→ 提取改进项<br/>→ 创建新任务或更新 backlog"]
        A4 --> A5

        A5["Ac5 跨会话桥接<br/>handoff-work<br/>manual 'handoff' 仅保留为用户入口"]
        A5 --> A6

        A6["Ac6 追加日志<br/>write-journal Mode A(Task Close)<br/>⛔ 前置: meta.disposition 必须存在<br/>journal/YYYY-MM-DD.md<br/>三段格式: 任务进度/关键决策/阻塞项<br/>追加到末尾不覆盖历史(T0264)"]
        A6 --> A7

        A7["Ac7 提交(含 disposition)<br/>⛔ 先检查 evidence/manifest.jsonl<br/>不存在→提示先 register-evidence<br/>存在→ git add -A && git commit<br/>-m 'task <id>: 完成并归档'"]
        A7 --> A8

        A8["Ac8 归档<br/>① advance-phase 目标 archive<br/>  校验 disposition → phase=archive + active=false<br/>② git commit -m 'task <id>: 归档 metadata'<br/>③ mv pdca/tasks/<MMDD-slug><br/>   pdca/tasks/archive/YYYY-MM/"]
    end

    A8 --> END((归档完成))
```

> 图例：`⛔` 标记跳过/前置门禁。rejected 直达 Ac6（跳过 Ac3/4/5）；
> partial 跳过 Ac1 但走完整 Ac3-Ac8；confirmed 走全链。
