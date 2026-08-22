# 跟进：四模块协商语义与枚举统一重构（H4+M1，T0348）

## 问题陈述

- **现状**: 协商语义三种并存——rpc"优先客户端+回落"（rpc-server.cpp:244-249）、其余三模块"无条件采纳"、dmsbtex `dm_hs_decide()`（protocol.c:192-213）决策树生产/测试零调用且其依赖的 flags 在实际帧格式中无处承载；算法枚举 5 处重复定义 + 映射函数 4 份（RDB_HS/DM_HS/HS/OBK_HS）；libobk 握手 body 主机序与其它三模块网络序不一致（M5 关联）。
- **目标**: 选定唯一协商语义，枚举收敛到 libs 单一头文件，删除死代码。
- **差距**: T0348 审查报告 H4/M1/M5。

## 实现决策

- 协商语义：**语义 B**——服务端"无条件采纳客户端算法" + 白名单拒绝（依赖 T0357）。rpc 经 T0357 的 `hs_negotiate_algorithm` 已去除"回落服务端配置"，四模块语义实质一致；本任务聚焦统一表达、去除残留分支并固化测试。
- 枚举单一来源：收敛到 **libs/common.h**（算法枚举常量 + 名称映射函数），四模块 include 此头，删除各自 5 处重复定义与 4 份映射。
- 死代码清理：删除 dmsbtex 的 `dm_hs_encode`/`dm_hs_decode`/`dm_hs_decide` 及其协议层无调用残留；`dm_hs_decide` 决策树生产/测试零调用，随语义 B 一并移除。
- 测试策略：复用 T0357 四模块畸形算法拒绝测试；新增枚举唯一来源 grep 校验 + 跨模块互通集成测试（x86 目标）。

### 声明的测试接缝
- seam: rdbcomm/tests/handshake_session_test.c -> rdbcomm/server.c
- seam: libobk/test/session_test.c -> libobk/lib/logic/oracleCmdTbl.c
- seam: dmsbtex/test/session_test.c -> dmsbtex/network.c
- seam: rpc/tests/mixed_mtls_integration.cpp -> rpc/rpc-server.cpp

## 验收标准

- [ ] AC-1: 算法枚举与名称映射全仓库唯一来源（grep 无第二处定义）
- [ ] AC-2: 四模块协商决策路径唯一且有测试覆盖（含算法不匹配场景）
- [ ] AC-3: 死代码（dm_hs_encode/decode/decide 或其替代实现之外的残留）清零
- [ ] AC-4: 跨模块互通集成测试通过（x86 目标）

## 备注

- 非破坏性：运行时协商值不变（仅代码位置收敛与死代码移除），无需版本兼容评审即可进入 Do。
- 范围外：语义 A 的 flags 强一致扩展（破坏性协议变更）、M5 libobk 握手 body 字节序网络序改造（需对端同步升级，破坏性）均另排独立任务。
- 依赖：T0357 服务端白名单校验（已归档）。
