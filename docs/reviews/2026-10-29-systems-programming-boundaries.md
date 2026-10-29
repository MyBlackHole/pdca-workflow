# 系统编程技能命名与职责边界审查

日期：2026-10-29。修改前基线：`1c610e6`。用户确认使用 `systems-programming`，并要求检查与 `secure-coding` 等工程技能的重合。本文记录本次维护审查，不创建正式 PDCA task。

## Scope Review

- 将 `skills/linux-kernel-engineering/` 改为 `skills/systems-programming/`，同步目录、frontmatter、标题与 UI 名称。调用标识发生变化，独立版本由 1.2.0 升至 2.0.0；手动调用改用 `$systems-programming`。不保留第二个可发现的旧名入口，避免两个技能同时匹配同一任务。
- 修改三个相邻参考技能的适用范围和直接冲突条目：`secure-coding`、`code-review-checklist`、`build-config`，各自从 5.0.0-rc.2 升至 5.0.0-rc.3。`testing-strategy` 的描述已经限定为策略、框架或覆盖审查，不需要为统一外观修改。
- 维护范围为系统资源设计及相邻技能的配合，不是对安全技能全部历史示例、所有语言或所有技能的完整审计。使用精确文件 allowlist，未访问或枚举 `records/`。
- `skills/catalog.json` 未改变；工程参考技能不增加运行时入口。现有 `skills/README.md` 的用户修改未纳入本次改动。历史审查和主线来源清单保留旧名称作为当时基线，未批量改写历史证据。

## Consistency Review

命名应表达任务职责。旧名容易使用户把技能理解为内核专用规则；新名覆盖用户态/内核态的资源与接口设计，Linux 内核仍是方法和平台资料的主要来源。其他平台只迁移原则，平台 API 需另行核对。

| 技能 | 主责 | 组合边界 |
| --- | --- | --- |
| systems-programming | 所有权、内存预算、锁协议、异步退出、ABI/UAPI 与领域验证 | 资源设计任务直接使用；不因使用 C/Rust 就加载全部工程技能 |
| secure-coding | 信任边界、权限、恶意输入、注入、敏感数据与漏洞触发 | 安全关键系统接口同时核对资源不变量；普通队列设计不自动变成完整安全审计 |
| code-review-checklist | diff/PR 通用审查流程、覆盖维度与问题表达 | 具体资源语义由 systems-programming 补充；专项安全审计不自动叠加通用 PR 流程 |
| testing-strategy | 框架、覆盖规划与完整测试策略 | 系统技能保留并发交错、资源耗尽、取消及 ABI 的针对性检查，不复制完整策略 |
| build-config | 构建、依赖、工具链和运行器 | 现有 CMake、语言模式和依赖限制优先，示例不构成迁移或加库授权 |

边界检查、失败回滚、对象存活在系统设计中不可省略，因此保留必要交集。减少的是互相抢占任务、重复展开完整流程，以及把语言示例提升为全局规则。

C 风格 C++ 禁用 C++ 库的配置，在本技能及三个配合入口均有明确约束。安全/通用审查技能仍可服务允许 STL 的其他项目；未使用的模板、异常等条目标记不适用，不要求为清单引入设施。内核及 `no_std` Rust 使用目标树接口，不要求用户态 `std::error::Error`。

## Adversarial Review

修改前独立行为基线读取旧系统技能及四个相邻入口，覆盖六项：C 队列设计、Python 安全专项、禁库 C++ PR、Go/Python 测试策略、既有 CMake 修复、内核 ioctl。基线没有出现引入禁用库或错误改用系统技能的行为；不能声称本次修订“修好了六个行为失败”。但安全专项仍搭配了通用审查技能，文本尚未明确限制该组合。

追加静态反例基线确认了三处文本风险，独立回答本身均作出正确判断：

