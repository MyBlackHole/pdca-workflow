# openssl替换gmssl SM4审查（T2151·纯调研）

## 背景

s3file/s3mount用GmSSL底API（`sm4_cbc_padding_*`等），本仓`third_party/openssl4`实为3.x线（含provider SM4-GCM/CCM）。
审查能否替换及改写代价，结论沉淀`sm4-s3`节点。不改代码。

Grill（round1-2，均captured:true）：全项审查；锚定s3节点，章节=CBC对照/GCM对照/构建链接。

## 目标

API逐项对照表 + 构建链接归属 + 替换结论（可行/代价/前提），沉淀s3节点。

## 范围

输入：`s3tools`调用点、`third_party/gmssl/include/gmssl/sm4.h`、`third_party/openssl4`（evp.h/provider）。
输出：`research-report.md` + s3节点修订。不做：不改代码、不切库验证。

## 验收标准

- [ ] AC-1: CBC对照：4个GmSSL底API逐项给出openssl EVP等价（`EVP_sm4_cbc`+padding语义差）
- [ ] AC-2: GCM对照：GmSSL `sm4_gcm_*`对openssl provider SM4-GCM（含硬件加速文件存在性）
- [ ] AC-3: 构建链接：s3file链`gmssl`与`ssl/crypto`的归属（xmake）及openssl4是否参与构建
- [ ] AC-4: 本体沉淀：结论入`sm4-s3`节点，覆盖脚本零警告
- [ ] AC-5: 全程零代码改动

## 关联本体节点

```
ontology:pattern/sm4-s3-encryption
ontology:pattern/sm4-storage-encryption
ontology:concept/pdca-task
ontology:concept/pdca-evidence
```

## 拆分映射

- CBC/GCM对照 -> ontology:pattern/sm4-s3-encryption
- 构建链接与结论 -> ontology:pattern/sm4-s3-encryption
