---
schema: pdca.protocol-release/v1
protocol_revision: 3.4.11
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
  revision: 3.4.11
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-continuous-improvement.md
  digest:
    algorithm: sha256
    value: b772a587da1f316db231cc0f87ae026bba66fa37adc481c31604af91610ba46c
- id: ontology:concept/pdca-evidence
  revision: 3.4.9
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-evidence.md
  digest:
    algorithm: sha256
    value: db22e30b0344b944580a8eb9644c3aded6541dfe97161f3cdbade3668d68907b
- id: ontology:concept/pdca-execution-contract
  revision: 3.4.11
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca-execution-contract.md
  digest:
    algorithm: sha256
    value: 452000dd5efe6648c3630e4c0131b2e3b0898aea1f317150d825c5b69aad869e
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
  revision: 3.4.11
  role: protocol_or_normative_navigation
  ref: ontology/concept/pdca.md
  digest:
    algorithm: sha256
    value: 35c76928e87b0fec693161bff6c99f9984b00247847733648e29e959a580fa1c
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
  revision: 3.4.11
  role: protocol_or_normative_navigation
  ref: ontology/concept/task-unit-test.md
  digest:
    algorithm: sha256
    value: f1c0e5a7975ed7f204d47e70a0cc43777d5c59c43e4647815518711d9f9ea5db
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
  revision: 3.4.11
  role: protocol_or_normative_navigation
  ref: ontology/process/flow-act.md
  digest:
    algorithm: sha256
    value: 508e5bf837352ba2d034c101ff912ddee5eb85b8b20086f3ad798c32f519a42b
- id: ontology:process/flow-check
  revision: 3.4.11
  role: protocol_or_normative_navigation
  ref: ontology/process/flow-check.md
  digest:
    algorithm: sha256
    value: 6d37232f59ee5043455b5128216ec0fdd295b8dea33cfaa9ecd82db26b87a898
- id: ontology:process/flow-do
  revision: 3.4.11
  role: protocol_or_normative_navigation
  ref: ontology/process/flow-do.md
  digest:
    algorithm: sha256
    value: 7fd27684c0e42ac40f1b25ee085ea23d408e79dc6b2a44a19b45abfb5e16dff0
- id: ontology:process/flow-plan
  revision: 3.4.11
  role: protocol_or_normative_navigation
  ref: ontology/process/flow-plan.md
  digest:
    algorithm: sha256
    value: ae8341ab3fd9e87da44e84ef429a3c986137de9a1ecf5c4b051862d931e4037e
- id: ontology:process/independent-work-review
  revision: 3.4.11
  role: protocol_or_normative_navigation
  ref: ontology/process/independent-work-review.md
  digest:
    algorithm: sha256
    value: ce606f65a9303442fe57e35c5f1c8634180c8c51d793c310baf551c53a5ccf49
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
    value: 42f940d103318b725349150db0fd4d2b36154016f13b4fc6da9b518f042c9e2f
- ref: ontology/INDEX.md
  digest:
    algorithm: sha256
    value: 97d81d20e2bbb49748827953410bf737e59cd1a5f42b5c698fa6d6931ad3a53a
- ref: ontology/LOAD-MAP.md
  digest:
    algorithm: sha256
    value: 68cf87d30bbaab01540911817a070a817f1ca131e4c8ce72abcdeb2c2a59137d
- ref: ontology/README.md
  digest:
    algorithm: sha256
    value: 7451c152e4baf1ed9ffbaee3eec39cff762f9153adc28470982062d612052027
- ref: templates/README.md
  digest:
    algorithm: sha256
    value: 1c71fa23e1144d72b0940c7ec1f2f4e0bdb9e8a0260d062a2c6d5a2db463d471
- ref: templates/archive-receipt.md
  digest:
    algorithm: sha256
    value: bad1580c3e58c3b40764f9d57b36622ed5e63d59c400ba7c6d8b28f369350fa0
- ref: templates/baseline.md
  digest:
    algorithm: sha256
    value: 3eb56c27a9219e5f508f65a9edf4e4f6b9238fc7e8acd66a17b212fbf276eedd
- ref: templates/capability-check.md
  digest:
    algorithm: sha256
    value: 7035e0258980e02fb3a02dd19eccfea5465044f51158d3c1dea44bcb0cceab37
