---
schema: pdca.records-subject/v1
fixture_only: true
family: dependency
auto_edges:
- producer: root
  consumer: child
  scene: ontology_modeling
consumed_inputs:
- producer: root
  scene: ontology_modeling
  artifact: &id001
    ref: seed.md
    digest: 3e5bb865eb76e8fb29304cfc072c7b0be195e09c0714cec2611ad2b8ad105e8f
- producer: root
  scene: ontology_modeling
  artifact:
    ref: root-suite.md
    digest: dbc6bf92048032eaf2a7f3dc6ac50ec2055b2684740ea68df059667aecb4c079
declared_artifacts:
- *id001
---

固定合成对象，不认证任何真实身份或历史事件。
