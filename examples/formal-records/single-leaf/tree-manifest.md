---
schema: pdca.tree-manifest/v1
state: candidate
protocol_revision: 3.4.4
work_id: W
tree_revision: TR
proposal_id: FIXTURE-PROP
root_node_id: N
tree_spec:
  ref: tree-spec.md
  digest: 87a3e3c7ff427205d4054d928c617283ab151c3ca198df794088868b15d3f954
objects:
- object_id: tree_spec
  role: tree_spec
  revision: '1'
  required: true
  ref: tree-spec.md
  digest: 87a3e3c7ff427205d4054d928c617283ab151c3ca198df794088868b15d3f954
  dependencies:
  - closure-61f6305a420cc8be
  - node
  - protocol_baseline
  - subject_snapshot
- object_id: node
  role: node
  revision: '1'
  required: true
  ref: artifacts/node.md
  digest: 81eaa221789cdfeff30be867b6bb55b0e2a0ab89879119e4b4d75fb682b8ecc4
  dependencies:
  - protocol_baseline
  - subject_snapshot
  - suite_modeling
  - suite_projection
  - suite_verification
- object_id: graph
  role: graph
  revision: '1'
  required: true
  ref: graph.md
  digest: 6089319f76e733736acf81c0ef915bac783f6f0d4d8a3d7a37f0770ffe08065f
  dependencies: []
- object_id: graph_check
  role: graph_check
  revision: '1'
  required: true
  ref: graph-check.md
  digest: f3f3ce14b3b0fce804142c6c477513bbbe1999bce8ada19d8be573565e341fe0
  dependencies:
  - graph
- object_id: modeling_delivery
  role: modeling_delivery
  revision: '1'
  required: true
  ref: records/T-M/delivery.md
  digest: 4016dc778178c6d9c94166472aaba953e4bbae9d701d7622c3cecc6bc69d9b69
  dependencies:
  - closure-f310ce52237c422e
  - closure-fae60b9ffb87556e
  - node
  - suite_modeling
  - suite_projection
  - suite_verification
- object_id: modeling_terminal
  role: modeling_terminal
  revision: '1'
  required: true
  ref: records/T-M/archive.md
  digest: 11951c5b7bad92a8cd9109f8aaa7bec3e2d905a954d4355f54ace90cf4f52c61
  dependencies:
  - closure-59ef92f1f9bbd255
  - closure-847cca9bb60aad2c
  - closure-a5a5687ec8f7fc02
  - modeling_delivery
- object_id: protocol_baseline
  role: protocol_baseline
  revision: '1'
  required: true
  ref: inputs/protocol.md
  digest: 5e2889519440d299afb53ff2bc159c4b8f5c0635ba45408864badfd18c87dc6e
  dependencies:
  - closure-0c4160b956d93b36
  - closure-0da29a0d5b5b5c76
  - closure-1de36500771a63ad
  - closure-24c52b4d8a2bc24e
  - closure-24d10c5b6561837e
  - closure-2561c5e85aae731c
  - closure-2825a75cc8a952fd
  - closure-37a49842358eb585
  - closure-3ef2f154583cf86e
  - closure-44ada5b40c1ecdb7
  - closure-457118c5ec6959c2
  - closure-47a5cfe898ee2ed8
  - closure-5475d29bbc747604
  - closure-572badcf455b9405
  - closure-61f6305a420cc8be
  - closure-7fd88f56f461df26
  - closure-8be25320d3008c17
  - closure-8d623f7777f68322
  - closure-9742c9b2b1319767
  - closure-9eb45479cc0531dd
  - closure-a000b11bf0210761
  - closure-a305a069bee532e0
  - closure-af68af2a541cde29
  - closure-aff3d4a34fcad92f
  - closure-bc1719a5a48ee4b2
  - closure-d586c86271afa18c
  - closure-e0ea2c57978b0b12
  - closure-e6d57ecfa69f17ce
  - closure-e8c1ca91f2db0ed2
- object_id: subject_snapshot
  role: subject_snapshot
  revision: '1'
  required: true
  ref: inputs/subject.md
  digest: bcba729e20fdabb1399845aeea812410e1c75c6ff114f93e9e72aadc159898e9
  dependencies:
  - closure-61f6305a420cc8be
- object_id: suite_modeling
  role: suite
  revision: '1'
  required: true
  ref: suites/node-modeling.md
  digest: 5451ede14cb85ac2ad38162ab64d3a21fd7d4a32a684675133341b6bc22505c5
  dependencies:
  - closure-69901734f875b764
  - closure-9fcc4020fc81cfbb
- object_id: suite_projection
  role: suite
  revision: '1'
  required: true
  ref: suites/node-projection.md
  digest: 2767a507098cdb00dd6fbe15951011cb351299f3ed41d881aed00fa7f66aea2d
  dependencies:
  - closure-2f0640fb494c4550
  - closure-333627034504dfc0
- object_id: suite_verification
  role: suite
  revision: '1'
  required: true
  ref: suites/node-verification.md
  digest: 9f10bd4c2556f211da7bf71a72cae9498604033a10f536ec0082f34dc628b156
  dependencies:
  - closure-5e9bb7736d03db61
  - closure-679e814e7277717d
- object_id: closure-61f6305a420cc8be
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: inputs/goal.md
  digest: ce772e62b7d969c3678c5a7854f214dfe0b655934b146fb07bff5bfa721f3e41
  dependencies: []
- object_id: closure-fae60b9ffb87556e
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: suites/entry.md
  digest: 945864d4ca2669f7b9af32ffa9fabd8f91476ace9b0a5e7bc143b7b359a1d9eb
  dependencies:
  - closure-0706f4f186eefd07
  - closure-20764639f87c4fa5
  - closure-2d854ea3c80174a8
  - closure-32e9e5d8614a42df
  - closure-4dcb78589d7bdfcf
  - closure-62317262477a674f
  - closure-661fb2136dafc4b4
  - closure-887e114cfea82895
  - closure-97405b147bd39d1b
  - closure-b324c601b71587ba
  - closure-c3cc97b63a57c8b1
  - closure-cc81cdb9f0f3950a
  - closure-cde6bd3d736fd39b
  - closure-e84e00e1c3e34b9d