- ref: templates/claim-review.md
  digest:
    algorithm: sha256
    value: 4e2f1b2075d9a67d3da46bedbd16be39244a009aca78142578a87591c80c19d4
- ref: templates/conclusion.md
  digest:
    algorithm: sha256
    value: 7ea2c53ffbfa6e0efa0fe75d571694817d265817337d3d0143ed7edd151a17c0
- ref: templates/conformance-review.md
  digest:
    algorithm: sha256
    value: 5a8bec5e2735ce35581e84ed0ab73b69a9e50b30efe6636adb9bd7dc551e1636
- ref: templates/control-event.md
  digest:
    algorithm: sha256
    value: 46dbea5d47b68478ff6b47334a38d4accf471867069338b8dfc4dfc87a85d35d
- ref: templates/control-state.md
  digest:
    algorithm: sha256
    value: 50296d92eb13eb4029242f8d4b2e63f839a1070ab5f41d301cbd7ebb1e004870
- ref: templates/delivery.md
  digest:
    algorithm: sha256
    value: b9e0498a08c193393c22a2f9e85233dc107086adb73e09162da0b5dd782721de
- ref: templates/dependency-check.md
  digest:
    algorithm: sha256
    value: 014da8fa23fcd783ef671361f5d1764b0961dd57fe71a4a98d0ca3b212b181b7
- ref: templates/dependency-snapshot.md
  digest:
    algorithm: sha256
    value: 0b3d12171db9e4fc0f0a7fb3b357aaea3b7aedb5bd56de6fa77a909282b0f335
- ref: templates/dispatch.md
  digest:
    algorithm: sha256
    value: 7838ca17296a1e3afacdb4060cebf60f33140a8263141724c95513be1a4d5bc0
- ref: templates/evidence.md
  digest:
    algorithm: sha256
    value: 667b96921d8bca2be3f98e3d1aefd4ee928f9810b798bd7b23f0722c2b7e4e02
- ref: templates/gate-check.md
  digest:
    algorithm: sha256
    value: 2677e26afbdba060822196a773d3c3a9225ed4de036eef858d85abf85a7ddccc
- ref: templates/integrity-event.md
  digest:
    algorithm: sha256
    value: dfdf8adb29e01929275d319e7422d92162a39f5b710e4c473869601da0233efc
- ref: templates/knowledge-catalog.md
  digest:
    algorithm: sha256
    value: 3cebe01fdc011e5347c9421a4941b4fd92230f21db7c1493080fd59bedec7045
- ref: templates/observation-binding.md
  digest:
    algorithm: sha256
    value: 7a2979f210e1e4ad7724e4c91e3d80813506ca81835a1dcc9e112c5ee60b8265
- ref: templates/ontology-adoption.md
  digest:
    algorithm: sha256
    value: eb643288f8c3cc10c7e65a5e891dce10bd7fb7c257b3b927e34f25829fc34e99
- ref: templates/ontology-advisory.md
  digest:
    algorithm: sha256
    value: 513a977755a4355584a9baf3a8f1f8d82ec6d7570748662728f4ff15e348655a
- ref: templates/ontology-impact.md
  digest:
    algorithm: sha256
    value: df9ef08daa906b5c890b41dd017a62a1671d2ae73fef108b7a601035e8f874b5
- ref: templates/ontology-publication.md
  digest:
    algorithm: sha256
    value: 67f8dad0d81bf5de5608f27190066f599e07256c2888ddf216e3cd880ec1aef7
- ref: templates/ontology-release.md
  digest:
    algorithm: sha256
    value: 3b2190be5600dcb418a0742b593a3dbd8b96e2366b8c6db46da1e733f950c962
- ref: templates/ontology-revision.md
  digest:
    algorithm: sha256
    value: 0f61b4ec294d794f4d55cf4500166abadf0b4a013d671c2a7a9606f27ba2f9b8
- ref: templates/operation.md
  digest:
    algorithm: sha256
    value: 7dbd94c4c8b9bfb041bd621956d98d6eb52510c7aa117bc1b7bc872096b40d3e
- ref: templates/regression-extension.md
  digest:
    algorithm: sha256
    value: 39b76ae00ef3ded3b35a4a773b6fa736b1b6956fe639b6b74607d3f50ad67008
- ref: templates/request-decision.md
  digest:
    algorithm: sha256
    value: ad3efd387aed51951a5c9f9ed18e9116fbb1dabd0099f40f48cdcb38c64bbd77
