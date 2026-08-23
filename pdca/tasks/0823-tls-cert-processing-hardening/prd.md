# TLS 证书处理流程安全纵深与确定性优化（高优 1/2/3/4）

## 问题陈述

四模块（rdbcomm / dmsbtex / libobk / rpc）共用的证书处理中枢 `libs/tls_cert.c`
（加载 → ca_cn 提取下发 → 握手 → 链验证 → 审计）已完成 T0354–T0364 系列改造
（fail-closed 严格解析、双算法收敛、ca_cn 不可用拒绝帧）。但代码审查（T0364 推荐）
仍暴露四类缺陷：

1. **对端身份未绑定**：`tls_cert.c:601` 仅判 `SSL_get_verify_result==X509_V_OK`
   （验链有效性），未校验对端证书 CN/SAN 是否匹配预期身份。OpenSSL 默认只验
   "链可信" 不验 "你是谁"。
2. **ciphersuites 静默失败（fail-open）**：`tls_cert.c:87-91` 套件设置失败仅
   `ErrorLog` 不返回错误，继续用默认套件；而算法名即套件名，设置失败意味着
   协商语义失效。
3. **ca_cn 提取不确定性**：`tls_cert.c:240-258` 服务端从 `X509_STORE_get1_objects`
   遍历取 "首个有 CN 的 CA 对象"，依赖遍历顺序、循环内反复清空逻辑绕。
4. **ED25519 隐式回退（刻意保留）**：`tls_cert.c:200-204,119-179` 的 `stat` 探测回退用于
   兼容旧证书格式，属兼容性需要，**本次不处理**（保持旧证书可用）。

## 目标

对 `libs/tls_cert.c` 做 4 项强化，提升证书处理的安全纵深与确定性，保持 fail-closed
精神，四模块经统一接口间接受益、无需逐模块改动。

## 范围

- **在范围**：`libs/tls_cert.c` 的 4 项修改 + 单测覆盖；调用约定文档化（ca_cn 语义、
  ED25519 布局规范）。
- **不在范围**：证书生成/热加载/轮换（P2-6）、CRL/OCSP 吊销检查（P2-7）、
  错误码前缀归一（T0364 follow-up）、审计对端 CN（P2-5，可顺带但不设 AC）。

## 验收标准

- [ ] AC-1: 对端身份绑定——服务端用 `SSL_set_verify` 回调校验客户端证书 subject CN
  属于协商 `ca_cn` 命名空间；客户端校验服务端证书身份匹配预期（pin `ca_cn`）。
  新增单测：构造 "链有效但 CN 不匹配" 的对端，握手须被拒绝。
- [ ] AC-2: ciphersuites fail-closed——`tls_cert_set_ciphersuites` 设置失败改为返回
  错误并拒绝该 profile（不再静默用默认套件）。单测：注入非法算法名，`init` 应失败。
- [ ] AC-3: ca_cn 提取确定性——服务端从主 CA 文件路径（`profile->ca_cert`）确定性
  解析 subject CN，去掉 `X509_STORE_get1_objects` 遍历取首个逻辑。单测：多 CA 对象
  store 下提取结果稳定且等于主 CA CN。
- [ ] AC-4: 客户端 ctx 缓存复用——在客户端侧按 `(cert_dir, algorithm, ca_cn)` 三元组
  缓存 `tls_cert_ctx_t *`，一次 init、多次握手复用，消除每次连接重复读取 CA/cert/key
  文件并重建 SSL_CTX 的开销（服务端已有全局 `server_tls_ctx`/`sbt_server_ctx` 缓存，
  客户端缺失该非对称点）。**并发安全（硬约束）**：缓存表须加锁保护；每个 ctx 采用
  引用计数，获取时 +1、连接关闭释放时 -1，归零才真正 `tls_cert_cleanup`；同 key 多连接
  并发共享同一 `SSL_CTX`（OpenSSL SSL_CTX 本身线程安全，可并发 `SSL_new`）。单测：同一键
  两次握手复用同一 ctx（验证 `SSL_new(slot->ssl_ctx)` 共享）且 `tls_cert_init_client` 仅
  一次；并发压测下无 use-after-free / 双重释放 / 竞态。

## Seam 分析

### 声明的测试接缝

- seam: `libs/tests/tls_cert_test.c` -> `libs/tls_cert.c`（单元：ca_cn 确定性、ciphersuites
  失败、客户端 ctx 缓存复用）
- seam: `libs/tests/tls_cert_test.c` -> `libs/tls_cert.c` 身份绑定回调（需新增双 CA
  测试夹具：主 CA +  rogue CA，验证 CN 不匹配拒绝）

## 范围外

- ED25519 隐式回退（`tls_cert_pick_ed25519_*`）为兼容旧证书刻意保留，本次不去除
- 证书热加载/轮换（建议另立 P2 任务）
- CRL/OCSP 吊销检查（建议另立 P2 任务）
- 错误码前缀归一（T0364 follow-up 跟踪）
- 审计对端 CN（P2-5，顺带优化，不设 AC）

## 备注

- 参考 `knowledge/tls/mtls-four-module-supplementary-review.md`、
  `mtls-server-alg-whitelist.md`、`mtls-handshake-enum-unify.md`。
- 沿用 T0358 fail-closed、T0359 枚举收敛既有范式。
- 四模块调用方（rdbcomm / dmsbtex / libobk / rpc）经 `tls_cert_*` 接口间接受益，
  不逐模块改动；若 AC-1 身份绑定需协议层新字段再评估。