- object_id: closure-f310ce52237c422e
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/run.md
  digest: 005a6fab6785cf4e7f9095077868730d6205ffdcf734ce26c67a265586b9e975
  dependencies:
  - closure-0706f4f186eefd07
  - closure-0e76ebbbe37119c6
  - closure-1cba82db03e30cf3
  - closure-20764639f87c4fa5
  - closure-23b91d12867c5a04
  - closure-2b68420fea1d1c22
  - closure-2d854ea3c80174a8
  - closure-2f96a0480912cca2
  - closure-32e9e5d8614a42df
  - closure-3dfd275f33d84ca9
  - closure-3fbd1eed8c66c214
  - closure-4dcb78589d7bdfcf
  - closure-4e0323e07cd27bf5
  - closure-4eb0c880c16b61cc
  - closure-56fc6c77e0f6d72d
  - closure-59ef92f1f9bbd255
  - closure-62317262477a674f
  - closure-661fb2136dafc4b4
  - closure-6d3ceea2929edafd
  - closure-6d702176ecf2a592
  - closure-7e8f36a2f26c312d
  - closure-887e114cfea82895
  - closure-97405b147bd39d1b
  - closure-a8102ebfa4c3978f
  - closure-b324c601b71587ba
  - closure-c3cc97b63a57c8b1
  - closure-c46c55dc23959739
  - closure-cc81cdb9f0f3950a
  - closure-cde6bd3d736fd39b
  - closure-d942e66832f918e1
  - closure-e84e00e1c3e34b9d
  - closure-f143b45ed6de0805
  - closure-fae60b9ffb87556e
  - node
- object_id: closure-a5a5687ec8f7fc02
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/transition-4.md
  digest: fe7c6381cd6e556fabde2a51e275c5c4fe8bbe3374d7c0d0bf2b3120dce387ef
  dependencies:
  - closure-30e851eb4dc722cf
  - closure-59ef92f1f9bbd255
  - closure-96192c4cdc511a1f
  - closure-a31653dabbdd41c9
  - closure-f310ce52237c422e
  - modeling_delivery
- object_id: closure-847cca9bb60aad2c
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/chain-check.md
  digest: eeceed02bab45f833921df936ffc6a81bce88e43aae1d83258e58926fde6cc78
  dependencies:
  - closure-19dd7b8aa168d203
  - closure-4920af625fe38b5b
  - closure-955c1796a0bdde18
  - closure-a5a5687ec8f7fc02
- object_id: closure-59ef92f1f9bbd255
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: inputs/host-source.md
  digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  dependencies: []
- object_id: closure-0da29a0d5b5b5c76
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/capability-protocol.md
  digest: ce0bbb57b6ddb3ce559f6ba23da25120808b83d831d575d0375c226e260a86bf
  dependencies: []
- object_id: closure-a305a069bee532e0
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/ontology-adoption.md
  digest: 38acbaadb313494d214c04c2f8d8731c1baa1cf6275be9b07d9613d37c33453b
  dependencies: []
- object_id: closure-0c4160b956d93b36
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/ontology-asset.md
  digest: f9eec623f4a3f15cdf3aa057502f99d0ca07c05dee6f0437c445a517357fb716
  dependencies: []
- object_id: closure-d586c86271afa18c
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/ontology-evolution.md
  digest: c38aa55b3500d9bcb11a62834313b4c4371b65a6d4bcb00c3429436587d3ac74
  dependencies: []
- object_id: closure-5475d29bbc747604
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/ontology-reuse.md
  digest: 461ad0d78c538eea59fcd8b4839aa5e4a2958c87a5a480f8b8a2a76a90b85853
  dependencies: []
- object_id: closure-24c52b4d8a2bc24e
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/pdca-ai-friendly-confirmation.md
  digest: 18ac31894ed212114595db88bbc19343b8c18199fc2c304ca44d931f8ea4ddfb
  dependencies: []
- object_id: closure-457118c5ec6959c2
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/pdca-continuous-improvement.md
  digest: c0f4d8d531482c4ed59f9181d742b6973884cc4adef68e7f393a86d3ab121db4
  dependencies: []
- object_id: closure-8d623f7777f68322
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/pdca-evidence.md
  digest: 3aca77b4d1aa4bb4bfa33a74dd6fe600581377b178d60be41ca78704dd85a955
  dependencies: []
- object_id: closure-2825a75cc8a952fd
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/pdca-execution-contract.md
  digest: ab30d1012e7f5d1b70acda508d4d3aa5523d293793a3da56f60324ce1cd06295
  dependencies:
  - closure-ccd6e8a065cac865
- object_id: closure-37a49842358eb585
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/pdca-gate.md
  digest: 8a8d1425ea34904b79215fd1ad73d29a7531ea1a2a3c6bc6e314ab904513b1e1
  dependencies: []
- object_id: closure-3ef2f154583cf86e
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/pdca-phase-status.md
  digest: 493d012cfeb8beda78e300b5871d83a92084d5a822b0866d3a323e9cb4c6e068
  dependencies: []
- object_id: closure-e8c1ca91f2db0ed2
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/pdca-recovery.md
  digest: 26cc72ba19b7c71a1c3fe112a63843d21448b43739bdb077811730de6a19ac8a
  dependencies: []
- object_id: closure-e0ea2c57978b0b12
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/pdca-task.md
  digest: 850f779c9eff7e2aee338e1ec8c13f9cca16a4d790d5066d4d100117a5d6dad5
  dependencies: []
- object_id: closure-47a5cfe898ee2ed8
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/pdca-transition.md
  digest: 7368bb438005e4fdfbf3848f88ec5f53b9ffc6b22a76adda12fa3b1b5baf60a4
  dependencies: []
- object_id: closure-bc1719a5a48ee4b2
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/pdca-verdict.md
  digest: ebb64f4316a2dde6a897d0338c2b16bef56f4e3591bbdb33bc20b53d5d3033b1
  dependencies: []
- object_id: closure-24d10c5b6561837e
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/resource-ownership.md
  digest: c84a72447d952f8719cc824f78a4c3ce7f6d93197f7c57d80bd55825d22de052
  dependencies: []
- object_id: closure-44ada5b40c1ecdb7
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/task-control.md
  digest: ecf839bd1b58bf1f1c9a23575516ccbd162c0d046fbe39c6d2d299eec4aa9af5
  dependencies: []
- object_id: closure-a000b11bf0210761
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/task-decomposition.md
  digest: 543309e1392808f5ac95a4d2b08a51492991226a259a562f39aed027021d56a7
  dependencies: []
- object_id: closure-572badcf455b9405
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/task-rework.md
  digest: 8cb6fd3553c07cd8809c873004891f597aefe4f4a97cc8c84c73b69fde899bbc
  dependencies: []
- object_id: closure-e6d57ecfa69f17ce
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/task-test-case.md
  digest: 53ad0b46af6cba14077ed0136385e5df2d2f73f725b989e8e99828bc576f1ca5
  dependencies: []
- object_id: closure-8be25320d3008c17
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/task-unit-test.md
  digest: a4bb3a782b9e29c04caf21efb26c31e0692c69650655ebf9cf5984d0b35249ec
  dependencies: []
- object_id: closure-aff3d4a34fcad92f
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/work-dependency-graph.md
  digest: ac21a7168c2a2672dcf02eafae862c336e723f26a911fa12436417092a4dbca1
  dependencies: []
- object_id: closure-af68af2a541cde29
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/work-node-contract.md
  digest: 710c7cf3be8e26c0a8b8f97f3741412b8fd39c0343ce91a8c696cf33fc00f2ef
  dependencies: []
