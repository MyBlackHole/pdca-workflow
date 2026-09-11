---
schema: pdca.protocol-release/v1
protocol_revision: 3.4.10
distribution_kind: repository_snapshot
runtime_publication_proven: false
rule_authorities:
  TREE-01: ontology:concept/work-ontology-tree
  NODE-01: ontology:concept/work-node-contract
  SCENE-01: ontology:process/work-scenarios
  SCHED-01: ontology:concept/work-tree-scheduling
  TASK-01: ontology:concept/pdca-task
  CAP-01: ontology:concept/capability-protocol
  CONTRACT-01: ontology:concept/pdca-execution-contract
  CONTEXT-01: ontology:process/select-task-subgraph
  TEST-01: ontology:concept/task-unit-test
  CASE-01: ontology:concept/task-test-case
  REWORK-01: ontology:concept/task-rework
  REVIEW-01: ontology:process/independent-work-review
  CONFIRM-01: ontology:concept/pdca-ai-friendly-confirmation
  GATE-01: ontology:concept/pdca-gate
  TRANSITION-01: ontology:concept/pdca-transition
  EVIDENCE-01: ontology:concept/pdca-evidence
  VERDICT-01: ontology:concept/pdca-verdict
  RECOVERY-01: ontology:concept/pdca-recovery
  LEARN-01: ontology:concept/pdca-continuous-improvement
  ONTOLOGY-01: ontology:concept/ontology-asset
  STATE-01: ontology:concept/pdca-phase-status
  CONTROL-01: ontology:concept/task-control
  RESOURCE-01: ontology:concept/resource-ownership
  DEPENDENCY-01: ontology:concept/work-dependency-graph
  REUSE-01: ontology:concept/ontology-reuse
  EVOLVE-01: ontology:concept/ontology-evolution
  ADOPT-01: ontology:concept/ontology-adoption
  DECOMP-01: ontology:concept/task-decomposition
assets:
- id: ontology:concept/audit/project-review
  revision: 3.4.1
  role: reusable_work_definition
  ref: ontology/concept/audit/project-review.md
  digest:
    algorithm: sha256
    value: c03b22ba57965e92c4d816ccfd6028d1c02dfca357dcd3d07a830fc6f6b679fa
- id: ontology:concept/audit/rule-consistency-review
  revision: 3.4.0
  role: reusable_work_definition
  ref: ontology/concept/audit/rule-consistency-review.md
  digest:
    algorithm: sha256
    value: 1037890af100b65d7d28df0b4b8b056c99eaf82c63cf51f39abdb4c664614249
- id: ontology:concept/audit/source-claim-review
  revision: 3.4.0
  role: reusable_work_definition
  ref: ontology/concept/audit/source-claim-review.md
  digest:
    algorithm: sha256
    value: 1caeeb1c273f9bbdfb624d832ed76f03de5a2119d645ab62e3f1640f4e7a83d6
- id: ontology:concept/audit/test-contract-review
  revision: 3.4.1
  role: reusable_work_definition
  ref: ontology/concept/audit/test-contract-review.md
  digest:
    algorithm: sha256
    value: b1bc229e75d90b6e87f7e9862ca1c84eb7f615f6ff7ffa586afc50243c28548f
- id: ontology:concept/auto-induce-evidence
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/auto-induce-evidence.md
  digest:
    algorithm: sha256
    value: bd93b603779fee4f20105d944b6c388b20e9c93ced885bc0f1525bd5ce56ddda
- id: ontology:concept/auto-induce-flow-trigger
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/auto-induce-flow-trigger.md
  digest:
    algorithm: sha256
    value: f72a056687054bd4caae7fe42fd3052d7f8b24a98666af905469032be41f6922
- id: ontology:concept/blocking-edges
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/blocking-edges.md
  digest:
    algorithm: sha256
    value: 40468f6756d20d9ad350b9f086dc0af3b365017b5c8947e12c7c337f027cac7d
- id: ontology:concept/capability-protocol
  revision: 3.4.10
  role: protocol_or_normative_navigation
  ref: ontology/concept/capability-protocol.md
  digest:
    algorithm: sha256
    value: 00ce0d48311b5a20e8e2ffd2fdd076e26098788efdc37c8e31b7256746c683bd
- id: ontology:concept/context-pointer
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/context-pointer.md
  digest:
    algorithm: sha256
    value: c227b579e4b809265c4d4ad3280467f7d5f232fa980f0b8455e069d8df833e1e
- id: ontology:concept/external-evidence-collection
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/external-evidence-collection.md
  digest:
    algorithm: sha256
    value: 12b66c49e1f7d51d7b4351099bc16fcd333e2ffc0d95b1325523cf354e02c086
- id: ontology:concept/frontier
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/frontier.md
  digest:
    algorithm: sha256
    value: cfebf6c11f8c39c9d5db1c1e282f064665d84c399d702ec532d088ccee267c2a
- id: ontology:concept/grilling-completion
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/grilling-completion.md
  digest:
    algorithm: sha256
    value: 970b18e0cdafb401af7b81f7da23e293689d9f822e8e8439b1085851b220a903
- id: ontology:concept/grilling-methodology
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/grilling-methodology.md
  digest:
    algorithm: sha256
    value: 77eefa40316b7fde3ecd04e6f866f9ef6e4276e52a88ca41dc45cc2cb13d4801
- id: ontology:concept/knowledge-provenance
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/knowledge-provenance.md
  digest:
    algorithm: sha256
    value: bd38c3f1121a3edaa3a364897f20c5defae1bb4b98e788ecccece343a0c4891a
- id: ontology:concept/meta-ontology
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/meta-ontology.md
  digest:
    algorithm: sha256
    value: 26a515a8c14c1839f1dea1e955e6f4cb836ee719d53caf22a1f6a8dacb74933f
- id: ontology:concept/ontology-adoption
  revision: 3.4.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-adoption.md
  digest:
    algorithm: sha256
    value: 38acbaadb313494d214c04c2f8d8731c1baa1cf6275be9b07d9613d37c33453b
- id: ontology:concept/ontology-asset
  revision: 3.4.6
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-asset.md
  digest:
    algorithm: sha256
    value: ff3bb36c3c398fba6b2c8a93513997f38362aa9f6b498b1eae476ce9dfeda82f
- id: ontology:concept/ontology-creation-gate
  revision: 3.4.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-creation-gate.md
  digest:
    algorithm: sha256
    value: 189792afa12f5ef39216e0da8f2a2c35d372111506298f2bf02568f1a4d1dcfc
- id: ontology:concept/ontology-detach-verdict
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-detach-verdict.md
  digest:
    algorithm: sha256
    value: 2b1762dabb88040b111f853861a5314921dee0ecb591f2e149ec8301ea3223bd
- id: ontology:concept/ontology-evolution
  revision: 3.4.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-evolution.md
  digest:
    algorithm: sha256
    value: c38aa55b3500d9bcb11a62834313b4c4371b65a6d4bcb00c3429436587d3ac74
- id: ontology:concept/ontology-fidelity-criterion
  revision: 3.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-fidelity-criterion.md
  digest:
    algorithm: sha256
    value: 0bd891da6328d7adc99c82b142939e6895138a049c4a02d71d123f5257f8f3d6
- id: ontology:concept/ontology-reuse
  revision: 3.4.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-reuse.md
  digest:
    algorithm: sha256
    value: 461ad0d78c538eea59fcd8b4839aa5e4a2958c87a5a480f8b8a2a76a90b85853
- id: ontology:concept/ontology-rule-acyclic
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-rule-acyclic.md
  digest:
    algorithm: sha256
    value: 646d384bae0cd4fa02880f2c6afd39c8a47d8dbb2905d2f5b88b5abe850bc37f
- id: ontology:concept/ontology-rule-attr-testable
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-rule-attr-testable.md
  digest:
    algorithm: sha256
    value: 709b56a965539d81f74e749dc207ce5ba1b7a231ce2b90aafc3326453545a285
