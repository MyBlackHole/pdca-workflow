# systems-programming 主线来源与贡献政策复审：3.4.1 → 3.4.2

日期：2026-10-30，Asia/Shanghai。技能基线为 `82405593c663405831f0b7872e80357345273a79`。
本轮关闭官方 Git 来源和逐文件比对的证据缺口，修正将旧版本辅助标签要求推广到所有版本的问题。
skill 仍只包含 Markdown 规则、参考与 YAML；可运行验收资产保留在仓库 tests/。

## 实际取得的官方主线

在 2026-10-29 17:01 UTC 前后，官方 `torvalds/linux.git` 的 `refs/heads/master` 返回
`c339f4010dea8b0d754f84ace70cd1b089878ef8`；随后核实 Torvalds 的 GitHub 镜像返回同一提交。
独立浅克隆固定于该提交，路径为 `/home/black/Documents/linux-mainline-review-20261030`，
origin 为 `https://github.com/torvalds/linux.git`，过滤器为 `blob:none`，只稀疏检出获准的精确文件。
这是观测时点的主线快照，不声明 master 此后不变，也不以目录名称认证版本。

该提交日期为 `2026-10-28T07:36:32-10:00`，摘要为合并 `platform-drivers-x86-v7.4-1`。
实际 Makefile 仍为 VERSION=7、PATCHLEVEL=3、SUBLEVEL=0、EXTRAVERSION 为空；
不能用合并标签、目录名或 Makefile 单独替代完整提交身份。

kernel.org 服务端不支持本次 blob 过滤，核实镜像同提交及过滤能力后切换传输来源。
正文获取曾遇 TLS EOF、HTTP 429 和超时；保留失败，按缺失对象续取并遵守退避，未把计划或部分下载当完成。
复用原文件和取得镜像正文时，均先核对固定提交的 Git 树对象标识，再用原生 Git 验证，
不是因为文件名相同或来自下载页面就接受内容。最终 63 个工作副本文件全部匹配树对象，限定状态干净。

原 `/home/black/Documents/linux-7.3` 的 63 个文件前后 SHA-256 均未改变；它仍没有 Git 元数据。
其中 41 个文件与固定主线相同，22 个不同。这只能证明所列文件的关系，不能认证原整树的来源、完整性或是否原版。

## 比对范围与发现

范围包含 coding-style、development-process 的八个正文、提交/AI/安全/stable/许可/回归政策、
Rust 指南，以及内存、锁、清理、等待、workqueue、容器、DMA、VFS 的文档、声明、实现与已用调用者。
63 个精确路径与逐文件摘要保存在本轮工作区，不递归盘点 Linux 或 PDCA。
逐文件校验不等于逐行读完所有实现：本轮读完 22 份差异，结合相关函数及 API 注释解释；
另完整读取补查的 submit-checklist、stable、security、license、handling-regressions 和两份 Rust 文档。

| 实际差异或复核点 | 对技能的判断 |
| --- | --- |
| coding-assistants 删除 Attribution 及步骤中的固定辅助标签要求；submitting-patches 删除对应标签小节 | 旧版要求不能无条件推广；本轮修正唯一规则位置 |
| generated-content 字节未变；coding-assistants 保留人工 DCO 与 AI 不加签要求 | 来源、提示/影响部分和真实验证仍须披露；取消固定标签不等于取消透明度 |
| 内存分配文档、cleanup helpers、XArray 标记和 VFS 接口演进 | 当前规则已要求按目标树核对默认 GFP、移交/清理、容器和接口语义，没有把旧 helper 当通用模板 |
| workqueue 的 flush/pwq/在途计数与锁组织有较大内部变化，公共 workqueue 文档未变 | 按真实控制流分析仍持有的锁、重入队及退出；不能从结构变化推导性能数字或把局部结构推广到用户态 |
| list/timer/kthread 访问、等待 helper 和字符串实现变化 | 继续区分访问约束、排序与对象存活；现有规则不依赖被替换的内部细节 |
| 回归文档仅代词变化；Rust general-information 更换条件编译示例 | 不固化示例符号/编译器门槛；目标树支持与专项原文责任足够，本轮不新增规则目录 |
| mutex_unlock 对对象存活、mempool 保留下界、kthread 启动/停止与 task 引用 | 相关声明和实现支持现有约束；没有发现需要再改的技术结论 |