- object_id: closure-9eb45479cc0531dd
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/work-ontology-tree.md
  digest: 13c677d0cd9d05b46ce3e4a77d1d9267fc47c5e7f353b0cde1370a44583b3e6c
  dependencies: []
- object_id: closure-1de36500771a63ad
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/concept/work-tree-scheduling.md
  digest: cf5be810de31dd09a18f8af52a3ee87626e3a118507d0fbdbf4db99bdb6f68ad
  dependencies: []
- object_id: closure-9742c9b2b1319767
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/process/independent-work-review.md
  digest: 4c89f100d5bd6cf60ad941c83ed8a89f4b20c7a6d601201bd0f0aa8a21046d80
  dependencies: []
- object_id: closure-2561c5e85aae731c
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/process/select-task-subgraph.md
  digest: 7291961aba26ec723715ca5ff9f95566cb4616d776eeb3d2424083cea14a40f5
  dependencies: []
- object_id: closure-7fd88f56f461df26
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:ontology/process/work-scenarios.md
  digest: a0a8109baa8ad1ac78cee71f93cf04da8c5ae64756d4c5b36658a7457673d9de
  dependencies: []
- object_id: closure-9fcc4020fc81cfbb
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/modeling/MODELING-P.md
  digest: 2448ba740f734a7c07e8c600f448234d8c3e4175b89acc1936f47e74e780f4a3
  dependencies: []
- object_id: closure-69901734f875b764
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/modeling/MODELING-N.md
  digest: 0b9dadfa3f9d3aba9b3f112800dc8af0a3ba12904e4afaeeb676339400af77cf
  dependencies: []
- object_id: closure-2f0640fb494c4550
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/projection/PROJECTION-P.md
  digest: 81c20657207f2d8eb31a17fab7cc130b7dc768c258b252d7a9ce82f8e06de047
  dependencies: []
- object_id: closure-333627034504dfc0
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/projection/PROJECTION-N.md
  digest: 8195fef66d13382d7d3aae789fee7d83c51351f446f270f694dfdb44412e2938
  dependencies: []
- object_id: closure-5e9bb7736d03db61
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/verification/VERIFICATION-P.md
  digest: 92f5d01900256e89afd9d8f0caa7d5830ccbb5cb1f8be0bafb9cff0584a5e54e
  dependencies: []
- object_id: closure-679e814e7277717d
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/verification/VERIFICATION-N.md
  digest: 10216607d495ccd9085409e17b57d4c7c81b284ac7add58e20acffdb2de4f709
  dependencies: []
- object_id: closure-0706f4f186eefd07
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME01.md
  digest: 89744c7c8810ea07ceffda7176c0e2feeef5b2cf216cee611cb60bfef3188a30
  dependencies:
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - closure-7f6dbdee9e86e9be
  - closure-eed2ed8a7c2cb048
  - protocol_baseline
- object_id: closure-20764639f87c4fa5
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME02.md
  digest: 8fc0fc9f93a7d8f6fcfbcc0d6d905e4b8ec68076592d406d35e3d46774025f6d
  dependencies:
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - closure-6e5023beaa8cecf4
  - closure-7f6dbdee9e86e9be
  - closure-8846211595ce5c6e
  - closure-991802aca59476d1
  - closure-c5b6dfe5647f8edf
  - closure-eed2ed8a7c2cb048
  - protocol_baseline
- object_id: closure-661fb2136dafc4b4
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME03.md
  digest: 5bcd06a3019704bb6e1eaba7c565c0ca4f038a4ebe1eb57fb046bb257f8eb30b
  dependencies:
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - protocol_baseline
- object_id: closure-4dcb78589d7bdfcf
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME04.md
  digest: 23b07fc75019e48fb83802d963ca3962c3ca44af490536eaab26b986623a3ae1
  dependencies:
  - closure-0936eecb203dd6e3
  - closure-1d43c56c49a9d6c8
  - closure-31d6ad014db0614e
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - protocol_baseline
- object_id: closure-887e114cfea82895
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME05.md
  digest: 1e40daaa71c97b4aaa845d9ec518eceb2cfd0f51dff311f44ac8347af07af185
  dependencies:
  - closure-0936eecb203dd6e3
  - closure-31d6ad014db0614e
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - protocol_baseline
- object_id: closure-b324c601b71587ba
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME06.md
  digest: c931710d509ae63333194e9d268cf5c3fdd95110ee4a1e3c265a0c83d22619bc
  dependencies:
  - closure-1d43c56c49a9d6c8
  - closure-31d6ad014db0614e
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - protocol_baseline
- object_id: closure-97405b147bd39d1b
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME07.md
  digest: 8d909aebd1e2270a8a4d8ecd14a243ce189e01bd0f0f88b9e076e544c1457105
  dependencies:
  - closure-136a4727893733ce
  - closure-21bce21db7791d18
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - closure-b7f1de1cc20b0ba2
  - closure-fe6ddf501a0c4c7b
  - protocol_baseline
- object_id: closure-cc81cdb9f0f3950a
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME08.md
  digest: 22a502a7f90cf01bd684d9555ead186ea727d115bb74ea6bce42378ae8362b78
  dependencies:
  - closure-0169765f2a3b60e9
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - closure-746e80bf24ab6be3
  - closure-7ec35590ec284e8d
  - closure-8b55ad52897d2a32
  - closure-92aeed975c94d356
  - protocol_baseline
- object_id: closure-e84e00e1c3e34b9d
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME09.md
  digest: 8e59b4a929ddc5cddfae11f9a332496ba5502dc610a698da2c28901a106148d4
  dependencies:
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - closure-76705b2006975135
  - closure-cbd674e54e85f1d9
  - closure-d89522f1eb7cb986
  - closure-fa82d31c917da5d7
  - closure-ff67aad5d82f0aba
  - protocol_baseline
- object_id: closure-2d854ea3c80174a8
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME10.md
  digest: c59c70fbef6d93090af0d7fd41845b93d0987925378ae9d0535f275b6967b666
  dependencies:
  - closure-1f468b35d31aba62
  - closure-47b0f6ee251d43e1
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - closure-aa434c48fdbd6228
  - closure-b0fb152eba60b9fb
  - closure-cbafba8d28d0e5ae
  - closure-ea22c39aebf043d0
  - protocol_baseline
- object_id: closure-32e9e5d8614a42df
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME11.md
  digest: 12aeaa5effe505e3b5b22a139054fb83e90f3538caaf3a77ca330036b640da95
  dependencies:
  - closure-0e4adbd4400b396c
  - closure-12960e92a0408ee2
  - closure-57b632572a204bc8
  - closure-58a28402913d88fe
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - closure-91d1f63da82a973c
  - closure-94c9013e4d5bae8e
  - closure-e2ca9f7f2501775c
  - protocol_baseline
