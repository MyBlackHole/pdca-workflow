# 为 rdb-tools-design 新增 6.1.1.0 调用链地图

## 背景

现有 `rdb-tools-design` 已按工具业务域建立版本化知识地图，但当前只有 `6.2.0.0.md`。本任务按用户给出的 `rdb-feature-design/references/` 结构范式，在现有知识域目录中新增 `6.1.1.0.md`，并更新共享入口与版本路由。6110 的业务事实必须从 aio-tools 6110 release 独立分析，不从 6200 版本页复制、推导或比较。

## 已确认目标

- 唯一源码事实基线：`/home/black/Public/aio/aio-tools/6110/release`。
- Git 基线：`6.1.1.0-release@5ec42fd4`。
- 目标 skill：现有 `/home/black/Public/aio/rdb-skills/skills/rdb-tools-design`，不新建带版本后缀的 skill。
- 结构参照：`rdb-feature-design` 的“共享 SKILL + 总索引 + 业务域目录 + 每版本一文件”。
- 覆盖对象：6110 release 独立发现的全部业务工具及其外部可触发操作。
- 验证边界：静态源码、构建配置、协议双端、符号锚点和文档路由；不要求真实部署或外部系统联调。

## 用户场景

1. 用户给出 6110 工具或操作，skill 先确定 `6.1.1.0`，再路由到对应知识域版本文件。
2. 用户只给出备份、恢复、传输、挂载、限速、构建发布等需求，索引能路由到相应工具与逐操作链。
3. 用户给出协议、端口、opcode、ioctl、ABI 或错误，版本地图能定位生产端、传输边界、消费端与返回路径。
4. 6110 缺少仓内消费者或协议对端时，地图明确标记 `external`、`isolated`、`build-only`、`deprecated`、未闭合或无法确认。

## 范围

### 纳入

当前从 6110 release 构建与入口独立发现的 23 个候选业务工具：

- 文件备份：`fs-cli`、`fsdeamon`、`fsbackup_tools`、`fsbackup.ko`、`makeFsbackup`。
- RPC/RDBComm：`aio-speed`、`aio-speedd`、`rpc-keygen`、`rdbcomm`、`rdbcommd`。
- S3/FUSE：`s3-tool`、`s3file`、`s3mount`、`afsd`、`afs-cli`。
- 数据库介质：`xbsa64`、`rch-tools`、`sbt`、`FileTransferAgent`、`dmsbtex`、`dm-ftp`。
- 公共工具：`bwlimit_tools`、`tls-keygen`。

最终工具数以 6110 基线的 target kind、安装配置、程序入口和公开消费证据为准；发现遗漏或非交付 target 时必须按源码修正。

### 排除

- `6110/IPV6`、`6110/test`、`6110/old-dm` sibling 源码树。
- 6200 源码以及 `rdb-tools-design` 下现有 `6.2.0.0.md` 的业务事实。
- 跨版本复制、差异推断或“6110 应与 6200 相同”的假设。
- aio-tools 产品源码和构建行为修改。
- 真实端口可达、服务部署、内核模块装载、备份恢复成功和第三方数据库联调。

## 产物结构

沿用现有 `rdb-tools-design`，对齐 `rdb-feature-design` 的版本化知识地图组织：

```text
skills/rdb-tools-design/
├── SKILL.md                                      # 更新：先定版本再路由
└── references/
    ├── 00-index.md                               # 更新：加入 6.1.1.0 版本路由
    ├── 01-fs-backup-knowledge-map/
    │   ├── 6.1.1.0.md                            # 新增：6110 独立事实
    │   └── 6.2.0.0.md                            # 保留，不作为本任务事实源
    ├── 02-rpc-rdbcomm-knowledge-map/
    │   ├── 6.1.1.0.md                            # 新增
    │   └── 6.2.0.0.md                            # 保留
    ├── 03-libs-knowledge-map/
    │   ├── 6.1.1.0.md                            # 新增
    │   └── 6.2.0.0.md                            # 保留
    ├── 04-s3-xbsa-knowledge-map/
    │   ├── 6.1.1.0.md                            # 新增
    │   └── 6.2.0.0.md                            # 保留
    └── 05-build-release-knowledge-map/
        ├── 6.1.1.0.md                            # 新增
        └── 6.2.0.0.md                            # 保留
```

错误草案 `skills/rdb-tools-design-6110/` 不属于最终产物，进入 Do 后删除。不得创建 `references/00-signals.md` 或 `references/01-call-chains.md`。

## 版本路由契约

1. `SKILL.md` 不再把事实源硬编码为 6200；强制先读 `00-index.md` 定版本。
2. `00-index.md` 明确列出 `6.1.1.0` 与 `6.2.0.0`，精确版本优先，不做跨版本向下取底来替代已存在的 6110 地图。
3. 选中 6110 后，五个知识域链接必须全部指向各自的 `6.1.1.0.md`。
4. 每个 `6.1.1.0.md` 自完备声明源码基线、覆盖工具、操作路由、状态和证据边界，不依赖 `6.2.0.0.md` 才能理解。
5. 共享索引仅负责版本与业务域路由，不把某一版本事实写成跨版本通则。

## 逐操作调用链契约

每个外部可触发操作是最小记录单元。复杂链至少给出 5 个有序 `path:symbol` 节点，并尽可能覆盖：

```text
入口 → 参数/请求构造 → switch/if/method/opcode/ioctl 分发
→ 核心函数 → 进程/内核/SDK/ABI 边界 → 对端 handler/结果落点
→ 返回/回写/清理
```

