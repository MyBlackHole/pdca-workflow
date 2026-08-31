---
schema: pdca.asset/v1
id: ontology:domain/core-verify-all-aggregate-pattern
type: domain
layer: Knowledge
status: active
summary: verify_all 聚合校验入口模式
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 verify-all-aggregate-pattern 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# verify_all 聚合校验入口模式

## 适用场景

引擎/系统存在多个独立的一致性校验 API，调用方需要一次运行全部校验
（健康检查、测试断言、恢复后验证）。

## 模式要点

1. **全部执行、首个错误优先**：对齐 recovery pass 驱动的 C 惯用法
   `ret = __bch2_run_explicit_recovery_pass(...) ?: ret`（recovery.c:68-98）
   ——每个校验都运行（不短路），首个错误保留返回。Rust 等价：
   `first_err.get_or_insert(err)` 逐校验收集，最后返回 Option。

2. **顺序即依赖序**：校验顺序按 pass 依赖序固定（拓扑最基础→派生→
   索引→守卫），passes_format.h 的 BIT_ULL 依赖标记是顺序依据；调用方
   从返回的首个错误即可判断最底层的不一致。

3. **聚合不改变单校验**：单个校验 API 保持独立可调用（局部校验场景），
   聚合入口只是组合；校验行为、错误类型、锁序均不因聚合而改变。

4. **锁在局部作用域**：聚合入口不跨校验持锁——需要遍历 btree 判断
   live 集时在局部作用域获取并释放（快照式），每个校验自行 lock_fs，
   避免重入与死锁。

## 测试模式

- 正常路径：聚合 Ok。
- 单失败：构造一个校验的失败态（如 open∧free 守卫失败）→ 返回对应
  错误变体。
- 多失败顺序：同时构造两个独立失败态（索引坏 + 守卫坏）→ 返回顺序
  靠前的错误（桶索引先于守卫），验证顺序正确性。

## 边界

- 测试故意构造的非法态（如 not_rw 设备上 free 桶）在聚合入口必然失败，
  这类测试点保留单校验断言而非聚合——聚合入口是"全健康"检查，不是
  局部状态断言工具。
