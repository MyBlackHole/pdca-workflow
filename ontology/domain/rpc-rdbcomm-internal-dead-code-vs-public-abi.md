---
schema: pdca.asset/v1
id: ontology:domain/rpc-rdbcomm-internal-dead-code-vs-public-abi
type: domain
layer: Knowledge
status: active
summary: internal-dead-code-vs-public-abi
domain:
- ontology:domain/rpc-rdbcomm
relations:
  specializes:
  - ontology:domain/rpc-rdbcomm
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


---
schema: pdca.ontology/domain/v1
title: 清理网络遗留代码时区分内部死代码与公共 ABI
source: records/T0316-0818-rpc-legacy-helper-cleanup/conclusion.md
---

## 可复用规则

发现未使用函数时，应先按链接边界分类：静态内部函数若无仓库内调用，可在构建和完整测试保护下删除；公共头文件中的无内部调用函数不能仅凭源码搜索删除，应保留并单独评估外部 ABI。

编译器的 `unused` 属性也要区分：实际有调用的函数只需移除错误属性；属性本身不是删除函数的证据。网络收发辅助函数还必须确认其帧格式和 I/O 所有权，不能把旧原始 fd 实现误删为当前 TLS session 实现。

## 来源

T0316 对 `rpc-net`、`tls-keygen` 和 TLS 公共 API 的分类审查，以及 36 项完整测试结果。
