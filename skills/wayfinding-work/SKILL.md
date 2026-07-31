---
name: wayfinding-work
description: 推进已有 Wayfinder 地图，每 session 解决一张决策票。由 wayfinder 委托加载，不直接调用。
---

# Wayfinding — 推进地图（Work）

### 1. 读 MAP.md
看 destination 和 decisions-so-far。

### 2. 选票
取 frontier 票（open + unblocked）。

### 3. 执行
按 ticket type 加载对应技能：
- **research** → `$PDCA_HOME/skills/research/SKILL.md`
- **prototype** → `$PDCA_HOME/skills/prototype/SKILL.md`
- **grilling** → `$PDCA_HOME/skills/grilling/SKILL.md` + `$PDCA_HOME/skills/domain-modeling-work/SKILL.md`
- **task** → 直接执行

### 4. 记录
更新 ticket 为 `resolved`，一行摘要追加到 MAP.md Decisions So Far。

### 5. 消雾
此票揭示了新方向则开新票或移入 Not Yet Specified。

**规则**：每 session 只解决一张票（research 除外可并行）。地图清空后，最终输出进入正常 PDCA Plan → Do → Check → Act。