- id: ontology:concept/ontology-rule-fidelity-body
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-rule-fidelity-body.md
  digest:
    algorithm: sha256
    value: 89113a290841b588f96ba89dbf1fbb3074062421ee681348a7ea911550e01703
- id: ontology:concept/ontology-rule-fidelity-diagram
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-rule-fidelity-diagram.md
  digest:
    algorithm: sha256
    value: d21820ca0eb42351f366a750858783eff18f552b93e454918f4c501bc7a3b20c
- id: ontology:concept/ontology-rule-fidelity-generic
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-rule-fidelity-generic.md
  digest:
    algorithm: sha256
    value: 8cd3452d17b6a250ae929e8f6c8c59f5dd35dc7cbceba4ef5e2232d4f4d3d0ae
- id: ontology:concept/ontology-rule-guides-range
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-rule-guides-range.md
  digest:
    algorithm: sha256
    value: d9a4870815efd7795b4e00df5d3748681d9495d756fd15240161442bf170899b
- id: ontology:concept/ontology-rule-non-dangling
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-rule-non-dangling.md
  digest:
    algorithm: sha256
    value: 89eab8b84ab8ed5fb29a325c0d6a06a98919489b44762dad1ab5eb01c2a0ad37
- id: ontology:concept/ontology-rule-richness
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-rule-richness.md
  digest:
    algorithm: sha256
    value: 6d140592c7cce83b1a49d3afee441dff376e45cc07ce9966b9d75cc2fc8bd8be
- id: ontology:concept/ontology-rule-type-controlled
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-rule-type-controlled.md
  digest:
    algorithm: sha256
    value: a3223f5bd6aad07a31d250ecbf8f79573cd8d04112475f0eb2032050eb8f87fb
- id: ontology:concept/ontology-rule
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-rule.md
  digest:
    algorithm: sha256
    value: 8dc501512aab8fceaf4c418970287e9510c14d2aa5f8e73a77f5cc7930b4f2ff
- id: ontology:concept/ontology-validate
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/ontology-validate.md
  digest:
    algorithm: sha256
    value: b9e3ac8324566d15c55e18fb5f6ff06381b2fd38f5fa9cd209308b0e8fb44825
- id: ontology:concept/pdca-acceptance-criterion
  revision: 3.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-acceptance-criterion.md
  digest:
    algorithm: sha256
    value: 583eaadd85493bc12cf1558895e74b0c95603ba8f6a8a9b5be8ea1b6297d80e9
- id: ontology:concept/pdca-ai-friendly-confirmation
  revision: 3.4.1
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-ai-friendly-confirmation.md
  digest:
    algorithm: sha256
    value: 18ac31894ed212114595db88bbc19343b8c18199fc2c304ca44d931f8ea4ddfb
- id: ontology:concept/pdca-architecture-review-metrics
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-architecture-review-metrics.md
  digest:
    algorithm: sha256
    value: 97d72c79ac9b0d2882a4c8066fc6371814e00a62cb575a0fdccbf9eadb6f2c15
- id: ontology:concept/pdca-architecture
  revision: 3.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-architecture.md
  digest:
    algorithm: sha256
    value: 900c5263baed946f4a41fb8e5cfa6a0e6f41db860cc62d2756089d86fa338b35
- id: ontology:concept/pdca-continuous-improvement
  revision: 3.4.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-continuous-improvement.md
  digest:
    algorithm: sha256
    value: c0f4d8d531482c4ed59f9181d742b6973884cc4adef68e7f393a86d3ab121db4
- id: ontology:concept/pdca-evidence
  revision: 3.4.9
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-evidence.md
  digest:
    algorithm: sha256
    value: db22e30b0344b944580a8eb9644c3aded6541dfe97161f3cdbade3668d68907b
- id: ontology:concept/pdca-execution-contract
  revision: 3.4.7
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-execution-contract.md
  digest:
    algorithm: sha256
    value: 179f776752061ef10dde3761fcf6eb59801e6b58bd655a5bedcd26a27e911db9
- id: ontology:concept/pdca-feedback
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-feedback.md
  digest:
    algorithm: sha256
    value: 238ab7981d52bd1790290c03f156b3abae23677a790e05ef0fe039ec56c780a0
- id: ontology:concept/pdca-gate-do
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-gate-do.md
  digest:
    algorithm: sha256
    value: dc3e64874cc6e178eea7512ad3e393fc9c24d4db58054cf8a30df1961cf70069
- id: ontology:concept/pdca-gate
  revision: 3.4.7
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-gate.md
  digest:
    algorithm: sha256
    value: 5590c56bb740ac2958c5ab154cc4b5512dde574453de72d1fd4ee35fad40a333
- id: ontology:concept/pdca-ontology-ready
  revision: 3.1.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-ontology-ready.md
  digest:
    algorithm: sha256
    value: 981262b55766aa5e914e53a0e06c5ab6eb7c724500698195298512164ad61e38
- id: ontology:concept/pdca-phase-status
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-phase-status.md
  digest:
    algorithm: sha256
    value: 493d012cfeb8beda78e300b5871d83a92084d5a822b0866d3a323e9cb4c6e068
- id: ontology:concept/pdca-phase
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-phase.md
  digest:
    algorithm: sha256
    value: 6d8cbd4718e6a7c947217d29bc50381deda054f27a92c5c8441de35ea7eb2259
- id: ontology:concept/pdca-provable-skill-increments
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-provable-skill-increments.md
  digest:
    algorithm: sha256
    value: 866e6149a5fe29f6a1caf6382cdf0b078636620304a16ddebf56b23f1423d815
- id: ontology:concept/pdca-recovery
  revision: 3.4.10
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-recovery.md
  digest:
    algorithm: sha256
    value: 74fc700c4e9c5a40b5f1848b147cc243679b66751a992074bc65bdd85aaf4b99
- id: ontology:concept/pdca-source-diagram-doc-verification
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-source-diagram-doc-verification.md
  digest:
    algorithm: sha256
    value: eaf68e3a496d93f57028e6687b4ac569d0c4d87a331d85f00410086b0f52efce
- id: ontology:concept/pdca-task
  revision: 3.4.10
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-task.md
  digest:
    algorithm: sha256
    value: 12cc169105c8cd5528ea30bd4814ccc632d89bae089c8876a9df78d6d5019427
- id: ontology:concept/pdca-transition
  revision: 3.4.2
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-transition.md
  digest:
    algorithm: sha256
    value: 7368bb438005e4fdfbf3848f88ec5f53b9ffc6b22a76adda12fa3b1b5baf60a4
- id: ontology:concept/pdca-verdict
  revision: 3.4.7
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-verdict.md
  digest:
    algorithm: sha256
    value: 16861d5581df97b94eeca6953fe2aba461e042c98a1e474f5899ca0fafc4058f
- id: ontology:concept/pdca
  revision: 3.4.10
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca.md
  digest:
    algorithm: sha256
    value: 8fffa40f0b9f507b34fc271d5f828fce78520f6fb00a0d3ea477d4d386e6a6df
- id: ontology:concept/phase-boundary-decision-tree
  revision: 3.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/phase-boundary-decision-tree.md
  digest:
    algorithm: sha256
    value: 4bb2c628c221d688f62c1fe0da1826fed74c1327b65b44a3edf84864e1f3e206
- id: ontology:concept/process-complexity-ruling
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/process-complexity-ruling.md
  digest:
    algorithm: sha256
    value: 931b4cf4dfc488c6d0cf23f7b2bf088ed5c541b5af7f5e83339e14c57267b693
- id: ontology:concept/process-value-verdict
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/process-value-verdict.md
  digest:
    algorithm: sha256
    value: ee25ee2ef82bfc31c9c78ab8ba89e5c3e2ef8b711a3b1eacd8484eaefee036bd
- id: ontology:concept/real-project-mechanism-validation
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/real-project-mechanism-validation.md
  digest:
    algorithm: sha256
    value: 07e835476a7e6170405241e9d9e536c698f176e8f72b01abb3cc7a5cb4b9d7b7