- object_id: closure-62317262477a674f
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME12.md
  digest: cc502318e442aa6953b58569065376845b83eaaccce25fd82df2e96764ad46b8
  dependencies:
  - closure-3dea635076fecc76
  - closure-47b0f6ee251d43e1
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - closure-a7540a602bbc7f93
  - closure-b43eabce8665bdf5
  - closure-b963469e9ca7e855
  - closure-be7f69e3744f4e5a
  - protocol_baseline
- object_id: closure-c3cc97b63a57c8b1
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME13.md
  digest: 07bef17b379bcd0cc2a84d80b1e6d43f2eae6d2a2a6de497f0d2ffaca4c60e81
  dependencies:
  - closure-0e4adbd4400b396c
  - closure-1eecc4bbadf7289f
  - closure-57c796917b697d21
  - closure-5caf8cd820c5b40d
  - closure-5e51900c3a05419d
  - closure-61f6305a420cc8be
  - closure-673766950884ad93
  - closure-a54e4a5536657e6a
  - closure-c5a1a7e89738f2eb
  - protocol_baseline
- object_id: closure-cde6bd3d736fd39b
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: cases/entry/ME14.md
  digest: c5ac6799c1dd6d74a6f79181218e124f0cc918edcbea82692c0fe42d124a6105
  dependencies:
  - closure-0ec887db7ec7f986
  - closure-15466ee21c82ffba
  - closure-1c2bdc89c8a0cd0d
  - closure-421300ad1886382d
  - closure-5caf8cd820c5b40d
  - closure-61f6305a420cc8be
  - closure-716d5f4c8c543435
  - closure-8fecda12b8ae24c7
  - closure-ad136d04488918e8
  - closure-b62074b773fe089c
  - closure-cc91e79529b5c94e
  - closure-ebed9751f1677168
  - closure-ed6079a722e59d8b
  - protocol_baseline
- object_id: closure-2b68420fea1d1c22
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME01.md
  digest: 76a7c35bccaaa89a514f39f676ae144c34862521ed86e1b5e29850a767077768
  dependencies: []
- object_id: closure-6d3ceea2929edafd
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME02.md
  digest: 40dfeaeac50d03f86d0151751f9f1a95ae0b2421a7f9449aae3aa3cdf67fec4e
  dependencies: []
- object_id: closure-7e8f36a2f26c312d
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME03.md
  digest: 6efeb924e6e4e5d9d9193a1dfefc17e6a42f116e2f7a21e55e37d383e5ba2cde
  dependencies: []
- object_id: closure-a8102ebfa4c3978f
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME04.md
  digest: 22ab6e8caa8d68caaee867ff843182d1f3b1e7e3848a25966fc0e7738ae3f118
  dependencies: []
- object_id: closure-1cba82db03e30cf3
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME05.md
  digest: 56fb077afc10267732b91ac8456392ee9e159e857820fe73467eb7876f9ce53f
  dependencies: []
- object_id: closure-0e76ebbbe37119c6
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME06.md
  digest: 8b96018331d72d3b26c4f489c1085f89b5ede6583b2a053274d8709e6c9e4d9a
  dependencies: []
- object_id: closure-2f96a0480912cca2
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME07.md
  digest: 74bd02ccff5b7c7e8cf1f3c1b12fabde10254d012a8f80df508832e61e66e3da
  dependencies: []
- object_id: closure-3fbd1eed8c66c214
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME08.md
  digest: 32cf635f4e59b817f7aae0891177194e0c610b0033b23b1e5d65d708585e21d0
  dependencies: []
- object_id: closure-d942e66832f918e1
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME09.md
  digest: a2599ea7c1fa0430d6b215fbb858d1a95d860ef78b28996baf491d997f9ed11e
  dependencies: []
- object_id: closure-4eb0c880c16b61cc
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME10.md
  digest: 3ea870bdb37b307012e9827acaa139b3ecda0268ee2d8223dc656e1fb1df5013
  dependencies: []
- object_id: closure-56fc6c77e0f6d72d
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME11.md
  digest: 87e0d946020541e544775040b1c35ff6006bde19bb1845b83c847355b89ec618
  dependencies: []
- object_id: closure-3dfd275f33d84ca9
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME12.md
  digest: ad45128353f17c072b7844c317ecb34ebf9b1f526033e22ed9ea9e492b0b2615
  dependencies: []
- object_id: closure-23b91d12867c5a04
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME13.md
  digest: 7c144447e4a0e135bbc060eda47f1a59cdb3bba1b13cb804d067e8b1f62cec52
  dependencies: []
- object_id: closure-f143b45ed6de0805
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/observations/ME14.md
  digest: ddd56016ed4f6532be3c8c3ab5e36531f316a88d2065900afb9fdee871d70f0b
  dependencies: []
- object_id: closure-c46c55dc23959739
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: inputs/checker.md
  digest: 274f675b87ab3926f2821320058ac69a85bd67e1ddf749de26c802d0939438c5
  dependencies: []
- object_id: closure-4e0323e07cd27bf5
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/visible-inputs.md
  digest: a1dce6b8da89119aa63d435e0107521ce4b044df6937ced303a34bdfda16f469
  dependencies:
  - node
- object_id: closure-6d702176ecf2a592
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/evidence.md
  digest: 8b29f1987a2a8bdc2d7dd2eac94733508164095b7db98dfd540cf547ed4be89d
  dependencies:
  - closure-0e76ebbbe37119c6
  - closure-1cba82db03e30cf3
  - closure-23b91d12867c5a04
  - closure-2b68420fea1d1c22
  - closure-2f96a0480912cca2
  - closure-3dfd275f33d84ca9
  - closure-3fbd1eed8c66c214
  - closure-4e0323e07cd27bf5
  - closure-4eb0c880c16b61cc
  - closure-56fc6c77e0f6d72d
  - closure-6d3ceea2929edafd
  - closure-7e8f36a2f26c312d
  - closure-a8102ebfa4c3978f
  - closure-c46c55dc23959739
  - closure-d942e66832f918e1
  - closure-f143b45ed6de0805
  - node
- object_id: closure-a31653dabbdd41c9
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/review.md
  digest: 3135251561a449216af0aeb4780548c73648eb259913df7512fe83395f4b7462
  dependencies:
  - closure-f310ce52237c422e
  - node
- object_id: closure-30e851eb4dc722cf
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/inputs-4.md
  digest: 67cc86b672638fcd3060f9fb359a98e086b72340c1fe5ed4cffb3f457cc462b2
  dependencies:
  - modeling_delivery
- object_id: closure-96192c4cdc511a1f
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/gate-4.md
  digest: 631399a3a61b592bfe368eb84f87654c162170798043497e15a597b455d9f67b
  dependencies:
  - closure-59ef92f1f9bbd255
  - modeling_delivery
