# 结论（T2125 存储国密落改调研重做）

## AC核验（逐章映射）

- AC-1 §3.2三态写：通过。证据`r2-report`（`main.cpp:954,1155/919/139`、`config.cpp:130`重验命令附报告）。
- AC-2 §3.2/§3.4读端与门禁：通过。证据`r2-report`（`fuse-file.cpp:823,914`、`obs-service count=2`、`main.cpp:1488`）。
- AC-3 §3.3 NFS清单：通过。证据`r2-report`（`enc-algo`零命中、`rpc-common.cpp:446`XOR、四字段清单）。
- AC-4 §四密钥管理：通过。证据`r2-report`（同钥/分离/轮换另立/丢钥丢数据四条）。
- AC-5 §3.1/§3.5/Y对齐：通过。证据`r2-report`（承接参数、Y矩阵、内测灰度）。
- AC-6 本体沉淀：待Act执行，计划见下节。证据`r2-prd-anchor`（PRD锚定三pattern）。
- AC-7 零改动：通过。证据`r2-zero`（目标仓`git status`0字节）。

## 偏差

- 本轮Grill含覆盖必问、AC逐章映射，未发现新缺口；旧票三缺口转为本轮沉淀项。
- 过渡门禁曾报PRD标题后缀与AC冒号格式问题，已修正（标题须精确`## 验收标准`、AC行`- [ ] AC-x: `）。

## 本体沉淀

- 决策：Act执行三项本体表达，均引用本record：
  1. `ontology:pattern/sm4-storage-encryption`追加修订记录R4（NFS清单四字段+密钥全量四条+门禁旧挂载清理+灰度边界）；
  2. 新建`ontology:pattern/sm4-nfs-encryption`（NFS预加密独立表达，specializes指向storage）；
  3. `ontology:pattern/sm4-s3-encryption`与`sm4-zfs-encryption`复核引用（已有T2107内容，不足再补）。
- 校验：归档前跑覆盖脚本（严格词表须零警告）+`check-research-ontology-settlement.py`，`disposition.reason`须含`ontology:`。