- id: ontology:concept/research-first-compliance
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/research-first-compliance.md
  digest:
    algorithm: sha256
    value: 9d6f36d6a2687ec8ff5a9c57f6262941179b46796a700cd1d74c1149ae1de333
- id: ontology:concept/research-first-gate
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/research-first-gate.md
  digest:
    algorithm: sha256
    value: 231c156f179397bed7f58cb9ed6206b90212ff4d390cb934ee9e69aa5592deba
- id: ontology:concept/research-web-mandatory-gate
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/research-web-mandatory-gate.md
  digest:
    algorithm: sha256
    value: 322b93ca361df468c24494327b58ed34279a8b9eedd9497a64baafa56e097e94
- id: ontology:concept/resource-ownership
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/resource-ownership.md
  digest:
    algorithm: sha256
    value: c84a72447d952f8719cc824f78a4c3ce7f6d93197f7c57d80bd55825d22de052
- id: ontology:concept/router-skill
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/router-skill.md
  digest:
    algorithm: sha256
    value: 02f8f8746ae773dd26e536d552efc939887e027fabee9f4a6dc2e7634e7e0a03
- id: ontology:concept/runtime-transition-coordinator
  revision: 3.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/runtime-transition-coordinator.md
  digest:
    algorithm: sha256
    value: 0b940bf970ac46b60eef77c291f4f0d6e911aa83b4ebc4bea75eff600d337359
- id: ontology:concept/scope-coverage-gate
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/scope-coverage-gate.md
  digest:
    algorithm: sha256
    value: adde47492ed28ea6654769d6ce6353234c1297288154df8eb9707e06efec74b8
- id: ontology:concept/self-optimization-loop
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/self-optimization-loop.md
  digest:
    algorithm: sha256
    value: 5f6836c2cf905db73c6a87b78873f13e091f66d63670c2ff0919e043af7d340e
- id: ontology:concept/skill-invocation-contract
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/skill-invocation-contract.md
  digest:
    algorithm: sha256
    value: 1858c60456e78bedc0e1c099d1992d71b9bcca723a6b1d74ea84ab43d1377b80
- id: ontology:concept/skill-mechanics-detail
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/skill-mechanics-detail.md
  digest:
    algorithm: sha256
    value: fa89bae10fa2af433c0129fed6b4992cab675e2bebd99ce34844168a83184f80
- id: ontology:concept/skill-mechanics
  revision: 3.4.6
  role: protocol_or_normative_navigation
  ref: ontology/concept/skill-mechanics.md
  digest:
    algorithm: sha256
    value: f1a34ce42371df95f35411e7d0867ebcb2e9487350932565acdeca3c7acfcdc5
- id: ontology:concept/task-control
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/task-control.md
  digest:
    algorithm: sha256
    value: ecf839bd1b58bf1f1c9a23575516ccbd162c0d046fbe39c6d2d299eec4aa9af5
- id: ontology:concept/task-decomposition
  revision: 3.4.9
  role: protocol_or_normative_navigation
  ref: ontology/concept/task-decomposition.md
  digest:
    algorithm: sha256
    value: ad4d51543b9a3f1165e719dc2a786f6173b03fdbcc7f7f57f5f0b76bd9231ff7
- id: ontology:concept/task-record-identity
  revision: 3.4.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/task-record-identity.md
  digest:
    algorithm: sha256
    value: 65413fde779a03f6f41d858b2fadbc45810c3cbc840fffa773c1e39f822265a7
- id: ontology:concept/task-rework
  revision: 3.4.7
  role: protocol_or_normative_navigation
  ref: ontology/concept/task-rework.md
  digest:
    algorithm: sha256
    value: 4a49c74ecb7a13c196c0fce2c5a7f0c46160714686a569f19eee016d33b21f9e
- id: ontology:concept/task-test-case
  revision: 3.4.6
  role: protocol_or_normative_navigation
  ref: ontology/concept/task-test-case.md
  digest:
    algorithm: sha256
    value: 46c695bc1f846d66b3c02bd142493f86891521479d358e3c66a60bd1007d2bda
- id: ontology:concept/task-unit-test
  revision: 3.4.7
  role: protocol_or_normative_navigation
  ref: ontology/concept/task-unit-test.md
  digest:
    algorithm: sha256
    value: d5701d5503a0767396a9d1ab64ae51523e45dae4e2c46d05464d95bf02f777c8
- id: ontology:concept/template-minimal
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/template-minimal.md
  digest:
    algorithm: sha256
    value: 14729374a5c843a8a7b70cb72c193fe2e3caebd755a65a892b09ecfd7a71f63d
- id: ontology:concept/timeline-integrity-gate
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/timeline-integrity-gate.md
  digest:
    algorithm: sha256
    value: 559b003f0dada2266eee6ec9d3f4bd4040aaf9eb975a9185800e9edc35e0ddcd
- id: ontology:concept/triage-state-machine
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/triage-state-machine.md
  digest:
    algorithm: sha256
    value: 47a85db9004f195cc93636586b10df96313e9d0d50b6cfda0fa1cab2e9c62d2c
- id: ontology:concept/work-dependency-graph
  revision: 3.4.2
  role: protocol_or_normative_navigation
  ref: ontology/concept/work-dependency-graph.md
  digest:
    algorithm: sha256
    value: ac21a7168c2a2672dcf02eafae862c336e723f26a911fa12436417092a4dbca1
- id: ontology:concept/work-node-contract
  revision: 3.4.1
  role: protocol_or_normative_navigation
  ref: ontology/concept/work-node-contract.md
  digest:
    algorithm: sha256
    value: 710c7cf3be8e26c0a8b8f97f3741412b8fd39c0343ce91a8c696cf33fc00f2ef
- id: ontology:concept/work-ontology-tree
  revision: 3.4.2
  role: protocol_or_normative_navigation
  ref: ontology/concept/work-ontology-tree.md
  digest:
    algorithm: sha256
    value: 13c677d0cd9d05b46ce3e4a77d1d9267fc47c5e7f353b0cde1370a44583b3e6c
- id: ontology:concept/work-tree-scheduling
  revision: 3.4.5
  role: protocol_or_normative_navigation
  ref: ontology/concept/work-tree-scheduling.md
  digest:
    algorithm: sha256
    value: 418d5fef3200f77a927749da4bff01c5b803922ab518b18b5ca59875e2986676
- id: ontology:concept/workflow-state
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/concept/workflow-state.md
  digest:
    algorithm: sha256
    value: dac8bc8e6a1e0e1cccd388fd1b693e3eeb2ef1f6b61f67bd739406e678bb4e29
- id: ontology:entity/evidence-convergence-map
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/evidence-convergence-map.md
  digest:
    algorithm: sha256
    value: 5e4effbccffd906a16b826bf8ead8f0d16bc6b56b1623c11e94f13d0a0a3efd8
- id: ontology:entity/evidence-review
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/evidence-review.md
  digest:
    algorithm: sha256
    value: a52c61a11d8e79921fca7203245a49f50a5e2d704a6e8965128c5ac758118d32
- id: ontology:entity/evidence-test-result
  revision: 3.0.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/evidence-test-result.md
  digest:
    algorithm: sha256
    value: 11d811015eec7a9dbebb7c33018c45d24313a0bc8dd99ce9f0f91780344ff416
- id: ontology:entity/phase-act
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/phase-act.md
  digest:
    algorithm: sha256
    value: 71312161b4e46de463edef06dc9e23a29a94d24e72aeebcbf6cfcc41cdee541b
- id: ontology:entity/phase-archive
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/phase-archive.md
  digest:
    algorithm: sha256
    value: a7d6a0056c6f42701759cbfb081a293bcfa5a5b8ba43344b97fb402107829ad5
- id: ontology:entity/phase-check
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/phase-check.md
  digest:
    algorithm: sha256
    value: debdc3384dd5ff1ce3870424f8f88ca0f477f22078b7d69e1d52008df907cc27