1. 原安全示例和 C 审查项把 `free(ptr); ptr = NULL;` 视为 UAF 防护，缺少别名及异步使用者前提。修订后要求完整存活/回收协议；置空只使当前持有位置失效。
2. 原 Rust “安全”示例仅检查非空和对齐，无法证明已释放对象可访问。改为有效借用示例，并要求真实裸指针操作的完整安全契约；同时修正“unsafe 绕过所有安全保证”的说法。依据 [Rust 指针 Safety](https://doc.rust-lang.org/std/ptr/index.html#safety)、[Rust Reference：unsafe](https://doc.rust-lang.org/reference/unsafe-keyword.html) 与 [The Rust Programming Language：Unsafe Rust](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html)。
3. 原 C++ 智能指针、`std::mutex` 和 Rust 用户态错误类型条目未限定环境。现在先应用项目配置，再选择适用条目；普通现代 C++ 项目不会因此被全局禁止使用库。

独立复测先读取五个入口，再按场景读取允许的系统参考资料，共只读十个文件。八个场景均得到与职责和项目约束一致的决定：

| 复测场景 | 实际决定与关键输出 |
| --- | --- |
| 8 生产者、4–64 KiB 消息、1 MiB 预算、锁外发送及可停止 | 只用 systems-programming；合并头与数据，分配前原子预留，构造/排队/在途均计费，真正释放后退款；单 mutex 与条件变量、非阻塞发送及可唤醒等待，不盲目池化/无锁化；给出两组停止/预算交错 |
| Python SSRF 与命令注入专项 | 只用 secure-coding，不追加通用 PR 或系统设计；保留实际目标、重定向与参数语义的检查前提 |
| 禁 C++ 库的引用/取消 PR | code-review-checklist 配合 systems-programming；显式所有权与现有 C 同步，不建议 unique_ptr/std::mutex |
| Go/Python 测试框架与覆盖 | testing-strategy；仅在配置运行器时配合 build-config，不自动引入其他流程 |
| 既有 CMake 修 pthread 和告警 | build-config；保持构建系统，不新增 fmt、升级语言或开启异常/RTTI |
| 不可信内核 ioctl 异步 buffer | 安全重点由 secure-coding 主导，systems-programming 配合所有权、上下文、在途预算与卸载；两者均使用，不要求其他整套流程 |
| C 别名/回调、已释放 Rust 指针、内核 no_std | 拒绝以置空或非空/对齐证明存活；修复异步生命周期时配合系统技能；不要求 std::error::Error |
| 已允许 STL 的现代 C++ 容器变更 | code-review-checklist；按真实容器失效规则审查，不全局禁库，也不自动加载系统技能 |

队列回答主动区分了申请容量与 RSS，要求先确认停止是否允许丢弃、提交成功语义与句柄存活契约。性能收益未被预先宣称。以上是阅读技能后的设计和选择行为，不是运行队列或 ioctl 的测试结果。

## Evidence Review

- `quick_validate.py` 分别验证系统技能及三个修改过的相邻技能：四次均输出 `Skill is valid!`。
- 通用 Python 事实检查：31 个本地 Markdown 链接均可解析；UI YAML 可读取，简述为 33 个字符；旧名 `SKILL.md` 不存在。检查以 `python3 -B -c` 执行，不写入临时文件。首次 here-doc 形式因 shell 临时文件只读而失败，检查逻辑未执行，随后改用无 here-doc 形式。
- 将新路径中的六份未修改参考资料逐字节与基线 Git 对象比较：共同原则、用户态、内核态、资料索引、内存与锁设计、源码与规范比对均相同。主线源码学习成果完整保留；验证参考仅增加职责转介并去掉重复的通用审查流程。
- `git diff --check` 和 `git diff --cached --check` 对本次精确路径均通过；暂存名称差异显示预期的新路径、旧入口撤除和相邻技能修改。提交使用精确路径及 `--only`，避免包含其他已暂存工作。
- 一次性独立只读审查按 Scope、Consistency、Adversarial、Evidence 检查修改与证据，未发现本次新增或修改造成的可执行问题；未发现无限转介、必须更新却遗漏的运行入口，或历史条目直接抵消本次修订。

本次是技能文本、选择行为与静态证据审查；未编译内核、运行 C/Rust 示例或测量性能，不据此宣称实际项目已获得性能改善，也不保证任意模型在任意上下文均遵循规则。
