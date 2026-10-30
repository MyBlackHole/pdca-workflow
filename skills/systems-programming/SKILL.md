---
name: systems-programming
description: Use when designing, implementing, debugging, auditing, testing, reviewing, building, documenting, or preparing authorized Git commits for software, especially C, C-style C++ without C++ libraries, Rust, or Linux userspace/kernel code. 软件工程统一入口。
metadata:
  version: 3.5.0
---

# 系统编程与软件工程

统一承载本包的工程规范和任务方法。以 Linux 内核长期生产验证的资源纪律、并发设计、可维护性、兼容性和可验证性为基线，覆盖设计、实现、调试、安全、测试、审查、构建、文档及提交。对本用户请求覆盖范围内的新增与修改代码，本技能适用的规范是必须遵守的工程要求，不是可选建议；详细要求按任务读取参考文件。

把内核规范中可迁移的工程经验用于未来内核态和用户态开发：共同的所有权、内存预算、并发、失败、兼容与生命周期要求必须落实到两种环境；具体 API、执行上下文、ABI、子系统和贡献流程必须按目标环境及目标树采用。C 与 C 风格 C++ 的代码风格默认遵守本技能归纳的 Linux 内核风格；用户态只迁移适用的语言风格和工程约束，不能调用内核专属 API。源码学习按 [规范与实现比对](references/sources/mainline-reading.md) 区分共同原则和局部约定。

## 适用边界

- 主语言为 C。C++ 按 C 风格使用，**不使用 C++ 库**：不引入 STL、`std::`、iostream、智能指针或基于库的 RAII，采用 C 接口、显式所有权和成对释放；不主动引入类层次、模板、异常或 RTTI。
- Rust 按目标环境选择抽象：用户态遵守项目库与工具链约定，内核态使用目标树支持的 `no_std`/kernel 接口。Go、Python 及其他项目沿用共同工程方法，具体 API、框架与错误约定按相应环境核对。
- 用户及目标项目约束优先。已有项目中的库或其他语言风格不构成全仓迁移授权；本次新增代码遵守已确定的配置，不为满足通用规范重写无关实现。
- 对新代码必须执行本技能适用的规范。若目标项目、ABI、工具链或上游原文存在明确冲突，必须指出具体冲突，按更具体且获准的目标约束实现，并记录未满足的通用规则及原因；不得默默跳过或把所有规则降为“建议”。
- Linux API 资料聚焦目标源码树、版本、架构和配置；其他平台迁移原则后另核对平台契约。不将最新文档或单个主线实例当成所有版本的保证。
- 只修改获准对象；保留其他人的工作。用户已授权的必要设计、实现与验证连续推进，不重复请求例行确认；提交、推送、外部发送及生产变更仍需要对应授权。

## 资料分类

- `references/principles/`：共同工程约束、资源设计、编码文档与可选项目约定。
- `references/workflows/`：调试、安全、测试、验证、审查、构建与提交的任务方法。
- `references/environments/`：用户态/内核态执行环境、API 和上下文限制。
- `references/sources/`：官方依据定位、本地主线阅读与版本比对方法。

分类说明资料职责，不代表整个目录都要读取。按下面任务直接定位文件，再补本次相关的原则和环境约束。

## 按任务读取

先从获准的需求、构建入口、调用者和邻近代码确认环境、接口、执行上下文、生命周期及验证条件。只询问现有资料无法确定且会影响正确性的事项；其他独立工作继续推进。