- id: ontology:entity/phase-do
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/phase-do.md
  digest:
    algorithm: sha256
    value: ff4fcd3d430bf49e5c7ae53daa2791ba238b91aa070ca68b3dc0e3a9a2e5e028
- id: ontology:entity/phase-plan
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/phase-plan.md
  digest:
    algorithm: sha256
    value: 417a871cd2ca99ca8e8674c492a9d51cc6ee4ee8c2441f52bda969892545fc86
- id: ontology:entity/transition-act-archive
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/transition-act-archive.md
  digest:
    algorithm: sha256
    value: 015bdc6481bb13dd29ae4d951d7ed56bc135629abd6aaee26f251659cd112c6c
- id: ontology:entity/transition-check-act
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/transition-check-act.md
  digest:
    algorithm: sha256
    value: 4e4bed40fde2326ce1e8718c43f2e6843677913afdc8728d210d31fdf4347766
- id: ontology:entity/transition-do-check
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/transition-do-check.md
  digest:
    algorithm: sha256
    value: ea5edd25f7430cdee390c6d24bb59bc860ce509d917c79c9c5edaf96a368ccd4
- id: ontology:entity/transition-plan-do
  revision: 3.2.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/transition-plan-do.md
  digest:
    algorithm: sha256
    value: a4df78c89a32c4f06b375cebc18c186f633644262d527d46cd115330bd433fd9
- id: ontology:entity/verdict-confirmed
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/verdict-confirmed.md
  digest:
    algorithm: sha256
    value: ae39e491785cf2ea32a2b3e2bd326e7119aa10e52b96a10706da567075673dba
- id: ontology:entity/verdict-partial
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/verdict-partial.md
  digest:
    algorithm: sha256
    value: c5ff5b092573d1526bb9f6edb9a1e4f0aea3f22833b75dbf48c765227a6e27d4
- id: ontology:entity/verdict-rejected
  revision: 2.0.0
  role: protocol_or_normative_navigation
  ref: ontology/entity/verdict-rejected.md
  digest:
    algorithm: sha256
    value: 7eaf8af0eeef6d2f03f86fa67d9b73b423f19457769aae75af4aaa3c9ab24420
- id: ontology:pattern/audit/project-review-composition
  revision: 3.4.0
  role: composition_pattern
  ref: ontology/pattern/audit/project-review-composition.md
  digest:
    algorithm: sha256
    value: dec8504b50bc49e7b86590a33e63dc8fe3b2e31f06ff291fbfb0e427b9f4dde3
- id: ontology:pattern/ontology-reuse-reengineering
  revision: 3.3.0
  role: protocol_or_normative_navigation
  ref: ontology/pattern/ontology-reuse-reengineering.md
  digest:
    algorithm: sha256
    value: db3bce8fe2f968a9b1df917914a421f534755a95b1673b7a1da1607677f3a58e
- id: ontology:process/flow-act
  revision: 3.4.1
  role: protocol_or_normative_navigation
  ref: ontology/process/flow-act.md
  digest:
    algorithm: sha256
    value: 2a921cd48a1963fd97c6e5531dba425d33ce00cb4eedc3f056eb16233a037799
- id: ontology:process/flow-check
  revision: 3.4.9
  role: protocol_or_normative_navigation
  ref: ontology/process/flow-check.md
  digest:
    algorithm: sha256
    value: 8c96a80e2185f341c178dce7a79361d283dd44dfe5f7f66483b1768f5b8d2496
- id: ontology:process/flow-do
  revision: 3.4.9
  role: protocol_or_normative_navigation
  ref: ontology/process/flow-do.md
  digest:
    algorithm: sha256
    value: 9eb5541e2eaca14e23f77e2dc4001311b67c0ea7cc634dadaaf857e61ac9096e
- id: ontology:process/flow-plan
  revision: 3.4.9
  role: protocol_or_normative_navigation
  ref: ontology/process/flow-plan.md
  digest:
    algorithm: sha256
    value: 0c108a3df77a45412d393f4d4a91c3a7c5d5ec5ffb911af95066fddda6cf9461
- id: ontology:process/independent-work-review
  revision: 3.4.9
  role: protocol_or_normative_navigation
  ref: ontology/process/independent-work-review.md
  digest:
    algorithm: sha256
    value: 555d7fbc3b330f5c5b23161c6ee2e54dad5f43585684421a1e46c46c0f5a640c
- id: ontology:process/pdca-flow-model
  revision: 3.0.0
  role: protocol_or_normative_navigation
  ref: ontology/process/pdca-flow-model.md
  digest:
    algorithm: sha256
    value: 292a3ab64a963456ccec1edf19ba68f21147e210d014a67ee91e9c66c8871069
- id: ontology:process/select-task-subgraph
  revision: 3.4.9
  role: protocol_or_normative_navigation
  ref: ontology/process/select-task-subgraph.md
  digest:
    algorithm: sha256
    value: d836f5106e6d7522e855fa8602710f7b1e6a8985060b43bcad673d1d9cff833c
- id: ontology:process/work-scenarios
  revision: 3.4.2
  role: protocol_or_normative_navigation
  ref: ontology/process/work-scenarios.md
  digest:
    algorithm: sha256
    value: a0a8109baa8ad1ac78cee71f93cf04da8c5ae64756d4c5b36658a7457673d9de
- id: ontology:concept/skill-as-ontology
  revision: 3.4.6
  role: reference_structure_revision_not_factual_certification
  ref: ontology/concept/skill-as-ontology.md
  digest:
    algorithm: sha256
    value: 47fcc355bd3d0717c6bf67314184248952e6dc33525c99e80add0bde50ac1462
- id: ontology:domain/core/ontology-skill-model
  revision: 3.4.6
  role: reference_structure_revision_not_factual_certification
  ref: ontology/domain/core/ontology-skill-model.md
  digest:
    algorithm: sha256
    value: 044592e22b3b3bf58e2be86acf6c3999fef42f20c9f7317faaa04b41b5e4b9ec
- id: ontology:concept/skill-invocation
  revision: 3.4.6
  role: reference_structure_revision_not_factual_certification
  ref: ontology/concept/skill-invocation.md
  digest:
    algorithm: sha256
    value: 8dc30eccdbe5bad64b60edaa0d3572fdae81a38f323fc0d15d7392eaf0e71751
- id: ontology:concept/failure-mode
  revision: 3.4.6
  role: reference_structure_revision_not_factual_certification
  ref: ontology/concept/failure-mode.md
  digest:
    algorithm: sha256
    value: f457b3f554cd22911cd9bc8b44485d863bcbbe4384b50d013e36dec90d557e25
- id: ontology:concept/implement
  revision: 3.4.6
  role: reference_structure_revision_not_factual_certification
  ref: ontology/concept/implement.md
  digest:
    algorithm: sha256
    value: 7d605fe54af5b95f25d36b851d0f87001a2a98f6806ab28940a66580d922cf6a
- id: ontology:concept/to-spec
  revision: 3.4.6
  role: reference_structure_revision_not_factual_certification
  ref: ontology/concept/to-spec.md
  digest:
    algorithm: sha256
    value: d6dc33ebe3b85183577a5cb0335269868496db648bfa473b3137f72593c3a841
supporting_files:
- ref: AGENTS.md
  digest:
    algorithm: sha256
    value: 2c35560c357030b3c755bccf4f0ca4d5cbdbd9565672144b2a177d0c97722a7c
- ref: README.md
  digest:
    algorithm: sha256
    value: 7ad4b0f4a2c8d73c9871b44c720393c124284d6e2ced0eb031975fef8208dc67
- ref: ontology/INDEX.md
  digest:
    algorithm: sha256
    value: c8a1b05e674073378f5be0db52baf098631e0e97dbcf130b83e7783328843c5c
- ref: ontology/LOAD-MAP.md
  digest:
    algorithm: sha256
    value: d22c0a103085eeffdc58fe47327cc370944cbd10ae8c9174a3070ea6173029c1