- ref: templates/request.md
  digest:
    algorithm: sha256
    value: 4f57b4201fac723e76def691364d54218675a86c528b3434dd16eaafcbd95f30
- ref: templates/resource-reservation.md
  digest:
    algorithm: sha256
    value: 467fd42417ac1b268319b629afd65ea43900425428b253731e0e87cc341a8395
- ref: templates/response.md
  digest:
    algorithm: sha256
    value: 5ce838a1353f64d4c31bb3bb110ca5ad0aac752cecdd51423ceaec2c012cc4fa
- ref: templates/reuse-decision.md
  digest:
    algorithm: sha256
    value: 7d9cdd190ffaff256148db72bc2e4f6d397abf8a20f5b64f27e4d93f6e6b5475
- ref: templates/review-package.md
  digest:
    algorithm: sha256
    value: c1608aacfbd6c30af2c1f9a5b15100b9c6519070003059a3311411f78cf15984
- ref: templates/rework.md
  digest:
    algorithm: sha256
    value: 7bb010e29b6c6fa5fcc717acde59e370e18a1d85a1353545eb619d8f3215cf36
- ref: templates/scenario-coverage.md
  digest:
    algorithm: sha256
    value: 3a15124b732350953766404351e3340cd2bdf72073175cfe77750f79df11cbbc
- ref: templates/subject-snapshot.md
  digest:
    algorithm: sha256
    value: f760c101a995c43e0fa6fcf2644ad6be449e04c21a71fdb2f0b75f44c34ef6ee
- ref: templates/task.md
  digest:
    algorithm: sha256
    value: 7b35d783f805c6005b5bddeddc339c9d35b8d3517e8a9eb3ecfd1acc366c7da3
- ref: templates/termination.md
  digest:
    algorithm: sha256
    value: aa9721c418c2168d305fea9b45d54a16237edf5912e4faed8cbb427202dede41
- ref: templates/test-case-binding.md
  digest:
    algorithm: sha256
    value: 33c31e86d76871c70d34cb9a21425278a01b66e1fc5463eb3e40321ba321aa9b
- ref: templates/test-case.md
  digest:
    algorithm: sha256
    value: 0c0a7c6fcf5be1cf52bbd05ca343392bf834344ced84f22ba7c17fa0c286fdd3
- ref: templates/test-run.md
  digest:
    algorithm: sha256
    value: 925245a0e898f99c0dbe07edff15f784361aa48fbfc98e90b6b76968a6bd217e
- ref: templates/test-suite.md
  digest:
    algorithm: sha256
    value: 148a9c91fcfbf9b0d9d596312621c36048a048a19a6c6c1725a32c08861fc5e6
- ref: templates/transition.md
  digest:
    algorithm: sha256
    value: 2980415d691a0c04e76f836c450adfd0f402a6c16503410af82d70387c5bb832
- ref: templates/tree-confirmation-request.md
  digest:
    algorithm: sha256
    value: ff3c0be0933c65e6e01f9d8f677dcf0bb186815c5b5eb3d0a9f1fed20ac5fa5b
- ref: templates/tree-confirmation-response.md
  digest:
    algorithm: sha256
    value: 0afe387e702d85a5ecd6a60a618ec32b5347eed8a66ababe6bb960666e1cccf4
- ref: templates/tree-freeze-receipt.md
  digest:
    algorithm: sha256
    value: 49017598aad4b55c513e84e05d47e21fe50d7c418b5c82afee6eba2a1e18d9b3
- ref: templates/tree-manifest.md
  digest:
    algorithm: sha256
    value: 6436a62efbe576e2f22b6ce0c54957cc1b3614549cddb6dd35da500dfccb721c
- ref: templates/tree-readiness.md
  digest:
    algorithm: sha256
    value: a7e753e062f850e7ea9f52ad04b608e9fc23c7f04f78f65238a9696c8278f234
- ref: templates/tree-spec.md
  digest:
    algorithm: sha256
    value: 030526198635576767d58cfa75764561610f982b4dda02a6c087f50795febe85
- ref: templates/wait-policy.md
  digest:
    algorithm: sha256
    value: 7fa8428e9633a843d530c48702566933afcf89607832cfac3e8b1b5f6c29bc82
