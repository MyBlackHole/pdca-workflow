# 受控实现验收：C 异步消息队列

这是验证工程 skill 实际使用的隔离案例，不是 PDCA 产品代码。以 `rq.h` 为固定公开 C ABI，完成可审查的实现及真实验证。

用户请求：实现一个用于 C / C 风格 C++ 服务的单消费者异步消息模块。多个线程可提交消息；回调允许查询状态及再次提交。停止后不再接收新请求，返回时所有已接受消息均已交付且所有仍在构造消息的提交者已经收敛。请在该模块范围内选择合适的数据结构、资源与同步设计，说明取舍并验证。

## 行为契约

- 每个队列有一个工作线程。成功提交复制输入，在消费回调执行期间其数据有效；成功消息按提交的线性化顺序 FIFO、恰好回调一次。不把调用者缓冲借给后台。
- `max_items` 与 `max_payload_bytes` 是逻辑活跃消息的条数/负载预算，涵盖构造、排队、正在回调和延迟释放。单条零长度消息允许 NULL 输入，仍占一个条数。每项取得的预算到其实际数据释放后才退还。真实分配容量、元数据和 RSS 的关系另外说明。
- 提交不等待空余预算：容量不足返回 `-EAGAIN`；单条负载超过配置上限返回 `-EMSGSIZE`；关闭后合法提交返回 `-ESHUTDOWN`。分配失败返回 `-ENOMEM` 且不泄漏预算或资源；其他无效参数返回 `-EINVAL`。使用负 errno 内部约定，不读取 errno 推断 pthread 返回。
- `rq_get_stats` 可并发调用；live 与 peak 都符合对应预算。close 已关闭准入时 closed 为 true，成功 close 后 live 均为零。
- 多个外部线程可以同时 `rq_close`，重复 close 成功；所有成功返回的 close 都满足收敛条件。消费回调中的 close 返回 `-EDEADLK`，不改变开放状态，也不等待自身。
- `rq_destroy` 由独占所有者在其他公开 API 调用已退出后调用；它负责必要的 close、工作线程回收和最终释放。禁止在消费回调中 destroy；不要求实现能在任意 API 调用之后抵抗已销毁句柄的访问。
- `rq_create` 参数无效或任一步失败不留存线程/分配，out 在失败时为 NULL；配置上限及回调不能为空/零。公开头支持 C 风格 C++ 调用，但实现可保持 C。不得使用 C++ 库、内核私有头或新的第三方依赖。

## 验证要求

沿用系统 C/pthread 与工具链。需要真实编译运行：容量涵盖在途回调、回调重入、并发生产/close、重复 close、失败后资源平衡及公开 C++ 调用；测试断言公共行为，不镜像队列算法。可采用适用的内存诊断，性能未测就不宣称加速。

所有源码、构建、临时目录、日志及缓存均留在此工作区。运行编译器/测试前设置 TMPDIR/TMP/TEMP 并核对子工具，禁止向 /tmp 写测试产物。保持父级 skill 仓库和 Linux 源码只读。验收结果需区分实际运行、静态推断及未验证条件。

## 本轮可重复验证

这是此前验收实现及公开接口测试的固定副本。测试放在仓库 `tests/`，不作为 skill 正文或生产代码加载。
`Makefile` 要求显式 OUTPUT_ROOT；源码目录不接收构建输出。普通、ASan/UBSan、TSan 分别构建，C++ 调用者
禁用异常和 RTTI，并由 GCC 链接，从而检查没有引入 C++ 库。

```sh
cd /home/black/.agents/pdca/tests/systems-programming/practical/userspace
output=/home/black/skill-work/validation/engineering-consolidation/practical-userspace-replay
mkdir -p "$output/tmp" "$output/logs"
export TMPDIR="$output/tmp" TMP="$output/tmp" TEMP="$output/tmp"
make OUTPUT_ROOT="$output" check asan tsan bench > "$output/logs/verification.log" 2>&1
timeout 60 "$output/normal/bench_plain" 4 4096 20000
timeout 60 "$output/normal/bench_profile" 4 4096 20000
```

`test_rq` 有 11 组接口/依赖故障场景；`test_parent` 是另写的公共接口检查。
GNU ld wrap 拦截分配与 pthread 依赖，用于故障注入、暂停交错和资源归零，既不包含私有结构也不增加产品接口。
ASan/UBSan 设置 `detect_leaks=0`；本机初次 LSan 因 ptrace 限制失败，不能声称通过泄漏扫描。
已经运行的 wrapper 分配归零断言有自己的证明范围，不能替代完整 LSan。

## 资源与性能基线

两个 benchmark 接受 `生产者数 payload字节数 总消息数`。总数须能被生产者数整除，payload 至少容纳 16 字节标头。
队列额度固定为 512 项及 512 × payload 字节；每个新进程执行一个有限批次，逐条检查内容、唯一消费、最终归零与峰值不越界。
计时从生产者启动屏障前至全部生产者退出且 close 收敛，排除队列创建和最终 destroy，包含回调验证、调度及容量重试。
每条延迟从最终成功的 submit 尝试开始到消费回调入口；之前的 EAGAIN 重试不计入该条延迟，但计入吞吐总时长。
因此它是 submit-to-callback 延迟，不是端到端请求延迟或回调执行完毕延迟。

- `bench_plain` 使用未插桩的队列；其吞吐、p50/p99、close 时间、逻辑峰值和进程峰值 RSS 用作当前实现基线。
- `bench_profile` 只将 rq.c 的 malloc/free、mutex lock/unlock 和 cond_wait 重命名到测量包装器。
  模块分配次数和活跃分配不混入测试框架的 calloc、线程资源或 libc 内部分配。
  显式 lock 调用的等待时间与持锁区段单独累计；cond_wait 的睡眠及隐含重获锁排除在持锁区段外，也未计入显式 lock 等待。
  包装器的时间读取和原子计数会扰动运行，持锁区段在调用 unlock 前结束，不能把这些数字当成未插桩锁时长。
- `process_peak_rss_kib` 读取 Linux `/proc/self/status` 的 VmHWM，包含线程栈、分配器、测试数组和装载开销；它不等于 payload 预算。
  `rusage_maxrss_kib` 另保留 getrusage 结果。exec 前的进程高水位可能使后者带入 Python 启动器的历史值；报告使用 VmHWM，不据此声称模块独占内存。

应在没有本任务构建负载竞争时，对 1/4 生产者、64/4096 字节各运行多个新进程并保存逐次 JSON。
报告中位数和范围；不混合普通与插桩吞吐，不把单机短批次推广到生产，也不从基线虚构优化收益。
