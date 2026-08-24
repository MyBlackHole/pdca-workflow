# tls-keygen 清理：算法前缀文件名、删除 purpose/EKU、-n 区分客户端/服务端

## 问题陈述

- **现状**: tls-keygen 当前生成的文件名始终为 `host.key`/`host.csr`/`host.crt`，不区分算法。SM2 和 Ed25519 证书使用相同文件名，导致同一目录下无法共存多种算法的证书。此外，`--purpose` 参数和 EKU（Extended Key Usage）扩展增加了不必要的复杂度，客户端/服务端的区分应由目录结构（`-n` 参数）隐式决定。
- **目标**: 简化 tls-keygen，使文件名包含算法前缀（如 `sm2_host.key`），删除 purpose/EKU 逻辑，通过 `-n` 参数的值区分客户端和服务端证书目录。
- **差距**: 当前文件名无算法前缀，purpose/EKU 增加了不必要的复杂度。

## 解决方案

1. **文件名算法前缀**: `create` 和 `sign` 子命令生成的文件名改为 `{algo}_host.key`/`{algo}_host.csr`/`{algo}_host.crt`。CA 证书同理：`{algo}_ca.key`/`{algo}_ca.crt`。
2. **删除 purpose/EKU**: 移除 `sign` 子命令的 `--purpose` 参数，移除 `tls_keygen_sign_with_algo()` 中的 EKU 设置逻辑。客户端/服务端不再通过 purpose 区分。
3. **-n 区分客户端/服务端**: `-n` 参数的值作为输出子目录名（如 `-n Server` → `/opt/aio/cfg/certs/Server/`，`-n ClientA` → `/opt/aio/cfg/certs/ClientA/`）。目录名本身区分了客户端和服务端角色。

## Seam 分析

### 测试接缝
- seam: libs/tests/tls_cert_test.c -> libs/tls_keygen.c
- seam: libs/tests/tls_keygen_test.c (if exists) -> libs/tls_keygen.c
- seam: rdbcomm/tests/tool_integration.c -> libs/tls_keygen.c (间接，通过 tls-keygen CLI)

## 用户故事

1. 作为维护者，我希望 tls-keygen 生成的文件名包含算法前缀，以便同一目录下可以共存 SM2 和 Ed25519 证书。
2. 作为维护者，我希望删除 purpose/EKU 逻辑，以便简化证书生成流程，减少不必要的复杂度。
3. 作为维护者，我希望通过 `-n` 参数区分客户端和服务端证书目录，以便清晰地组织证书文件。

## 实现决策

### 文件命名规则

| 子命令 | 当前文件名 | 新文件名 |
|--------|-----------|---------|
| create | `host.key`, `host.csr` | `{algo}_host.key`, `{algo}_host.csr` |
| sign | `host.key`, `host.csr`, `host.crt` | `{algo}_host.key`, `{algo}_host.csr`, `{algo}_host.crt` |
| ca | `ca.key`, `ca.crt` | `{algo}_ca.key`, `{algo}_ca.crt` |

### 删除 purpose/EKU

- 移除 `handle_sign` 中的 `--purpose` 选项解析
- 移除 `tls_keygen_sign_with_algo()` 中的 `purpose` 参数和 EKU 设置逻辑
- `tls_keygen_sign()` 默认函数签名简化（移除 purpose 参数）

### 路径约定

- **服务端**: 默认输出到 `/opt/aio/cfg/certs/`（不需要 `-n`），文件为 `{algo}_host.key`/`{algo}_host.crt`
- **客户端**: 输出到 `/opt/aio/cfg/certs/{xxxx}/`，`xxxx` 通过 `-n` 配置，文件为 `{algo}_host.key`/`{algo}_host.crt`

### -n 参数语义

`-n` 仅用于客户端证书目录名。例如：
```bash
# 服务端（不需要 -n）
tls-keygen create -a sm2                    # → /opt/aio/cfg/certs/sm2_host.key
tls-keygen sign -a sm2 --ca-cert ... ...    # → /opt/aio/cfg/certs/sm2_host.crt

# 客户端（-n 指定目录名）
tls-keygen create -n ClientA -a sm2         # → /opt/aio/cfg/certs/ClientA/sm2_host.key
tls-keygen sign -n ClientA -a sm2 ...       # → /opt/aio/cfg/certs/ClientA/sm2_host.crt
```

## 测试决策

- 好测试定义：验证文件名包含算法前缀，验证 purpose/EKU 已移除，验证 `-n` 参数正确创建子目录。
- 被测模块：tls_keygen CLI 和库函数。
- 先例：`tls_cert_test`、`rdbcomm_tool_integration` 测试风格。

## 验收标准

- [ ] AC-1: `tls-keygen create -a sm2 -o /tmp/test` 生成 `sm2_host.key` 和 `sm2_host.csr`（而非 `host.key`/`host.csr`）
- [ ] AC-2: `tls-keygen create -a ed25519 -o /tmp/test` 生成 `ed25519_host.key` 和 `ed25519_host.csr`
- [ ] AC-3: `tls-keygen ca -n TestCA -a sm2 -o /tmp/test` 生成 `sm2_ca.key` 和 `sm2_ca.crt`（而非 `ca.key`/`ca.crt`）
- [ ] AC-4: `tls-keygen sign -a sm2 --ca-cert ... --ca-key ... --key ... --csr ... --out ...` 生成的证书不包含 EKU 扩展
- [ ] AC-5: `tls-keygen sign` 不再接受 `--purpose` 参数（报错退出）
- [ ] AC-6: `tls-keygen create -a sm2`（无 -n）生成文件到 `/opt/aio/cfg/certs/sm2_host.key`
- [ ] AC-7: `tls-keygen create -n ClientA -a sm2` 生成文件到 `/opt/aio/cfg/certs/ClientA/sm2_host.key`
- [ ] AC-8: 所有现有测试（tls_cert_test、rpc_handshake_test、rdbcomm_tool_integration 等）适配新文件名后通过
- [ ] AC-9: `xmake build` 与 `xmake test` 全部通过

## 范围外

- 不修改 TLS 握手逻辑、证书加载、profile 模型。
- 不修改 rdb-config 通用解析 API。
- 不做性能/压测。

## 备注

- 源自 T0338 完成后的清理需求：简化 tls-keygen 接口，使文件命名更直观。
- 当前 `tls_keygen_sign_with_algo()` 的 `purpose` 参数和 EKU 逻辑是 T0338 之前引入的，现予以移除。

---

*由 to-spec 流程合成。术语表见 `pdca/CONTEXT.md`，架构决策见 `docs/adr/`。*
