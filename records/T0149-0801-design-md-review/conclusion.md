---
schema: pdca.asset/v1
id: T0149-0801-design-md-review
phase: check
source_ids: [design-md, poc-result, test-gmssl]
---

## 上下文

任务 T0149：审查重构 design.md，移除行业实现对照节和代码细节，根据 GMSSL 替代 OpenSSL 可行性 PoC 调整设计方向。

## 假设与结果

| 假设 | 结果 | 证据 |
|------|------|------|
| GMSSL v3.1.1 (xmake-repo) 可替代 OpenSSL 进行 SM2 证书签发和验签 | ✅ 已确认 | test-gmssl: 6 组基础测试通过（SM2/SM4-GCM/X.509/TLS/TLCP） |
| GMSSL SM2 证书可被 OpenSSL 验证 | ✅ 已确认 | test-gmssl 8/10: openssl verify OK |
| design.md 可精简移除行业对照和代码细节 | ✅ 已确认 | design-md: 对比 prd.md AC1-5 逐条满足 |
| GMSSL 不能直接替换 OpenSSL（存量证书兼容问题） | ✅ 已确认 | poc-result: Ed25519 不支持、OpenSSL SM2 互操作差异 |

## 分析

### 1. GMSSL 替代可行性

GMSSL v3.1.1 功能完整，可独立完成 SM2 证书签发、SM4-GCM 加解密、TLCP/TLS13 上下文创建。但：

- **Ed25519 完全不支持**：存量 tls-keygen 证书无法由 GMSSL 解析
- **OpenSSL SM2 互操作问题**：GMSSL 可解析 OpenSSL SM2 证书的公钥和 TBS，但签名验证 (`sm2_do_verify`) 失败
- **GMSSL SM2 证书可被 OpenSSL 验证**：单向兼容

### 2. 设计方向

从"GMSSL 替换 OpenSSL"调整为**双后端设计**：
- OpenSSL 后端：维护存量 Ed25519 证书、处理非国密节点
- GMSSL 后端：签发新 SM2 证书、处理国密节点
- 运行时自动选择：按 `alg=auto/sm2/rsa` 配置和握手探测决定

### 3. design.md 重构

- 行业实现对照节 → 已移除（~42 行）
- 代码细节（API 对照表、CLI 示例、文件路径） → 已移除（~80 行）
- 新增 PoC 结论节、双后端选择策略、更新决策矩阵
- 文档独立可读，无"参见 implement.md"跳转

## 适用边界

- PoC 仅验证了 xmake-repo GMSSL v3.1.1 包，未测试 prebuilt (`third_party/gmssl/`) 版本
- SM2 互操作问题限于 OpenSSL SM2 → GMSSL 验签方向，反向正常
- 未测试 ARM64 架构的 GMSSL 编译

## 下一轮建议

1. 在 aio-tools 项目中实现 tls_cert 双后端抽象层
2. tls-keygen 新增 `--alg sm2` 子命令
3. 对接 prebuilt GMSSL 库（`third_party/gmssl/`）验证 ARM64 兼容性
4. dmsbtex/libobk 链路 TLS 改造

## 2026-07-31 修订（最终产出）

本次会话基于 NBU 实际环境实证（T0162 抓包 / T0163 静态分析）进一步收敛设计：

- **设计方向演进**：从"GMSSL 双后端并存"改为**复用现有 TLS 库内置国密算法**（SM2/SM3/SM4 + ECDHE-SM4-* 国密套件），不引入额外第三方库，无新增编译依赖
- **模型简化**：采用 NBU 实证的单端口协商模型（明文协议头能力宣告 → 同连接升级 TLS），加密/明文连接并存于同一端口，配置变更仅影响新连接、无需重启
- **语义简化**：不设 enforced/preferred 两级，开启即强制——加密失败作业失败、不降级明文（需求 4a/4b）
- **文档终态**：design.md 106 行纯文字设计文档（无行业对照、无代码内容、无组件选型表述），已提交 aio/F/139 仓库 730f013；nbu-comparison.md 补充实际环境验证偏差章节（8 项偏差）
- **遗留**（下轮 PDCA 处理）：docs/ 未提交、TLCP 双证书若验收强制要求需另行评估、实现任务立项

## 下一轮建议（更新）

1. 按最终设计实现 tls_cert 国密套件路径（含协商逻辑）
2. tls-keygen 新增 SM2 算法选项
3. 评估 TLCP 双证书需求（如验收强制）
4. dmsbtex/libobk 链路 TLS 改造