- object_id: closure-955c1796a0bdde18
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/transition-1.md
  digest: 5066dd2f9fdae0fbfb8ae60672aad5e2ef4d4268d85f1571be3539f10b1b9a56
  dependencies:
  - closure-3c9f18e7e5e57439
  - closure-440ecd83b5ecfd01
  - closure-46650ade84c5efd4
  - closure-59ef92f1f9bbd255
  - closure-751e8d402b87d0ef
  - closure-ea2b967199110116
- object_id: closure-19dd7b8aa168d203
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/transition-2.md
  digest: f0bcc1d6ae40c5061fab29a4fb3f3368b69a5b65af80f0e20c4880bbbad6f927
  dependencies:
  - closure-59ef92f1f9bbd255
  - closure-93a8edb83706cbf6
  - closure-c1d81cb871005b4e
  - closure-f310ce52237c422e
- object_id: closure-4920af625fe38b5b
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/transition-3.md
  digest: 12464810aeaa5875701008e9b798bccdacecfee5c63adf1c869f9faa031a4914
  dependencies:
  - closure-0883b980f20a3289
  - closure-3716e86123b7eefc
  - closure-51222fd70fd6ada2
  - closure-59ef92f1f9bbd255
  - closure-a31653dabbdd41c9
  - closure-f310ce52237c422e
  - closure-fff568dbf02b8b19
- object_id: closure-5caf8cd820c5b40d
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/modeling-entry/control-input.md
  digest: 0dbaa2f599095f2631e99f7c34b0a95de9b4ef8dbcc9458d685eb9d5cc7f506d
  dependencies: []
- object_id: closure-eed2ed8a7c2cb048
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F067.md
  digest: 07eac34136527e331ca5ea63b4d293637e6ec3e2c1e5ea605866af3e68b7c4c6
  dependencies: []
- object_id: closure-7f6dbdee9e86e9be
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F068.md
  digest: 2ccc3b29ae4c8f69e1f8d769e558cbb61ec9fe65b03be532f9b40aae62ed2522
  dependencies: []
- object_id: closure-8846211595ce5c6e
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F013.md
  digest: fbea74a4ba1286a51423c8d33bebdf8cf32f23aa0fd39fd771438a1900136988
  dependencies: []
- object_id: closure-6e5023beaa8cecf4
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F014.md
  digest: 487d1986998eeeb3d105a657db37ba8ea13608862cc4e2f308c2850f66f709ad
  dependencies: []
- object_id: closure-991802aca59476d1
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F015.md
  digest: 8945cd04a3c727854e6ae8f877e56d6392db3a8665859b208e2b823955a6fc26
  dependencies: []
- object_id: closure-c5b6dfe5647f8edf
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F016.md
  digest: 480df0cdebc4ae4e683ff25bd5c446de886649038e988eeb19b24cc060670e04
  dependencies: []
- object_id: closure-31d6ad014db0614e
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F025.md
  digest: b8fae6e89204d1360bbd0a391aa0d1477ed1ad1ee79ecd10b60f3752454d67f6
  dependencies: []
- object_id: closure-0936eecb203dd6e3
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F026.md
  digest: 4b50c440bec8b57bf6e3b745ff004f69202bbda35a7e1a34c356cfa7ef91b03b
  dependencies: []
- object_id: closure-1d43c56c49a9d6c8
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F027.md
  digest: 3556f2631d9aea2c8bd1f144bf022677cd45bbbea53411af149b678995d426b6
  dependencies: []
- object_id: closure-fe6ddf501a0c4c7b
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F049.md
  digest: 0e2425187b1e185aa2596192428f6275972d7c448fbd5b4504b7d33e0428875b
  dependencies: []
- object_id: closure-b7f1de1cc20b0ba2
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F050.md
  digest: 297f314e9abd77700c05cbc6097d85fc05bfd36048f0b7019e217d78682a89fa
  dependencies: []
- object_id: closure-21bce21db7791d18
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F051.md
  digest: 40ed9ad1a7d0cc3b6a8fe11873d2d902598a8606ae19fced1876fcbff00e564a
  dependencies: []
- object_id: closure-136a4727893733ce
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F052.md
  digest: dfafe4132ba7034d753546584a3925df9e0a271a4bd53ee26b04ef0079235231
  dependencies: []
- object_id: closure-8b55ad52897d2a32
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F017.md
  digest: e88627bcf9c4ccbecd7aef16ab387092cd1d4ae6448ae8c8f9289677b1f852a8
  dependencies: []
- object_id: closure-746e80bf24ab6be3
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F022.md
  digest: 2bb64a99fdacb8eaa51fc024a521892406946445ff93b32581a3b589d3d9a25f
  dependencies: []
- object_id: closure-0169765f2a3b60e9
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F064.md
  digest: 381dbd7ffb980ff5bba25cebad852dd6979d39412b5092f61a10e51471c08051
  dependencies: []
- object_id: closure-92aeed975c94d356
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F065.md
  digest: bab94849056ef2d43e5e32e2531bc90e405bc9c53db1dabc70d1d0f9889424b3
  dependencies: []
- object_id: closure-7ec35590ec284e8d
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F066.md
  digest: 959fe0dc1fd162ece5d9e3f68bd63c8b087f38aa2b950c0b9aa33470a8511149
  dependencies: []
- object_id: closure-cbd674e54e85f1d9
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F028.md
  digest: 8165a47826ef16c1784d557ec03f8b3c760322094c0b5b481931423f1bd70ecc
  dependencies: []
- object_id: closure-76705b2006975135
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F029.md
  digest: fb305e6022dd5809e87ef94590836dc068fe72601a0baee2b8189a97f69b90e1
  dependencies: []
- object_id: closure-fa82d31c917da5d7
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F030.md
  digest: 8f950e4319477e24d43d8aa2c3e3da578194efeb8ba42d178c4018f7dfa4b7ae
  dependencies: []
- object_id: closure-ff67aad5d82f0aba
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F031.md
  digest: 65dfcc6907e39405cb54e4b0380af04f7192e4cb5602145a2f526f804e46cd50
  dependencies: []
- object_id: closure-d89522f1eb7cb986
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F032.md
  digest: 3ac6a9d1deb6f087b2190c8e0be76c51b85f794308f510e59323412e0f7dc182
  dependencies: []
- object_id: closure-ea22c39aebf043d0
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F033.md
  digest: 112f7034fd8aac8ff6caedee831aac47daf8dc5ef1c345e144e38edc78f703e9
  dependencies: []
- object_id: closure-1f468b35d31aba62
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F034.md
  digest: bb6c9a8822ff52580e3d3d879b8c47cb5acf5c97c021381c9296e4c5d01e8dd2
  dependencies: []
- object_id: closure-cbafba8d28d0e5ae
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F035.md
  digest: de9866d067339e83e508c5793d06bfd7ff017a1f992d81508f837afd1a79d939
  dependencies: []
