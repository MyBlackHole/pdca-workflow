# PDCA 流程本体关系图（T2130）

边全部取自各节点 frontmatter `specializes/part_of/relates_to`，非手编。
来源：`ontology/process/flow-plan.md`、`flow-do.md`、`flow-check.md`、`flow-act.md`。

```mermaid
flowchart TD
  PDCA["ontology:concept/pdca"]
  PROC["ontology:concept/process"]
  PHASE["ontology:concept/pdca-phase"]

  PLAN["ontology:process/flow-plan"]
  DO["ontology:process/flow-do"]
  CHECK["ontology:process/flow-check"]
  ACT["ontology:process/flow-act"]

  PROC -->|"specializes"| PLAN & DO & CHECK & ACT
  PLAN & DO & CHECK & ACT -->|"part_of"| PDCA
  PLAN & DO & CHECK & ACT -->|"relates"| PHASE

  PLAN -->|"relates"| P_ARCH["pdca-architecture"]
  PLAN -->|"relates"| P_BOUND["pdca-scenario-boundary-rule"]
  PLAN -->|"relates"| P_CONF["pdca-ai-friendly-confirmation"]
  PLAN -->|"relates"| E_PLAN["entity/phase-plan"]

  DO -->|"relates"| D_READY["pdca-ontology-ready"]
  DO -->|"relates"| D_GATE["pdca-gate-do"]
  DO -->|"relates"| D_EXEC["executor-adapter"]
  DO -->|"relates"| D_EVT["external-evidence-collection"]
  DO -->|"relates"| D_SAFE["destructive-cleanup-safety"]
  DO -->|"relates"| D_REAL["real-project-mechanism-validation"]
  DO -->|"relates"| D_HOME["pdca-home"]
  DO -->|"relates"| E_DO["entity/phase-do"]

  CHECK -->|"relates"| C_EVT["pdca-evidence"]
  CHECK -->|"relates"| C_VER["pdca-verdict"]
  CHECK -->|"relates"| C_AC["pdca-acceptance-criterion"]
  CHECK -->|"relates"| C_ARM["pdca-architecture-review-metrics"]
  CHECK -->|"relates"| E_CHECK["entity/phase-check"]

  ACT -->|"relates"| A_IMP["pdca-continuous-improvement"]
  ACT -->|"relates"| A_PROV["knowledge-provenance"]
  ACT -->|"relates"| A_SELF["self-optimization-loop"]
  ACT -->|"relates"| A_ID["task-record-identity"]
  ACT -->|"relates"| A_TIME["timeline-integrity-gate"]
  ACT -->|"relates"| A_INC["pdca-provable-skill-increments"]
  ACT -->|"relates"| E_ACT["entity/phase-act"]

  PLAN -->|"plan→do"| DO
  DO -->|"do→check"| CHECK
  CHECK -->|"check→act"| ACT
  ACT -->|"act→archive"| PLAN
```

## 解读

- 主干：`process` 被四 flow 特化，四 flow 组成 `pdca` 且循环推进（plan→do→check→act→archive）。
- Plan 锚架构/边界/确认三概念；Do 锚 ready/门禁/执行器/证据收集/销毁安全/真实验证/家目录七概念；Check 锚证据/ verdict/验收/评审四概念；Act 锚改进/溯源/自优化/身份/时间线/可证增量六概念。
- 每 flow 各对接一个 phase 实体（plan/do/check/act）。
