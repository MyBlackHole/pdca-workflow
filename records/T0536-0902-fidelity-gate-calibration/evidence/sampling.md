# G6泛化门禁有效误报率抽样 — T0536 AC-1

> 方法：对 `audit-ontology-fidelity` 判为 `ATTR_GENERIC` 的124节点，随机种子42抽样20例，人工判定是否“有效误报”（L3定义：开发者未正向行动即误报）。

## 抽样清单（20例）

| # | id | 含可执行动词 | 判定 |
|---|----|--------------|------|
| 1 | linux-epoll-eventloop-multireactor-so-reuseport | 是 `python3 scripts/ontology-validate` | 有效误报（泛化但可执行） |
| 2 | benchmark-small-pack-streaming-decode | 是 | 有效误报 |
| 3 | ai-efficiency-unified-entrypoint-discipline | 是 | 有效误报 |
| 4 | rdb-config-audit-findings | 是 | 有效误报 |
| 5 | core-fsck-style-cli-healthcheck | 是 | 有效误报 |
| 6 | core-file-metadata-management-via-lmdb | 是 | 有效误报 |
| 7 | core-device-bucket-geometry-pointer-contract | 是 | 有效误报 |
| 8 | build-config-hide-static-lib-symbols | 否 | 真泛化 |
| 9 | benchmark-paired-comparison-noise | 是 | 有效误报 |
| 10| mysql-schema-nullable-contract | 是 | 有效误报 |
| 11| workflow-code-review-dual-axis | 是 | 有效误报 |
| 12| data-formats-t0250-mysql-parquet-physical-evidence-evidence | 是 | 有效误报 |
| 13| backup-xtrabackup-incremental-schemes | 是 | 有效误报 |
| 14| debugging-stream-frame-integration-traps | 是 | 有效误报 |
| 15| core-transactional-pointer-runner-publication | 是 | 有效误报 |
| 16| ai-efficiency-uplift-assessment-before-adoption | 是 | 有效误报 |
| 17| core-deterministic-interleave | 是 | 有效误报 |
| 18| core-discard-boundary-guards | 是 | 有效误报 |
| 19| data-formats-pg-to-parquet-path-benchmark | 是 | 有效误报 |
| 20| kernel-debugging-device-mapper-blk-mq-uaf-vmcore-method | 是 | 有效误报 |

**统计**：有效误报 19/20 = **95%**，真泛化 1/20 = 5%。

## 结论

当前“含‘检查本文件’即判泛化”过于敏感，95%泛化实则同时含可执行动词（如 `python3 scripts/ontology-validate`），按L3“有效误报”定义属过度执法（远超10%阈值）。**建议G6改为“含泛化短语且无required_verbs才拒”**，可将有效误报率从95%降至5%，符合L3编译期0%阈值（增量零容忍仅拒真泛化）。

Source: `scripts/audit-ontology-fidelity.py` 124泛化 + `ontology/.fidelity-exempt.json` + L3 CACM 10%阈值

## 复现

```bash
python3 -c "import json,random; rows=[json.loads(l) for l in open('/tmp/fidelity.jsonl')]; g=[r for r in rows if r['has_generic']]; print(len(g)); import random; random.seed(42); s=random.sample(g,20); [print(x['id']) for x in s]"
```
