# 结论（T2071 NBU数据加密实现分析，含Tag/IV逻辑）

## 逐项判定

- AC-1 算法清单可复现：通过。证据 ev-evp、ev-ciphers、ev-mangle、ev-hard、ev-geninit、ev-digest、ev-kdf 均已登记，复现命令见 research-report-v4.md 第10节。
- AC-2 加密链路可验证：通过。证据 ev-client、ev-tape、ev-bpkeyfile、ev-nbkms、ev-nbcrypt、ev-msdp、ev-mdec、ev-eb2、ev-tagiv 支撑7幅mermaid图，每图1来源，新增4b.7 Tag/IV专节。
- AC-3 结论有证据锚定：通过。证据 ev-report4、ev-map6 已登记，映射覆盖全部AC。

## 总体 verdict

confirmed：报告247行，Tag/IV逻辑已落文档，每次加密独立12B随机IV与16B Tag，多块多组，重备必变。

## 本体沉淀

ontology:concept/nbu-data-encryption：新建概念节点，沉淀NBU三链加密模型与GCM多Tag规则。

## 偏差记录

- ev-report历经v2/v3/v4替换链，最终为ev-report4；ev-map最终为ev-map6，收敛唯一且valid。
