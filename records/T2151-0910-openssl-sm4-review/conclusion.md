# 结论（T2151 openssl替换gmssl SM4审查）

## AC核验

- AC-1 CBC对照：通过。证据`ossl-report`（4API→EVP等价表，`evp.h:1094`）。
- AC-2 GCM对照：通过。证据`ossl-report`（legacy无GCM、provider有`cipher_sm4_gcm.c`+硬加速，须走fetch接口）。
- AC-3 构建链接：通过。证据`ossl-report`（s3链预编译gmssl+系统ssl/crypto；libs静态编openssl4；全仓零EVP_sm4调用）。
- AC-4 本体沉淀：待Act执行（结论入`s3`节点）。证据`ossl-prd`（锚定）。
- AC-5 零改动：通过。证据`ossl-zero-v2`（目标仓0字节）。

## 偏差

- 初判曾误言“不可替换”（只查legacy漏provider），用户纠正后深查整树反转结论；教训：vendored第三方库须全树grep，不可只看主头文件。

## 本体沉淀

- 决策：Act在`ontology:pattern/sm4-s3-encryption`追加“SM4库选型”节：GmSSL现状（底API直调）vs openssl4 provider方案（CBC-EVP/GCM-fetch/硬加速）、替换三前提（调用层重写/xmake切包/互通测试），引用本record。
- 校验：`check-research-ontology-settlement.py`，`disposition.reason`须含`ontology:`。
