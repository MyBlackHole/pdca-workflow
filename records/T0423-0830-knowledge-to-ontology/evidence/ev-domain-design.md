# 证据：AC-1 ontology/domain/ 接入设计
- 28 个域根节点 `ontology:domain/<domain>`（type=domain，specializes pdca，relates_to pdca）。
- 122 个叶节点 `ontology:domain/<domain>-<slug>`（type=domain，specializes 域根，`domain` 属性指向域根）。
- 连接：叶→根→pdca，无孤岛；`type` 均等于父目录名（domain），通过 ontology-validate。