政策差异直接见固定提交的
[coding-assistants](https://github.com/torvalds/linux/blob/c339f4010dea8b0d754f84ace70cd1b089878ef8/Documentation/process/coding-assistants.rst)、
[submitting-patches](https://github.com/torvalds/linux/blob/c339f4010dea8b0d754f84ace70cd1b089878ef8/Documentation/process/submitting-patches.rst) 与
[generated-content](https://github.com/torvalds/linux/blob/c339f4010dea8b0d754f84ace70cd1b089878ef8/Documentation/process/generated-content.rst)。
此前读取的滚动渲染页面仍含旧标签要求，因此渲染站地址不能证明目标贡献的适用政策版本。

## 最小修订与独立验收

[贡献流程](../../skills/systems-programming/references/workflows/kernel-contribution.md#ai-归属与人工认证)
改为依据适用政策决定辅助标签；旧版本明确要求时仍按其格式处理，不把 git/gcc/make 列为专项分析工具。
[官方映射](../../skills/systems-programming/references/sources/official-docs.md#风格文档与贡献)
补充政策版本与披露责任。入口只更新版本；未在其他参考复制第二份标签规则。

一次只读独立场景向新上下文提供两个来源的三份政策原文和必要技能资料，
要求为真实工具参与、尚无构建/行为测试结果的贡献给出建议；未提供预期标签答案或本轮修正结论。
结果区分了原资料明确要求的 `Assisted-by: LLM sparse` 与固定主线不再强制该标签的情形，
两者均保留生成内容披露、人工认证和 AI 不加签约束；没有将工具使用说成检查通过，
没有拿当前快照提交冒充引入缺陷的 Fixes 提交，也未声称未读必读资料或未测行为已完成。
父级对照实际原文复核了这些结果；这是一个条件分支验收样本，不是普遍模型效果或性能提升的统计证明。

## 原始要求与完成边界

统一入口、C 为主/C 风格 C++ 禁库/Rust 边界、主动内存锁设计、旧工程入口归并、
references 分类与唯一维护责任，沿用已逐页复核的当前 20 个技能文件及
[工程迁移表](../engineering/INDEX.md)。本轮没有扩大或撤销用户要求。
coding-style 的 22 章主题责任和全文入口处理见
[来源读取复审](2026-10-30-systems-programming-source-reading-review.md)；其中核对的 `Documentation/process/coding-style.rst` 与本轮固定主线字节一致。
共同原则、环境机制和局部约定分别迁移，未来任务仍须核对真实目标版本、架构和配置。

[实体验收](2026-10-29-practical-skill-validation.md) 的两份缓存实现、KUnit 6/6、
队列普通/ASan-UBSan/TSan 与 C++ 调用、40 进程性能基线已在前轮重新核对冻结产物。
这些结果针对当时实现、原源码副本与配置；本轮为来源/政策修订，没有重复运行或冒称新官方快照已通过这些测试。
LSan 的 ptrace 限制、真实设备、其他架构及 RT 等未验证范围保持原结论。

本轮没有新增产品实现、专用语义校验器、PDCA 生命周期、宿主配置或外发操作。
测试/临时/缓存/日志只使用工作区，原五个保护文件的字节与 Git 索引另行核对。
元数据校验实际返回 `Skill is valid!`；20 个 Markdown 输入的 172 条限定本地链接均可解析，UI YAML 可解析。
本轮对暂存及工作区差异执行原生 `git diff --check`，最终退出状态与输出归档于 `W/logs/verification.json`。

工作区 W：`/home/black/skill-work/validation/engineering-consolidation/mainline-provenance-20261030-r6`。
精确范围在 `W/sources.json`；来源结果在 `W/logs/final-source-facts.json`，实际差异在 `W/logs/diffs/`；
独立验收的父级摘要在 `W/independent-policy-acceptance.md`，逐项需求审查在 `W/REQUIREMENTS-AUDIT.md`。
这些是证据位置，不是 skill 正常加载的依赖。

- Scope：限定三处技能文件与本报告；保留原 Linux 树及无关工作，不推送。
- Consistency：标签要求只有一处维护，版本来源优先级与按需读取没有变成全量加载。
- Adversarial：检查旧/新政策、标签/披露、人工认证、基础工具/分析工具、Fixes 身份及未运行证据的相反条件。
- Evidence：原生 Git 身份/对象、全文与差异、独立场景、旧运行证据各支持自己的结论，不相互替代。

本轮关闭已确认的来源和政策缺口。所有未来内核/用户态场景的正确性仍依赖实际设计、原文和针对性验证；
没有把有限复审解释为内嵌全部 Linux 文档、证明所有平台或保证 AI 每次产出最优方案。
