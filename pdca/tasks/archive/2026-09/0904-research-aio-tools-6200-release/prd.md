# 调研 aio-tools 6200/release 全景：14 模块架构、版本与构建链路

## 背景

目标路径 `/home/black/Public/aio/aio-tools/6200/release` 为 aio-tools 仓库 `6.2.0.0-release` 分支的 release 快照（`git log` 顶端 `fe9d4364 B-1912 libdmsbtex 1.1.0.0->1.1.0.1`），工作区干净、与 `origin/6.2.0.0-release` 一致。顶层含 14 个业务模块 + `libs` 公共库 + `third_party` + `xmake.lua` 总控构建 + `.gitlab-ci.yml` 四阶段流水线。历史 PDCA 已围绕该仓库的 `fs-backup/fsdeamon` 链路做过 T0457 等缺陷定位（8811 端口 hostfwd、aio-speedd、fsbackup.ko 协同问题），但缺乏对 6200/release 全景的系统性调研。本任务作为纯结论性调研，不产可测试代码，产出 `research-report.md` 供后续开发/重构决策复用。

输入锚点（primary sources）：
- `file: /home/black/Public/aio/aio-tools/6200/release/xmake.lua:1` — 总控版本与 `includes()` 清单
- `file: /home/black/Public/aio/aio-tools/6200/release/.gitlab-ci.yml:1` — CI 四阶段
- `file: /home/black/Public/aio/aio-tools/6200/release/version.log.in:1` — 17 产物版本映射
- `file: /home/black/Public/aio/aio-tools/6200/release/build/version.log:1` — 实际生成版本
- `git -C /home/black/Public/aio/aio-tools/6200/release log --oneline -20` — 近期 B-1912/B-2005/B-2053 等修复脉络

## 目标

对 6200/release 做一次可回溯、可重跑的系统性调研，输出 `research-report.md`（含 ≥3 mermaid 图 + ≥3 Source 引证 + 每结论可验证途径），覆盖：

1. **全景架构**：14 模块职责、依赖关系、产物清单（C4 L1/L2）。
2. **版本与分支策略**：`xmake.lua` 11 个版本变量、`version.log.in`/`build/version.log` 双层映射、`version.h` 生成链路。
3. **构建与 CI**：xmake 总控、`libs`/`rpc`/`fs-backup` 等子 `xmake.lua` 组织、`.gitlab-ci.yml` 的 check_message/test/get_version/sync_version 四阶段与 aio-public-module 版本同步。
4. **核心链路采样**：至少深入 `rpc(aio-speed/aio-speedd)`、`fs-backup(fsdeamon/fs-cli/fsbackup.ko)`、`rdbcomm`、`s3tools(s3file/s3mount)` 四条主链路，给出时序/状态机。
5. **本体沉淀决策**：明确是否抽取可复用本体节点（若含可复用模式/清单则本体化，否则 records-only）。

## 范围

- 输入：仅 `/home/black/Public/aio/aio-tools/6200/release` 快照（含 `build/` 已生成物作为观测样本，不重新全量编包除非验证需要）
- 输出：`research-report.md` + `records/<record-id>/` 证据登记 + Check 阶段本体沉淀决策
- 不做：不改业务代码、不做跨分支 diff、不做性能压测、不产可执行重构

## 功能需求

1. **目录与度量**：盘点顶层 20 条目 + 488 源码文件（不含 build/.xmake/third_party）+ 18.9 万 LOC 分模块分布表；给出 `find ... | wc -l` 可重跑命令。
2. **版本体系**：梳理 `xmake.lua:rpc_version/fsdaemon_version/rdbcomm_version/.../fsbackup_kernel_version` 11 变量 → `version.h.in/version.log.in` → `build/version.h + build/version.log` → `tools-versions.txt` 同步链路；核对 `build/linux/x86_64/release/` 产物版本文件一致性。
3. **构建体系**：解析总 `xmake.lua` 的 `includes()` 顺序、公共 `add_cxflags/add_rules`、`makeFsbackup` Go 目标特殊处理；采样 2-3 子模块 `xmake.lua` 说明库/可执行目标划分。
4. **CI 流水线**：逐阶段解读 `.gitlab-ci.yml` 的 workflow rules、cache key、image、sync_version 的远程分支检测/rebase/MR 创建逻辑。
5. **模块职责矩阵**：14 模块一行一职责 + 关键入口文件 + 产物 + 版本号（见 `xmake.lua` 与 `build/*.version`）。
6. **核心链路深潜**：`rpc` 的 `aio-speedd` (服务端) ↔ `aio-speed`/`rpc-client` ↔ `fsbackup.ko ioctl` 链路；`fsdeamon` 的多源监控/备份调度；`rdbcomm`/`s3tools` 的关键流程（各配 mermaid 时序/状态机）。
7. **历史关联**：回链 `T0457 fsbackup 8811 connect failure` 等存量任务，标注 6200/release 相对于历史修复点的版本演进（B-2005 rpc_recv_msg EOF、B-1912 libdmsbtex 等）。
8. **研究方法自检**：报告含 `研究方法` 章，声明 Diátaxis 象限归属与 arc42 自检结果（`grep -q Diátaxis/arc42` 可检）。

## 非功能需求

- 仅采信 primary source（官方 doc / 源码 file:line / xmake/git 实测）；二手转述降级为"待验证假设"并标置信度
- 报告 UTF-8 bytes 预算显式记录；`grep -c '```mermaid' ≥3` 且 `grep -c 'Source:' ≥3` 门禁
- 每条关键结论附可重跑命令或 file:line 引用

## 验收标准

- [ ] AC-1 `research-report.md` 已生成且含 `## 调研目标/## 方法/## 发现/## 结论与建议/## 术语表/## 参考资料` 七段结构，且 `grep -c '```mermaid' ≥3`、`grep -c 'Source:' ≥3`
- [ ] AC-2 架构图 C4 L2 + 逻辑时序图 + 生命周期/状态机图各 ≥1，且每图附 `Source:` 引证到 file:line 或官方 doc
- [ ] AC-3 模块职责矩阵覆盖 14 模块 + libs + third_party，含版本、入口文件、产物三列，与 `xmake.lua`/`build/version.log` 一致且可 `xmake f --yes` 重跑验证
- [ ] AC-4 版本/构建/CI 三链路可重跑：`xmake f --yes && cat build/version.log`、`git log --oneline -20`、`cat .gitlab-ci.yml` 均在报告中给出验证途径
- [ ] AC-5 核心链路 ≥2 条有 mermaid 时序/状态机且链到源码 file:line（如 `rpc/rpc.cpp:fsbacup_dev_ioctl`、`fs-backup/fsdeamon/*.cpp`）
- [ ] AC-6 已 `register-evidence` 且 Check 阶段 `conclusion.md` 含 `## 本体沉淀` 显式决策（`ontology:` 或 `records-only`），`meta.disposition.reason` 含关键词且通过 `check-research-ontology-settlement.py` 校验

## 关联本体节点

```
ontology:concept/pdca-task
ontology:pattern/scientific-research-methodology
ontology:pattern/research-diagram-methodology
```

## 拆分映射

- 全景/版本/构建/CI -> research-report.md#发现.全景
- 核心链路深潜 -> research-report.md#发现.链路
- 历史关联与演进 -> research-report.md#结论
