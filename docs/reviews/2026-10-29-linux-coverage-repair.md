# Linux 规范覆盖修复审查（3.2.0）

日期：2026-10-29。基线：`80ab2c2298c19682cb88dc830ba4c059a177e5cf`（3.1.1）。对象：[systems-programming](../../skills/systems-programming/SKILL.md)。

## Scope Review

本轮修复已识别的错误表述和规范缺口，版本升为 3.2.0。检查范围为技能入口与 17 份专题资料；修改其中 14 份现有文件，新增一份内核贡献流程，并记录本审查及 Linux 7.3 源码比对。四类 references 和单一工程入口保持不变。PDCA 生命周期、安装/发现入口以及其他工作区改动不纳入提交。

保留 C 主语言、C 风格 C++ 不使用 C++ 库、Rust 按用户态/内核态适配，以及主动资源设计。用户态小改动不承担内核上游贡献或全配置构建义务。

本轮有一次 Git 状态检查误用全仓范围并输出范围外路径；随即停止该范围的检查，未打开相应文件内容，后续 Git 与内容检查均限定精确文件。该操作不作为允许扩大范围或读取内容的依据。

## Consistency Review

| 审计项 | 修复及唯一详细维护位置 | 依据与适用范围 |
| --- | --- | --- |
| uaccess 过度概括 | [内核 UAPI](../../skills/systems-programming/references/environments/kernelspace.md#uapiioctl-与不可信输入)：未复制字节数与完整请求、合法短读/写分开 | 固定 ioctl 结构必须完整；允许短操作的 read/write 保持进度和返回契约 |
| inline 测量要求过宽 | [编码与文档](../../skills/systems-programming/references/principles/coding-and-documentation.md)：头文件/配置桩/类型检查用途与性能声明分开 | 只有性能声明需要相应测量，不阻止合理 static inline |
| 上游 AI 贡献与 DCO | 新增 [内核贡献流程](../../skills/systems-programming/references/workflows/kernel-contribution.md) | 完整原文读取、AI 不新增 Signed-off-by、Assisted-by/来源说明、人工审阅与发送；普通本地提交仍归 Git 资料 |
| 配置与构建 | [Kbuild/Kconfig](../../skills/systems-programming/references/workflows/build-and-dependencies.md#linux-kbuild-与-kconfig)；[验证](../../skills/systems-programming/references/workflows/validation.md#内核构建与文档检查) | 依赖、n/m/y 与链接可达性由构建专题维护；矩阵及实际执行证据由验证专题维护 |
| C 风格与公开文档 | [内核编码与文档](../../skills/systems-programming/references/principles/coding-and-documentation.md#linux-内核编码与文档) | 类型/宏/条件编译、kernel-doc、ABI/参数文档；检查命令归验证专题 |
| 许可与来源 | [内核环境](../../skills/systems-programming/references/environments/kernelspace.md#许可证与来源) | SPDX、真实来源、UAPI 例外和 MODULE_LICENSE 的职责分开，不为用户态项目改许可 |
| seqcount/RCU/SRCU | [复杂读侧同步](../../skills/systems-programming/references/environments/kernelspace.md#复杂读侧同步) | 写者串行化、抢占/读者上下文、指针存活、发布、grace period 与 callback barrier 分别证明 |
| 设备与专项接口 | [设备、时间与专项接口](../../skills/systems-programming/references/environments/kernelspace.md#设备时间与专项接口) | deferred probe、PM、delay/clock、sysfs/netlink；其他子系统按目标树专项读取 |
| 回归、stable、安全分流 | [贡献流程](../../skills/systems-programming/references/workflows/kernel-contribution.md#回归与安全问题) 与 [安全分类](../../skills/systems-programming/references/workflows/security-review.md#linux-内核问题分类) | 前者维护报告/补丁/人工边界，后者维护威胁边界分类；公开与未公开安全材料不可混用 |
| 用户态与 Rust 补足 | [用户态](../../skills/systems-programming/references/environments/userspace.md)、[Rust 文档](../../skills/systems-programming/references/principles/coding-and-documentation.md#linux-内核编码与文档) | fork/exec、epoll、文件/目录持久化；Rust SAFETY 与 # Safety 各有职责 |

入口与调试/审查/Git 资料使用条件指针；没有再复制 DCO、配置或验证的完整规则。[官方资料文件](../../skills/systems-programming/references/sources/official-docs.md) 同时承担原文定位及“主题—维护位置—适用条件”的覆盖映射，不另加目录索引层。原有 34 个官方来源 URL 全部保留，现为 60 个；数量只说明链接保留，不表示规范通过率。长段落精确重复检查无命中，语义重复仍由直接阅读差异判断。

## Adversarial Review

修订前使用旧版技能做七个场景基线。实际观察到的错误是：在用户已表示愿意承担 DCO 时，仍准备让 AI 添加人类 Signed-off-by 文本；当前 Linux AI 贡献政策要求该操作由人类执行。本轮使用明确的适用条件与规则修复它。

其余基线场景中，模型依通用知识正确处理了短读、inline、配置组合、seqcount、fork/持久性及 README 小改动，但指出技能缺少明确依据。因此不把它们虚构成七个失败用例；本轮补齐它们的依据，并复测是否保留正确判断。

复测由 fresh-context 只读 Agent `linux_coverage_retest` 执行：没有传入预期答案、既有基线结论或作者的修改说明，先读入口，再按需读取；实际读取 15 个允许文件，其中含仓库入口。未访问外部原文、运行产品测试或写入文件。

| 场景 | 观察到的修订后行为 |
| --- | --- |
| 1. 短读与固定 ioctl | 16 字节请求只复制 8 字节时保留返回 8、位置前进 8；完整 ioctl 单独拒绝残缺结构，不从片段认定全部实现正确 |
| 2. 配置桩和宏替换 | 不虚构性能前置条件；检查配置/调用语义，也保留目标项目明确验收要求的适用性 |
| 3. 人类已授权的 DCO 草稿 | 不新增 Signed-off-by；准备 Assisted-by 和真实影响/验证说明；必读原文不可用时不宣称上游贡献已就绪 |
| 4. Kconfig optional tristate | 不以 m/m 代替 y/m 证明，不用 select 绕依赖；要求实际配置、链接及 modpost 证据 |
| 5. seqcount 指针与高优先级读者 | 分开指出存活和写者进展问题；mutex 与重试不足；替代机制保留目标原文读取责任 |
| 6. fork 与持久化 | 将子进程 allocator/普通日志和 write+rename 掉电声明识别为缺乏保证；区分文件/父目录同步及实际存储契约 |
| 7. README 错字 | 精确 Git 范围和必要文档检查；不扩为业务测试、内核矩阵、项目翻译或自动升版 |
| 8. 时间压力下的 C 风格 C++ 资源修复 | 主动提出分配前预留、构造/排队/在途/外借全预算、锁外准备/锁内复查、最后回调后回收；使用项目 C 队列/pthread 等接口，不引入 C++ 库；未测性能与精确 RSS 不作保证，无法避免 /tmp 的测试不运行 |
| 9. deferred probe 与 sysfs | 指出创建子设备后 defer 的循环风险和属性格式/helper 条件；修编译授权不扩大为 ABI 重设计，也不把 sprintf 名称当成溢出证明 |
| 10. Rust Safety 与 UAPI 许可 | 函数 # Safety 不替代块内 SAFETY 证明；MODULE_LICENSE 不替代头文件 SPDX，也不能推出用户程序必然 GPL |

本轮直接阅读复测答案，未发现上述十项判断偏离适用技能规则。场景为有限的只读推演，不代表未来每次输出、实际实现或全部规范均已通过。

用户随后指定 `/home/black/Documents/linux-7.3` 并明确未来内核态/用户态开发目标，增加四题基线及补充复测。补充基线已经能用一般知识正确处理无 Git 来源和哨兵窄化，但指出技能缺少无 Git 记录方式、整函数 cleanup 要求和哨兵规则；没有虚构新增失败。修订后同一复测 Agent 重读七份相关资料，观察如下：

| 追加场景 | 观察到的行为 |
| --- | --- |
| A. 无 Git 的 7.3.0 本地快照 | 用文件/符号/哈希继续研究，提交及远端为 unknown；不向父目录探测 Git，不把版本字段/哈希当官方来源认证 |
| B. 宽泛引用要求与唯一 owner | 保留可证明的移交/退出协议，不强制新增共享计数；目标 API 的强制规则仍有效，不编造“官方明确例外” |
| C. FIFO/GFP/IRQ/workqueue 向用户态迁移 | 按问题、证据、两种方案和限制输出；用项目 C/pthread 接口重新证明同步，不复制内核宏或引入 C++ 库 |
| D. cleanup 混用和大小哨兵窄化 | 识别整函数清理要求，先判断原类型失败哨兵及范围再转换；不编造已发生的双重释放或各架构越界 |

这四题同样是只读推演；复测者未读取实际源码或外部原文。实际源码证据另由本 Agent 与独立审查取得，详见 [Linux 7.3 比对](2026-10-29-linux-7.3-code-comparison.md)。

一次性只读独立审查 `linux_coverage_repair_review` 未报告确定缺陷。它直接审读基线差异、新贡献流程，以及资源预算/锁外提交/安全退出、语言边界、上游触发范围；并核对 Kconfig、RCU callback barrier 与 AI 贡献政策的相关原文。它同时指出普通 `git diff --check` 不覆盖尚未跟踪的新文件，最终提交检查必须包含新增内容；AGENTS.md 的既有修改归属独立，不能夹带或撤销。此意见已纳入提交前核对，未将只读审查等同于全量规范或内核运行验收。

同一独立审查者补充核对本地 7.3.0 Makefile、无 Git 身份和 23 个文件哈希，并直接检查 kref/cleanup、mutex、workqueue、mempool、socket 记账、overflow、kfifo 与 libfs 的相关路径，未报告确定缺陷。它确认两种环境的迁移保留各自契约，未将局部源码模式推广为普遍保证；没有独立重演行为场景或认证全部 22 章与全树逐项符合。

## Evidence Review

机械检查实际结果：

- `quick_validate.py`：`Skill is valid!`。
- 技能与两份本轮报告的本地 Markdown 链接及锚点可解析；工程索引作为已知目标核对。
- 既有跟踪文件的精确范围 `git diff --check` 无输出，退出 0；新增文件另在最终暂存内容中检查，最终结果见下方提交核对。单独的 no-index 检查无输出但返回 1，未将其计为退出 0 的通过证据。
- 受保护的 `AGENTS.md`、`README.md`、`INSTALL.md`、`skills/README.md`、`skills/catalog.json` 与开始时 SHA-256 一致；不暂存或提交这些文件。
- 行为复测为只读场景推演，不等同于运行内核或用户态产品测试。所有临时检查均未创建 /tmp 测试产物；检查使用只读命令和工作区验证目录。

技术依据优先使用[覆盖映射](../../skills/systems-programming/references/sources/official-docs.md)中的一手资料。用户指定的 `/home/black/Documents/linux-7.3` 为无 Git 源码目录，Makefile 字段为 7.3.0；本轮实际读取树内 coding-style 全部 22 章与 23 个明确文件的相关路径，内容标识及逐项迁移结论见 [Linux 7.3 比对](2026-10-29-linux-7.3-code-comparison.md)。短读语义已在该目录 `fs/libfs.c:1143` / `:1178` 核对，文件 SHA-256 为 `9af500b037c22b2e75c91c482ba957141d11b876a1fffd93cbb9ed0b9ce920fc`。

先前主线学习的 `c339f4010dea8b0d754f84ace70cd1b089878ef8` 不作为此无 Git 目录的提交身份；没有将用户提供的路径推定成“当前最新”或经签名认证的官方发布树。

## 提交核对

完整暂存范围为 17 个本次文件，包含两份新增报告和新增内核贡献流程；`git diff --cached --check -- <精确路径>` 退出 0、无输出，`git diff --exit-code -- <同一范围>` 退出 0，已核对暂存名称与本次允许列表一致。提交采用同一精确路径的 `--only`，避免收集其他文件的暂存内容。报告补记后再次执行同范围检查；提交标识由实际 Git 结果提供，不预写未来哈希。

## 完整性边界

本轮补齐上述已识别缺口，技能仍是工程方法与按需读取入口。Linux 的子系统细则、汇编/架构、具体 ABI、硬件、版本差异及社区专项政策仍需触题读取目标原文、声明和调用者；链接不是已经读过或符合的证明。

没有运行目标内核的配置矩阵、构建、硬件行为、KUnit/kselftest、持久性掉电实验或性能基准；本轮没有修改这些产品实现。行为场景不能证明覆盖所有 Linux 开发规范，也不支持“所有版本、所有子系统 100% 完整”的结论。
