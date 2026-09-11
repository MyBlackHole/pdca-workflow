# 按 rdb-feature-design 颗粒度深化工具调用链

## 纠偏背景

用户明确指出“我需要的是调用链”，并指定 `/home/black/Public/aio/rdb-skills/skills/rdb-feature-design` 为参照。此前“每工具独立详解页 + 通用设计栏目 + 强制配图”的方向偏离目标，本票将其全部撤销。

参照 skill 的关键特征不是篇幅，而是：先定义统一业务阶段，再对每个对象的每个操作从真实入口开始，以代码块逐层写出 API/CLI、服务或分发、模型/核心实现、跨仓或系统出口；同时写清 if/elif 分支、隐式字符串契约、现行/历史状态和返回/回调链。

## 目标

把 `rdb-tools-design` 从“23 个工具的一行入口清单”深化为“23 个工具的逐操作真实调用链地图”，使 agent 能像使用 `rdb-feature-design` 一样，直接回答：

1. 用户从哪个命令、参数、method 或 ABI 进入；
2. 入口经过哪些实际函数、类方法和分发分支；
3. 在哪里跨进程、跨模块、进入内核或第三方库；
4. 对端由哪个 handler 接收，最终产生什么结果；
5. 结果、错误或回调沿什么路径返回；
6. 哪些同名实现是孤岛、旧链或仅构建存在。

## 参照颗粒度

采用 `rdb-feature-design/references/03-aio-cdm-knowledge-map/6.2.0.0.md` 的表达方式：

- 统一列出“操作/阶段约定”，每个工具不存在的操作明确写“不适用”；
- 每个操作用独立代码块表达多层符号链，格式类似 `入口符号 (path) -> 分发符号 -> 核心符号 -> 下游边界 -> 返回/回写`；
- 分支判断直接展开到对应实现，不用“进入相关处理”一笔带过；
- 必要机制说明紧跟链路，只解释为何转向、如何分发、契约是什么、状态是否现行；
- 源码行号用于复核关键转折点，但稳定导航以文件和符号名为主。

## 范围

调用链覆盖现有 23 项独立交付入口：

- fs-backup：`fs-cli`、`fsdeamon`、`fsbackup_tools`、`fsbackup.ko`、`makeFsbackup`
- rpc/rdbcomm：`aio-speed`、`aio-speedd`、`rpc-keygen`、`rdbcomm`、`rdbcommd`
- S3：`s3-tool`、`s3file`、`s3mount`、`afsd`、`afs-cli`
- XBSA/SBT：`xbsa64`、`rch-tools`、`sbt`、`FileTransferAgent`、`dmsbtex`、`dm-ftp`
- 公共工具：`bwlimit_tools`、`tls-keygen`

不是每个工具只写一条“启动链”。必须从源码的参数解析、subcommand、method、消息类型、导出函数或 handler 分支枚举该工具实际提供的对外操作，并分别建链。简单叶工具可在到达库函数或系统调用后终止；复杂工具必须继续跨过进程/协议边界到对端 handler 和最终结果。

## 调用链编写契约

每条链按实际存在的节点展开：

```text
操作名称 / 触发条件
入口：main/导出 ABI/内核入口 (path:symbol[:line])
  -> 参数解析或请求构造 (path:symbol)
  -> 分发条件：<真实 switch/if/method/消息号>
     -> 核心实现 (path:symbol)
        -> 下游库、socket、ioctl、文件或进程边界
           -> 对端接收/内核 handler/第三方 ABI (path:symbol)
              -> 结果落点
返回：响应构造/错误传播/资源清理 -> 调用方可见结果
状态：current / external / operator / build-only / isolated / deprecated
```

约束：

- 链路节点必须是源码中的真实函数、方法、target、handler、系统调用或协议字段。
- 不为凑层级重复写目录、文件或抽象名；无法继续追踪时明确写断点原因。
- 有多个分支时逐支列出条件和去向；公共前缀只写一次。
- 跨进程/模块链同时列发送端、常量/字段、传输边界、接收端和响应端。
- 同一个工具的启动链、业务操作链、回写/回调链可以分开写，但必须相互引用。

## 文档落点

- 保留现有 `SKILL.md + references/00-index.md + 01–05 版本化分册`，与 `rdb-feature-design` 的入口/索引/知识地图结构同构。
- 01–04 分册按工具及其操作补写调用链；03/05 中的公共能力与构建装配作为链路下游被引用。
- 05 分册维护 `target -> 入口 -> 所属调用链章节 -> 安装/交付` 映射，不以构建 target 冒充运行时调用链。
- 00-index 同时提供“工具 → 操作 → 分册章节”和“需求类型 → 主调用链”路由。
- 不要求创建 23 个独立工具页；只有单个版本分册过大且存在明确按需加载收益时才可进一步拆分。