- object_id: closure-b0fb152eba60b9fb
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F055.md
  digest: e259ee1a3926d21db9988ddde02f644127f877d529099631ab2e4e92a22de253
  dependencies: []
- object_id: closure-47b0f6ee251d43e1
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F056.md
  digest: 966d5b6c67853e4128773523f15ea2b7af54b62db08e3da43861190ed2839857
  dependencies: []
- object_id: closure-aa434c48fdbd6228
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F057.md
  digest: 9129a70ed75cd9c554087e685a424f9d0b8c20fe5e905958e931ab1ffe2f7e20
  dependencies: []
- object_id: closure-58a28402913d88fe
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F036.md
  digest: 4d4cfabe0ba41467b535d8f84609471e2d13fc2ccaa40828343dce4a0d4c6096
  dependencies: []
- object_id: closure-94c9013e4d5bae8e
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F037.md
  digest: a12ce5b2f274f5af676b687e3a04e80cb379c28b804c031af5dc40276ca16641
  dependencies: []
- object_id: closure-57b632572a204bc8
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F038.md
  digest: e5cba12a1ec3318f165b15604e89087544d3f15fd97e5e1ed7c6ef8b6daae1f8
  dependencies: []
- object_id: closure-0e4adbd4400b396c
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F039.md
  digest: 39ffd625e50931eaa1a1adafe41632d5b0266edb6ddcbf487eeb6f2e864a1133
  dependencies: []
- object_id: closure-e2ca9f7f2501775c
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F044.md
  digest: 261e7bf592d1282ce5f7c62b2800195035ceb00ae70c3dc3217ae33e22973f8f
  dependencies: []
- object_id: closure-91d1f63da82a973c
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F045.md
  digest: c7f7f445977e8e94959e3feb56c6e1a3aaf9ceebb4b11ea4aa5c760454ae4180
  dependencies: []
- object_id: closure-12960e92a0408ee2
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F046.md
  digest: 9a51642099b6d6ed9cd3ce66a8cb4b1d5cc17cdd95ef39642a75a0f1980c5d4f
  dependencies: []
- object_id: closure-b963469e9ca7e855
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F023.md
  digest: 76698ca3ce7f21f23fb4771f2a3c9a94dd77b433c7f9db70734447892a556626
  dependencies: []
- object_id: closure-be7f69e3744f4e5a
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F024.md
  digest: 2bbfddf2e24313ba02d0545095323a3ea70cd3a46448f6b88e90874e75e59a93
  dependencies: []
- object_id: closure-3dea635076fecc76
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F061.md
  digest: 09f23a19670d66b7259d61b6afb5023691c95e89b93e5e404ca01a345e07453b
  dependencies: []
- object_id: closure-b43eabce8665bdf5
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F062.md
  digest: e3418e84f84081194d8a6c12db86f098b5d172472b2bac1ea8136666dfcc596a
  dependencies: []
- object_id: closure-a7540a602bbc7f93
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F063.md
  digest: b7f64c180ce0f84d35dcd638e7dca98becd94c442ce78092e6cbb05f29528ba5
  dependencies: []
- object_id: closure-a54e4a5536657e6a
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F040.md
  digest: 72ec046363ccb643e39ee65c0bb960c15b5faed7fe5dcda8d696a8a20f5b1fa8
  dependencies: []
- object_id: closure-57c796917b697d21
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F041.md
  digest: b0065e2c323c59b6c7ffd5304719121048840a963a23a866ed948fb63260ba17
  dependencies: []
- object_id: closure-c5a1a7e89738f2eb
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F042.md
  digest: 6c92e577fe581ab087cba7286b21ca699e6da5792abc108d928a5e81848f617e
  dependencies: []
- object_id: closure-1eecc4bbadf7289f
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F043.md
  digest: 8703f816894c64c7cbfa5bbabd84f9ab46db57eb4206c904cf29cbb1897ae7af
  dependencies: []
- object_id: closure-5e51900c3a05419d
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F053.md
  digest: 5c6fe7d489bb83f3bc3851b867b5e1f04078f7711fd06e892f4f6275faba1cfb
  dependencies: []
- object_id: closure-673766950884ad93
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F054.md
  digest: 37e557b3c1f1364c10ec95a9d01ccc87eb26bf8f6398716dcd2a5dec85536e13
  dependencies: []
- object_id: closure-ebed9751f1677168
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F001.md
  digest: bc5de310a743c72eb428c66a7c325650cef4bc44fafc7e18908814ac18d3aa07
  dependencies: []
- object_id: closure-716d5f4c8c543435
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F002.md
  digest: b2b1e3142dec4ff5a66970f6f3cd332076e414abe6e0571ec2e7957946c4a3a3
  dependencies: []
- object_id: closure-8fecda12b8ae24c7
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F003.md
  digest: 0ca7f51756b14ee19b233d419309ecf4aea62e0af69e41796b86a0afd86d3360
  dependencies: []
- object_id: closure-15466ee21c82ffba
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F004.md
  digest: 3c43bae6956c67d9c6b5e2fdebdd87aec35a7d9d99ade8d40610627031d68400
  dependencies: []
- object_id: closure-b62074b773fe089c
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F010.md
  digest: ce3ccbf96a4e421035860db50e455469340c278360e54e5f83cc9433884c668d
  dependencies: []
- object_id: closure-1c2bdc89c8a0cd0d
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F011.md
  digest: 627eb64d15dedb2c179bbb4343b8504b9e7734ce32c332e56a2872b6b0b20779
  dependencies: []
- object_id: closure-ed6079a722e59d8b
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F012.md
  digest: 28fccac0a72ef1a762a557895fe548efe6367e2552417777fbb95465fc796a0b
  dependencies: []
- object_id: closure-ad136d04488918e8
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F069.md
  digest: 8697f816ec60a8c4531c1ae75288d5294416fb18be6992d00688a02cef9dc09c
  dependencies: []
- object_id: closure-0ec887db7ec7f986
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F070.md
  digest: 7b095f68c0f035bca4be346daaa8cf561193e8131cf399655e9505d3a0686853
  dependencies: []
- object_id: closure-cc91e79529b5c94e
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F071.md
  digest: a1cb6313db3a40c93ef194efe0ac0bc1ecfa2d8e06cc8e8e3f8e662a2a35e596
  dependencies: []
- object_id: closure-421300ad1886382d
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: protocol:tests/records-regression/cases/F072.md
  digest: 23c0424c7281128fec8ea3fb7f7dc0613a9291f34c64d4d0b69bc2106df99dd7
  dependencies: []
- object_id: closure-3c9f18e7e5e57439
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/baseline.md
  digest: 3358a67a8e390fbfc3670af90614b20a486ec4f510bac3cc77ba97c1eb65f2b6
  dependencies:
  - closure-61f6305a420cc8be
  - closure-fae60b9ffb87556e
  - graph
  - protocol_baseline
  - subject_snapshot
