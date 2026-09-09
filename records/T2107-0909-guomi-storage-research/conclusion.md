# 结论（T2107 存储国密加密方案落地调研）

## AC核验（每行可grep证据ID）

- AC-1 三类差距行号定位：通过。证据`guomi-research-report`（§1–§3复核命令：`main.cpp:919-923,954,1155`、`config.cpp:129-136`、`fuse-file.cpp:224,823,914`、`obs-service.cpp:309/370`、`rpc-common.cpp:446-447`）。
- AC-2 落改点清单：通过。证据`guomi-research-report`（§1三态统一+nonce、§2对象自适应+`meta_data_count` 2→3+过渡策略、§3 `--enc-algo`+清单）。
- AC-3 Y对齐矩阵：通过。证据`guomi-research-report`（§4：Y2/Y3/Y6/Y7本仓可改，Y1/Y4/Y5外部依赖，非目标与方案一致）。
- AC-4 报告门禁：通过。证据`guomi-research-report`（5图/7源/3URL，`check-research-web-evidence` valid）。
- AC-5 零代码改动：通过。证据`guomi-zero-ontology-proof`（目标仓`git status`空）。
- AC-6 本体锚定：通过。证据`guomi-zero-ontology-proof`（PRD锚定三pattern）；沉淀决策见下节。

## 偏差记录

- 建票triage误判development，走错半程后经用户纠正：T2099封存，T2107从零重走。本结论只基于T2107重验证据，不继承旧票草稿。
- 过程发现：本体沉淀校验只在Act触发，Plan/Do无提醒（`check-research-ontology-settlement.py`在plan期SKIP实测）；已补AC-6兜底。

## 本体沉淀

- 决策：Act强制回写（`scenario-research-first-gate` T0513起必须新建或更新本体节点），执行以下本体表达（每条修改对应节点，见AC-6清单）：
  1. `ontology:pattern/sm4-storage-encryption`追加修订记录R3（本报告§1–§4落改清单）；
  2. `ontology:pattern/sm4-s3-encryption`补F/143行号级落改细节并引用本record；
  3. `ontology:pattern/sm4-zfs-encryption`补承接清单并引用本record；
  4. `ontology:concept/pdca-scenario-boundary-rule`错配实例表新增T2099行（声明development/实际纯调研/期望research）；
  5. 新建`ontology:pitfall`节点记录Plan期本体计划无门禁提醒的空档（靠Grill必问本体兜底）。
- 关联节点：`ontology:pattern/sm4-storage-encryption`、`ontology:pattern/sm4-s3-encryption`、`ontology:pattern/sm4-zfs-encryption`。
- 校验：归档前跑`check-research-ontology-settlement.py`，`disposition.reason`须含`ontology:`。
