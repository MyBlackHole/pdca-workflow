# 测试用例 → PDCA 本体映射表（T2130，63/63）

以本体节点为锚（flow/skill/concept/entity/pattern/domain），脚本仅作执行旁证。锚点均已验证存在。

## flow 门禁与流转

- test_convergence.py → ontology:domain/pdca/skill-verify-convergence + ontology:concept/pdca-evidence
- test_flow_audit.py → ontology:concept/pdca-transition
- test_gate_compliance.py → ontology:concept/pdca-gate
- test_gate_negative.py → ontology:concept/pdca-gate
- test_gate_remediation.py → ontology:concept/pdca-gate
- test_fix_confirmation_gate.py → ontology:concept/pdca-ai-friendly-confirmation
- test_identity_diagnostics.py → ontology:concept/task-record-identity
- test_task_identity.py → ontology:concept/task-record-identity
- test_state_contract.py → ontology:concept/pdca-phase-status
- test_operations.py → ontology:concept/pdca-home
- test_workflow_ai_usability.py → ontology:concept/pdca-ai-friendly-confirmation
- test_mechanism_fixes.py → ontology:concept/real-project-mechanism-validation
- test_research_first_gate.py → ontology:concept/research-first-gate
- test_tickets_gate.py → ontology:concept/tickets-leaf-exemption
- test_seam_ci_gate.py → ontology:process/flow-plan
- test_seam_contract.py → ontology:process/flow-plan

## 研究与证据

- test_research_web_evidence.py → ontology:concept/research-web-mandatory-gate
- test_register_evidence_anchor.py → ontology:concept/pdca-evidence
- test_recall_brief_decisions.py → ontology:concept/triage
- test_ontology_full_lifecycle.py → ontology:concept/pdca-evidence

## Grill / Triage / Tickets

- test_grilling_efficiency.py → ontology:domain/pdca/ai-efficiency-frontier-batch-grilling + ontology:domain/pdca/skill-grilling
- test_triage_brief.py → ontology:concept/triage
- test_ticket_dag.py → ontology:concept/blocking-edges + ontology:domain/pdca/skill-to-tickets
- test_to_tickets_tree_split.py → ontology:domain/pdca/skill-to-tickets
- test_t0474_ontology_tree.py → ontology:entity/ontology-deep-integration
- test_ontology_tree_split.py → ontology:domain/pdca/skill-to-tickets
- test_ontology_clash.py → ontology:domain/pdca/skill-to-tickets
- test_out_of_scope.py → ontology:concept/triage-state-machine
- test_t0472_ontology_split.py → ontology:entity/ontology-deep-integration-split + ontology:domain/pdca/skill-to-tickets

## Skill 契约与内容

- test_skill_structure.py → ontology:concept/skill-mechanics
- test_gotchas_contract.py → ontology:concept/skill-mechanics
- test_content_audit.py → ontology:domain/pdca/ai-efficiency-lever-audit-limits
- test_ai_friendliness_hardening.py → ontology:domain/pdca/ai-efficiency-ai-friendliness-review-methodology
- test_execution_and_invocation_contracts.py → ontology:domain/pdca/ai-efficiency-ai-execution-and-invocation-contracts
- test_harness.py → ontology:domain/pdca/ai-efficiency-contract-test-pattern
- test_skills_increments.py → ontology:concept/pdca-provable-skill-increments
- test_self_audit.py → ontology:concept/pdca-provable-skill-increments
- test_writing_for_agents_levers.py → ontology:domain/pdca/ai-efficiency-writing-for-agents-levers
- test_diagnosing_bugs_enhance.py → ontology:domain/pdca/skill-diagnosing-bugs
- test_deepening_policy.py → ontology:domain/pdca/skill-design-it-twice
- test_merge_conflicts_intent.py → ontology:domain/pdca/skill-resolving-merge-conflicts
- test_scenario_boundary_check.py → ontology:concept/pdca-scenario-boundary-rule
- test_prd_template_ontology_section.py → ontology:concept/template-minimal

## 本体脚本群语义锚

- test_ontology_validate.py → ontology:concept/ontology-validate
- test_ontology_validator_from_nodes.py → ontology:concept/ontology-rule
- test_meta_ontology.py → ontology:concept/meta-ontology
- test_ontology_auto_induce.py → ontology:concept/auto-induce-evidence + ontology:concept/pdca-continuous-improvement
- test_ontology_induction.py → ontology:concept/auto-induce-evidence
- test_ontology_reason.py → ontology:concept/domain-modeling
- test_ontology_fragment_scope.py → ontology:concept/ontology-creation-gate
- test_t0478_ontology_ci.py → ontology:concept/ontology-creation-gate
- test_ontology_deep_integration_overview_scaffold.py → ontology:domain/pdca/ontology-deep-integration-overview
- test_ontology_split_scaffold.py → ontology:entity/ontology-deep-integration-split
- test_t0473_ontology_test.py → ontology:pattern/testable-signal-to-test-derivation + ontology:domain/pdca/skill-testing-strategy
- test_testable_signal_scaffold.py → ontology:pattern/testable-signal-to-test-derivation
- test_pdca_context.py → ontology:concept/context-pointer
- test_pdca_ontology_correct.py → ontology:concept/pdca
- test_pdca_task_consumption.py → ontology:concept/pdca-task
- test_t0475_ontology_knowledge.py → ontology:concept/pdca-task
- test_t0477_ontology_existing_tree.py → ontology:entity/backup-system + ontology:entity/report-center-system
- test_arch_review_hotspots.py → ontology:concept/pdca-architecture-review-metrics
- test_arch_review_html.py → ontology:concept/pdca-architecture-review-metrics

## 脚本 → 本体（删改依据）

- 49/50 脚本有本体锚（门禁脚本→pdca-gate系，本体脚本群→ontology-creation-gate/meta-ontology/auto-induce，运维脚本→pdca-home，skill审计脚本→skill-mechanics/ai-efficiency系）。
- 无本体对应脚本（删除候选）：`scripts/validate-gate.sh` 唯一（D-1，待用户确认）。
