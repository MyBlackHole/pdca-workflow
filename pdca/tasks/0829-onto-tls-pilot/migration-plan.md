# T0402 tls 试点迁移计划（基于 SSOT v3 实体树）

> 配套：prd.md（AC 定义）、tls-ontology-map-example.md（16 文件语义映射样例）。
> 本文是把 v3 模型落到 tls 域的执行清单。

## 1. 类节点层次（需新建，specializes 以 `Entity` 为根）

抽象类用 `concept/` 目录承载（避免与实例 type 目录语义混淆）：

| 类节点 id | type | specializes | 备注 |
|---|---|---|---|
| `ontology:concept/entity` | concept | （根，无父） | Entity 根 |
| `ontology:concept/domain-entity` | concept | `ontology:concept/entity` | 领域实体根 |
| `ontology:concept/knowledge-artifact` | concept | `ontology:concept/entity` | 知识实体根 |
| `ontology:concept/process` | concept | `ontology:concept/entity` | 过程根 |
| `ontology:pattern` | pattern | `ontology:concept/knowledge-artifact` | Pattern 类 |
| `ontology:principle` | principle | `ontology:concept/knowledge-artifact` | Principle 类 |
| `ontology:pitfall` | pitfall | `ontology:concept/knowledge-artifact` | Pitfall 类 |
| `ontology:fact` | fact | `ontology:concept/knowledge-artifact` | Fact 类 |
| `ontology:entity/tls-session` | entity | `ontology:concept/domain-entity` | composed_of MTLSHandshake/X509Certificate；configured_by TLSConfiguration |
| `ontology:entity/mtls-handshake` | entity | `ontology:concept/domain-entity` | composed_of X509Certificate |
| `ontology:entity/x509-certificate` | entity | `ontology:concept/domain-entity` | |
| `ontology:entity/tls-configuration` | entity | `ontology:concept/domain-entity` | |
| `ontology:entity/tls-test-harness` | entity | `ontology:concept/domain-entity` | |
| `ontology:entity/exec-stdin-pump` | entity | `ontology:concept/domain-entity` | |
| `ontology:process/code-review-process` | process | `ontology:concept/process` | |

## 2. 16 知识实例迁移映射（纠正 pattern=10，principle=3，pitfall=2，fact=1）

| # | 源（knowledge/…） | 目标 type/slug | specializes | guides / relates_to | source_task（待核对） |
|---|---|---|---|---|---|
| 1 | linux-epoll-eventloop/backupstream-plain-tls-ingress.md | pattern/backupstream-plain-tls-ingress | ontology:pattern | guides entity/tls-session | T0287 |
| 2 | tooling/cli-tls-mtls-configuration.md | principle/cli-tls-mtls-configuration | ontology:principle | guides entity/tls-configuration | （cli 约定） |
| 3 | nbu/gmssl-tlcp-mtls.md | pattern/gmssl-tlcp-mtls | ontology:pattern | guides entity/mtls-handshake | records/0727 |
| 4 | rpc-rdbcomm/mtls-review-fd-session-boundary.md | principle/mtls-review-fd-session-boundary | ontology:principle | guides entity/mtls-handshake | T0309 |
| 5 | rpc-rdbcomm/unified-first-stage-mtls-time.md | pattern/unified-first-stage-mtls-time | ontology:pattern | guides entity/mtls-handshake | T0302 |
| 6 | tls/link-level-mtls-test-pattern.md | pattern/link-level-mtls-test-pattern | ontology:pattern | guides entity/tls-test-harness | T0352/T0353/T0354 |
| 7 | tls/mtls-server-alg-whitelist.md | pattern/mtls-server-alg-whitelist | ontology:pattern | guides entity/mtls-handshake, entity/tls-configuration | T0357 |
| 8 | tls/structured-mtls-failure-diagnostics.md | principle/structured-mtls-failure-diagnostics | ontology:principle | guides entity/tls-session | T0314 |
| 9 | tls/mtls-param-review-findings.md | pitfall/mtls-param-review-findings | ontology:pitfall | guides entity/mtls-handshake, entity/tls-configuration | T0348 |
| 10 | tls/tls_cert_reload_appdata_safety.md | pitfall/tls-cert-reload-appdata-safety | ontology:pitfall | guides entity/x509-certificate | T0366 |
| 11 | tls/mtls-four-module-supplementary-review.md | pattern/mtls-four-module-supplementary-review | ontology:pattern | guides process/code-review-process | T0364 |
| 12 | tls/mtls-handshake-enum-unify.md | pattern/mtls-handshake-enum-unify | ontology:pattern | guides entity/mtls-handshake | T0359 |
| 13 | tls/mtls-handshake-netorder-libobk.md | pattern/mtls-handshake-netorder-libobk | ontology:pattern | guides entity/mtls-handshake | T0362 |
| 14 | debugging/tls-exec-truncation-investigation-state.md | fact/tls-exec-truncation-investigation-state | ontology:fact | relates_to entity/exec-stdin-pump | T0345/T0347 |
| 15 | dmsbtex/sbt_config_mtls_override.md | pattern/sbt-config-mtls-override | ontology:pattern | guides entity/tls-configuration | T0366/T0328 |
| 16 | oss/oss_https_tls.md | pattern/oss-https-tls | ontology:pattern | guides entity/tls-configuration, entity/tls-session | T0368 |

## 3. 每实例 frontmatter 模板
```yaml
schema: pdca.asset/v1
id: ontology:<type>/<slug>
type: <type>            # == 目录名
layer: <Knowledge|Experience|...>   # 按来源
status: active
summary: <一句话>
source_task: <来源任务/记录 id>      # record identity 保持（ADR-0030）
also_type: []           # 可选
attributes:             # 从原文提取，至少其一
  - name: applicability
    desc: <适用场景/边界>
    constraint: <约束>
    testable_signal: <可测信号>
  - name: constraints
    ...
  - name: testable_signal
    ...
relations:
  specializes: [ontology:<类>]
  guides: [ontology:entity/..., ontology:process/...]   # 或 relates_to
```

## 4. 执行步骤
1. 建 §1 类节点层次（concept/ + entity/ + process/ 共 15 个类节点）。
2. 逐篇迁移 16 实例：`cp` 到 `ontology/<type>/<slug>.md`；补 frontmatter（id/type/layer/status/summary/attributes/relations/source_task）；从原文提取 attributes。
3. 原 `knowledge/` 位置写 redirect 说明（保留引用，ADR-0030）。
4. 跑 `python3 scripts/ontology-validate.py --ontology-dir ontology` → 全 PASS（AC-1~AC-6）。
5. 用 `register-evidence` 登记迁移证据（Do→Check 门禁所需）。

## 5. 校验
- `python3 scripts/ontology-validate.py --ontology-dir ontology` 退出码 0。
- 16 实例 GUIDES/RELATES_TO 全覆盖；类节点树无环；source_task 齐备。

## 6. 不在本任务范围
- `records/*/evidence/` 的 tls 代码/日志文件（约 20 个）→ T0403 全量。
- 图数据库迁移（见 ADR-0031，当前用 md 承载）。
