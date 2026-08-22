# 跟进：四模块协商语义与枚举统一重构（H4+M1，T0348）

## 问题陈述

- **现状**: 协商语义三种并存——rpc"优先客户端+回落"（rpc-server.cpp:244-249）、其余三模块"无条件采纳"、dmsbtex `dm_hs_decide()`（protocol.c:192-213）决策树生产/测试零调用且其依赖的 flags 在实际帧格式中无处承载；算法枚举 5 处重复定义 + 映射函数 4 份（RDB_HS/DM_HS/HS/OBK_HS）；libobk 握手 body 主机序与其它三模块网络序不一致（M5 关联）。
- **目标**: 选定唯一协商语义，枚举收敛到 libs 单一头文件，删除死代码。
- **差距**: T0348 审查报告 H4/M1/M5。

## 实现决策（待 Plan 阶段评审）

- 候选语义 A（推荐）：dm_hs_decide 强一致模型——flags 显式表达 mtls 意愿 + 双端算法一致性校验；需扩展 rdbcomm/sbt/dmsbtex 帧格式携带 flags（破坏性协议变更）
- 候选语义 B：维持"无条件采纳客户端"+ 服务端白名单（依赖 T0357），仅统一 rpc 回落行为并删除 dm_hs_decide 死代码
- 枚举单一来源：libs/common.h 或新建 libs/hs_protocol.h
- M5 字节序：libobk 握手 body 改网络序（需对端同步升级，评审版本兼容策略）

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

破坏性协议变更（帧格式/字节序），需版本兼容策略评审后进入 Do；建议排在 T0357/T0358 之后执行。
