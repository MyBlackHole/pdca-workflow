# 调研报告 — 最后提交 dbc20b5e【F-139】TLS/mTLS 全栈实现分析

## 调研目标

系统性梳理仓库最后一次提交 `dbc20b5ee7db3f0302196ce30229883563fb63e2`（2026-08-21，black）的修改内容：第三方引入与自研改造的边界、模块级改动主题、功能主线归纳。

> **版本说明**：本报告分析期间该提交经历一次 amend 重写（`0e2d8c35` → `dbc20b5e`，标题与父链不变）。差异为新增 `dmsbtex/common.c`、`dmsbtex/xmake-arm.lua` 并精简各模块 xmake.lua 冗余约 157 行。本报告所有数据以 amend 后的 `dbc20b5e` 为准，统计口径统一为 `git show --no-renames`。

## 方法

1. `git log -1 --stat` / `git show HEAD --numstat --no-renames` 全量取证，按路径前缀聚合规模；
2. 对非第三方 266 个文件按目录归类，逐模块抽样 diff 提炼改动主题；
3. 以提交标题声明的五条主线为索引，在 commit 内寻找文件/符号级证据印证。

所有统计与结论均可通过文末"参考资料"中的 git 命令复核（注意先核对当前 HEAD 指纹）。

## 发现

### 一、规模与边界（AC-1）

| 分层 | 文件数 | 新增行 | 删除行 |
|------|-------:|-------:|-------:|
| 第三方引入 `third_party/openssl4/` | 3857 | +1,279,668 | 0 |
| 自研改造（其余全部） | 266 | +34,304 | -2,560 |
| **合计** | **4123** | **+1,313,972** | **-2,560** |

- 第三方部分为 **OpenSSL 4.0.1**（`VERSION.dat`：MAJOR=4, MINOR=0, PATCH=1，RELEASE_DATE="9 Jun 2026"）上游源码**纯新增**整体引入。
- 真正的自研逻辑改动集中在 266 个文件、约 3.4 万行，占提交行数约 2.6%。

自研部分目录分布（文件数）：

| 目录 | 文件数 | 改动主题 |
|------|-------:|---------|
| `oss/` | 121 | 新增 Go 工具 aio-oss（含 vendor） |
| `libs/` | 52 | TLS 证书/密钥核心库 + 测试证书 |
| `rpc/` | 31 | mTLS 协商服务端改造 + 集成测试 |
| `rdbcomm/` | 14 | 守护进程握手改造 |
| `libobk/` | 12 | 备份库 TLS/会话适配 |
| `fs-backup/` | 10 | 文件备份客户端/守护进程适配 |
| `dmsbtex/` | 12 | 网络协议层适配（含新增 common.c 与交叉构建配置） |
| 根目录 | 3 | xmake.lua、version.h.in、version.log.in |
| `s3tools/`、`packages/`、`xbsa/`、`rpc-keygen/`、`test/` | 各 1–4 | 构建适配、本地包定义、脚本测试 |

### 二、功能主线归纳（AC-3，五条主线证据）

**主线 1：OpenSSL4 国密支持（单库替代 gmssl 双后端）**
- 引入 `third_party/openssl4/`（OpenSSL 4.0.1，含 SM2/SM3/SM4 国密实现与 QUIC/FIPS 模块）；
- 新增本地包定义 `packages/o/openssl4/xmake.lua` 与 `packages/o/openssl4/configure/patch.lua`；
- 架构决策已沉淀 ADR：`docs/adr/ADR-0001-openssl4-单库替代gmssl双后端.md`（xmake.lua 注释中亦引用）；
- 国密套件常量落地：`HS_ALG_TLS_SM4_GCM_SM3`（libs/hs_algorithm.c）。

**主线 2：tls-keygen 多算法**
- `libs/tls_keygen.c/h` 重写，版本 1.0.0.0 → 1.0.0.3；
- 测试证书覆盖双算法体系：`libs/tests/certs/SM2_Test_CA/`（国密）与 `libs/tests/certs/ED25519_Test_CA/`（国际）各含 ca/host 三件套；
- 版本号注入构建配置变量 `TLS_KEYGEN_VERSION`。

