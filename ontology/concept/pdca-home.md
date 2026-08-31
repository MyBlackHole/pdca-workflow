---
schema: pdca.asset/v1
id: ontology:concept/pdca-home
type: concept
layer: Knowledge
status: active
summary: PDCA_HOME 环境变量配置与仓库发现规则（两种模式：独立 / 外部项目）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# 全局仓库配置（pdca-home）

## PDCA_HOME

所有路径引用以 `$PDCA_HOME` 为基路径：

```bash
export PDCA_HOME=~/pdca-workflow
```

## 仓库发现规则

1. `PDCA_HOME` 环境变量为第一优先级。
2. 仅包含 `ontology/process/flow-plan.md` 的目录视为有效 workflow 仓库。
3. 外部项目通过 `scripts/init-external.sh` 初始化，在项目根目录生成引用 `$PDCA_HOME` 的 `AGENTS.md`。

## 两种模式

- **独立模式**：当前仓库即是 workflow root，`PDCA_HOME` 指向本项目。
- **外部项目模式**：`PDCA_HOME` 指向管理中心仓库，外部项目通过 init 脚本获得引用。

## 来源

- `（原知识层）global-repo-config.md`