## 必须优先闭合的复杂链

1. `fs-cli` method/FS_* → 8901 `fsdeamon` 分发 → FsSource/BackupHelper → unix socket、内核 ioctl 或本地快照/元数据 → response。
2. `aio-speed` 请求/MT_* → rpc session → 6611 `aio-speedd` accept/dispatch → 文件或块处理 → 响应与错误返回。
3. `rdbcomm` 命令/模块/文件操作 → 6610 `rdbcommd` opcode handler → 读写/执行 → 响应。
4. `s3file`、`s3mount`、`afsd`、`afs-cli` 的命令/FUSE 回调 → S3 公共层 → SDK/对象操作 → 本地输出或 FUSE 返回。
5. `xbsa64`、`sbt`、`dmsbtex` 等导出 ABI → 会话/对象/传输实现 → 外部消费者或服务进程，并明确仓内无调用者不等于无对外链路。

## 非目标

- 不建设每工具通用设计百科，不强制结构体、资源生命周期或 Mermaid 成为所有工具的固定栏目；仅在解释调用链转折时补充。
- 不以“一行入口 → 核心 → 输出”作为完成链路。
- 不修改 aio-tools 的 C、C++、Go、xmake 或运行时行为。
- 不覆盖 6.2.0.0 之外的版本，不以静态阅读替代运行环境联调。
- 不重写与调用链无关的业务介绍、安装说明或通用教程。

## 实施步骤

1. 从每个工具的 main、导出符号、内核入口和 target 建立入口清单。
2. 从参数解析、switch/if、method/opcode 表提取全部对外操作与分支。
3. 沿调用者/被调用者追踪到文件、socket、内核、SDK、外部 ABI 或真实终止点。
4. 反向追踪响应、回写、回调、错误和清理路径。
5. 写入 01–04 对应版本分册，更新 00/05 路由和交付映射。
6. 对 23 工具、操作分支、跨端契约、源码符号和引用闭合做自动/人工验证。

## 验收标准

- [ ] AC-1（回链父 AC-1）: 23 个工具在 6.2.0.0 地图中均有独立调用链章节；每个工具源码中可从入口到达的公开 subcommand、method、opcode、导出 ABI 或 handler 操作均被枚举，缺失操作为零。
- [ ] AC-2（回链父 AC-2）: 每条调用链从真实入口开始，逐层写出参数/请求构造、分发条件、核心符号、下游边界和返回/回写；链路节点使用 `path:symbol`，禁止用“相关模块/核心处理”等抽象词替代。
- [ ] AC-3（回链父 AC-2）: `fs-cli↔fsdeamon`、`aio-speed↔aio-speedd`、`rdbcomm↔rdbcommd`、S3/FUSE 与 XBSA/SBT 复杂链均跨到真实对端或外部边界，且代表性主链至少包含五个可复核符号节点。
- [ ] AC-4（回链父 AC-4）: method、FS_*、MT_*、ioctl、opcode、端口、socket 路径和导出 ABI 的发送/生产端与接收/消费端逐字核对；未闭合契约显式列出，不冒充完整链。
- [ ] AC-5（回链父 AC-5）: `00-index.md` 可按“工具 + 操作”和“需求类型”路由到对应分册调用链；05 分册把构建 target 链接到运行链章节并区分 build-only 与 runtime/external。
- [ ] AC-6（回链父 AC-6）: 每条链标明 current/external/operator/build-only/isolated/deprecated，现行性由调用方、构建装配或对外 ABI 实证；不把孤岛实现推荐为现行修改落点。
- [ ] AC-7（回链父 AC-7）: 23 工具清单、公开操作覆盖、内部引用、源码路径/符号和 skill frontmatter 校验全部通过；无 TODO、示例占位或以单个入口锚点代表整条复杂链。
- [ ] AC-8（回链父 AC-8）: aio-tools 产品源码和构建行为无本任务变更；变更限定为 `rdb-tools-design`、T2180 evidence 与后续知识处置。

### 声明的测试接缝

本票只修改 skill 文档与 references，不修改可执行产品代码，测试接缝免责。验证接缝为：工具/操作清单检查、Markdown 引用检查、源码 `path:symbol` 存在性检查、关键协议两端对照和 `quick_validate.py`。

## 关联本体节点

- `ontology:domain/pdca/rdb-tools-independent-call-chain`
- `ontology:concept/skill-invocation-contract`
- `ontology:concept/progressive-disclosure`
- `ontology:concept/knowledge-provenance`

## 拆分映射

- rdb-tools 调用链知识投射 -> ontology:concept/skill-invocation-contract

## 不再拆分

本票为叶票；五分册的共享契约与索引必须在同一迁移中闭合，继续拆分会形成路由指向旧链或跨端只完成一侧的中间状态。
