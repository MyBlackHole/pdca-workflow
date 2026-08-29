---
schema: pdca.asset/v1
id: ontology:pattern/mtls-four-module-supplementary-review
type: pattern
layer: Knowledge
status: active
summary: 四模块 TLS/mTLS 已 commit 修改补充审查范式
source_task: T0364
relations:
  specializes: [ontology:pattern]
  guides: [ontology:process/code-review-process]
attributes:
  - name: applicability
    desc: 多模块合并前对已 commit TLS/mTLS 改动的独立审查
    constraint: ""
    testable_signal: 缓冲区总长分配/strtol 全串校验/三态 bool 收敛均通过审查清单
---

# 四模块 TLS/mTLS 已 commit 修改补充审查范式（T0364）
# 四模块 TLS/mTLS 已 commit 修改补充审查范式（T0364）

> 适用：多模块合并前，对已经 commit 的 TLS/mTLS 相关 diff 做独立补充审查。
> 来源：T0364 对 T0354–T0363 四模块（rdbcomm / libobk / dmsbtex / rpc）已 commit 改动的逐 commit 复核。

## 审查清单（范式）

1. **栈溢出 / 缓冲区**
   - 缓冲区按 `header + body` 总长分配，非仅 body；
   - 重叠拷贝用 `memmove` 而非 `memcpy`（消除 UB）；
   - 读满总长，短读即失败。

2. **fail-closed 严格解析**
   - 数值解析 `strtol` 全串校验（仅合法值，否则拒绝）；
   - 算法名 `strcmp` 精确白名单，删别名；
   - 不存在 fail-open 分支（rpc CLI 解析同样 `strtol` + 全串 `*end != '\0'`）。

3. **死字段 / 死代码清理**
   - 纯删除须以编译 + 多套测试 PASS 佐证无残留引用；
   - 注意版本号 / 构建文件同步（T0360 漏改 `xmake.lua` 未落地，由 T0361 修正）。

4. **三态 bool 收敛**
   - 删除 CLI 临时 `parse_bool`，统一 `sec_resolve_bool`：分层严格校验仅 `"0"/"1"`，非法返回 `-1` 哨兵；
   - 载体字段一字段三用（配置打底 → CLI 覆盖 → 校验消费），`<0` 启动失败；
   - 顺带修复偶发 SIGPIPE（exit=141）flaky（补 `signal(SIGPIPE, SIG_IGN)`）。

5. **枚举 / map 收敛**
   - 算法枚举与名称映射收敛到 `libs` 单一来源，删重复声明；
   - 删 `dm_hs` 死代码，修 `common.h` include-guard 冲突。

## 残留 LOW 项（非阻塞，follow-up 候选）

- 四模块错误码前缀不统一（`RDB_HS_ERR_` / `DM_HS_ERR_` / `OBK_HS_ERR_` / `RPC_`）→ 归一到 libs 单一宏；
- 空串 env/ini 值当前当 `0`（禁用，fail-closed 方向安全）；如需更严格可显式拒绝；
- T0354 明文零握手直通路径补充端到端回归用例（高风险删改需证据）。

## 关联知识

- 全量回归 PASS ≠ AC 满足（畸形/未知值未覆盖时回落 bug 静默残留）→ 见 `mtls-server-alg-whitelist.md`；
- 多模块握手协商语义与枚举统一 → 见 `mtls-handshake-enum-unify.md`；
- 握手字节序一致性（M5）→ 见 `mtls-handshake-netorder-libobk.md`。