- ref: ontology/README.md
  digest:
    algorithm: sha256
    value: 7451c152e4baf1ed9ffbaee3eec39cff762f9153adc28470982062d612052027
- ref: templates/README.md
  digest:
    algorithm: sha256
    value: ebf27869c7f2385aef4828f82cc6e246add731833faa79ceaeee63d60c44f375
- ref: templates/archive-receipt.md
  digest:
    algorithm: sha256
    value: c5587e3693d436fabcb4d6af5b67b4c832d92570bec40fd0f2c399f62f52a6f2
- ref: templates/baseline.md
  digest:
    algorithm: sha256
    value: 0d0788b6e7b31a8c4886be32111aaf18a20a2c412957876728edf608ef955f23
- ref: templates/capability-check.md
  digest:
    algorithm: sha256
    value: ffc586a56aaed85a5638b8e189ea491d3610b1cbf0652af93c20d686d6ffb973
- ref: templates/claim-review.md
  digest:
    algorithm: sha256
    value: 699c8ec1ff294e1efeb22fbd5a9632b79e3118cd89a231d39fe1607cd4dde3f1
- ref: templates/conclusion.md
  digest:
    algorithm: sha256
    value: c3836617ec1dbcff9a21cb17c00411dfcb35829421fdc32f5db4d3d58b59f743
- ref: templates/conformance-review.md
  digest:
    algorithm: sha256
    value: 8a334b9ab131df814856dc1932d7a4c81c36d34a89d5771c0208639a6d02c4b0
- ref: templates/control-event.md
  digest:
    algorithm: sha256
    value: fcc12f6045460f824a24b210b0dc6b78ca63a71f93bb82498b0bb5b0bbad0cd9
- ref: templates/control-state.md
  digest:
    algorithm: sha256
    value: 016b70f5d84cba1e16c2180b6f927ddc4eab6392d782c5926207ec88971244c6
- ref: templates/delivery.md
  digest:
    algorithm: sha256
    value: e959a7ac78a003d785b8d81b1c9fb499ab0c787620fd8caa00aa6c49c30a5a09
- ref: templates/dependency-check.md
  digest:
    algorithm: sha256
    value: 142ed8e5dcb4ecfecc1f8ebcbf28ed298bebac032abc00f4faa4f0e1711e68cb
- ref: templates/dependency-snapshot.md
  digest:
    algorithm: sha256
    value: aa88681af88c6f7c77de0279f039499bb2e4d497e1c8e139329ac02e11bf4053
- ref: templates/dispatch.md
  digest:
    algorithm: sha256
    value: 7f943092f2791a6391bd17a672c18bf7617401c06776c43419d89c7cc85db0ff
- ref: templates/evidence.md
  digest:
    algorithm: sha256
    value: 25e2c1912f75d7a8df58cc6c79cfc3c64d09f779f0347714f96e0d90e7a6836b
- ref: templates/gate-check.md
  digest:
    algorithm: sha256
    value: 2573ff0e445e08df5fb2fcf3a8b44482b7491b2a4ccad1a6029ca389ad815e11
- ref: templates/integrity-event.md
  digest:
    algorithm: sha256
    value: dc99ce179f5d6cd33a57c1e39a83cb3eb9d300d0131df5ff124bae8cdefa2dd5
- ref: templates/knowledge-catalog.md
  digest:
    algorithm: sha256
    value: 4e0397c4a38038c4d6bad5c6d6f979e930fb8633a4d19479563965b389bb99f3
- ref: templates/observation-binding.md
  digest:
    algorithm: sha256
    value: c5be54574c3d5752613baca80f0a431288a87b66683e33075a0235187f6d0b8a
- ref: templates/ontology-adoption.md
  digest:
    algorithm: sha256
    value: 6a6dd377d39b0fdf10028e2256610e7ca1bac3cefbca282a5f8e21d2ca4f2864
- ref: templates/ontology-advisory.md
  digest:
    algorithm: sha256
    value: bb5e3568fab610701154611666603fce5a29ec5c3b21d6d61f9a39142f5daf9a
- ref: templates/ontology-impact.md
  digest:
    algorithm: sha256
    value: 3c215950e77c9f80731365aa0b3d050612e6882b3d2add64fb327d3c3cf9381a
- ref: templates/ontology-publication.md
  digest:
    algorithm: sha256
    value: df32f3619c35c9470c87c3dd4e63e9955fd8aef23cb16dfbcaa74bfe09c6eea9
- ref: templates/ontology-release.md
  digest:
    algorithm: sha256
    value: de7781d4e6bb25ea7ac9185a478bbb2d4833a59e606e56ec36fdac4d761587e2
- ref: templates/ontology-revision.md
  digest:
    algorithm: sha256
    value: 9299db6ec379e1c93f516aef943646fa402e7a87ed0e592ebb3ca3dc0ca01753
- ref: templates/operation.md
  digest:
    algorithm: sha256
    value: e856f734bb51bbc3379e6612cf5858426fe8b7c55697b82a1c95dedb127cb059
- ref: templates/regression-extension.md
  digest:
    algorithm: sha256
    value: 525de451b2eb91caf85b38d7730c963a208acadc8676603d7a8fafeea463a779
- ref: templates/request-decision.md
  digest:
    algorithm: sha256
    value: f7a9b13a147a224a95bd75c37ece2fa16fd01a335881519cfdff027e8fbef333
- ref: templates/request.md
  digest:
    algorithm: sha256
    value: 166e627f689dd263d84b80ed4c4ef87a7d3f4b66a8afb432279c40fa0f405796
- ref: templates/resource-reservation.md
  digest:
    algorithm: sha256
    value: 24f7e47ddf1d3d18169cb2ffe7a152e6969321fe2bdd8bfccca76c9a452a9f33
- ref: templates/response.md
  digest:
    algorithm: sha256
    value: 277b21ea3c27c6068bf3811ab577d556d00d34784b4d89701e809d0a41c6c7d2
- ref: templates/reuse-decision.md
  digest:
    algorithm: sha256
    value: b48b5d9ce1c821a23d75f8c22c22dcca00962af571cf3a56679659bb29f0f7a1
- ref: templates/review-package.md
  digest:
    algorithm: sha256
    value: b9eafaf991793ee51b60547456bc66a939e430889f5fff5008563657303583b4
- ref: templates/rework.md
  digest:
    algorithm: sha256
    value: 1f19fed84c15ee3bb6fb97e4443df2d488ead12b90f496176705ce17de6ad75c
- ref: templates/scenario-coverage.md
  digest:
    algorithm: sha256
    value: b99bf00c37b02e2b19b7182f2e5d04bb1eddf2122e8a58fcbdd7e66317ab7cf2
- ref: templates/subject-snapshot.md
  digest:
    algorithm: sha256
    value: e5156598aa15388863a5e06170729ee165e2637b1210df619ed2b635af3b80fa
- ref: templates/task.md
  digest:
    algorithm: sha256
    value: 1409bf24be104cbf2ee23796a11ad76d75a943191980ded935427670d530612e
- ref: templates/termination.md
  digest:
    algorithm: sha256
    value: bc15ab1f7324e4d1831fa250343c0b597f31de99d721ec66cd30fe9b9c67548b
- ref: templates/test-case-binding.md
  digest:
    algorithm: sha256
    value: 3505419061bc0ab9b0e62ed28f8008b34738582af417589717d6eec8c94a4ff5
- ref: templates/test-case.md
  digest:
    algorithm: sha256
    value: fe7de33ace2d3681d4753ff78334707e6e395e597579c336365378e64ddb2303
- ref: templates/test-run.md
  digest:
    algorithm: sha256
    value: 695e0725a32eea8fcc8411292766321658776490c72c2e5a22fb26418b610ff6
- ref: templates/test-suite.md
  digest:
    algorithm: sha256
    value: 8c05ba9c4d65493316c941251309cca702e5458c2fbb0e1d68e3fa3f360ad364
- ref: templates/transition.md
  digest:
    algorithm: sha256
    value: e3a4a238e830f6fab8e5bf0b3701d65262c62227a50d0ad05398cf4f828b38f4
