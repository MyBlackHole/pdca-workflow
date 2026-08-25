# 审查报告：HEAD 提交 004ebafe（T3963）

## 审查对象

`004ebafe` 【F-T3959】libobk: FileTransferAgent 支持 --mtls-enable/--tls-algorithm CLI 参数
（20 files, +562/-177，已推送至 origin/6.2.0.0/F/139）

## ⚠️ 重大发现：提交为三个逻辑变更的混合体

git reflog 显示该分支经历了一次 rebase（T3959 被 amend 两次），**T3961 提交（5a6017f7 服务端算法锁定）未被 pick 而其改动连同工作区用户未完成改动一并被吞入本次提交**。提交信息仅描述 T3959，与实际内容严重不符。

实际包含：

| 来源 | 内容 | 文件 |
|------|------|------|
| T3959（信息所述） | FTA CLI 参数 + sbt_server_tls_config_init 签名扩展 | libobk/main.c、oracleCmdTbl.h/c |
| T3961（被吞并） | 四模块服务端算法锁定+无默认值+cli_algorithm 去重+e2e S18/S19 | rpc-config.h/cpp、main.cpp、rpc-server.cpp、rdbcomm/server.{c,h}、rdbcommd-main.c、dmsbtex/network.c、oracleCmdTbl.c、mixed_mtls_integration、e2e 脚本、xmake.lua 版本号 |
| 用户未完成改动（被裹挟） | 删除 sec_tls_client_cert_paths 及 10 个 key/env 宏；dmsbtex/sbt.c 格式化+create_dir→mkdir_path；dmsbtex/xmake.lua add_deps(tools) | libs/rdb-config.c/h、dmsbtex/sbt.c、dmsbtex/xmake.lua |

## 逐项发现

### CRITICAL-1 提交信息与内容严重不符
- 信息称"协议帧与握手逻辑零变更"，实际含四模块握手协商锁定语义变更（rpc-server.cpp:261 等）。
- 信息称"libobk_version 1.0.1.4 -> 1.0.1.5"，实际 xmake.lua 同时升了 rpc 3.6.4.26 / rdbcomm 1.0.2.4 / libobk 1.0.1.6 / dmsbtex 1.1.0.5。
- 影响：bisect/blame 误导；回滚 revert 该提交会连带撤销锁定功能与用户清理。
- **已推送远端，无法安全 amend。**

### CRITICAL-2 未完成改动被固化
- libs/rdb-config.c/h 的删除属用户进行中的工作（sec_tls_client_cert_paths 及关联宏整体移除）。
- 已验证：被删符号全仓库零残留引用（含 .go）；全量 xmake 构建通过——功能上自洽。
- 但"未完成"状态无法从历史判断，且 rdb-config.h 公共头收缩对下游是接口变更。

### HIGH-1 混合提交的回滚粒度丢失
- revert 此提交将同时撤销 FTA CLI、算法锁定、证书 API 收缩三件事，与"回滚方案: revert 本 commit"的描述矛盾。

### 验证健康度（缓解因素）
- 全量 xmake 构建通过；mixed_mtls_integration AC-1~9（含锁定用例）通过；libobk/dmsbtex session_test 通过。
- 功能完整性不受混合影响——问题在工程治理而非代码质量。

## 建议

1. **接受现状 + 文档化**（推荐，已推送）：追加一个说明性 commit 或在分支 README/CHANGELOG 记录"004ebafe 实际包含 T3959+T3961+证书API清理 三项变更及真实版本号"。
2. 若团队规范允许 force push 个人功能分支：软重置后拆分为三个语义化提交（T3959 / T3961 / chore-cleanup）。
3. 流程改进：rebase 前确保工作区干净（stash 或先行提交），避免 autostash/脏区混入。

## 验证记录

- 被删符号残留引用 grep = 0（6 个符号）
- 全量构建 ok；mixed_mtls_integration AC-9 锁定用例 PASS 确认 T3961 功能完整混入
