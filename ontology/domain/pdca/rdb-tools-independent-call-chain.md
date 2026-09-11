---
schema: pdca.asset/v1
id: ontology:domain/pdca/rdb-tools-independent-call-chain
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/rdb-tools-independent-call-chain/1.0.1
summary: 6200 release 工具按可触发操作展开、跨端闭合的调用链设计与审查规则
relations:
  specializes:
  - ontology:concept/skill-invocation-contract
  relates_to:
  - ontology:concept/knowledge-provenance
---

# RDB Tools 独立调用链

T2157 的可复用规则：每个可交付工具必须独立记录“入口参数或子命令 → 分发函数或构建 target → 核心实现 → 输出、文件、socket、端口或安装副作用 → 调用方状态”。同一产品线的工具可以共享事实来源，但不得用合并行隐藏独立入口；`fsbackup.ko`、`fsbackup_tools` 和 `makeFsbackup` 也必须分别建链。

来源：`T2157-0911-aio-tools-t2155-runtime-call-chain`；理由：用户确认“所有工具都应该独立存在调用链”，并指出 `fsbackup` 遗漏。该规则已落实到 `rdb-tools-design/references/00-index.md` 与 `05-build-release-knowledge-map/6.2.0.0.md`。

## Revision 2：可触发操作级调用链（T2180）

工具独立只是索引层要求，调用链的最小完备单元是一个**外部可触发操作**：子命令、method、opcode、ioctl、公开 ABI 或构建 target。每项操作必须单独枚举，不能用工具级单行摘要代替其真实分支。

每条运行时调用链按可验证证据展开：

1. 命令、API 或协议入口；
2. 参数解析、请求构造或 dispatch 条件；
3. 当前操作对应的分支函数；
4. 核心实现符号及必要的中间层；
5. socket、RPC、ioctl、内核、SDK 或外部 ABI 边界；
6. 对端接收、处理、结果生成；
7. 响应解析、状态转换、清理和最终输出。

跨进程或跨模块协议必须同时定位发送端与接收端，并对齐 method/opcode/消息结构；只有发送端而在当前基线找不到接收端时，必须标记“未闭合”，不得推断或伪造对端。链路状态统一区分 `current`、`external`、`operator`、`build-only`、`isolated`、`deprecated`。构建 target 只说明产物来源，必须与运行时入口及调用链分开表达，再通过索引连接。

来源：`T2180-0911-rdb-tools-call-chain-deepening`；摘要：23 个工具按公开操作展开到入口、分发、核心、跨端及返回路径，登记 138 个去重 `path:symbol` 锚点，并明确 6 个 `afs-cli` 网络 method 在 6.2.0.0 基线中未闭合；理由：用户明确要求“调用链”，并指定 `rdb-feature-design` 的逐操作、多层符号颗粒度作为参照。关键证据：`t2180-call-chain-index-v1`、`t2180-fs-call-chains-v1`、`t2180-rpc-rdbcomm-call-chains-v1`、`t2180-s3-xbsa-call-chains-v1`、`t2180-validation-report-v1`。