- ref: templates/tree-confirmation-request.md
  digest:
    algorithm: sha256
    value: 1378789c65076c615bd0fe8ebc36644a98fc25b15fd1fce0ead5dbb89e310800
- ref: templates/tree-confirmation-response.md
  digest:
    algorithm: sha256
    value: c6b10804f3e17b902ed709b3c129600807f43c7b3287d56badbc917d2d9b0b82
- ref: templates/tree-freeze-receipt.md
  digest:
    algorithm: sha256
    value: 73fa35eedc735c8747ab21c3e300ba478282bdd5d3e619579e3021231af6f3cd
- ref: templates/tree-manifest.md
  digest:
    algorithm: sha256
    value: 91a3c56b2773bf237a89849c9002e38854d282929510b493f3bd15ecda47ef42
- ref: templates/tree-readiness.md
  digest:
    algorithm: sha256
    value: b1e08b419c65c16a7e97376398ce20e3c4a8f73970ece8c954615bd0476ebaa8
- ref: templates/tree-spec.md
  digest:
    algorithm: sha256
    value: 781edd8a5f1254d8d076fe5b02163aadd15a211d633af3723ceb8381bfc3ec9f
- ref: templates/wait-policy.md
  digest:
    algorithm: sha256
    value: caca9c2c78f397636aa7e0a2065c94b13c83fb40ab16992ddbf0a87df6da1a4f
- ref: templates/work-budget.md
  digest:
    algorithm: sha256
    value: 4d05b1b1f2dc12142c40a3c3adfe51163a35134e133aca7bf425d94611477638
- ref: templates/work-node.md
  digest:
    algorithm: sha256
    value: ecaa74785e6ca58c85c0911526e5eebad4f337a94ff3a5855c1674612e2bf6d0
- ref: templates/work-release-manifest.md
  digest:
    algorithm: sha256
    value: b0523f943c9103bec5d4d723cbfb2660a7183add1b1ca6b10ed14ca419369d84
- ref: templates/work-release-receipt.md
  digest:
    algorithm: sha256
    value: 99a74b14ebf33db24cfc0b4e6ad92a8745653be7473e6f8bfd41bbd13d42223a
- ref: templates/work-tree.md
  digest:
    algorithm: sha256
    value: 63e8d60161d8c700a56621497caaaf183177d90665a272cc8302db0755d0258d
- ref: tests/README.md
  digest:
    algorithm: sha256
    value: e5d246bbdeaaa9c100ac7c2635639e17a5554c892dc3d23c760822d0c702b6e3
- ref: tests/audit-contracts/README.md
  digest:
    algorithm: sha256
    value: c7381bb2d4379f271130c1ad423ed415e6e36fb8e7b1e40ebcdf83d9b836df4c
- ref: tests/audit-contracts/project-review-composition/suite.md
  digest:
    algorithm: sha256
    value: 074a07ca9a0a397ad6b36886fe685f9c8d9c1363b3248245b2c837e0b06d6496
- ref: tests/audit-contracts/project-review/suite.md
  digest:
    algorithm: sha256
    value: 21e20800146dc7418177654a7e0d5f6cf5e8013e495be2052920f2b16810fb32
- ref: tests/audit-contracts/rule-consistency-review/suite.md
  digest:
    algorithm: sha256
    value: 4086178d418a638abf39605a2bc42a86d689fc49712a01fed9b0b13f9d745f24
- ref: tests/audit-contracts/source-claim-review/suite.md
  digest:
    algorithm: sha256
    value: bb3af34ce1b26c06265c0bb56806a0a76463fb232f0c3e4ec2ca6e3c3f68f6ed
- ref: tests/audit-contracts/test-contract-review/suite.md
  digest:
    algorithm: sha256
    value: f4ceca26eb108f89e22ea0ec7951d5ab4ee66b1369dd838eca67b7b34d01b8a0
- ref: tests/modeling-entry/manifest.md
  recursive_manifest: true
  digest:
    algorithm: sha256
    value: b52e10714adf33b9ddfc23d7826acb52269e1334032de0b8392396f906a2c755
- ref: tests/records-regression/manifest.md
  recursive_manifest: true
  digest:
    algorithm: sha256
    value: 39200829a9d2e851f3303fc2eb03515177b8a50acc33fd3574dc28ebece3194e
- ref: examples/formal-records/manifest.md
  recursive_manifest: true
  digest:
    algorithm: sha256
    value: 900fa9203a3563ec1a79b2c7afe5a43ac3b42d82cb8a137e0e08ffb53f382934
- ref: tests/formal-records/manifest.md
  recursive_manifest: true
  digest:
    algorithm: sha256
    value: 50373fcd6f950004ce88c5b20e14ee670195b8f0bd705a51e731d6e7926245d7
- ref: tests/semantic-review/manifest.md
  recursive_manifest: true
  digest:
    algorithm: sha256
    value: 0e60260007cdb6a7f463176535daa07cac72fe011a0294b7776d2eae82113a9a
- ref: tests/records-boundaries/manifest.md
  recursive_manifest: true
  digest:
    algorithm: sha256
    value: 618157dbb51a9050920c0050d57a9df9cc2560f40753010a0567ddd0fde74e81
- ref: migration/v3.4.2-MIGRATION.md
  digest:
    algorithm: sha256
    value: d2b4c48e9ceac485ef7eaa95e361d5b2f5ccd6b033c264e7a46b3bcf84b97527
- ref: migration/v3.4.2-CHANGES.md
  digest:
    algorithm: sha256
    value: a97407c5dcbfadc50d1df57571c9efbd1de0c93940d5bba998e24ee748f2439f
- ref: migration/v3.4.2-VALIDATION.md
  digest:
    algorithm: sha256
    value: 18822c004c96f2ed7475f5015d32b277806f31bfc8b3bb383efbb5124ec29d04
- ref: ontology/contracts/record-relations.md
  digest:
    algorithm: sha256
    value: 974b73ffd062b787fe2d3f6d46141c1f1d747c0c6ea5a47d8aa37a593dbe7a30
- ref: ontology/contracts/record-shapes/archive-receipt.md
  digest:
    algorithm: sha256
    value: 61a5ff0cad839c771d9d70b4c26843222dc76f85f9f813b2033185e3d80467a1
- ref: ontology/contracts/record-shapes/baseline.md
  digest:
    algorithm: sha256
    value: 95491d3266c31a94b289f0404d643f9e81b254a8b3a6e8afc34526cbf90a96cd
- ref: ontology/contracts/record-shapes/delivery.md
  digest:
    algorithm: sha256
    value: 446b1324019f3f19626346b8862defffa63c2fc6ed37e2c1f21859aac6abbb40
- ref: ontology/contracts/record-shapes/dependency-check.md
  digest:
    algorithm: sha256
    value: e513e6df89c2dcb0b26170c44ccb5695dec42be58fa5e0a4d9f10b904f072ab7
- ref: ontology/contracts/record-shapes/dependency-snapshot.md
  digest:
    algorithm: sha256
    value: 731f6f807576e5916b39e1bca57d5a35b1fa0ae7fda31281b244016150e0b3d8
- ref: ontology/contracts/record-shapes/gate-check.md
  digest:
    algorithm: sha256
    value: 26a60486cba5a34572ac20ff086a73cd125271d92b46190e909dae00ac23392f
- ref: ontology/contracts/record-shapes/index.md
  digest:
    algorithm: sha256
    value: 6c74cc434bff4ccc10d9aec15f472b89e0f4ccd8528e94e292b9c2971704d30f
- ref: ontology/contracts/record-shapes/request-decision.md
  digest:
    algorithm: sha256
    value: 55aaa2f5227159dfdcb31a0055663b50257bfa7da2fe0818df6bde3eaa20f845
- ref: ontology/contracts/record-shapes/request.md
  digest:
    algorithm: sha256
    value: a0488db919ea9576fb45390617a15b7b67f94a2e835550428cbc515c9e11bd2a
