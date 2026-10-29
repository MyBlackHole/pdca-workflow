# systems-programming 完整性复审：3.3.0 → 3.4.0

审查跨 2026-10-29 至 2026-10-30（Asia/Shanghai），基线 `1cf2a3e760ba49d9898232ffef37df49962e8c99`。
目标仍是归纳 Linux 规范及实现理由，服务未来内核与用户态开发，主动做好资源和同步设计。
本轮修订五个 skill 文件；实验代码与日志只在工作区，不进入技能正文或 references。

## 当前发现与修订

| 主题 | 原有不足与触发条件 | 最小修订位置 |
| --- | --- | --- |
| 内核线程 | 通用停止原则缺少 create/run 的立即执行、合作停止及自然退出后的 task 存活约束；仅等工作谓词可能使卸载无法退出 | [内核等待与停止](../../skills/systems-programming/references/environments/kernelspace.md#等待per-cpu-与停止) |
| 回收队列 | 原段仅要求核对进展，弱化了目标文档对回收 workqueue 的强制条件；严重内存压力与相互依赖时尤为重要 | [内核资源](../../skills/systems-programming/references/environments/kernelspace.md#内存资源与设备)：保留 WQ_MEM_RECLAIM 的适用要求，区分普通/BH 队列 |
| 条件变量时钟 | 单调截止时间建议未写明默认条件变量的时钟，直接混用可立即超时 | [用户态线程](../../skills/systems-programming/references/environments/userspace.md#线程信号与取消)：时钟选择、初始化失败和截止时间契约 |
| 数据报返回零 | 普通短 I/O/EOF 规则不足以区分合法空消息 | [用户态 I/O](../../skills/systems-programming/references/environments/userspace.md#错误与-io)：按对象类型、请求长度判断 |
| 断连信号 | 只处理错误码不能确保服务存活；SIGPIPE 可能先终止进程 | 同一 I/O 节：适用的逐调用机制及项目级信号策略，避免擅改全进程行为 |
| 满额后的进展 | 证明预算不越界，不能单独证明长期缓存还能更新 | [内存设计](../../skills/systems-programming/references/principles/memory-and-locks.md#内存先所有权和预算再分配器)：业务进展、替换余量与恢复准入分别验证 |
| 纯统计原子 | 原来“使用原子时”的发布配对表述可能过度约束独立计数 | [锁设计](../../skills/systems-programming/references/principles/memory-and-locks.md#锁先减少共享再缩小临界区)：条件化发布协议，保留适用的 relaxed 统计，不把独立读取当整体快照 |
| 重叠操作顺序 | “不让旧结果覆盖新状态”可能让 AI 给合法全量替换增加未要求的开始顺序/代际限制 | 同一锁设计节：存活、提交一致性和接口顺序分别证明；复查真正依赖的状态 |

这些条目包括具体适配缺失与歧义收窄，不把它们全称为已发生的产品 bug。
没有新增参考分类、第二份规则清单、池/无锁模板或统一强制实现。
入口只调整版本至 3.4.0；C 为主、C 风格 C++ 禁库、Rust 适配及已有项目边界保持其约定。

## 范围、规范与重复审查

直接读取当前入口、全部 18 个 references、UI 元数据，以及迁移索引。
检查工程原则、内存/锁、数据/接口、编码文档、用户态/内核态、调试、安全、测试/TDD、
验证、审查、构建、提交、内核贡献及来源定位之间的职责。
未发现需要再拆文件或合并的实质重复；入口摘要与任务路由、共同原则与环境适配有各自责任。

本地 `Documentation/process/coding-style.rst` 共 1294 行，本轮逐章复读其 22 个顶层章节，
并对照 [官方页面](https://docs.kernel.org/process/coding-style.html) 的章节和相关条款。
排版/命名/类型/函数/宏/注释由编码资料维护，生命周期与资源由内存和内核环境维护，
Kconfig、验证、贡献及来源由相应专题负责。函数、局部变量及内联的经验性数量不能机械推广为用户态硬门槛；
汇编、属性排列等完整细则仍要求使用时核对目标原文。
这证明主题有责任落点，不意味着摘要内嵌了规范每句话或所有子系统细则。

官方专项中，workqueue 的回收执行保证与本地原文相符；等待时钟核对 POSIX 手册与 glibc 文档；
I/O 核对 man-pages 的真实返回值和信号语义。
[历史 LinuxThreads 的条件变量页面](https://man7.org/linux/man-pages/man3/pthread_cond_wait.3.html)
包含“忽略属性”的历史实现描述，不能据此判断现代实现不支持时钟属性。
部分最初请求的条件变量文档地址不可访问，Open Group 页面返回 403；未据失败页面推导事实，
最终使用可获取的 [POSIX 时钟属性](https://man7.org/linux/man-pages/man3/pthread_condattr_getclock.3p.html)
和 [glibc 显式时钟等待](https://sourceware.org/glibc/manual/latest/html_node/Waiting-with-Explicit-Clocks.html) 核对。

本地 `/home/black/Documents/linux-7.3` 仍无可核验的 Git 来源；7.3.0 的版本标记不证明最新主线或整树原版。
仅按获准的精确文件读原树，没有改原树。以下摘要固定本轮内容：

| 原树文件 | SHA-256 |
| --- | --- |
| Documentation/process/coding-style.rst | `332454d2ab9a0462dd9f292c52291cf3b5e1afcd638aa06df15f557c47a126f5` |
| Documentation/core-api/workqueue.rst | `aed77b8b690883caffa7ddd8c09dc19f86bc46d4e92c7e73bfaebcd54c0745db` |
| kernel/kthread.c | `7e09320e7b846d7143f635ae4a77625c70fcac022081041b4e6d4fa3be024a14` |
| include/linux/kthread.h | `2288d17939c5b2abc3a1824c7fe89bc20c1a2aef30e36a0e12f2af286cd86ea9` |
| Documentation/driver-api/basics.rst | `39b823d16ba01ba06a2abc74b296ca2c8e252aab0605eeb061d2799e133e7b98` |

kthread 依据为本地 `kernel/kthread.c:532–549,732–766` 及 run 宏；
`basics.rst:78,81` 包含相应 kernel-doc，不只读取 include 入口就声称已读其全部契约。
[Workqueue 官方规则](https://docs.kernel.org/core-api/workqueue.html) 的本地对应位置为
`workqueue.rst:214–218,345–352`；回收队列标志不能替代锁/资源依赖证明。

## 运行证据

本轮工作区 W：
`/home/black/skill-work/validation/engineering-consolidation/completeness-20261029-r4`。
所有 C 编译设置工作区 TMPDIR/TMP/TEMP，使用 `-save-temps=obj` 和显式输出；
探针不创建外部测试文件，不写 /tmp。原始源码、构建、日志都在 W，不复制到 skill。

`probe_clock_io.c` 以严格 C11 告警构建，`timeout 10 ./build/probe_clock_io` 退出 0：

| 观察 | 实际结果 |
| --- | --- |
| 默认属性条件变量接收 MONOTONIC 绝对时间 | 默认时钟实测为 CLOCK_REALTIME；仅约 5308 ns 即 ETIMEDOUT |
| 正确配置 MONOTONIC 的条件变量 | 同样的 50 ms 预算，约 50114799 ns 返回 ETIMEDOUT |
| AF_UNIX 数据报空消息后再收普通消息 | 空 recv 返回 0 且被消费，下一条仍正常接收 |
| 已断开 AF_UNIX 流上的默认 write | 隔离子进程被 SIGPIPE 终止 |
| 同一断连条件采用 MSG_NOSIGNAL | 父进程继续运行，返回 EPIPE |

此为本机有限观察，等待时间包含调度；没有把微秒差异当性能结果，也未改变系统时钟或全局信号策略。
数据报探针使用 AF_UNIX，不冒充真实 UDP 网络测试；Internet 空数据报语义另据
[recv(2)](https://man7.org/linux/man-pages/man2/recv.2.html)。
逐调用信号机制与进程级策略的差异另据 [send(2)](https://man7.org/linux/man-pages/man2/send.2.html)。

`probe_capacity.c` 将原冻结实现投影到**新增**业务条件：
max_versions=1、无借用、已有 key 满额后仍须全量更新。
对照返回 0；前轮加载 skill 的实现返回 -11（EAGAIN），该新增条件探针退出 1。
旧题没有要求满额原位更新，保守准入也已在其说明中披露，因此不是回写旧验收为失败；
原实现、旧报告和固定输入均保持原样。
这个反例只证明“预算不越界”不足以证明新增业务进展要求，促使规则要求明确取舍，不强制所有项目满额替换成功。

| W 下的事实文件 | SHA-256 |
| --- | --- |
| probe_clock_io.c | `673025c0699c88eef5b5a4828a48191216c2e8ada4e098deebeb8fc570c4abde` |
| probe_capacity.c | `41f65e39782dde4154b94c18f7cce880db90ac0f17cb44f90bf96aa22ebe1fae` |
| logs/probe-clock-io.log | `bd35d85635e52baa4cca928396156d37cc74963888588517b085525c173e8e37` |
| logs/capacity-control.log | `07afb02562b9928fa56a659d198d28003849697156086c341a9383785c696cef` |
| logs/capacity-with-skill.log | `c7bb25965f5f4fb440d0352d9501f6e5a91aaf2161c7c92999b0a154718eeea5` |

## 独立视角与反例检查

一次性 fresh-context 只读审查未接收本轮怀疑项、拟议修复或旧报告。
其独立结论支持 kthread 与回收队列适配缺失，另建议收窄纯统计原子措辞；
父级复查对应原文、来源摘要及反例，未把静态意见当运行结果。

另一 fresh-context 按当前资料处理 A–F 六个业务场景：满额缓存、内核线程、
回收/普通/BH 队列、条件变量预算、空数据报/流断连、独立统计/一致业务状态。
答复能区分这些主要条件，但暴露“旧构造不得覆盖新状态”的过宽表述。
给出线性化的无条件替换契约后，答复认可 B 先提交、A 后提交的合法顺序；
父级据此修订唯一规则位置，避免隐含增加请求顺序。

修订后另一个 fresh-context 读取新规则，审查全量替换、余额条件更新、close 与裸指针：
正确允许重叠全量替换按 B→A 发布；区分真实余额前提与无条件替换；
关闭与提交共用裁决协议；局部裸指针不足以保证存活。
父级逐项读实际答复与题给契约，未发现新增时序/所有权要求。
完整事实摘要在 `W/independent-review-and-consultation.md`；这是父级归档摘要，不冒充原始对话全文。
本轮没有无技能/旧版的同题统计对照，不计算因果提升、通用正确率或未来必然表现。

## 直接复审与剩余证据边界

- Scope：只修已证实的适配缺失、措辞歧义与覆盖定位，不修改产品、旧案例或宿主配置；
  原有五个混合工作区文件及其暂存状态保持原样。
- Consistency：规则仍由唯一资料维护；来源表只负责定位，不复制规则正文。
  对象存活、状态同步、操作顺序、资源上界与进展明确区分。
- Adversarial：同时保留普通非回收/BH 队列、relaxed 独立计数、合法重叠替换和允许拒绝的满额策略，
  避免将新增条件变成普遍禁令；复查关闭期间构造、自然结束线程及信号退出反例。
- Evidence：官方文档与本地注释支持规范判断；C 探针支持本机行为；
  新上下文支持能否应用当前指引。三类证据不互相替代。

已运行 skill-creator 的 `quick_validate.py`，结果 `Skill is valid!`；
它只检查前置元数据，不作为技术正确性证明。精确文件的链接/锚点及最终差异检查另外记录于 W/logs。

本轮没有重新运行前轮 KUnit/ASan/TSan 或性能矩阵，因为未改那些实现；
旧结果仍只证明当时的固定源码和配置。
没有实测极端回收压力、真实设备、其他架构或所有未来工程场景，也没有重新抓取全部上游贡献政策。
这些边界保留为专项核对责任；不将“本轮确认缺口已修订”升级为绝对完美。
