# tls 试点 16 文件 → 完整本体图映射样例

> 目的：用真实文件验证 v2 本体模型（实体类型层次 + 属性 + 关系图；知识形态作独立 KnowledgeArtifact 子类，经 guides 挂接）。
> 来源：knowledge/ 下 16 个 tls 相关 md。

## 一、实体类型层次（specializes = is-a / kind-of）

```
Entity
├─ DomainEntity ── specializes ──> Entity
│   ├─ TLSSession        (specializes DomainEntity)  composed_of: [MTLSHandshake, X509Certificate, TLSConfiguration]
│   ├─ MTLSHandshake     (specializes DomainEntity)  composed_of: [X509Certificate]
│   ├─ X509Certificate   (specializes DomainEntity)
│   ├─ TLSConfiguration  (specializes DomainEntity)
│   ├─ TLSTestHarness    (specializes DomainEntity)
│   └─ ExecStdinPump     (specializes DomainEntity)   ← tls-exec 截断
├─ Process ── specializes ──> Entity
│   └─ CodeReviewProcess (specializes Process)        ← 四模块补充审查
└─ KnowledgeArtifact ── specializes ──> Entity
    ├─ Pattern   (knowledge_form=pattern)
    ├─ Principle (knowledge_form=principle)
    ├─ Pitfall   (knowledge_form=pitfall)
    ├─ Fact      (knowledge_form=fact)
    └─ Decision  (knowledge_form=decision)
```

## 二、16 文件逐篇映射（type=knowledge_form / specializes / guides 实体 / attributes 摘要）

| # | 文件 | knowledge_form | specializes | guides(领域实体) | attributes 摘要（可派测试的信号） |
|---|------|---------------|-------------|------------------|----------------------------------|
| 1 | linux-epoll-eventloop/backupstream-plain-tls-ingress | pattern | KnowledgeArtifact | TLSSession | 双路径分离；admission 两层分离；弹性会话池；共享事件域；事件原语防失效 |
| 2 | tooling/cli-tls-mtls-configuration | principle | KnowledgeArtifact | TLSConfiguration | 统一 CLI 键；优先级固定 CLI>env>段>security>默认；拒绝未知算法 |
| 3 | nbu/gmssl-tlcp-mtls | pattern | KnowledgeArtifact | MTLSHandshake | API 不兼容表（TLS_CTX≠SSL_CTX）；vtable 连接生命周期抽象 |
| 4 | rpc-rdbcomm/mtls-review-fd-session-boundary | principle | KnowledgeArtifact | MTLSHandshake | 连接对象须携带 SSL*；cleanup 覆盖失败/初始化/正常/线程退出 |
| 5 | rpc-rdbcomm/unified-first-stage-mtls-time | pattern | KnowledgeArtifact | MTLSHandshake | 统一第一阶段 TIME/NEGOTIATE；协商失败不降级；按 ca_cn 选证书 |
| 6 | tls/link-level-mtls-test-pattern | pattern | KnowledgeArtifact | TLSTestHarness | socketpair+fork；决策树复刻；SIGPIPE 忽略；CN 白名单 `[A-Za-z0-9._-]` |
| 7 | tls/mtls-server-alg-whitelist | pattern | KnowledgeArtifact | MTLSHandshake, TLSConfiguration | 四模块入口锚点；fail-closed；错误码 0x8005；先取算法名再查 ca_cn |
| 8 | tls/structured-mtls-failure-diagnostics | principle | KnowledgeArtifact | TLSSession | 日志含 role/stage/alg/路径；证书失败记录标识不记私钥；移除错误码 |
| 9 | tls/mtls-param-review-findings | pitfall | KnowledgeArtifact | MTLSHandshake, TLSConfiguration | slot 空回落；atoi fail-open；strstr 子串匹配；枚举单源收敛 |
| 10 | tls/tls_cert_reload_appdata_safety | pitfall | KnowledgeArtifact | X509Certificate | app_data 悬空 UAF；SIGPIPE 终止进程；相对路径依赖 CWD |
| 11 | tls/mtls-four-module-supplementary-review | pattern | KnowledgeArtifact | CodeReviewProcess | 缓冲区总长；strtol 全串校验；三态 bool 收敛；枚举单源 |
| 12 | tls/mtls-handshake-enum-unify | pattern | KnowledgeArtifact | MTLSHandshake | 单头真实定义；模块别名宏；include guard 同名遮蔽；链接依赖遗漏 |
| 13 | tls/mtls-handshake-netorder-libobk | pattern | KnowledgeArtifact | MTLSHandshake | 网络序 htons/ntohs；put_u16_be 封装；测试断言契约字节序 |
| 14 | debugging/tls-exec-truncation-investigation-state | fact | KnowledgeArtifact | ExecStdinPump, TLSSession | partial；已知事实 sent=61440≈credit；排除端口/证书/队列丢弃 |
| 15 | dmsbtex/sbt_config_mtls_override | pattern | KnowledgeArtifact | TLSConfiguration | 解析块位置避免 goto 跳过；基线+仅覆盖存在键；fail-closed |
| 16 | oss/oss_https_tls | pattern | KnowledgeArtifact | TLSConfiguration, TLSSession | 单端口 HTTPS；算法前缀解析；4 层优先级；受限 TLS 保留 h2 套件 |

