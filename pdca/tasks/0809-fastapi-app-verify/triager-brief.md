# T0234 Triage Brief — FastAPI 应用验证 PDCA 流程

## 来源
用户明确需求：**开发一个新项目来测试 PDCA 流程**（"使用 python web 测试"）。
选择 Flask/FastAPI 应用形态。这是对 T0232/T0233 新机制在真实工程场景的
元验证（原 T0218 buf 字节序载体因 6110 工作区 T0222 未提交改动冲突而放弃）。

## 分类
- 类型：enhancement
- scenario_type：development
- 验证对象：PDCA 流程自身（seam 契约 / ready-set / 词汇契约 / 内容预算）

## Claim 验证（P0）
- Python 3.14.6 + FastAPI 0.141.1 已装（flask 未装）✅
- pytest 9.0.3 可用 ✅
- knowledge/ 无 fastapi/web 应用资产（无重复）✅
- skills/ flows/ 无 web 应用开发技能覆盖（空白领域）✅

## 验证目标（新机制在真实工程的实测）
1. P3.5 seam 确认门禁：PRD seam 清单 → 契约测试守护（文件存在/模块一致）
2. P4 ready-set 拆解：to-tickets + dependencies + compute-frontier
3. 词汇契约：接口设计只用 module/interface/seam/... 拒绝 component/API 等
4. 内容预算：新增资产不突破 bytes baseline

## 后续
P1 澄清 → P2 Grill → P3 PRD → P3.5 seam → P4 拆解 → P5 → P6 → Do
