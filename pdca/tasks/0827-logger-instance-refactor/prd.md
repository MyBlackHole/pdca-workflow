# logger 去全局化：实例型日志器 — 规格文档

## 问题陈述

- **现状**: `libs/logger.c` 以单一全局单例 `static logger_t logger; static logger_t *g_logger = &logger;` 提供日志能力，所有写路径（`__log__`/`__raw_log__`/`__audit_log__`）共用两个全局互斥量 `g_mutex`/`g_audit_mutex`。`init_logger(dir, name)` 直接改写全局 `g_logger`，并在每次调用时重复注册 `pthread_atfork` 与 `atexit` 处理函数。dmsbtex/libobk 在运行期（每 SBT agent、每备份任务）反复调用 `init_logger` 切换日志文件，与并发写日志线程形成数据竞争（use-after-close、字段撕裂）。
- **目标**: 彻底去除全局状态。日志器以"实例句柄"形式存在，调用方显式持有并传递 `logger_t *`，任何日志调用都必须传入该句柄；并发安全由每个实例自带的互斥量保证，不再存在跨实例的全局锁或全局单例。
- **差距**: 当前 661 处日志宏调用（`InfoLog`/`ErrorLog`/`DebugLog`/`WarningLog`/`RawLog`/`AuditLog*`）与 7 处 `init_logger` 调用全部隐式依赖全局 `g_logger`；`libobk/simulator/main.c` 已出现分裂的实例式 `init_logger(&__logger__, ...)` API，需统一。

## 解决方案

将 logger 重构为不透明的实例类型：

1. **实例 API**：提供 `logger_t *logger_open(const char *dir, const char *name)`（失败返回 NULL）与 `void logger_close(logger_t *log)`；审计日志通过同一实例的 `logger_init_audit(log, dir, app_name)` 开启。统一吸收 simulator 现存的 `init_logger(logger_t **, dir, file)` 形态。
2. **每实例自有状态**：`logger_t` 内部含递归互斥量、独立的 `FILE *output`/`FILE *audit_output`、target、缓冲、路径、app_name。移除全局 `g_logger`/`g_mutex`/`g_audit_mutex`。
3. **显式句柄宏**：日志宏改为首参为句柄，如 `InfoLog(lg, fmt, ...)`、`ErrorLog(lg, ...)`、`LogRaw(lg, ...)`、`LogAudit(lg, ...)`。保留现有宏名但强制首参为句柄，使全部 661 处调用点编译期报错并被迫显式传参（编译失败即迁移信号，杜绝隐式全局）。
4. **句柄传递策略**：各模块把 `logger_t *` 挂到既有的上下文结构体（`dmsbtex` 的 `sbt`/`sbt_tls_config_t`、`libobk` 的 `data`/全局上下文、`rdbcomm` 的 `server`/`io`、`rpc` 的 `io`），深层级函数从上下文取句柄；无上下文的函数新增 `logger_t *log` 形参。
5. **生命周期（atfork/atexit）**：因不再有全局 logger，采用进程内"实例注册表"（一个仅用于生命周期登记的受保护链表，非共享日志状态）实现：进程退出 `atexit` 关闭所有未关闭实例；`pthread_atfork` 的 prepare 锁全部实例互斥量、child 中逐个重新初始化，避免 fork 后子进程日志崩溃。注册表仅为生命周期管理，不属于"全局日志器"。

## Seam 分析

### 测试接缝
- 新实例 API 在 `libs/tests/logger_test.c` 单测覆盖：创建、并发多线程写同一实例无竞争、关闭后无 use-after-close、fork 后子进程日志可用。
- 各模块迁移的回归 seam 为其既有测试：`dmsbtex/test/session_test.c`、`libobk/test/session_test.c`、`rdbcomm` 相关测试、`libs/tests/rdb_config_test.c` 等，确保迁移后编译通过且行为不变。

### 声明的测试接缝
development/bugfix 场景必填（机器可读，供契约测试校验）。每行一个 seam：

- seam: libs/tests/logger_test.c -> libs/logger.c
- seam: dmsbtex/test/session_test.c -> dmsbtex/network.c
- seam: libobk/test/session_test.c -> libobk/lib/sbt/libobk.c
- seam: libs/tests/rdb_config_test.c -> libs/rdb-config.c

### 验收可测性
- 每处迁移可由"模块编译通过 + 该模块既有测试通过"独立判定。
- 并发安全可由 `logger_test.c` 中的多线程压力用例 + 可选 ThreadSanitizer 构建判定。
- fork 安全可由专门构造的 fork+日志用例判定。

## 用户故事

1. 作为 dmsbtex/libobk 的开发者，我需要每 SBT agent / 每备份任务拥有独立日志实例，以便并发运行时不互相污染日志文件、无 use-after-close 崩溃。
2. 作为 logger 维护者，我希望日志器无全局单例与全局锁，以便新增模块时显式持有句柄、不存在隐式共享状态带来的并发隐患。
3. 作为测试者，我希望 `xmake test` 全量通过且可用 TSAN 验证无数据竞争，以便并发改造可信。

