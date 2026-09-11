---
schema: pdca.asset/v1
id: T2180-0911-rdb-tools-call-chain-deepening
phase: check
source_ids:
  - t2180-skill-contract-v1
  - t2180-call-chain-index-v1
  - t2180-fs-call-chains-v1
  - t2180-rpc-rdbcomm-call-chains-v1
  - t2180-libs-call-chains-v1
  - t2180-s3-xbsa-call-chains-v1
  - t2180-build-runtime-routing-v1
  - t2180-validation-report-v1
  - convergence-map
---

# T2180 Check 结论：按 rdb-feature-design 颗粒度深化工具调用链

## 上下文

用户在首次 Do 启动后纠偏：“我需要的是调用链”，并指定 `rdb-feature-design` 为参照。T2180 因而撤销“23 个独立百科页、通用栏目、每工具强制配图”的旧方向，改为在现有 `SKILL.md + 00-index + 01–05 版本地图` 内，按每个外部可触发操作展开真实多层调用链。

## 假设与结果

Plan 假设是：若调用链像参照 skill 一样从真实入口逐层展开到分发、核心、跨端边界和返回路径，且索引能按工具及操作定位，`rdb-tools-design` 就能从“一行入口清单”升级为可直接用于需求定位和故障分析的调用链地图。

Do 观测支持该假设：23 个工具均被索引；公开操作清单覆盖 fs-cli 21 个 method、fsbackup_tools 5 个命令、afs-cli 18 个 method、rpc 19 个 MT 请求与 19 个 persistent opcode、XBSA 16 个 ABI、SBT2 11 个 API、DMSBT 13 个 ABI；新增 138 个去重 `path:symbol` 锚点，01/02/03/04 分册分别有 11/8/4/12 条至少五节点链。

## 分析

- **AC-1** ✅ 23 个工具均有独立调用链章节或明确分册落点，公开 method/subcommand/opcode/ABI 清单对照通过，无工具缺项（t2180-call-chain-index-v1、t2180-validation-report-v1）。
- **AC-2** ✅ 复杂链从入口、请求构造和真实分发条件展开到核心、边界和返回；抽查 snapshot、backup、restore、rdbcomm download/upload 和 S3/FUSE 链均采用 `path:symbol`（t2180-fs-call-chains-v1、t2180-rpc-rdbcomm-call-chains-v1、t2180-s3-xbsa-call-chains-v1）。
- **AC-3** ✅ `fs-cli↔fsdeamon`、`aio-speed↔aio-speedd`、`rdbcomm↔rdbcommd`、S3/FUSE、XBSA/SBT 均跨到真实对端或外部边界；代表性链超过五个符号节点（t2180-fs-call-chains-v1、t2180-rpc-rdbcomm-call-chains-v1、t2180-s3-xbsa-call-chains-v1、t2180-validation-report-v1）。
- **AC-4** ✅ FS_*、MT_*、persistent opcode、ioctl、rdbcomm opcode、socket/端口及外部 ABI 完成双端对照；afs-cli 的 6 个网络 method 因本基线无接收端而明确标为“未闭合”，未伪造对端（t2180-fs-call-chains-v1、t2180-rpc-rdbcomm-call-chains-v1、t2180-s3-xbsa-call-chains-v1）。
- **AC-5** ✅ `00-index.md` 同时支持“工具 + 操作”和“需求类型”路由；05 分册将构建 target 连接到对应运行链，并区分构建与运行状态（t2180-call-chain-index-v1、t2180-build-runtime-routing-v1）。
- **AC-6** ✅ 调用链状态使用 current/external/operator/build-only/isolated/deprecated，孤岛、外部 ABI 与真实现行链没有混用（t2180-skill-contract-v1、t2180-call-chain-index-v1、t2180-libs-call-chains-v1、t2180-s3-xbsa-call-chains-v1）。
- **AC-7** ✅ quick_validate、23 工具索引、公开操作、53 个 Markdown 引用、138 个源码锚点、协议双端和占位扫描全部通过（t2180-validation-report-v1）。
- **AC-8** ✅ aio-tools 产品树 `git status --short` 与 `git diff --stat` 均为空，HEAD 未改变；产物仅位于 `rdb-tools-design` 与 PDCA 记录（t2180-validation-report-v1）。

## 失败原因

无失败 AC。首次方案偏离已在进入实质实现前中止并回滚；T2180 的产物不包含该旧方案。

## 适用边界

- 静态源码只能证明 6.2.0.0 的调用关系和契约形状，不能证明实际部署中的端口可达、TLS/权限、内核装载或真实备份恢复成功。
- `afs-cli` 的 `list-file/lock-snapshot/unlock-snapshot/full-cache/snapshot-cache-stat/local-cache-stat` 发送端存在，但本基线找不到 TCP 接收端；结论保持“未闭合”。
- XBSA、OceanBase SBT、达梦 DMSBT 的真实数据库消费者在仓外，自带 test/simulator 只作为示例消费证据。

## 下一轮建议

只有获得部署包、其它仓库或历史版本证据时，才继续闭合 afs-cli 的 6 个网络 method；只有具备目标内核和第三方数据库环境时，才增加动态调用证据。本轮不应凭静态源码补写这些结论。

## 本体沉淀

- 已将 `ontology:domain/pdca/rdb-tools-independent-call-chain` 从 1.0.0 更新为 1.0.1。
- 新增的可复用规则是：调用链以外部可触发操作为最小单元；跨进程链必须双端定位；缺失接收端必须明确标记“未闭合”；构建 target 与运行时链分开表达。
- 来源 record：`T2180-0911-rdb-tools-call-chain-deepening`；更新理由：用户明确纠偏为“需要调用链”，并要求达到 `rdb-feature-design` 的逐操作、多层符号颗粒度。

## Verdict

- outcome: `confirmed`
- reason: 用户确认 T2180 已将调用链作为主体，并达到参照 skill 的逐操作、多层符号、跨端与返回路径颗粒度；8 条 AC 均有登记证据。
- verdict_id: `V2180`
- at: `2026-09-11T16:24:47+08:00`
