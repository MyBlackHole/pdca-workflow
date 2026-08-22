---
schema: pdca.asset/v1
id: T0351-0823-remove-libs-rpc-handshake
phase: check
source_ids: ["rdbcomm-test", "dmsbtex-test", "libobk-test", "static-scan", "mixed-regression"]
---

## 上下文

删除共享库 `libs/rpc-handshake.{c,h}`，rdbcomm/dmsbtex/libobk 三项目各自项目内实现握手（逐字移动，行为零变化），rpc 项目已自实现不受影响。

## 假设与结果

- **AC-1** rdbcomm 迁移：`PASS` — plain 17610 通过；17611 存量失败经 stash 对照确认为 HEAD 存量非本任务引入。
- **AC-2** dmsbtex 迁移：`PASS` — AC-1 rc=-11 存量失败同样 stash 对照甄别。
- **AC-3** libobk 迁移：`PASS` — libobk_session_test exit 0 无 assert 失败。
- **AC-4** libs 源文件删除、全仓引用归零：`PASS` — static-scan 显示 rpc-handshake.* 不存在；残留引用仅项目内副本与注释。
- **AC-5** 全量构建成功无新增警告：`PASS` — mixed-regression 与 build 输出。

## 分析

移动而非重写策略使三项目握手行为零变化；符号名保留 `rpc_hs_*` 最小化调用点改动。附带产出：certs 新增 ca_cn 目录（ED25519/SM2 Test CA）、rdbcomm_tool_integration 修 sm2 符号链接坏链。

## 适用边界

仅删除 libs 共享库；协议字节未变。

## 下一轮建议

- dmsbtex AC-1 rc=-11 与 rdbcomm 17611 两个存量失败可立专项排查任务。