| 当前任务或风险 | 读取资料 |
| --- | --- |
| 任意新增或修改代码；设计、实现与正确性分析 | [共同工程原则](references/principles/engineering.md) 与 [编码与文档](references/principles/coding-and-documentation.md)；C/C 风格 C++ 必须遵守其中的默认风格，内核代码还须读取 [内核态约束](references/environments/kernelspace.md) |
| 分配、缓冲、异步对象、共享状态或同步路径 | [内存与锁设计](references/principles/memory-and-locks.md)，落实下方主动设计要求 |
| 容器、索引/句柄、数据表示、字符串缓冲或回调接口 | [数据结构与接口](references/principles/data-and-interfaces.md)，再按实际环境核对 API |
| C/C++/Rust 用户态、进程、线程、I/O 或 FFI | [用户态适配](references/environments/userspace.md) |
| 内核、驱动、IRQ、DMA、workqueue 或 Rust for Linux | [内核态约束](references/environments/kernelspace.md)；跨用户/内核边界同时核对用户态契约 |
| Linux 上游贡献、补丁准备，或明确要求遵循上游 AI 贡献规范 | [内核贡献流程](references/workflows/kernel-contribution.md)，先落实其完整原文读取和人工提交要求 |
| 实际故障、构建失败、测试失败或异常行为 | [根因调查](references/workflows/debugging.md) |
| 安全审计、安全关键边界或漏洞修复 | [安全边界](references/workflows/security-review.md)；普通功能不因此自动展开全量审计 |
| 测试体系、框架、覆盖规划或断言/替身设计 | [测试策略](references/workflows/testing-strategy.md)，单项测试只读相关小节 |
| 测试先行或回归循环 | [TDD](references/workflows/test-driven-development.md) |
| 当前改动的检查、回归、故障注入或基准 | [改动验证](references/workflows/validation.md)，不自动重建完整测试体系 |
| diff/PR 或明确的代码审查任务 | [代码审查](references/workflows/code-review.md)，再读取实际风险对应的领域资料 |
| 构建、依赖、工具链或交叉编译配置 | [构建与依赖](references/workflows/build-and-dependencies.md) |
| 普通注释、接口文档或技术说明 | [编码与文档](references/principles/coding-and-documentation.md)；仅明确采用中文项目或专门中文补注时读 [项目约定](references/principles/project-conventions.md) |
| 准备或执行已授权 Git 提交 | [提交与变更说明](references/workflows/git-commit.md) |
| 查询官方依据、版本差异或学习本地主线写法 | [官方资料索引](references/sources/official-docs.md) 与按需 [源码/规范比对](references/sources/mainline-reading.md) |

只读取当前任务需要的资料；Linux 贡献流程明确要求完整读取的原文不能用本技能摘要替代。普通开发直接承担相关设计、必要注释、构建约束和验证；README 错字等低风险修改不扩展为业务测试、审计或项目翻译。Linux 专项的官方依据、适用条件和维护位置见 [覆盖映射](references/sources/official-docs.md)。

## 核心决策

1. 复用已有子系统和项目抽象；先说明契约、状态不变量及退出协议，再选择结构与原语。
2. 失败和部分成功属于接口：明确剩余所有权、回滚、副作用、重试截止时间及幂等性。
3. 内存可见性、共享状态一致性与对象存活分别证明；`volatile`、引用计数或单个原子变量不是完整并发协议。
4. 外部 API/ABI、数据格式、错误和可观察行为需要兼容依据；内部实现可以演进。
5. 性能优化依据代表性测量；不凭“内核也这样写”加入池化、RCU、无锁结构或零拷贝。保留简单方案时说明其满足条件的原因。
6. 工程方法服从本次风险和环境；目标项目或上游明确要求的检查按其条件执行，其余不统一强加测试比例、覆盖率目标、假设数量、全量清单、语言迁移或每次提交升版。

## 必须执行的资源与同步设计

设计、实现或审查触及内存、缓冲、异步对象、共享状态或同步路径时，AI 必须主动分析并确定本次范围内合适的资源和同步方案，无需等待用户点名“优化内存/锁”。必须检查所有权与释放、分配/复制、资源上界、锁的保护对象与上下文、锁外操作的存活和提交一致性，以及停止/取消时所有生产者和在途执行者如何收敛。实现可证明的生命周期、资源上界及一致性改进；只读审查必须给出具体证据和结论，不自行修改业务代码。纯性能候选给出可复现的测量方法，不虚构收益。

| 设计项 | 必须讲清的决定 |
| --- | --- |
| 内存 | 谁拥有、何时转移和释放；分配/复制是否必要；预算覆盖构造、排队、在途、外借及缓存；失败和取消如何收敛 |
| 锁 | 哪份状态由谁保护；锁类型、上下文、范围及顺序；锁外操作的存活和提交一致性；停止、等待及最后回调如何结束 |
| 取舍与验证 | 采用或保留何种方案及原因；针对性反例与交错；需测量才能决定的优化和指标 |

保留原方案也是有效决定；范围外重构作为独立建议，不把主动设计扩展成全仓重写。

## 交付与证据

按任务规模说明实际行为或发现、相关设计决定、关键契约、实际验证和未覆盖项。发现给出位置、触发条件及影响；性能结论给出条件、基线和数据。静态推断、拟运行、未运行与实际通过分别表述。

测试产物只写工作区，**禁止向 `/tmp` 创建或写入测试文件、临时目录、日志、构建产物或缓存**；运行前按 [输出目录约束](references/workflows/validation.md#输出目录约束) 核对子工具及受限情况。保护凭证与个人信息，不输出完整环境或无关敏感数据。

本包其他工程入口已收敛于此，迁移位置见 [工程资料索引](../../docs/engineering/INDEX.md)。PDCA 阶段与场景仍是独立任务流程，不由本技能自动启动。
