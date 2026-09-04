# 调研 F-139 最后一次提交 d3b99ac8：TLS/mTLS全栈、签发加固与模板自解释的 squash 需求

## 背景

目标路径 `/home/black/Public/aio/aio-tools/6200/F/139` 的最后一次提交 `d3b99ac8` 为 **squash 需求提交**，合并原分散的 4 次提交（`F-139 TLS全栈 + B-T0451 UAF + B-T0457 回退熵/UB + F-T0458 rdb-cfg 模板`）为单次 `F` 类需求，便于版本归一与发布。`git show --stat HEAD` 显示 `4183 files`（含 `third_party/openssl4` 全量），核心业务变更为 `TLS/mTLS 全链路` + `tls-keygen 签发链路` + `rdb-cfg gen 模板`。

输入锚点：
- `git -C F/139 show --stat HEAD:4183 files` + `git log --oneline -1:d3b99ac8`
- `file: F/139/libs/tls_keygen.c:EVP_PKEY_free 时序` — T0451 UAF 修复
- `file: F/139/libs/rdb-config.h:allowed_values` — T0458 模板自解释
- `file: F/139/xmake.lua:1` — 7 组件版本一次性递进（`libobk/rpc/dmsbtex/rdbcomm/tls_keygen/rdb_cfg/oss`）

## 目标

产 `research-report.md`（`≥3 mermaid + ≥3 Source` + 可重跑清单），覆盖：
1. **squash 全景**：4 提交合并为 1 需求的 `T0451/T0457/T0458` 关联与 `F-139` 原量边界
2. **三线实现**：`TLS/mTLS 全栈`（`dmsbtex/libobk/rpc/fs-backup/oss` 全链路进程上下文化）+ `签发加固`（`EVP_PKEY_free` 时序/`RAND_bytes` 63 位随机/`int64` 消 UB）+ `模板自解释`（`allowed_values/[min,max]/最大长度` 三类约束展示）
3. **影响与版本**：`mTLS 全链路 5 模块` + `tls-keygen 双算法` + `rdb-cfg gen` 注释 3 类约束 + `7 组件` 版本递进（`libobk 1.0.0.1 + rdb_cfg/oss 1.0.0.1 首版` 等）

## 范围

- 输入：`F/139` 的 `d3b99ac8` 单次提交（`git show HEAD` 全量，`4183 files` 含 `third_party/openssl4`）
- 输出：`research-report.md` + `records/<id>/` 证据 + Check 本体沉淀
- 不做：不改代码、不重跑 `xmake test 51/51`、不压测 `RAND_bytes`

## 功能需求

1. **squash 关联**：`T0451/T0457/T0458` 的 `UAF/熵/UB/模板` 四遗留如何被 `F-139` 全栈收口为单需求
2. **三线实现图集**：TLS 全栈（`init_config` 收口 + `mTLS fail-closed`）/ 签发加固（`RAND_bytes` 回退 `clock_gettime^pid^&serial`）/ 模板自解释（`config_kv_def_t.allowed_values` 通用展示）各 1 `mermaid`
3. **影响矩阵**：`libobk/dmsbtex/fs-backup/rpc/oss` 5 模块 × `TLS` 链路 + `tls-keygen` 双算法 + `rdb-cfg gen` 3 类注释
4. **版本递进**：`7 组件`（`libobk/rpc/dmsbtex/rdbcomm/tls_keygen/rdb_cfg/oss`）的 `xmake.lua` 一次性递进表可重跑（`grep -n version xmake.lua`）

## 验收标准

- [ ] AC-1 `research-report.md` 含 7 段且 `mermaid≥3` `Source:≥3`，三线实现图各≥1
- [ ] AC-2 squash 全景可检：`git log fe9d4364..HEAD` 仅 1 条 `F` 且 `4 提交` 关联可 `git show` 溯
- [ ] AC-3 三线实现可回溯：`tls_keygen.c:EVP_PKEY_free` 时序 + `RAND_bytes` + `rdb-config.h:allowed_values` 各 `file:line`
- [ ] AC-4 影响与版本可重跑：`5 模块` 影响矩阵 + `7 组件` 版本表（`xmake.lua/version.log.in`）与 `git show` 一致
- [ ] AC-5 已 register-evidence 且 conclusion 含 `ontology:`/`records-only` 决策过 settlement

## 关联本体节点

```
ontology:concept/pdca-task
ontology:pattern/scientific-research-methodology
ontology:entity/aio-tools-6200-release
```

## 拆分映射

- squash 全景 -> report#发现.squash
- 三线实现 -> report#发现.TLS/签发/模板
- 影响与版本 -> report#发现.影响
