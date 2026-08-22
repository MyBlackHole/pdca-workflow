# T0359 设计 — 四模块协商语义与枚举统一（语义 B）

> 方案方向已 Grill 确认（语义 B / 枚举收敛 libs/common.h / 删除 dm_hs_decide 死代码）。
> 非破坏性：运行时协商值不变，仅代码位置收敛与死代码移除。

## 1. 枚举与映射单一来源

**现状（待 Do 阶段 grep 复核）**：算法枚举在 `RDB_HS_*` / `DM_HS_*` / `HS_*` / `OBK_HS_*` 共 5 处重复定义；名称映射函数 `rdb_hs_algorithm_name` / `dm_hs_algorithm_name` / `obk_hs_algorithm_name` / `hs_algorithm_name` 共 4 份实现。

**目标**：
- 在 `libs/common.h` 新增统一枚举（值保持不变：SM4=1 / AES=2 等）与统一名称映射函数（单一实现）。
- 四模块协议头改为 `#include "common.h"`，删除本地枚举定义与映射函数，调用统一入口。
- 兼容性约束：迁移前后运行时枚举值、错误码（0x8005）必须逐字节一致；Do 阶段以 grep 契约 + 现有测试守卫。

## 2. 死代码清理

- dmsbtex `protocol.c`：`dm_hs_encode` / `dm_hs_decode` / `dm_hs_decide`（决策树生产/测试零调用）确认无引用后删除；其依赖的 flags 字段在实际帧格式中无处承载，随语义 B 一并移除。
- Do 阶段 grep `dm_hs_decide|dm_hs_encode|dm_hs_decode` 全仓确认零调用再删。

## 3. 协商语义统一（语义 B）

- 四模块服务端入口语义已实质一致：rdbcomm/libobk/dmsbtex 为"采纳客户端算法 + 白名单拒绝"（T0357 落地）；rpc 经 `hs_negotiate_algorithm` 去除"回落服务端配置"（T0357 落地）。
- 本任务：固化该语义为单一表达，去除任何残留的回落/特殊分支；跨模块互通集成测试确认一致。

## 4. 测试策略

- **枚举唯一来源契约**：grep 断言全仓仅 `libs/common.h` 一处枚举/映射定义（对应 AC-1）。
- **复用 T0357 畸形拒绝测试**：四模块畸形算法值帧 → 回 ERR_ALGORITHM(0x8005)，未回落（对应 AC-2 算法不匹配场景）。
- **跨模块互通集成测试（x86 目标）**：rdbcomm↔rpc、libobk↔dmsbtex 等配对互通，协商值一致（对应 AC-4）。
- **死代码清零**：grep 断言 `dm_hs_*` 残留为零（对应 AC-3）。

## 5. 范围外（另排独立任务）

- 语义 A 的 flags 强一致扩展（破坏性协议变更）。
- M5：libobk 握手 body 主机序 → 网络序改造（需对端同步升级，破坏性）。

## 6. 风险

- 枚举值语义漂移：迁移时逐值对照 `libs/common.h` 与四模块原定义。
- 映射函数行为差异：四份原映射若有命名差异，统一后以统一名为准，测试用例覆盖命名边界。
