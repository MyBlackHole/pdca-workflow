# 调研项目 139 存在的潜在问题

## 背景

项目 139 历经 F-139 TLS 全栈、多个 bugfix（UAF/序列号/构建）及本次 8811 诊断修复（T0463），代码涉及 fs-backup、rpc、aip-speed/d、libobk、dmsbtex、rdb-config 等多域。需系统性调研现存设计/安全/可维护性问题，为后续改进提供输入。

此前 PDCA 已修复：
- T0463：fd 误判、日志透出等 4 文件
- 扩大范围：tools sprintf、snapshot snprintf 等

但仍有全量非 openssl 1677 文件未深度覆盖，需扩大至全项目（排除 third_party/openssl）进行调研。

## 目标

以 `code-review-checklist` 与 `secure-coding` 为框架，对项目 139 非 openssl 全量做研究型扫描，输出问题清单，每条含文件行号、严重度、类别、证据引用，不直接改代码。

## 验收标准

- [ ] AC-1：覆盖 6 维度（正确性/安全性/性能/可维护性/错误处理/测试）中至少 4 维度各有实例
- [ ] AC-2：每条问题可 grep 到文件行号，附最小复现/日志/代码片段证据
- [ ] AC-3：输出可行动清单，按 CRITICAL/HIGH/MEDIUM/LOW 分级，含修复建议与影响范围

## 非目标

- 不直接修改业务代码（纯调研，`research` 类型）
- 不重复深入已归档 T0463 的 4 文件已修复项（仅引用）
- 不处理 third_party/openssl 自身问题

## 关联本体节点

```
ontology:concept/pdca-task
ontology:domain/backup
```

## 风险

- 全量扫描耗时，需抽样 + 重点 hotspots（近变更高频文件）
