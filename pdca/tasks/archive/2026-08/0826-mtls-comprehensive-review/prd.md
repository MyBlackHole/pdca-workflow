---
schema: pdca.asset/v1
id: T0392-0826-mtls-comprehensive-review
title: mTLS 全面安全审查（配置/握手/降级/算法/证书/版本下限）
type: prd
scenario_type: review
parent: T0391
created_at: 2026-08-26T23:10:00+08:00
status: plan
problem: |
  在 T0388/T0389/T0390（rdb config fail-closed 系列）收尾后，对全仓库 mTLS 使用做一次
  全面、纵深的安全审查：覆盖配置解析硬失败、握手强制、降级拒绝、算法白名单、证书/CA 绑定、
  最低 TLS 版本六个维度，并下沉到 OpenSSL 层核心（tls_cert.c）。前期已发现 F1（中危，生产
  上下文未显式设最低 TLS 版本）并已通过 T0391 修复；需将全量发现整合为可追溯的审查报告。
plan: |
  review 场景（path F），产物为 review-report.md：
  1. 六维度比对矩阵：配置/握手/降级/算法/证书/版本下限，逐维给出 达标/偏差/不适用。
  2. 库核心深度：tls_cert.c 套件白名单、CRL、热加载安全性、审计。
  3. 覆盖性审计：全仓 SSL_CTX_new 扫描，确认修复无绕过路径（F1）。
  4. 发现清单 F1–F5（F1 已修复 via T0391，F2–F5 低风险/一致性建议）。
  5. 每项结论含源码符号级证据，可回溯。
verification: |
  报告内证据可回溯到源码符号；发现清单状态明确；含总体 verdict。
ac:
  - id: AC-1
    description: review-report.md 覆盖全部 6 个防线维度（配置/握手/降级/算法/证书/版本下限），且引用 rpc/dmsbtex/libobk/rdbcomm/tls_cert 五处以上源码符号。
  - id: AC-2
    description: 六维度每维给出明确判定（达标/偏差/不适用），每项结论附文件:行或函数名级证据，可 grep 命中对应源文件。
  - id: AC-3
    description: 发现清单 F1–F5 状态明确（F1 已修复 via T0391；F2–F5 附风险评级与建议），且含覆盖性审计结论（全仓仅 tls_cert.c 一处生产 SSL_CTX_new）。
  - id: AC-4
    description: 报告含总体 verdict 段，给出 mTLS 安全基线总体判定与后续建议。
impact: |
  可追溯的 mTLS 安全审查结论，纳入 PDCA 知识库；F2–F5 作为后续独立任务的输入。
---

# mTLS 全面安全审查

## 问题陈述
T0388/T0389/T0390 收尾后，对全仓库 mTLS 做一次全面纵深审查。前期"广泛属性审查 + 库核心深度审查"已发现 F1（中危，生产上下文未显式设最低 TLS 版本，已由 T0391 修复）。本任务整合全部发现为正式 review-report.md。

## 审查维度
1. **配置 fail-closed**：`sec_get_bool(..._MTLS_ENABLED)` 解析失败硬失败；CLI 非法值拒绝。
2. **握手强制**：服务端要求客户端证书（拒明文业务帧）；无 plain 回退。
3. **降级拒绝**：客户端不静默降级到明文。
4. **算法白名单**：fail-closed；服务端显式锁定唯一算法。
5. **证书/CA 绑定**：verify 回调校 issuer CN == 协商 ca_cn；双算法 slot。
6. **最低 TLS 版本**：生产上下文显式锁 TLS1.3（F1，已修复）。

## 库核心深度（tls_cert.c）
- 套件白名单（仅 TLS_SM4_GCM_SM3 / TLS_AES_256_GCM_SHA384）
- CRL 吊销（可选）
- 热加载安全性（app_data 重指向避免悬空指针）
- 审计（每握手记录 peer CN + IP）

## 覆盖性审计
全仓生产 `.c/.cpp` 的 `SSL_CTX_new` 仅：`libs/tls_cert.c:236`（已修复）、`libs/tls_keygen.c:1529/1534`（工具自身已设）、测试文件。rpc/dmsbtex/libobk/rdbcomm 均无直接 `SSL_CTX_new` → 修复无绕过路径。

## 发现清单
| ID | 严重度 | 状态 | 说明 |
|----|--------|------|------|
| F1 | 中 | 已修复(T0391) | 生产上下文未显式设最低 TLS 版本 |
| F2 | 低 | 建议 | CRL 仅当文件存在才启用，无 OCSP |
| F3 | 低 | 建议 | rpc GET_TIME 在 mTLS 强制下仍可预握手明文送达 |
| F4 | 低 | 建议 | dmsbtex dm_server_handshake 不检查 mtls_enabled |
| F5 | 低 | 设计说明 | 验证回调仅校 issuer CN，未校 subject/SAN 白名单 |

## 范围外
- 不修改任何代码（审查任务）。
- F2–F5 修复列为后续独立任务输入，不在本任务实施。

## 验收标准
- [ ] AC-1: review-report.md 覆盖全部 6 维度，引用 ≥5 处源码符号。
- [ ] AC-2: 每维明确判定 + 文件:行/函数名证据，可 grep 命中源文件。
- [ ] AC-3: F1–F5 状态明确，含覆盖性审计结论（仅 tls_cert.c 一处生产 SSL_CTX_new）。
- [ ] AC-4: 含总体 verdict 段与后续建议。
