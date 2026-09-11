# 投射 rdb-tools-design 23 工具代码级详解

## 父任务与目标

本票是 T2176 的单一实现叶票，完整投射父 PRD 已确认的信息架构和代码级深度。范围固定为 6.2.0.0 的 23 个工具，不修改 aio-tools 产品行为。

## 实现范围

1. 盘点 `fs-cli`、`fsdeamon`、`fsbackup_tools`、`fsbackup.ko`、`makeFsbackup`、`aio-speed`、`aio-speedd`、`rpc-keygen`、`rdbcomm`、`rdbcommd`、`s3-tool`、`s3file`、`s3mount`、`afsd`、`afs-cli`、`xbsa64`、`rch-tools`、`sbt`、`FileTransferAgent`、`dmsbtex`、`dm-ftp`、`bwlimit_tools`、`tls-keygen`。
2. 重构为短 `SKILL.md`、`00-index.md`、五个子系统分册和所属分册下 `tools/6.2.0.0/<tool>.md`。
3. 12 个 A 级工具覆盖函数、结构体、状态/线程/进程、数据流、协议、错误清理、扩展影响并配 Mermaid 图；其余 11 个 B 级工具覆盖真实存在的代码生命周期，非平凡链路按需补图。
4. 主链入口、分发、核心、输出/清理分别具有源码锚点；跨模块契约具有生产端和消费端锚点。
5. 验证工具清单、内部链接、源码路径/行号、Mermaid fence、frontmatter 和无产品代码行为变更。

## 验收标准

- [ ] AC-1（回链父 AC-1）: 23 个工具均有独立版本化详解页，清单、文件和索引一一对应。
- [ ] AC-2（回链父 AC-2、AC-6）: 所有工具页满足 A/B 模板，主链四阶段均有真实源码锚点，并说明状态、错误清理和扩展影响。
- [ ] AC-3（回链父 AC-3）: 12 个 A 级工具每页至少一幅具有源码映射的 Mermaid 图，B 级复杂链按需补图。
- [ ] AC-4（回链父 AC-4）: 跨模块协议与 ABI 具有生产端、消费端证据，未闭合项显式标记。
- [ ] AC-5（回链父 AC-5）: 入口、总索引、五分册和工具页形成三跳内可达且可反向导航的渐进披露结构。
- [ ] AC-6（回链父 AC-7）: quick_validate、清单、链接、源码锚点和 Mermaid 检查全部通过，无 TODO 或示例占位。
- [ ] AC-7（回链父 AC-8）: aio-tools 产品源码与构建行为无本任务变更。

### 声明的测试接缝

本票只修改 skill 文档与 references，不修改可执行产品代码，测试接缝免责；以 `quick_validate.py`、文档图检查、源码锚点检查及 `git diff --name-only` 验证。

## 关联本体节点

- `ontology:domain/pdca/rdb-tools-independent-call-chain`
- `ontology:concept/skill-invocation-contract`
- `ontology:concept/progressive-disclosure`
- `ontology:concept/knowledge-provenance`

## 拆分映射

- rdb-tools-design 文档投射 -> ontology:concept/skill-invocation-contract

## 不再拆分

本票是叶票。工具页、共享索引与链接校验必须作为一个原子迁移交付，继续拆分会产生索引指向不存在页面或部分工具仍停留在旧结构的中间状态。
