---
schema: pdca.asset/v1
id: ontology:domain/skill-wayfinding-work
name: wayfinding-work
summary: Wayfinding work for navigating complex task flows.
description: 推进已有 Wayfinder 地图，每 session 解决一张决策票。由 wayfinder 委托加载，不直接调用。
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/domain-model
---

---
name: wayfinding-work
description: 推进已有 Wayfinder 地图，每 session 解决一张决策票。由 wayfinder 委托加载，不直接调用。
---

# Wayfinding — 推进地图（Work）

### 1. 读 MAP.md
看 destination 和 decisions-so-far。

### 2. 选票
取 frontier 票（open + unblocked + **unclaimed**）。

### 2.5 认领（claim）
选定票后、执行前，**立即认领**，防止并发 session 重复处理：

- 在票状态写入 `claimed-by: <session-id>`，标记 `in-progress`。
- 只有 `open + unblocked + unclaimed` 的票是可选 frontier；已认领票对并发 session 不可见。
- 认领用 `scripts/check-ticket-claims.py` 状态机（见下文），产生 `tickets/claims.jsonl`。
- 并发 session 读取 MAP 时跳过已认领票。

### 3. 执行
按 ticket type 加载对应技能：
- **research** → `$PDCA_HOME/skills/research/SKILL.md`
- **prototype** → `$PDCA_HOME/skills/prototype/SKILL.md`
- **grilling** → `$PDCA_HOME/skills/grilling/SKILL.md` + `$PDCA_HOME/skills/domain-modeling-work/SKILL.md`
- **task** → 直接执行

### 4. 记录
更新 ticket 为 `resolved`（用 `check-ticket-claims.py resolve` 清除 claim），一行摘要追加到 MAP.md Decisions So Far。

### 5. 消雾
此票揭示了新方向则开新票或移入 Not Yet Specified。

## Ticket claim 状态机

用 `scripts/check-ticket-claims.py` 维护认领状态（输出 `tickets/claims.jsonl`）：

```bash
# 认领（重复认领返回非零，报 ALREADY_CLAIMED）
python3 "$PDCA_HOME/scripts/check-ticket-claims.py" claim --ticket TK-1 --by sess-a
# 解决并清除 claim（非认领者 resolve 返回非零，报 NOT_CLAIMANT）
python3 "$PDCA_HOME/scripts/check-ticket-claims.py" resolve --ticket TK-1 --by sess-a
```

- claim → in-progress；resolve → resolved 并清除 claim，之后可被再认领。
- 冲突检测：同一票被两 session 同时 claim 时后者被拒，冲突率可统计。
- claim → resolve 的单票完成时间可归因到 session（可证明指标）。

**规则**：每 session 只解决一张票（research 除外可并行）。地图清空后，最终输出进入正常 PDCA Plan → Do → Check → Act。

## 已知坑

- 两 session 同时 claim 同一票时后者被拒（冲突检测）；勿重复认领在途票（T0265）。
- `tickets/claims.jsonl` 是唯一状态源；绕过 claim 直接改票文件会被并发状态机覆盖。