- ref: ontology/contracts/record-shapes/response.md
  digest:
    algorithm: sha256
    value: 5ccfbfb0bf50d21df91fca040bed7323a7a5b77576788073bbe76e1539210ff5
- ref: ontology/contracts/record-shapes/review-package.md
  digest:
    algorithm: sha256
    value: 8b12ab5d7d81eae81696949917d114fbae666412a34bb85199610ac32c21a85f
- ref: ontology/contracts/record-shapes/subject-snapshot.md
  digest:
    algorithm: sha256
    value: cdd3d3b981a7d3677fc6c85abee50b07ad3fa51391370f974992f598a44c7448
- ref: ontology/contracts/record-shapes/task.md
  digest:
    algorithm: sha256
    value: 531d6fb118057a57cb24d84d2a0b910a996774b12b4e1d4741ac9fe1692785ea
- ref: ontology/contracts/record-shapes/test-case-binding.md
  digest:
    algorithm: sha256
    value: beb3fe051a6c672eaea63988e9ccbaec42c00597db3c9013657c0bf96722666f
- ref: ontology/contracts/record-shapes/test-case.md
  digest:
    algorithm: sha256
    value: a52a185cecc0ba56a559144a18ad86e57afb3ff1647840b8cca5fcc9f50950c2
- ref: ontology/contracts/record-shapes/test-run.md
  digest:
    algorithm: sha256
    value: 0239d3c5c3979c2e984d94716470391aba5546ec8f7e65d2726a8efa74a2ba82
- ref: ontology/contracts/record-shapes/test-suite.md
  digest:
    algorithm: sha256
    value: 00ac3af6d67d135d4f7acf0f2b0cb7cbda83883b7aef12b95ba6ae71c911d279
- ref: ontology/contracts/record-shapes/transition.md
  digest:
    algorithm: sha256
    value: e5aa99b49e39d28b1561459cacfa7a914f0bd5c863a751b4da65402d359ee491
- ref: ontology/contracts/record-shapes/tree-manifest.md
  digest:
    algorithm: sha256
    value: cb1f990ee31ff430badf79b780408036417250f0b351f352c3d1bc6cd46f766a
- ref: ontology/contracts/record-shapes/tree-spec.md
  digest:
    algorithm: sha256
    value: 11eef8116b560401fefedc4cfabd7db591d25fe0fa9299c6844bd0e65577c9e5
- ref: ontology/contracts/record-shapes/work-node.md
  digest:
    algorithm: sha256
    value: 8a981fec6c653e6e37154df674c90a319fdac35589edc2491c8c8757153e9148
- ref: tests/record-relations/manifest.md
  digest:
    algorithm: sha256
    value: 83075d6c29fb48e6befc13bcdd698ef1008dbe891e309666d97b66624202f81d
  recursive_manifest: true
- ref: migration/v3.4.3-MIGRATION.md
  digest:
    algorithm: sha256
    value: 3fa42e216a51bf621f51f786ab7d52c30628d64d160713ec0449a7d21a903c35
- ref: migration/v3.4.3-CHANGES.md
  digest:
    algorithm: sha256
    value: aebb2b9c925b144d5756a148c16edda84e98c502cfea263b5fdbfdadfe3bb642
- ref: migration/v3.4.3-VALIDATION.md
  digest:
    algorithm: sha256
    value: 25e441453da2f6070c0b3b107b0c125c5eba69b7a468f6af0c90ccf89b95c348
- ref: ontology/contracts/lifecycle-records.md
  role: bounded_lifecycle_contract_or_suite
  digest:
    algorithm: sha256
    value: aed90f77994d508625347e8ac736d2935d307dde16692cd54142d749cb826710
- ref: tests/lifecycle-records/suite.md
  role: bounded_lifecycle_contract_or_suite
  digest:
    algorithm: sha256
    value: 90099c42dda25620f54dbd22aac9ecda59f2460cd902ba6738556a195e3cdecc
- ref: migration/v3.4.4-MIGRATION.md
  role: bounded_lifecycle_contract_or_suite
  digest:
    algorithm: sha256
    value: ab923356dbe5b2fad493bd4874af5f42f6f49010e9c93445265a0b74c944d18d
- ref: migration/v3.4.4-CHANGES.md
  role: bounded_lifecycle_contract_or_suite
  digest:
    algorithm: sha256
    value: 0e4d490b1f6a109535a6ccac3559fdf9f3e191aeb7e7f18c53c31529d7e5857d
- ref: migration/v3.4.4-VALIDATION.md
  role: bounded_lifecycle_contract_or_suite
  digest:
    algorithm: sha256
    value: a13a58af8696352a33ad92ac6cc49ab2617b208bac74ac0ee19e603f4025e0aa
- ref: USE-PDCA.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: c93ff1b7068557982b5df98248d9d31a54bcf670f4af393b7edc3235480e4dd7
- ref: examples/cross-project/README.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: 4da52794bdf94baf76e1eec1909d792988ee31968a3532a9bf06152a48c4bd74
- ref: migration/cross-project.1-CHANGES.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: 40bcaf5d761d6eb30beb44b3c0c2e84eaaa5bac224a006855e684824aaf62c52
- ref: migration/cross-project.1-VALIDATION.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: 91da96da80715e4d7a083465f6a91d4b8f08fafd4a3e64a31113046d0913a28f
- ref: ontology/contracts/project-workspace.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: c4affa70a05d255635b8bb4c348ce31522891c4e2fcfaf469863631a88c67033
- ref: templates/project-index.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: dcb8458eae9513a3e4be6c432404c1ec844425ed91eaccda33c981841e0f783e
- ref: templates/project-task-context.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: 52f518d3a2b996a10fe49841baab153f8e925add6aa5681cdd5655252f353076
- ref: templates/project-workspace.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: c3750d5984da3c1f4634818d1e570819b74f26ca3024a54e0810b1d8b6ecb432
- ref: tests/cross-project/suite.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: dc9d269e5d6ce8102363304bc8a2593eee53c5f584df16ec2534445932ca420c
- ref: bootstrap/global-entry.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: b063e003b840a66a735831bedac9f0aac458921ebd439f258180181b03f6a067
- ref: migration/cross-project.2-CHANGES.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: 167afc225b4bd24a545187d079e6e6837be4c4e4b4f76260d484adc286cca511
- ref: migration/cross-project.2-VALIDATION.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: 445fc61db2ef1ec36a3391653c6a354b16a1a6f005dd238c5a72a2ab51ee0191
- ref: bootstrap/entry-check.md
  role: cross_project_entry_hotfix
  digest:
    algorithm: sha256
    value: 1fe673d65e3366d5ab6f70c75af552c71cba2cb4ba0daf4500a197f467a914f5
- ref: examples/cross-project/troubleshooting.md
  role: cross_project_entry_hotfix
  digest:
    algorithm: sha256
    value: 691fc324f2a9035a198bdea14615f4d536a85e0aae4f7cb4c6462c936b563816
- ref: tests/cross-project/entry-integration.md
  role: cross_project_entry_hotfix
  digest:
    algorithm: sha256
    value: 9f3644adc27bbda7406088031a3db6f41526b7f30e6b0316c81e31b0489e6a9b
- ref: migration/cross-project.2-hotfix.1-CHANGES.md
  role: cross_project_entry_hotfix
  digest:
    algorithm: sha256
    value: e0ee9f196ecac645e256ae8369e918119456e65e482d2cf44301d6afa4554208
- ref: migration/cross-project.2-hotfix.1-VALIDATION.md
  role: cross_project_entry_hotfix
  digest:
    algorithm: sha256
    value: 351eaa7d49704c78800c30a03b947871f2c11247fe5e9c12c6c2163f49897298
- ref: bootstrap/dispatch-guide.md
  role: full_pdca_dispatch_extension
  digest:
    algorithm: sha256
    value: f187ed3e50af629cea522e3d704d7c6d79aca0353a1e6d337fd52cce3d8bb1f8
