# NBU数据加密实现分析（T2071）

> 来源：/home/black/Public/aio/F/143/NBU 目录二进制逆向
> 场景：research（纯调研报告，无代码产出）
> 边界：仅 NBU 现状，不做 SM4 缺口对比（按用户追问结论）

## 背景

NBU 目录为 NetBackup 10.3.0.1 二进制集合，需回答数据加密如何实现：算法底座、算法清单、密钥管理、落盘形态。

## 需求

1. 对 `bpkeyutil / bpkeyfile / bpbkar / bptm / bpdm / nbkmscmd / nbcryptocmd / libcmncryptocoreST / libnbsslST / libkmsSH` 做逆向取证。
2. 输出算法清单（AES/DES/3DES/BF/CAST/RC/Camellia + 摘要/随机数/GCM），每项给符号证据。
3. 还原三条链：客户端备份加密、介质/磁带调度加密、磁盘/MSDP 调度加密。
4. 产 `research-report.md`，含 ≥3 幅 mermaid 链路图，每图附来源。

## 验收标准

- [x] AC-1 算法清单可复现：报告列出 AES/DES/3DES/BF/CAST/RC/Camellia 及 GCM/FIPS，每项附 `nm/strings/objdump` 证据与复现命令
- [x] AC-2 加密链路可验证：≥3 幅 mermaid 图（客户端/磁带/磁盘-KMS），每图 1 个来源标注，链路函数名与二进制一致
- [x] AC-3 结论有证据锚定：每结论附可复核验证途径，证据已登记，收敛映射可检

## 关联本体节点

```
ontology:concept/cipher-mode-gcm
ontology:concept/cipher-mode-cbc
ontology:concept/cipher-mode-cfb
```

## 拆分映射

- 底座与算法清单 -> ontology:concept/cipher-mode-gcm
- 客户端加密链 -> ontology:concept/cipher-mode-cfb
- 介质与密钥管理链 -> ontology:concept/cipher-mode-cbc
