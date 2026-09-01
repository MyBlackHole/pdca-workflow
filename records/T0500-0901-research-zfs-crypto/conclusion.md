# 结论报告 - T0500 调研 OpenZFS 加解密实现

## 1. 任务目标回顾

按 PRD 目标，对 OpenZFS 加解密体系（含 SM4-GCM 国密扩展）做端到端源码调研，产出可追溯报告覆盖算法、密钥、数据路径、磁盘格式、完整性与平台适配。

## 2. 逐项验收对照

| AC | PRD 要求 | 证据 ID | 判定 | 说明 |
|----|----------|---------|------|------|
| AC-1 | 加密算法套件与参数已梳理 | ev-report | ✅ 通过 | 报告 §2 已列 ZIO_CRYPT 枚举（`zfs.h:1959`）、zio_crypt_table（`zio_crypt.c:198`）、KCF机制名（`common.h:86`）、ICP provider、CCM/GCM 差异及 SM4 参数；可 grep 到 `include/sys/fs/zfs.h:1959` 等锚点 |
| AC-2 | 密钥管理与生命周期已梳理 | ev-report | ✅ 通过 | 报告 §3 已剖 wrapping/master/HMAC/current 四层、PBKDF2/HKDF 派生、spa_keystore 三树（`dsl_crypt.h:148-166`）、dsl_crypto_params 与 load/unload/change 全生命周期及 ZAP 持久格式 |
| AC-3 | 数据加解密路径与调用链已梳理 | ev-report | ✅ 通过 | 报告 §4 已给 zio→spa_do_crypt→zio_do_crypt_uio 全链、salt/IV/MAC 生成与编码（`encode_params_bp:751`）、ZIL/DNODE/ABD 专处、dedup 可重现 IV 的安全讨论 |
| AC-4 | On-disk格式与属性接口已梳理 | ev-report | ✅ 通过 | 报告 §5 已说明 blkptr 编码（DVA[2]/cksum/prop）、ZAP 键名、dataset 属性（`zfs_prop.c:562`）、用户命令与 SPA_FEATURE_ENCRYPTION |
| AC-5 | 校验与完整性机制已梳理 | ev-report | ✅ 通过 | 报告 §6 已列三级 MAC（L0 AEAD / L1+ SHA512 / objset HMAC 32B）、非可移植位清零（`bp_zero...:916`）、ECKSUM 语义与写入/读取顺序 |
| AC-6 | SM4-GCM扩展及QAT/FreeBSD适配已梳理 | ev-report | ✅ 通过 | 报告 §7 已逐文件分解 16 份 patch（SM4 128/32轮、仅 GCM、wrapping 固定 AES-256-CCM、GCM_USE_GENERIC 强制、QAT回退、FreeBSD ENOTSUP）、影响面与测试缺口 |
| AC-7 | 报告已登记且收敛映射可验证 | ev-report + ev-convergence-map-v2 | ✅ 通过 | `evidence/report.md`（ev-report）+ `convergence-map-v2.json`（ev-convergence-map-v2）已登记；`convergence_issues` 0 证据，`evidence manifest` 含 2 活跃条目，`convergence.schema.json` 校验通过 |

**验证命令：**
```
PYTHONPATH=$PDCA_HOME/scripts python3 -c "from pdca_core import convergence_issues, repo_root; ..."
# convergence issues: 0
cat records/T0500-.../evidence/manifest.jsonl
# 含 ev-report (review, 7 criteria) 与 ev-convergence-map-v2 (convergence-map)
```

## 3. 偏差与风险

- 无偏差：所有 Plan 预测的 7 项均在 Do 阶段观测到对应产物，无实现与预期不一致。
- 风险：SM4-GCM 目前软实现，AVX 加速被禁用导致 GCM 吞吐预计低于 AES-GCM 约 15-30%；后续若需性能追平，需为 SM4 单独实现 PCLMULQDQ 表或引入独立 SM4 加速引擎。
- 遗漏：SM4 缺乏 zfs-tests 功能覆盖，已在报告 §9 建议补充；不影响本次纯调研任务的收敛。

## 4. 科学方法视角（Plan-Do-Check 偏差分析）

- Plan 假说：ZFS 加解密可沿“算法→密钥→路径→格式→完整性→适配”六层逐层追溯，且每层均有明确源码锚点。
- Do 观测：实际代码证实六层假说成立，且发现 `gcm_init_ctx` 的 SM4 分支重构与 wrapping 固定 AES-256-CCM 两个 Plan 未预见细节，丰富了执行认知。
- Check 判定：观测支持假说，无需下一轮 PDCA 调整；偏差仅为“SM4 性能路径”这一新增认知，已纳入报告建议。

## 5. 本体沉淀

- 本任务消费本体节点：`ontology:concept/pdca-task`（默认锚点）、`ontology:domain/backup-crypto` 系列（domain）。
- 产出沉淀意向：见 Act 阶段 disposition，拟在 `ontology/domain/zfs-crypto.md`（新建）对本次六层体系做结构化沉淀，供后续国密化开发直接复用。

## 6. Verdict 建议

建议 `confirmed` —— 7/7 AC 均有证据支撑，收敛映射可验证，无未覆盖验收项。

## 7. 证据清单

- `records/T0500-0901-research-zfs-crypto/evidence/report.md` — digest `sha256:2590f4ef106620bfd420d26b9825355e737a298761b491e22db3aa5d9442e9d4` — evidences `ev-report`
- `records/T0500-0901-research-zfs-crypto/evidence/convergence-map-v2.json` — digest `sha256:9a38bdcbf709b25fd9e6274132da4b390cdfac02648c3fb9a81aed6e34064836` — evidences `ev-convergence-map-v2`
- `records/T0500-0901-research-zfs-crypto/evidence/manifest.jsonl` — 含 superseded 记录 `convergence-map.json → v2`

## 8. 门禁状态

- `validate-convergence`: PASS (0 issue)
- `evidence_issues`: PASS (empty)
- `acceptance_criteria`: 7 checkbox 已满足（PRD 第 7 章）

---
*结论生成于 2026-09-01T11:24+08:00，待用户 `check_confirmation` 后进入 Act。*
