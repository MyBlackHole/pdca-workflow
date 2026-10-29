# systems-programming 来源读取复审：3.4.0 → 3.4.1

日期：2026-10-30，Asia/Shanghai。基线为 `4145cc889bf28e983866310cc0ccf0eb711159d4`。
本轮修改入口版本和一处来源说明；测试代码仍在仓库 tests/，没有进入 skill。

## 已修正的缺口

本地 `Documentation/process/development-process.rst` 是引言与 toctree 导航，
正文在 `1.Intro.rst` 至 `8.Conclusion.rst` 八个文件中，共 2267 行。
本轮按这八个精确路径读完正文，未沿其中链接递归读取其他资料。
[官方目录](https://docs.kernel.org/process/development-process.html) 有九个顶层标题，
因为最后一个正文文件同时含 “For more information” 与 “Conclusion”；标题数不能当作文件数。

3.4.0 的来源说明仅点明 kernel-doc/include，未明确目录页及 toctree。
现在由唯一维护位置 [源码与规范比对](../../skills/systems-programming/references/sources/mainline-reading.md#每条结论的证据链)
统一说明：先固定正文精确路径，再按授权范围读取；要求全文时覆盖全文，普通查询仍按需。
受限正文明确列为未核对，不因目录或引用自动扩大访问。
[内核贡献流程](../../skills/systems-programming/references/workflows/kernel-contribution.md#固定对象与必读原文)
继续引用此方法，没有复制第二份规则。

这是已存在全文读取要求的参考澄清。没有基线模型失败，未声称本轮证明了模型行为改善；
也没有为低影响文档修订新建运行案例或重复编译旧案例。

## 原文核对

本轮完整读取本地 submitting-patches、threat-model、coding-assistants 与 generated-content。
在线提交指南和 threat model 的正文分段读取至末尾；没有把检索工具返回的总行数当成全文证据。
结合上一轮已读 AI/生成内容、安全与 stable 政策，未发现当前贡献资料中的人工 DCO、
辅助归属、真实验证披露、人工发送及按当前原文分流等要求存在矛盾。
这些政策只在相应 Linux 贡献任务触发；本轮没有对外发送材料。

对 [官方 coding style](https://docs.kernel.org/process/coding-style.html) 补齐此前未读的在线后半段，
现已覆盖 22 章正文。本地同名文件仍为前轮逐章读取的内容，SHA-256 为
`332454d2ab9a0462dd9f292c52291cf3b5e1afcd638aa06df15f557c47a126f5`。
当前责任核对如下，表中指的是规则维护或使用时读取责任，不是逐句内嵌原文：

| coding-style 章节 | 当前落点与迁移边界 |
| --- | --- |
| 1–6：缩进、行宽、大括号/空格、命名、typedef、函数/原型 | 编码与文档；目标内核完整细则按树内原文，用户态保留既有风格与语言语义 |
| 7：集中退出 | 内存与锁的取得/移交/逆序回收；内核 cleanup helpers 另按目标契约，不要求所有项目改用相同宏 |
| 8–9：注释、格式工具 | 编码与文档；保留必要契约，避免模板注释、无关重排及把编辑器示例变成配置修改授权 |
| 10：Kconfig | 构建与依赖；配置的缩进、依赖与 n/m/y 可达性按目标树，不照搬 C 排版 |
| 11、14：数据结构与分配 | 数据与接口、内存与锁、内核环境；分别证明存活、同步、额度及进展，不向用户态逐行复制内核 API |
| 12、15、18：宏/enum、inline、已有 helper | 编码与文档；区分类型检查、配置桩与性能优化，不机械采用内联行数门槛 |
| 13、22：日志与避免内核崩溃 | 内核环境；普通输入错误走错误路径，内部违约诊断按实际契约，考虑日志及 panic_on_warn 的影响 |
| 16–17：返回值与 bool | 编码与文档、数据与接口、环境资料；状态、谓词、实际结果和外部布局分别核对 |
| 19–21：modeline、汇编、条件编译 | 编码与文档、构建与依赖；汇编等完整细则在采用时读原文，不能凭摘要声称全文符合 |

原目录 `/home/black/Documents/linux-7.3` 没有可核验的 Git 来源，Makefile 仍标为 7.3.0。
远端、完整提交、是否原版及“最新主线”身份保持 unknown；文件名和哈希不认证这些事实。
本轮所读十三个流程文档的前后哈希一致，没有修改原 Linux 树。

## 对原始要求的复核

直接复读当前入口、全部 18 个 references、UI 元数据和迁移索引。
按实际契约检查内存/锁、数据/接口、环境适配、编码文档、调试、安全、测试/TDD、
验证、审查、构建、提交和来源定位；没有发现需要进一步拆分或归并的实质重复。

| 用户要求 | 当前证据与结论 |
| --- | --- |
| systems-programming 名称、位置及统一工程入口 | 位于 skills/systems-programming；[迁移表](../engineering/INDEX.md) 指向唯一资料位置，已知十个旧入口及中间 git-commit 入口的 SKILL.md 不再作为 tracked 入口存在 |
| C 为主，C 风格 C++ 禁用 C++ 库，兼顾 Rust | 入口及用户态、内核态、构建、测试和审查资料一致；Rust 的环境库选择不受 C++ 禁库要求影响 |
| 归纳 Linux 规范应用于未来内核与用户态 | 共同原则、环境机制和内核局部约定有明确迁移边界；官方来源按主题定位，完整原文不能由摘要替代 |
| AI 主动设计内存与锁 | 入口有触发条件、必需设计决定；详细资料覆盖所有权、预算、提交一致性和退出，保留简单方案的适用条件 |
| 能力有行为证据 | [实体验收](2026-10-29-practical-skill-validation.md) 的冻结源码、共同接口日志、KUnit 日志及基准摘要重新核对，哈希与报告一致；有限样本不代表普遍模型能力 |
| 既有具体缺口已修订 | [3.4.0 复审](2026-10-30-systems-programming-completeness-review.md) 的等待/I/O 探针和新增满额条件日志仍匹配原结论；没有把新增业务条件反写为旧题失败 |
| skill 保持规范而非固定业务实现 | 当前 tracked skill 文件是 Markdown 与 YAML；可运行验收资产在 tests/systems-programming/practical，正常加载不读取或执行它们 |

原有运行证据仍限于当时的源码与配置：两份版本缓存通过相同公共接口检查；
用户态队列普通、ASan/UBSan、TSan 各通过 11 组自测与 C++ 调用；KUnit 为 6/6。
LSan 的 ptrace 限制、真实设备/其他架构/RT 等未验证范围保留，未改写为通过。
本轮没有重跑这些实现，也没有将它们称为 3.4.1 的新增运行结果。

## 本轮校验与直接审查

工作区 W：`/home/black/skill-work/validation/engineering-consolidation/source-reading-20261030-r5`。
来源/技能哈希、保护文件及索引事实在 `W/logs/before.json`、`after.json`、`change-facts.json`。
元数据校验实际返回 `Skill is valid!`，只证明前置元数据有效。
20 个 Markdown 输入共取得 172 条本地链接，限定范围内的文件/标题锚点均可解析，UI YAML 可解析。
首次通用采集因正则转义错误返回 0 条，未作为通过证据；保留 `link-facts-initial.json`，
修正后人工核对实际链接样本，完整事实在 `link-facts.json`。diff 检查以最终输出为准，提交标识以 Git 历史为准。

- Scope：只修一处来源说明、版本和本报告，不创建业务 PDCA、不修改宿主配置、不推送。
- Consistency：来源说明是唯一维护位置；普通按需读取与上游特定全文要求各按条件适用。
- Adversarial：检查目录/正文混淆、章节标题/文件数混淆、受限正文、普通局部查询，未引入任意链接递归权限。
- Evidence：本地正文、官方页面、通用事实检查、旧运行日志分别支持相应结论；没有用导航、哈希或成功测试替代其他证明。

这次复核关闭了已确认的来源读取歧义。全量 Linux 文档、所有子系统和未来场景不能由一份摘要或有限测试证明完整；
它们的任务触发读取与验证责任仍由官方索引、来源方法和环境资料明确承担。