## 实现决策

**不包含具体文件路径或代码片段**（可能迅速过时）。记录：

- 新增/修改模块：`libs/logger.c`、`libs/logger.h`；以及 dmsbtex、libobk（含 simulator）、rdbcomm、rpc、libs 内部、第三方 sdk `huanweicloun-sdk-s3-data-backup` 的全部日志调用点。
- 接口定义：`logger_open`/`logger_close`/`logger_init_audit` 返回/接受 `logger_t *`；宏 `InfoLog(lg,...)`/`ErrorLog(lg,...)`/`DebugLog(lg,...)`/`WarningLog(lg,...)`/`LogRaw(lg,...)`/`LogAudit(lg,...)`。
- 架构决策（→ 同时记入 `docs/adr/`）：
  - ADR-1：实例式 vs 线程局部默认 logger —— 选实例式（用户明确要求彻底去全局）。
  - ADR-2：atfork/atexit 用内部实例注册表 —— 注册表仅管生命周期，非共享日志状态。
  - ADR-3：宏命名保持 `InfoLog(lg,...)` 首参句柄，而非全新宏名，降低审阅映射成本。
  - ADR-4：simulator 现有 `init_logger(&__logger__, dir, file)` 收敛到 `logger_open`，去除 API 分裂。
  - ADR-5：句柄通过既有上下文结构体传递，减少函数签名改动面。
- 数据模型变更：无持久化数据变更；仅内存中 `logger_t` 实例化的方式变化。
- API 合约：调用方负责 `logger_open` 后持有并在合适时机 `logger_close`；同一实例可多线程并发写。

## 测试决策

- 好的测试定义：仅测外部行为（日志写入正确文件、并发不崩溃、fork 后可用），不测 `logger_t` 内部字段。
- 被测模块：`libs/logger.c`（单测为主）；各模块迁移以编译 + 既有集成测试作回归。
- 现有测试先例参考：`libs/tests/logger_test.c` 现有 10 个用例，需扩展并发/fork 用例。

## 验收标准

使用规范 Markdown checkbox；系统按出现顺序确定 `AC-1`、`AC-2`……。

- [ ] AC-1: `libs/logger.c`/`logger.h` 中不再存在全局日志单例（`g_logger`）与全局日志互斥量（`g_mutex`/`g_audit_mutex`）；`logger_t` 为不透明实例且含自有递归互斥量。
- [ ] AC-2: 新实例 API `logger_open`/`logger_close`/`logger_init_audit` 可用；`libs/tests/logger_test.c` 新增并发多线程写同一实例用例，在普通与 ThreadSanitizer 构建下均无数据竞争报告。
- [ ] AC-3: 日志宏全部改为显式句柄首参形式（`InfoLog(lg,...)` 等）；全仓 661 处宏调用与 7 处 `init_logger` 调用均迁移，整个仓库 `xmake build` 通过（无隐式全局引用残留）。
- [ ] AC-4: 各模块通过既有上下文结构体（`sbt`/`server`/`io`/`data`）或新增参数显式传递 `logger_t *`，代码中不存在线程局部（`__thread`）或全局默认 logger 作为日志来源。
- [ ] AC-5: `libobk/simulator/main.c` 的实例式 `init_logger(&__logger__, ...)` 收敛到新 `logger_open` API，消除与 `libs/logger.c` 的 API 分裂；simulator 编译运行正常。
- [ ] AC-6: atfork/atexit 基于内部实例注册表实现；构造 fork+日志用例验证子进程日志不崩溃、不重复销毁互斥量；`xmake test` 全量通过（48 项）。
- [ ] AC-7: 第三方 sdk `huanweicloun-sdk-s3-data-backup` 的 64 处宏调用完成迁移或经明确的范围外决策搁置（见范围外），不在代码中遗留对旧全局 API 的引用。

## 范围外

- 日志内容格式、分级、轮转策略（`LOG_MAX_SIZE`/`switch_log_file` 行为）不在本次变更，仅改为实例归属。
- 第三方 sdk 若其维护边界不允许改动，可经 AC-7 决策搁置并保留兼容垫片（但垫片本身不得 reintroduce 全局单例）。
- 日志性能基准压测（benchmark）不在本次必交付项，仅保证无全局锁竞争的结构正确性。

## 备注

- 根因来自会话中对 `init_logger` 并发问题的排查：全局单例 + 每次调用重复注册 atfork/atexit 是 dmsbtex_session_test/libobk_session_test 失败与潜在崩溃的根。本次重构从架构上消除该根因。
- 迁移规模较大（约 661 处宏 + 7 处 init_logger），必须分期（见子任务 T0262–T0268），P6 终审前不调度子任务。

---

*由 to-spec 流程合成。术语表见 `pdca/CONTEXT.md`，架构决策见 `docs/adr/`。*