- ref: templates/work-budget.md
  digest:
    algorithm: sha256
    value: 5e13c126d06baf209b44c531bd8e5138f7f16df07960ccf114ce3c3e1f3ba452
- ref: templates/work-node.md
  digest:
    algorithm: sha256
    value: 84322c5de62e84a63d8e03fef01d5080fd1e7daab1dd0d4d9b22fed866428e71
- ref: templates/work-release-manifest.md
  digest:
    algorithm: sha256
    value: 42fac402d643f522d7f46fc8c24a2ff709d9573625f47302348fb863dd5cb1f2
- ref: templates/work-release-receipt.md
  digest:
    algorithm: sha256
    value: 46bf6613961a2fb4d46f2fed3c9331530078a8d5d4d39d4985a6262800670dac
- ref: templates/work-tree.md
  digest:
    algorithm: sha256
    value: 019605d67eb5bdfa4da571e5871ffc6213085acaa9cb95c65f184e3fb3c967f1
- ref: tests/README.md
  digest:
    algorithm: sha256
    value: decb99d547c4e00e21d4f61b5ab83265eab9969bcdc35232631dcda6e22f02dd
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
    value: 15814e267094cb9ea5432b4e0e7317070aaffdb73d4ee7d8dfdb0fc599bcc489
- ref: ontology/contracts/record-shapes/baseline.md
  digest:
    algorithm: sha256
    value: 1d82b17f9ea183e7225ef22c706236786e3fac454375131f495ec6c150c958f8
- ref: ontology/contracts/record-shapes/delivery.md
  digest:
    algorithm: sha256
    value: 64d1a92b889ccc606cfcfe00fab60c5ebc645df2b80e5c92f06beb36eac8c7a6
- ref: ontology/contracts/record-shapes/dependency-check.md
  digest:
    algorithm: sha256
    value: 84a1848469d026341ab78bd2cfdf55ed6dc554834f5dc486985b1738373ce547
- ref: ontology/contracts/record-shapes/dependency-snapshot.md
  digest:
    algorithm: sha256
    value: d011a7df77bb3e3906fb211d7c61305f6882e5fd2b601bba545a685b937e0a85
- ref: ontology/contracts/record-shapes/gate-check.md
  digest:
    algorithm: sha256
    value: eb4aa7f72c07aabf405f51128ff23f1ee6fe106cc0a77a7cc4baf0116a64df14
- ref: ontology/contracts/record-shapes/index.md
  digest:
    algorithm: sha256
    value: 41d7aa0cb4b787438faf4661cd169eef47d327a5240e9641c226b220bf30ad3a
- ref: ontology/contracts/record-shapes/request-decision.md
  digest:
    algorithm: sha256
    value: bcdbd2c5848f94491795cd63a8e891809df6460449ae68746b77447fd5129638
- ref: ontology/contracts/record-shapes/request.md
  digest:
    algorithm: sha256
    value: cb6b450110ccd7cdd55b17a57ba07550c69968f9c0aa6b2e614a3215fe641587
- ref: ontology/contracts/record-shapes/response.md
  digest:
    algorithm: sha256
    value: 11611bf6b814755a7473428b0333b7173687219d25c6298cded969aab276fa2a
- ref: ontology/contracts/record-shapes/review-package.md
  digest:
    algorithm: sha256
    value: 9196650edb90cb649ad089e99532b692a5b95feae6a6e1d5d9442bfdf56fe71f
- ref: ontology/contracts/record-shapes/subject-snapshot.md
  digest:
    algorithm: sha256
    value: 700edb57eabad8a13bf59892c050a6ba87d0d07f81b55d7eb0ceda268e26394c
- ref: ontology/contracts/record-shapes/task.md
  digest:
    algorithm: sha256
    value: caed40bbe963345bcd2beba27e705af553829d99df763efe785390e891bbf3d0
- ref: ontology/contracts/record-shapes/test-case-binding.md
  digest:
    algorithm: sha256
    value: d3c259393286a9f506f70ea90db3984cdf3dad91a1ad7a45b92e8acfdaf2b286
- ref: ontology/contracts/record-shapes/test-case.md
  digest:
    algorithm: sha256
    value: c82f6209019a1fcdb47816687e6411e84abd4d8885d34bff040a1caebfcfc174