- ref: examples/parallel-pdca.md
  role: full_pdca_dispatch_extension
  digest:
    algorithm: sha256
    value: 3f1debdc1453ec4fde1fcb0e8c24b2f2dff6a878dc67cf89c91ed991365b990b
- ref: migration/agent-dispatch.1-CHANGES.md
  role: full_pdca_dispatch_extension
  digest:
    algorithm: sha256
    value: 497a394394f14f30479eebb034deea2c367b961cb76a7aa7c6e03e2772ccff19
- ref: ontology/contracts/agent-dispatch.md
  role: full_pdca_dispatch_extension
  digest:
    algorithm: sha256
    value: e5d8d19994634b18fec5db2f6b1bbd17f7fb41eafd8dde9bfc2c7dd4bee9af03
- ref: templates/agent-assignment.md
  role: full_pdca_dispatch_extension
  digest:
    algorithm: sha256
    value: bb172387a2d9ae7f362acc3c1ab292378913f4805249b3c2bee637fa87fc2347
- ref: templates/scheduling-observation.md
  role: full_pdca_dispatch_extension
  digest:
    algorithm: sha256
    value: e454d2031ea9a10cae94d0c91837409c687a8a0f558bbcf539fdc5dc1766ef3c
- ref: tests/agent-dispatch/README.md
  role: full_pdca_dispatch_extension
  digest:
    algorithm: sha256
    value: ca34d4968805d2bb0bbe72764cdf81e29e9edee3c1c1a24d2f9d31db863f3f64
- ref: tests/agent-dispatch/suite.md
  role: full_pdca_dispatch_extension
  digest:
    algorithm: sha256
    value: 042c531231556b66798dd9a3e46585886bbe5a4a60588a4605503ffe37be9dce
- ref: migration/agent-dispatch.1-VALIDATION.md
  role: full_pdca_dispatch_extension
  digest:
    algorithm: sha256
    value: 2a0bfa67ddf3878d01db4d170343a88bbe2eb3c08a62c378cecc66eafc2661ad
- ref: tests/records-repair/suite.md
  role: records_repair_maintenance
  digest:
    algorithm: sha256
    value: 994389fba1c3a5dee32d5feda3afec3b1ad414dd8c8fae2aad90a9ec7a4936f1
- ref: migration/v3.4.6-CHANGES.md
  role: records_repair_maintenance
  digest:
    algorithm: sha256
    value: 143a19f7e013e47b66bae55c40761905a88de67af8abbfbefb80da3551660c8a
- ref: migration/v3.4.6-MIGRATION.md
  role: records_repair_maintenance
  digest:
    algorithm: sha256
    value: dba5e66844a2cabdbbb23032b5285c357fa8338a4b3781a97df2da47226c8e88
- ref: migration/v3.4.6-VALIDATION.md
  role: records_repair_maintenance
  digest:
    algorithm: sha256
    value: 2b7c3e8a24442ac25c0ffb2bb99d26221230b879142ef7cb2a17701de52c2518
- ref: ontology/contracts/record-shapes/conformance-review.md
  role: records_repair_maintenance
  digest:
    algorithm: sha256
    value: 830630c3043ba13a88371fb4be744c15b24a1cec0902fa68f05bf53cfebcb6cc
- ref: migration/v3.4.7-CHANGES.md
  role: records_integrity_maintenance
  digest:
    algorithm: sha256
    value: 28dbbd24c90e710f99626fbb58fddb9782f55e998983b41269e3dbd8daee9e76
- ref: migration/v3.4.7-MIGRATION.md
  role: records_integrity_maintenance
  digest:
    algorithm: sha256
    value: 9e354526144e3c77ff14d3e6c949b7eaa38df015db60e8f5257c6087ea02d304
- ref: migration/v3.4.7-VALIDATION.md
  role: records_integrity_maintenance
  digest:
    algorithm: sha256
    value: ca6eb16cc16c994df8d256d39f34152274879251485048b8dcf0ea5f632ac776
- ref: tests/records-integrity/suite.md
  role: records_integrity_maintenance
  digest:
    algorithm: sha256
    value: c4b31d852e7208e81e53d29190451ebf4047f323e676da9702fed62090ebbdaf
- ref: SKILL.md
  role: skill_entry_navigation
  digest:
    algorithm: sha256
    value: 4292d61e361a912b4c195f3236d887e8884890cda7656b168d3c8e5e659c515b
- ref: tests/entry-maintenance/suite.md
  role: entry_maintenance
  digest:
    algorithm: sha256
    value: 5eee1926aa81970f450380a990e5534780d9e1083b9b420df6d1ece913bf9f3c
- ref: migration/v3.4.8-CHANGES.md
  role: entry_maintenance
  digest:
    algorithm: sha256
    value: 09a357a821049e5aeb86605b4ee8588987788eef41b5dfe3623220c3dded5202
- ref: migration/v3.4.8-MIGRATION.md
  role: entry_maintenance
  digest:
    algorithm: sha256
    value: 7943af0f5d4777e58f0502d3a15e624a26a77eb75fbd6fd3429294b8fe01216f
- ref: migration/v3.4.8-VALIDATION.md
  role: entry_maintenance
  digest:
    algorithm: sha256
    value: bcde96d09d32deafb7fbd0cf0be19291282ec3068c2e5dbc9e112ed1e28746ea
- ref: ontology/entity/zfs-zio.md
  role: reference_knowledge_maintenance
  digest:
    algorithm: sha256
    value: 47a9fa742b027db5a8ad4aefc6d930b656b38843eda2431e7a8ad28a923fab64
- ref: tests/agent-behavior-eval/suite.md
  role: agent_method_maintenance
  digest:
    algorithm: sha256
    value: b242ed656c5fb6d99845af9a08d4300da74aff71f1ea1619c4028d7afa662f18
- ref: migration/v3.4.9-CHANGES.md
  role: agent_method_maintenance
  digest:
    algorithm: sha256
    value: 14ecb0162c90a2c1c8bd32b1d79e01a31d799bd2a1cbcb70cd664085d5330309
- ref: migration/v3.4.9-MIGRATION.md
  role: agent_method_maintenance
  digest:
    algorithm: sha256
    value: c7b36d45c86c5f05233da0151f2cdcde553186021aeaec138e507ba4792a56d4
- ref: migration/v3.4.9-VALIDATION.md
  role: agent_method_maintenance
  digest:
    algorithm: sha256
    value: 711aa2ba26cb4537290b91a89f41bdb9ce8009635f6f06d981c39735abb193d2
- ref: bootstrap/native-agent-notes.md
  role: dispatch_recovery_maintenance
  digest:
    algorithm: sha256
    value: ac0d046475ca69800b52db889d68f1a59a3c8ea59782b1e4635bac15c4eb832d
- ref: tests/agent-dispatch/recovery.md
  role: dispatch_recovery_maintenance
  digest:
    algorithm: sha256
    value: 9f3e6021f25b133f96d6eee6f912a2a3a3689a0fbed7d657ca15d8a46a453152
- ref: migration/v3.4.10-CHANGES.md
  role: dispatch_recovery_maintenance
  digest:
    algorithm: sha256
    value: 7f08df31874ebf19469fe21979aad10933997a21c1f7cb4d6f62443fd074e949
- ref: migration/v3.4.10-MIGRATION.md
  role: dispatch_recovery_maintenance
  digest:
    algorithm: sha256
    value: 373e666277673025f0fe72eada66c57aaf7e9407b4a448029cc5fd52006db334
- ref: migration/v3.4.10-VALIDATION.md
  role: dispatch_recovery_maintenance
  digest:
    algorithm: sha256
    value: a39aa2fc0b733deaf309ad3c8276ce6ed049bbffbc354e978788ce7b83825e6b
extension_revisions:
  entry_bootstrap: cross-project.2-hotfix.3
  project_workspace: cross-project.2
  agent_dispatch: agent-dispatch.1
  records_repair: records-repair.1
  records_integrity: records-integrity.1
---

当前仓库分发快照；只固定内容，不代表已获得真实宿主发布授权。