- object_id: closure-751e8d402b87d0ef
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/plan-response.md
  digest: dace32efe6278597ff9f1e9af20ce60e4d01d50a86f01655de9e3e291f147931
  dependencies:
  - closure-3c9f18e7e5e57439
  - closure-59ef92f1f9bbd255
- object_id: closure-ea2b967199110116
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/plan-decision.md
  digest: ae6e0637e274648561958bb357eae4ed358a7837ddb1c46a492a6b163362b23d
  dependencies:
  - closure-3c9f18e7e5e57439
  - closure-59ef92f1f9bbd255
  - closure-751e8d402b87d0ef
- object_id: closure-46650ade84c5efd4
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/inputs-1.md
  digest: bb7cd1e145b2c0bfc1f80136cefbaf20d5c895699d6673cab340faa938d870d6
  dependencies:
  - closure-3c9f18e7e5e57439
- object_id: closure-440ecd83b5ecfd01
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/gate-1.md
  digest: af1f98bd77705e15d51bfab9c9964400a31481c55db9a2e44aa06676f510506e
  dependencies:
  - closure-3c9f18e7e5e57439
  - closure-59ef92f1f9bbd255
- object_id: closure-c1d81cb871005b4e
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/inputs-2.md
  digest: 574eaeb008118104afecece3c87ed3579ac25b895299a6be44ce8dc0b5dba3e3
  dependencies:
  - closure-f310ce52237c422e
- object_id: closure-93a8edb83706cbf6
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/gate-2.md
  digest: 75ebf8b7f75d3c13b0df2ad7fa52009e983f652b3d6da93f0ec1bb4b72e7af97
  dependencies:
  - closure-59ef92f1f9bbd255
  - closure-f310ce52237c422e
- object_id: closure-51222fd70fd6ada2
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/check-response.md
  digest: 1e77b651bbbe4f83061b11035389664dc0de74f7c230f1b42b3ead67485e3e59
  dependencies:
  - closure-59ef92f1f9bbd255
  - closure-a31653dabbdd41c9
- object_id: closure-0883b980f20a3289
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/check-decision.md
  digest: 6a20011b42d0aa598c9b39426d288b330a27b4a76aba85672c392f2e99b391e9
  dependencies:
  - closure-51222fd70fd6ada2
  - closure-59ef92f1f9bbd255
  - closure-a31653dabbdd41c9
- object_id: closure-3716e86123b7eefc
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/inputs-3.md
  digest: c132e11ec8178e8e2833ccdb60fb2466d6f4d6ea808ae6615e5bca8f155fbf70
  dependencies:
  - closure-a31653dabbdd41c9
- object_id: closure-fff568dbf02b8b19
  role: closure_member
  revision: fixed-by-digest
  required: true
  ref: records/T-M/gate-3.md
  digest: 7b633fc516740ca5da566df3901a5836e617aeaee394b30245888c41c0a4f780
  dependencies:
  - closure-59ef92f1f9bbd255
  - closure-a31653dabbdd41c9
- object_id: closure-ccd6e8a065cac865
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/index.md
  digest: f165f4bd65a110afb1cf27dfbabee69ea61078cb230adda583b932479cae37df
  dependencies:
  - closure-14e61b9b31d2d7b5
  - closure-1b9ac1cb51a36324
  - closure-34ca69b794097edc
  - closure-4cd744e1231d7a5e
  - closure-503278e4307ed462
  - closure-54802188c81c0b69
  - closure-572f4b2d6311b27d
  - closure-5d62dd4683a38dc6
  - closure-6be867d08a31ad50
  - closure-728c751c772de754
  - closure-8bd285b1198b5daf
  - closure-8f1e99f149af7152
  - closure-8f2fdedf955dffee
  - closure-8fb292c6e2c88f3a
  - closure-910c33b156938d45
  - closure-9532bc272dacf06a
  - closure-a2800ff5ca40f7ea
  - closure-acfae79aa79988ef
  - closure-b60a691049b8f1ba
  - closure-dfc3f9a340a9eab4
- object_id: closure-728c751c772de754
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/archive-receipt.md
  digest: 954d8a53b5472a631d152bd073cef70b79917c60d86fc37e01eaa186d8357cc7
  dependencies:
  - closure-dd5ec805a6573d56
- object_id: closure-b60a691049b8f1ba
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/baseline.md
  digest: 068f9f51814c29c0e4494e82c9139e3b03d7bc1f77cc8a5181158f5fc4ce0cc1
  dependencies:
  - closure-e8d265a18cfaf4f0
- object_id: closure-34ca69b794097edc
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/delivery.md
  digest: 3ef44b9ba31636f3f99988aa935d42928eea041e143dc40133e95fea2c831723
  dependencies:
  - closure-defc80e073d6ede0
- object_id: closure-8f1e99f149af7152
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/dependency-check.md
  digest: 7528857e4a6254b26046845f87b571ea6ae497012ec237f5037d43dcd6f5a1d0
  dependencies:
  - closure-f7d97160ad20caeb
- object_id: closure-5d62dd4683a38dc6
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/dependency-snapshot.md
  digest: d3abd59d7f1a314c6099aa903f46b2813d190da578f051957683e74c92ae16df
  dependencies:
  - closure-77b2bb16c653c18f
- object_id: closure-1b9ac1cb51a36324
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/gate-check.md
  digest: 09a084b45565c83bdabedc51274bc03124f59df877e465e150013ff0106f36b2
  dependencies:
  - closure-387c9bfe2134b855
- object_id: closure-6be867d08a31ad50
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/request-decision.md
  digest: 9ddb8808370d4b173f9303ca3a3c82f61cc92d14a9a2b68ce8aa7ba1aec4d9f5
  dependencies:
  - closure-3c67b8036f6cc383
- object_id: closure-14e61b9b31d2d7b5
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/request.md
  digest: 94ee9039157fa0cdc458718b2ec631f03160c2b7c1e3932e0b9746f3922fd731
  dependencies:
  - closure-0ba8f6994ae64810
- object_id: closure-dfc3f9a340a9eab4
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/response.md
  digest: 2c2171e2c312160d077c804e20592accdc82ac8cbfe0d96afb748d471088ad44
  dependencies:
  - closure-861e3b02cc6a02e2
- object_id: closure-acfae79aa79988ef
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/review-package.md
  digest: c874f4e02323bda06ac549c11f9b75681413e0a12fe59e4e19a503248ae609fb
  dependencies:
  - closure-737769b2aa7675a4
- object_id: closure-9532bc272dacf06a
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/subject-snapshot.md
  digest: dd1a2673b27ba82e7c69a16b1df9ad7fc06495a739913d63c7850ce22ef6e75a
  dependencies:
  - closure-cca87ff2580f41df
- object_id: closure-8f2fdedf955dffee
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/task.md
  digest: 6ab809f949109236b8acb6a1946ccfc897ed304bbbbc709a0e05db9785da5b9d
  dependencies:
  - closure-058ab358375d6edd
