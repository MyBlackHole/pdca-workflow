# PRD — P1补图补例首批20节点

> 任务：T0538 / 0902-fidelity-p1-diagrams / development / plan
> 承接：T0534 P1路线，统计层G7-G10当前56%触发率仅统计未阻断，本任务首批20中频域补齐至可实现。

## 背景

413节点中 MISSING_DIAGRAM 234（56.7%）、MISSING_SOURCE 233等统计层过度但已降级，需分批补齐。

## 验收标准
- [ ] AC-1 20节点mermaid≥1且Source行号齐全
- [ ] AC-2 20节点含正反例与门禁且行数≥60
- [ ] AC-3 audit MISSING_DIAGRAM 234→214且validate 0

## 范围
Top20中频域（backup/ai-efficiency/benchmark等，按score升序取20），直接进Do分批实施。