- 跨端契约必须同时定位生产端和消费端；6110 基线缺端时写“未闭合”。
- 状态只使用 `current`、`external`、`operator`、`build-only`、`isolated`、`deprecated`，可组合。
- 每条关键结论标记 `[来源: path:symbol]`；源码不足时写“无法确认：缺少什么证据”。
- 构建 target 只能证明装配，测试/simulator 只能证明示例消费，二者不得冒充生产运行链。

## 五步工作流

1. 定版本：从用户输入或源码分支确定 `6.1.1.0`，完整读取 `references/00-index.md` 的版本路由。
2. 定业务域：按工具、操作、需求或协议选择 01–05 中一个或多个 `6.1.1.0.md`。
3. 读逐操作章节：只加载命中章节，记录入口、分发、核心、边界、返回和状态。
4. 源码复核：在 6110 release 对每个 `path:symbol` 和协议双端逐字核验；文档与源码不符时以源码为准并修正文档。
5. 输出定位：给出版本文件、完整调用链、分支条件、契约状态、结果与无法确认项。

## 实施步骤

1. 从 6110 release 的 Xmake、Makefile、安装规则、`main`、导出头文件独立建立工具与公开操作清单。
2. 更新 `SKILL.md` 为版本中立入口，加入“先定版本、再读地图、后源码验证”。
3. 更新 `00-index.md` 的版本清单、版本选择、工具/需求/协议路由，使 6110 精确指向五个 `6.1.1.0.md`。
4. 在五个现有知识域目录分别新增 `6.1.1.0.md`，逐操作展开真实调用链。
5. 删除错误的 `rdb-tools-design-6110/` 草案，验证覆盖、锚点、协议双端、版本路由、独立性、skill 格式和产品树零改动。

## 验收标准

- [ ] AC-1：所有 6110 事实锚点均位于 `/home/black/Public/aio/aio-tools/6110/release@5ec42fd4`；不引用 sibling 树或其它版本源码。
- [ ] AC-2：最终只使用现有 `skills/rdb-tools-design/`，不存在 `skills/rdb-tools-design-6110/`。
- [ ] AC-3：结构符合 `rdb-feature-design` 的版本化知识地图范式：共享 `SKILL.md`、`00-index.md`、业务域目录及每版本一文件。
- [ ] AC-4：五个现有知识域目录各新增且仅新增一个 `6.1.1.0.md`；原有 `6.2.0.0.md` 内容和路径保持不变。
- [ ] AC-5：`SKILL.md` 与 `00-index.md` 能从 6.1.1.0 基线、工具、需求或协议正确路由到全部 6110 版本页，且不默认落到 6.2.0.0。
- [ ] AC-6：五个 `6.1.1.0.md` 覆盖独立枚举的每个业务工具和公开操作；当前 23 项候选逐项有入口、状态、路由和源码证据。
- [ ] AC-7：复杂调用链至少包含 5 个有序 `path:symbol` 节点；跨端协议双端闭合，缺端明确标记“未闭合”。
- [ ] AC-8：五个 `6.1.1.0.md` 不含 6200、6.2.0.0 事实引用、跨版本链接、复制说明或“与 6.2 相同”等依赖表达。
- [ ] AC-9：全部 Markdown 路由与源码 `path:symbol` 锚点存活；skill-creator `quick_validate.py` 通过，无占位文本。
- [ ] AC-10：6110 release 的 `git status --short` 与 `git diff --stat` 在 Do 前后均为空；任务不修改产品源码。

## 验证证据

Do 至少登记：6110 工具/操作清单、五个版本页、共享入口与索引变更、版本路由检查、逐操作覆盖检查、源码锚点检查、协议双端检查、6200 独立性扫描、错误草案清理、quick_validate、产品源码零改动证明和 AC 收敛映射。

### 声明的测试接缝

本任务只修改 Markdown skill 资产，不修改可执行代码，免于声明代码测试 seam；以 `quick_validate.py`、源码锚点、Markdown 链接、版本路由和独立性扫描作为可观察验证。

## 风险与边界

- 共享 `SKILL.md` 和 `00-index.md` 同时服务多个版本，更新时不得破坏 6.2.0.0 的现有路由。
- 6110 工具名可能与 6200 相同，但同名不能证明实现、操作、协议或状态相同。
- 自带 test/simulator 只能证明示例调用，不能替代仓外数据库消费者。
- 静态源码不能证明端口、权限、TLS、内核兼容、S3 凭据或数据库环境可用。

## 任务拆解决策

不拆子任务。共享路由与五个版本地图组成一个不可分割的版本知识闭环；Do 阶段按入口/索引、五个版本页和验证结果分别登记 Evidence。

## 关联本体节点

```text
ontology:concept/skill-invocation-contract
ontology:concept/knowledge-provenance
ontology:domain/pdca/rdb-tools-independent-call-chain
```

## 拆分映射

- rdb-tools-design 6110 版本化调用链地图 -> ontology:concept/skill-invocation-contract

## Plan 确认摘要

用户最终以 `rdb-feature-design/references/` 树纠正结构：不新建 `rdb-tools-design-6110`，而是在现有 `rdb-tools-design` 的五个知识域目录中新增独立的 `6.1.1.0.md`，更新共享 `SKILL.md` 与 `00-index.md`。事实只来自 6110 release，不读取或依赖 6.2.0.0 版本页。等待本版 final confirmation 后方可重新进入 Do。
