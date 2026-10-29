---
name: systems-programming
description: Use when designing, implementing, debugging, auditing, testing, reviewing, building, documenting, or preparing authorized Git commits for software, especially C, C-style C++ without C++ libraries, Rust, or Linux userspace/kernel code. 软件工程统一入口。
metadata:
  version: 3.1.0
---

# 系统编程与软件工程

统一承载本包的工程规范和任务方法。以 Linux 内核的资源纪律、并发设计、可维护性、兼容性和可验证性为基础，覆盖设计、实现、调试、安全、测试、审查、构建、文档及提交；详细内容按实际任务读取参考文件。

## 适用边界

- 主语言为 C。C++ 按 C 风格使用，**不使用 C++ 库**：不引入 STL、`std::`、iostream、智能指针或基于库的 RAII，采用 C 接口、显式所有权和成对释放；不主动引入类层次、模板、异常或 RTTI。
- Rust 按目标环境选择抽象：用户态遵守项目库与工具链约定，内核态使用目标树支持的 `no_std`/kernel 接口。Go、Python 及其他项目沿用共同工程方法，具体 API、框架与错误约定按相应环境核对。
- 用户及目标项目约束优先。已有项目中的库或其他语言风格不构成全仓迁移授权；本次新增代码遵守已确定的配置，不为满足通用规范重写无关实现。
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
| 设计、实现与正确性分析 | [共同工程原则](references/principles/engineering.md)；源码及接口文档按 [编码与文档](references/principles/coding-and-documentation.md) |
| 分配、缓冲、异步对象、共享状态或同步路径 | [内存与锁设计](references/principles/memory-and-locks.md)，落实下方主动设计要求 |
| C/C++/Rust 用户态、进程、线程、I/O 或 FFI | [用户态适配](references/environments/userspace.md) |
| 内核、驱动、IRQ、DMA、workqueue 或 Rust for Linux | [内核态约束](references/environments/kernelspace.md)；跨用户/内核边界同时核对用户态契约 |
| 实际故障、构建失败、测试失败或异常行为 | [根因调查](references/workflows/debugging.md) |
| 安全审计、安全关键边界或漏洞修复 | [安全边界](references/workflows/security-review.md)；普通功能不因此自动展开全量审计 |
| 测试体系、框架或覆盖规划 | [测试策略](references/workflows/testing-strategy.md)；需要测试先行方法时读 [TDD](references/workflows/test-driven-development.md) |
| 当前改动的检查、回归、故障注入或基准 | [改动验证](references/workflows/validation.md)，不自动重建完整测试体系 |
| diff/PR 或明确的代码审查任务 | [代码审查](references/workflows/code-review.md)，再读取实际风险对应的领域资料 |
| 构建、依赖、工具链或交叉编译配置 | [构建与依赖](references/workflows/build-and-dependencies.md) |
| 普通注释、接口文档或技术说明 | [编码与文档](references/principles/coding-and-documentation.md)；仅明确采用中文项目或专门中文补注时读 [项目约定](references/principles/project-conventions.md) |
| 准备或执行已授权 Git 提交 | [提交与变更说明](references/workflows/git-commit.md) |
| 查询官方依据、版本差异或学习本地主线写法 | [官方资料索引](references/sources/official-docs.md) 与按需 [源码/规范比对](references/sources/mainline-reading.md) |

只读取当前任务需要的资料。普通开发直接承担相关设计、必要注释、构建约束和验证，不要求用户额外调用其他工程技能；README 错字等低风险修改不扩展为业务测试、审计或项目翻译。

## 核心决策

1. 复用已有子系统和项目抽象；先说明契约、状态不变量及退出协议，再选择结构与原语。
2. 失败和部分成功属于接口：明确剩余所有权、回滚、副作用、重试截止时间及幂等性。
3. 内存可见性、共享状态一致性与对象存活分别证明；`volatile`、引用计数或单个原子变量不是完整并发协议。
4. 外部 API/ABI、数据格式、错误和可观察行为需要兼容依据；内部实现可以演进。
5. 性能优化依据代表性测量；不凭“内核也这样写”加入池化、RCU、无锁结构或零拷贝。保留简单方案时说明其满足条件的原因。
6. 工程方法服从本次风险和环境，不强加测试比例、覆盖率目标、假设数量、全量清单、语言迁移或每次提交升版。

## 主动资源设计

设计、实现或审查触及上述内存/并发路径时，主动选择本次范围内更合适的资源和同步方案，无需等待用户点名“优化内存/锁”。实现可证明的生命周期、资源上界及一致性改进；纯性能候选给出测量方法，不虚构收益。只读审查提出结论，不自行修改业务代码。

| 设计项 | 必须讲清的决定 |
| --- | --- |
| 内存 | 谁拥有、何时转移和释放；分配/复制是否必要；预算覆盖构造、排队、在途、外借及缓存；失败和取消如何收敛 |
| 锁 | 哪份状态由谁保护；锁类型、上下文、范围及顺序；锁外操作的存活和提交一致性；停止、等待及最后回调如何结束 |
| 取舍与验证 | 采用或保留何种方案及原因；针对性反例与交错；需测量才能决定的优化和指标 |

保留原方案也是有效决定；范围外重构作为独立建议，不把主动设计扩展成全仓重写。

## 交付与证据

按任务规模说明实际行为或发现、相关设计决定、关键契约、实际验证和未覆盖项。发现给出位置、触发条件及影响；性能结论给出条件、基线和数据。静态推断、拟运行、未运行与实际通过分别表述。

编写或运行测试前确认全部临时文件、日志、缓存和构建产物能写入工作区，**不向 `/tmp` 创建或写入测试产物**。无法重定向的测试不运行并说明原因；仅设置 TMPDIR 不代表所有子工具都遵守。保护凭证与个人信息，不输出完整环境或无关敏感数据。

本包其他工程入口已收敛于此，迁移位置见 [工程资料索引](../../docs/engineering/INDEX.md)。PDCA 阶段与场景仍是独立任务流程，不由本技能自动启动。