- ref: ontology/contracts/record-shapes/test-run.md
  digest:
    algorithm: sha256
    value: f63b80b6750e0a2ac86e2338e3d6dcaa69e1fe52723679b4a683e8c63b060d8e
- ref: ontology/contracts/record-shapes/test-suite.md
  digest:
    algorithm: sha256
    value: 0ad7d462529604efc1637b47286855e8aed1f58f2fa9d64d077792074e621c41
- ref: ontology/contracts/record-shapes/transition.md
  digest:
    algorithm: sha256
    value: a54e2eb601ebc4cc4224dc031aa143bfe204e47310aa440c88a2fb6e66a7aae3
- ref: ontology/contracts/record-shapes/tree-manifest.md
  digest:
    algorithm: sha256
    value: dd732d8921d044f9bfea5def10da0c7a9c438f5bbe5fb81581814a2cda83960e
- ref: ontology/contracts/record-shapes/tree-spec.md
  digest:
    algorithm: sha256
    value: ffacd905865d7f6155b60b12d6db07258ac2f4669c19842ac1e8685a6ba88568
- ref: ontology/contracts/record-shapes/work-node.md
  digest:
    algorithm: sha256
    value: 47c7874b02a2cf32712aba5d08341c6d3e88a9e8ab029e175153a5601cbcd20a
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
    value: f28b132715ebb048270391b569a0286f2ed683e8099cc133c6c06b81f0783ed8
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
    value: aa4616a258bc7d97d72f5bef47a7b781d21e7d4acb2c77795f7db348fd60af17
- ref: templates/project-index.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: 52b89f1689f452c5bdc0a6bfc91f687007b71151b1e79830ce55c6fa211926e9
- ref: templates/project-task-context.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: 66809557033d3657d4a5b3dcb1e9a0d3230f926d6f2be641c625776b3d8df3e9
- ref: templates/project-workspace.md
  role: cross_project_extension
  digest:
    algorithm: sha256
    value: f22ff8e7ccb3a4dcdb1f063b008264222e38f5c6be5c3c0d6feb043701924b37
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
    value: ac58d254b357489aab5c9a74b46bcf8aaf727b1447956d16498a2af059db0660
- ref: templates/agent-assignment.md
  role: full_pdca_dispatch_extension
  digest:
    algorithm: sha256
    value: 828baff5884b56c7c68922e74507abac123a2c0f58b6ac76a92e4b2cb804ac86
- ref: templates/scheduling-observation.md
  role: full_pdca_dispatch_extension
  digest:
    algorithm: sha256
    value: e95a6ebdc9935045b0199edc8768006cccbdefe3cba1ded0c4f6b2f79a7baddc
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
    value: db22e1f2d84e9b16beba5d1c3b526d77481c019aa4b1a54fb4f417bd695ed21d
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
    value: 2639611a9f60ad8fcf15e89d1e2bfb9357cc5994bd4169cd4a2dac758dfb68b9
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
- ref: bootstrap/work-methods.md
  role: professional_method_navigation
  digest:
    algorithm: sha256
    value: 91abb2fd17bd3fee9c55fe85ce5eb8ce50bcb523017f2cc3e52859e0d7180645
- ref: tests/professional-work/suite.md
  role: professional_method_eval_navigation
  digest:
    algorithm: sha256
    value: d48999eb61f9eff0928d7fe68e8e857167092413802b6cddbd9288c2bbe3e776
- ref: migration/v3.4.11-CHANGES.md
  role: release_documentation
  digest:
    algorithm: sha256
    value: ebf636908ce04dee42dd0d40ef8edab5aa828611860bf0c4ddb8d834d871c944
- ref: migration/v3.4.11-MIGRATION.md
  role: release_documentation
  digest:
    algorithm: sha256
    value: c9a9725522904fd7da94663e8319092045b231f0e3e5fd12c203186c9fb411bc
- ref: migration/v3.4.11-VALIDATION.md
  role: release_documentation
  digest:
    algorithm: sha256
    value: b35099e6912046b0b3c3eb8a264131340ffab696951230ba081bf7e78aca4513
extension_revisions:
  entry_bootstrap: cross-project.2-hotfix.3
  project_workspace: cross-project.2
  agent_dispatch: agent-dispatch.1
  records_repair: records-repair.1
  records_integrity: records-integrity.1
---

当前仓库分发快照；只固定内容，不代表已获得真实宿主发布授权。
