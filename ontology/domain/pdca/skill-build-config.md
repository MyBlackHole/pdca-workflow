---
schema: pdca.asset/v1
id: ontology:domain/skill-build-config
name: build-config
summary: Set up build configuration for new projects, manage dependencies, and switch between build systems.
description: Use when setting up build configuration for new projects, adding/managing dependencies, or switching between C/C++/Rust/Go/Python build systems
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-build-config/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/design-tree
    - ontology:concept/domain-model
  testable_signal: "检查本文件构建相关章节的完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


-----|------|
| C/C++ (GCC) | `-fstack-protector-strong -D_FORTIFY_SOURCE=2 -Wl,-z,now` |
| C/C++ (Clang) | `-fsanitize=address,undefined` |
| Rust | 默认安全（unsafe 例外） |
| Go | 默认 W^X |

## 已知坑

- 依赖版本勿随意跳大版本；构建系统切换须保持全仓一致，混用会引入不可复现构建。