**主线 3：多算法 mTLS 协商**
- 服务端自动构建双算法链：`tls_cert.h` 注释明确 "cert_dir 必填，内部自动构建 SM4+AES 双算法链"，profile 含 `algorithm/ca_cn/cert/key/crl_path` 字段；
- 算法名映射收敛为单一实现：新增 `libs/hs_algorithm.c`（注释 T0359："四模块原各自维护一份同构实现，现收敛到此文件由 libs 统一链接"；T0358 H3 规范名精确匹配）；
- `rpc/rpc-server.cpp` +309/-148 行承载协商逻辑；新增集成测试 `rpc/tests/mixed_mtls.cpp`(+162)、`mixed_mtls_integration.cpp`(+327)、`rpc_own_handshake_test.cpp`(+308)；
- Go 侧对齐同一套配置语义：`oss/cmd/tls.go` 解析 rdb.conf 的 `[oss] mtls_enable/tls_algorithm` + `[security] tls_enable/ciphersuites/cert_dir` 四层模型。

**主线 4：客户端证书缓存**
- 新增 API `tls_cert_client_ctx_acquire(cert_dir, algorithm, ca_cn, &ctx)` / `tls_cert_client_ctx_release(ctx)`：按 `(cert_dir, algorithm, ca_cn)` 键控复用 ctx，引用计数并发安全（tls_cert.h:64-73 注释 AC-4）；
- `tls_cert_ctx_reload()` 支持运行期按算法热重载；`TLS_SSL.slot` 携带 `ca_cn/algorithm` 供审计；
- `cache` 在 `libs/tls_cert.c` 中出现 31 次。

**主线 5：xmake 构建与版本管理**
- 多组件版本升级：rpc 3.6.4.19→3.6.4.22、rdbcomm 1.0.1.8→1.0.2.1、libobk 1.0.0.0→1.0.1.2、dmsbtex 1.1.0.0→1.1.0.2、tls_keygen 1.0.0.0→1.0.0.3；
- 新增组件 `oss_version = "1.0.0.0"` 并注入 `version.h.in`（OSS_VERSION 宏）与 `version.log.in`（aio-oss 条目）；
- 注册本地仓库 `add_repositories("local-repo")` 供 packages/o/openssl4 本地源码包使用；`includes("oss")` 接入新目标；
- 下游模块（s3tools/s3file、s3tools/s3mount、xbsa、rpc-keygen 等）xmake.lua 同步适配；本次 amend 进一步精简了各模块构建脚本的冗余声明。

### 三、其他值得注意的改动

- **libs/rpc-net.c 净瘦身**：+69/-131（净 -62 行），配合 timed_net_key.c 精简——旧握手/密钥路径向 OpenSSL4 单库方案迁移后的清理；
- **oss/ 新工具**：Go 模块（go.mod/go.sum/vendor 101 文件），子命令含 bucket/object/config/server/request/response/tls/utils，附 `oss_https_test.go`；
- **测试资产**：新增 `libs/tests/`（logger/rdb_config/rpc_handshake/rpc_net_time/tls_cert 五个 C 测试）、`rdbcomm/tests/handshake_session_test.c`、`tool_integration.c`、`libobk/test/session_test.c`、`dmsbtex/test/session_test.c`、根目录 `test/inih-hide-symbols-test.sh`（符号隐藏验证）。

## 结论与建议

1. 该提交实质是 **F-139 安全栈换代的一次性落盘**：以 OpenSSL 4.0.1 单库替代原 gmssl 双后端，并在此之上重建了"多算法协商 → 证书管理 → 缓存复用 → 工具链"全链路；体量上 97% 是第三方源码，评审应聚焦 266 个自研文件。
2. 五条主线相互支撑：主线 1 是地基，主线 2/3/4 是其上的能力层，主线 5 把全部组件纳入统一构建与版本管理。
3. 建议（超出本任务范围，仅记录）：后续可将该巨型提交按主线拆分为多个可独立回滚的提交粒度。

## 参考资料

```bash
# 先核对 HEAD 指纹（提交可能再次被 amend）
git rev-parse HEAD   # 预期 dbc20b5ee7db3f0302196ce30229883563fb63e2

# 总量与边界（--no-renames 保证确定性）
git show HEAD --numstat --no-renames | awk -F'\t' '{p=$3; if (p ~ /^third_party\/openssl4\//) {tp++; tpa+=($1=="-"?0:$1)} else {non++; nona+=($1=="-"?0:$1); nond+=($2=="-"?0:$2)}} END {printf "openssl4:%d +%d | self:%d +%d/-%d\n", tp,tpa,non,nona,nond}'
# OpenSSL 版本
cat third_party/openssl4/VERSION.dat
# 主线证据
git show HEAD -- xmake.lua version.h.in version.log.in
git show HEAD -- libs/hs_algorithm.c
sed -n '1,73p' libs/tls_cert.h
grep -c cache libs/tls_cert.c
ls docs/adr/ADR-0001-openssl4-单库替代gmssl双后端.md
ls oss/cmd/
```
