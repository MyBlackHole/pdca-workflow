# mTLS 全栈整体分析报告（00f12df..4ef9c5c1 squash 整合视角）

## 分析范围

TLS/mTLS 栈全部层次：libs/tls_cert.c（930 行，证书/slot/ccache/握手/热加载）、libs/hs_algorithm.c（码表+文案）、四模块协商层（rpc-server.cpp / rdbcomm/server.c / dmsbtex/network.c / libobk oracleCmdTbl.c）、四模块客户端握手（rpc-io.cpp / rdbcomm/client.c / libobk.c / network.c）、配置分层（sec_resolve_*）、会话 IO 分发（函数指针 plain/tls）。

## 一、有没有问题

未发现阻塞级缺陷。以下为按优先级排列的潜在问题：

| # | 位置 | 问题 | 严重度 |
|---|------|------|--------|
| P1 | tls_cert.c:575-578 | **ccache 容量耗尽语义误导且无淘汰**：64 个缓存槽用尽后返回 `TLS_CERT_ERR_SSL_CREATE`（语义应为"SSL 创建失败"），且无 LRU 淘汰。长期运行、使用多种 (cert_dir,algorithm,ca_cn) 组合的客户端进程会在第 65 种组合起永久无法建立 mTLS 连接 | HIGH |
| P2 | tls_cert.c:894-922 | **slot 热轮换与 accept 并发竞态（潜伏）**：`tls_cert_slot_reload` 原子替换 slot->ssl_ctx 指针，但在途 SSL 引用计数保护的是 SSL 对象而非指针替换本身的可见性；当前无调用方触发 reload（预留 API），一旦接入定时轮换即成竞态 | MEDIUM |
| P3 | tls_cert.c:885 | **握手失败路径无条件 SSL_shutdown**：对端异常断开时 shutdown 写 close_notify 可能触发 SIGPIPE。测试进程均屏蔽了 SIGPIPE；生产 daemon 需确认同样屏蔽（aio-speedd 有 SignalShield 类处理，dm-ftp 待核） | MEDIUM |
| P4 | tls_cert.c:517 | calloc 失败返回 `INVALID_PARAM` 而非内存错误——全库错误枚举粒度限制，诊断时会误指参数问题 | LOW |
| P5 | oracleCmdTbl.c hs_send_frame 等 | header/payload 分两次 send 非原子——单线程单连接模型下安全，仅为多余 syscall（并入优化节） | LOW |

## 二、有没有可以安全简化

| # | 内容 | 收益/成本 | 建议 |
|---|------|----------|------|
| S1 | 四模块 config init 的"算法解析块"完全同构（sec_resolve NULL 默认 + CLI 覆盖 + 白名单校验 + from_name，各约 20 行）：可提取 `hs_algorithm_config_resolve()` 至 libs | 消除 4 份重复；需新增 libs 公共 API | ✅ 可安全简化，建议后续任务 |
| S2 | mixed_mtls_integration 的 server_serve 手工复刻 rpc-server.cpp 决策树：每次服务端改动需人工同步（本次 AC-8/9 已同步过一轮） | 消除漂移风险；需把决策树抽为可测纯函数（改动核心路径） | ⚠️ 结构性改进，需单独评审 |
| S3 | rdbcomm client.c 握手 `if(!fail && ...)` 链加深后嵌套较深 | 可读性 | LOW，顺手重构即可 |
| S4 | dmsbtex/libobk/rdbcomm 三套 hs_session 抽象同构（init_plain/init_tls/cleanup） | 归一到 libs 理论可行，但帧格式各异收益低 | ❌ 不建议 |

## 三、有没有可以优化的

| # | 内容 | 判断 |
|---|------|------|
| O1 | hs_err_str unknown 分支 `_Thread_local buf` + snprintf：仅错误路径执行 | 无需优化 |
| O2 | ccache 线性查找 64 项：握手频率=每连接一次 | 无需哈希化 |
| O3 | dm-ftp/FTA 每连接一线程模型：高并发线程开销 | 既有架构，超出 mTLS 范围 |
| O4 | handshake_common 失败路径二次 get1_peer_certificate 用于诊断 | 合理设计，保留 |

## 总体评价

mTLS 栈分层清晰（证书管理/协议协商/会话 IO 三层解耦），安全语义一致性好：全程 fail-closed、无降级、审计完整（auth 结果+peer CN）、双向身份绑定（issuer CN==ca_cn 校验）。**建议优先处理 P1**（ccache 淘汰或专用错误码），P2 在接入热轮换前补锁或文档声明单线程约束。

## 四、补充分析：每个工具使用 ini 配置 key 是否太过复杂

### 现状盘点（以 mtls 开关为例的一条配置要穿透 5 层）

```
CLI --mtls-enable=1
  > env   AIO_SPEEDD_MTLS_ENABLE            （每工具专属名）
    > ini [aio-speedd] mtls_enable           （工具 section）
      > ini [security] tls_enable            （全局 section，key 名不同！）
        > 默认 0
```

算法项同样 5 层，且全局层 key 叫 **ciphersuites**、工具层叫 **tls_algorithm**。

### 复杂度判定：分层合理，实现有三处不必要复杂度

| # | 发现 | 影响 |
|---|------|------|
| C1 | **跨层 key 名不一致**：mtls 工具层="mtls_enable"/全局层="tls_enable"；算法工具层="tls_algorithm"/全局层="ciphersuites"。运维在 [security] 与工具 section 间切换时必须记住 key 会改名 | 认知陷阱，配错静默回落 |
| C2 | **SBT_* env 宏双定义**：dmsbtex/network.h 与 libobk/oracleCmdTbl.h 各持一份同名同值定义，违反 T0359 确立的"libs 单一来源+别名"既定模式 | 双处漂移风险 |
| C3 | **sec_resolve 6 参数签名**：tool_section/tool_key 总是成对 NULL 或成对出现，调用点冗长 | 可读性 |
| C4 | env 前缀不统一：cert_dir 是全局 RPC_TLS_CERT_DIR 共享，mtls/algorithm 却每工具专属（AIO_SPEEDD_*/RDBCOMM_*/SBT_*） | "证书共享、策略独立"设计有意为之但未文档化 |

### 结论

**分层架构本身不算过度复杂**——CLI(运维覆盖)/env(编排注入)/ini(持久化)/默认值 是标准 12-factor 风格；"证书共享、策略独立"的划分也有依据。真正的问题是上述三处实现级复杂度，均可安全简化：

1. **C1 → 渐进统一 key 名**：[security] 新增 "mtls_enable"/"tls_algorithm" 规范 key（旧名双读兼容一个版本后废弃）；
2. **C2 → SBT_* 宏迁至 libs/common.h**，dmsbtex/libobk 改别名（与 HS_ERR/HS_ALG 归一同址，零运行时变化）；
3. **C3 → spec 结构体收敛签名**：`sec_resolve_bool_spec(&spec, default)`，机械重构零行为变化；
4. 附带产出一张五层配置对照表文档供运维使用。

以上均为低风险简化，建议归入下一个跨模块清理任务批量实施。
