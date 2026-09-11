---
schema: pdca.test-defaults/v1
scene: ontology_modeling
input_parameters:
- original_request_or_parent_seed
- protocol_snapshot
- authorized_scope
- requirement_mapping
- current_task_identity
- real_tool_binding
- work_budget
runtime_result: NOT_RUN
---

# 当前建模入口的公共设置

适用于根从原请求启动、孩子从已固定父seed启动。每任务在Plan形成自己的suite/case本地绑定，按TEST/CASE固定参数、必须案例、oracle和真实工具；不能直接把local_binding_required当运行节点身份。

Do后固定当前候选作为subject，逐例核验。正/负控制来自明确文件或按case指定的单一差异生成，执行前固定变体和注入核验；没实际运行控制不能说识别力通过。当前对象已知失败仍可诚实Check，不能篡改判据。全部本地实际结果来自当前任务，旧控制PASS不替代。

本套件只覆盖通用建模验收。领域专属要求在Plan追加不可删减的本地case；三场景产出suite在Do生成并受此套件检查，不反向当本次Plan判据。父本地检查不等后代；真实宿主条件仍由GATE/CAP核验，fixture不能放行。