## 三、关系实例（图，非树）

**guides（知识 → 领域实体）**：
- Pattern×9 → MTLSHandshake(3,5,7,12,13) / TLSSession(1) / TLSConfiguration(2,15,16) / TLSTestHarness(6) / CodeReviewProcess(11)
- Principle×3 → MTLSHandshake(4) / TLSConfiguration(2) / TLSSession(8)
- Pitfall×2 → MTLSHandshake+TLSConfiguration(9) / X509Certificate(10)
- Fact×1 → ExecStdinPump(14)

**composed_of（实体组合）**：
- TLSSession → {MTLSHandshake, X509Certificate, TLSConfiguration}
- MTLSHandshake → {X509Certificate}

**relates_to（跨文档关联）**：
- mtls-server-alg-whitelist ↔ mtls-param-review-findings（陷阱1）
- mtls-handshake-enum-unify ↔ mtls-four-module-supplementary-review
- mtls-handshake-netorder-libobk ↔ mtls-four-module-supplementary-review
- sbt_config_mtls_override ↔ tls_cert_reload_appdata_safety（T0366）

## 四、验证结论（证明 v2 模型可行）

1. **知识形态确为独立实体子类**：16 篇中 pattern=9、principle=3、pitfall=2、fact=1、decision=0，全为 `KnowledgeArtifact` 子类，经 `guides` 挂接领域实体——非目录分类、非降维属性。
2. **本体是图不是树**：除 is-a 外，有 `guides`/`composed_of`/`relates_to` 三类关系，形成跨文档网络（如 9 号 pitfall 同时 guides 握手与配置）。
3. **属性承载可测信号**：每篇 `attributes` 列即"可派测试的信号"（CN 白名单格式、fail-closed、网络序、SIGPIPE），呼应 Grill Q9"属性→派生测试"。
4. **建模真实实体而非系统**：节点是 tls-session / mtls-handshake / x509-certificate / tls-configuration / code-review-process 等真实领域概念，符合 Palantir "Model reality not systems"。
5. **目录平铺仅索引**：16 文件分布于 linux-epoll-eventloop/、tooling/、nbu/、rpc-rdbcomm/、tls/、debugging/、dmsbtex/、oss/ 八个平铺目录，语义全在关系图，不靠目录嵌套。

## 五、对校验器的影响

- `ontology-validate.py` 受控 `type` 词汇 = {domain, entity, concept, process, role, pattern, principle, pitfall, fact, decision}（实体类别 + 知识子类）。
- 新增 AC：`knowledge_form` 受控；`guides`/`relates_to`/`composed_of` 引用非空悬、无环；每 KnowledgeArtifact 至少 1 条 `guides` 或 `relates_to`（保证关系丰富度）。
- `specializes` 必须形成单根 `Entity` 的有向无环树。
