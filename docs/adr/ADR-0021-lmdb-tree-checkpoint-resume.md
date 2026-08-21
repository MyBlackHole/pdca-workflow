# ADR-0021: LMDB 增量索引与 TREE checkpoint 续传
日期: 2026-08-13
状态: Accepted

## 背景

海量目录的本地增量索引需要低延迟、有界查询和事务回滚；递归 TREE 在网络断开或进程重启后需要避免从零重传已经确认落盘的批次。现有单文件 partial resume 不能证明目录级恢复安全，现有 LMDB backend 也缺少与 SQLite 对称的生产测试门禁。

## 候选方案

1. 仅保存路径游标：实现简单，但源文件变化、目录重排或远端 generation 变化时可能错误跳过数据。
2. 仅依赖目标端文件存在：无需新增 checkpoint，但无法区分旧内容、错误 options 和未完成的原子发布。
3. 逐批确认并绑定 source fingerprint、remote generation、options fingerprint：需要额外记录和确认帧，但可以在重启后安全 replay 未确认批次，并对无法验证的记录保守回退。

## 决策

选择方案 3。checkpoint 使用可选 capability；新 peer 在 bounded batch 完成后确认，旧 peer 回退既有 TREE replay。LMDB 与 SQLite 通过同一 procedural MetadataStore contract 暴露 checkpoint 读写，不依赖 LMDB mapped pointer，也不静默转换 cache 格式。

## 影响

安全性优先于跳过目录扫描：恢复仍可重新扫描源目录，但已确认且 fingerprint/generation/options 全部匹配的 payload 不重复发送。checkpoint 损坏、generation 不一致、source 变化、options 变化或确认缺失均触发 replay。实现增加持久化状态和协议边界，但不改变旧 peer 的 wire 语义。