- object_id: closure-572f4b2d6311b27d
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/test-case-binding.md
  digest: 604610e60c13c343f2b50df6d36f45a3b294533f2db36dd8fc5a2dc41475ef92
  dependencies:
  - closure-edef53748857bf1d
- object_id: closure-8bd285b1198b5daf
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/test-case.md
  digest: 6dd8c7e4ce8f1d55043b35f2cf03ece5f4a09c1b306ed783c0b2f129fd6f7bd8
  dependencies:
  - closure-bdc3af89c9940131
- object_id: closure-4cd744e1231d7a5e
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/test-run.md
  digest: ab881a68fef530e6a4b053cbd2decb5d174bc72fdf79a46dc17e81b22d34edc3
  dependencies:
  - closure-8adbb694e8831941
- object_id: closure-910c33b156938d45
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/test-suite.md
  digest: 4f48761ab57b2ec403356eee26b91e8f45cfafaea9cb82c9e1cad0395cfa1e57
  dependencies:
  - closure-97e30c5a0e18002f
- object_id: closure-503278e4307ed462
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/transition.md
  digest: 8dab63f9586ad821ee8459975c0b96e022c6fb0633432e93eb5a80a1cf7abeeb
  dependencies:
  - closure-934bb37ca9094526
- object_id: closure-8fb292c6e2c88f3a
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/tree-manifest.md
  digest: d89a0149dd95d8f057533605916ce672477b1c94e93141de0859326900535eb3
  dependencies:
  - closure-5864732e8b90c341
- object_id: closure-54802188c81c0b69
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/tree-spec.md
  digest: eba9e64ab64c48ca0612966456e62c2b825767f58912fd7246ceeb857d0d19d9
  dependencies:
  - closure-1b08437bd082d035
- object_id: closure-a2800ff5ca40f7ea
  role: evidence
  revision: '1'
  required: true
  ref: protocol:ontology/contracts/record-shapes/work-node.md
  digest: ed5005c9c69057cc453208abe8a88eab5f93d98ce6365b55ab0cf09528fe21ef
  dependencies:
  - closure-dc557e4a8bace727
- object_id: closure-dd5ec805a6573d56
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/archive-receipt.md
  digest: 0599f92c19624b037202dcbf4fd38261cab348db308d469a04ac2893f8ed01e0
  dependencies: []
- object_id: closure-e8d265a18cfaf4f0
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/baseline.md
  digest: 5ccd9b9cee6f53cbf8315e3b1de1f0f35e5dc2c9928c8cd505b3b2252c935870
  dependencies: []
- object_id: closure-defc80e073d6ede0
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/delivery.md
  digest: 48cb831d8151644f934abf730ed5b1d726862a21ddad253b816f29a487e9affd
  dependencies: []
- object_id: closure-f7d97160ad20caeb
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/dependency-check.md
  digest: 6a9232d96c079e0c0fe36506e5801621f09fd5838321898a66331ee4d30b8497
  dependencies: []
- object_id: closure-77b2bb16c653c18f
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/dependency-snapshot.md
  digest: 594a18b3dd788a5f5362114200c59a17b2a9bddb19ef0821e40c50e00b101c79
  dependencies: []
- object_id: closure-387c9bfe2134b855
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/gate-check.md
  digest: aab2afe3254d22c04c2f2db4e371e38578c219146217dcd55c3a5b8a527efad6
  dependencies: []
- object_id: closure-3c67b8036f6cc383
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/request-decision.md
  digest: 156a7f3f2d89e98a5ebbb91b7e9c70292edca890a183e91957c51752870274d5
  dependencies: []
- object_id: closure-0ba8f6994ae64810
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/request.md
  digest: 53555425cd005be04bb22da0fded65b1506574cc62b2a112353bb14344b9a2a0
  dependencies: []
- object_id: closure-861e3b02cc6a02e2
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/response.md
  digest: 67e964259a9cd89a033329f700a2d0f02a406470c7d044647c4e1c4233e5c965
  dependencies: []
- object_id: closure-737769b2aa7675a4
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/review-package.md
  digest: bed6e390e586c906db16ef5efc789f9c133a5b4e5e6e5cebedfa178b8bf3a37f
  dependencies: []
- object_id: closure-cca87ff2580f41df
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/subject-snapshot.md
  digest: c8df6262b8ad34205d20e6a8e9e43725e9ca55f6ff43799b4caccd2d7c088b95
  dependencies: []
- object_id: closure-058ab358375d6edd
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/task.md
  digest: 90edf300395ffb8bb30ce61ec60b050d2ec63b7886d800daec209d837e789046
  dependencies: []
- object_id: closure-edef53748857bf1d
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/test-case-binding.md
  digest: 0da1531b0483c629d074490c92758dd415b2491b7871dfb78db6861921419e8e
  dependencies: []
- object_id: closure-bdc3af89c9940131
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/test-case.md
  digest: beabfa5d196ae998ec79ae00c15124adb043b72d1f456e7c4f73c4aff525665f
  dependencies: []
- object_id: closure-8adbb694e8831941
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/test-run.md
  digest: 97ec24eb299b111a2e3b90ca455106a44431701611320f78dcf0cfde36829ba4
  dependencies: []
- object_id: closure-97e30c5a0e18002f
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/test-suite.md
  digest: 2b29fc9624f975d67c5d34d919347e98e12f892cd3d7cf337db647ec7137fc28
  dependencies: []
- object_id: closure-934bb37ca9094526
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/transition.md
  digest: 9f98ccdbab9004236a94e0577d84b823f7a2e6dce97cf0f618565e4708221d4f
  dependencies: []
- object_id: closure-5864732e8b90c341
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/tree-manifest.md
  digest: 440c79af6a42ab657634c122c96a6a7160b3d65579fc7c4e23654262f00a5cc4
  dependencies: []
- object_id: closure-1b08437bd082d035
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/tree-spec.md
  digest: a734db453e6022932a7433dda8bce5b2830e3f486cc05ca15be219c5e1325053
  dependencies: []
- object_id: closure-dc557e4a8bace727
  role: evidence
  revision: '1'
  required: true
  ref: protocol:templates/work-node.md
  digest: edcd9b0b2fc80ddb0d50995cd5c3fe5f1d1e7a465f2fa062e8b8488447f0cf8a
  dependencies: []
node_bindings:
- node_id: N
  node_object_id: node
  task_id: T-M
  attempt: 1
  delivery_object_id: modeling_delivery
  terminal_object_id: modeling_terminal
  suite_object_ids:
    ontology_modeling: suite_modeling
    ontology_projection: suite_projection
    ontology_conformance_verification: suite_verification
knowledge_obligation_refs: []
closure_policy: explicit_required_recursive
view_paths_excluded:
- tree.md
- control/runtime.md
required_scenes:
- ontology_modeling
- ontology_projection
- ontology_conformance_verification
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
