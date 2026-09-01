# 补充科学调研方法论本体：C4+Diátaxis+arc42+I2S2生命周期

## 背景

T0501以C4+Diátaxis为背书沉淀 `research-diagram-methodology` 多图模板，但仅覆盖 `C4 L2/ L1 + mermaid`，未显式本体化 `arc42 12节`、`I2S2 Research Lifecycle（OAIS Representation Information）`、`Experimental Workflow（分支/线性）` 3支科学范式，`research` 仍缺可复用的评估门禁与文档四象限结构。

## 目标

- 沉淀 `ontology/pattern/scientific-research-methodology.md` 根（`composed_of` 4支：C4+Diátaxis+arc42+I2S2），各支 `attributes.testable_signal` 可 `scaffold`
- 使后继 `T0501` 类ZFS Crypto研究可直接 `specializes` 该根，6图外加 `arc42:10` 质量与 `I2S2` 生命周期可追溯

## 范围

- 输入：`c4model.com` `diataxis.fr` `arc42.org` `I2S2 OAIS` `sci-draw experimental workflow`、`T0501` 已沉淀多图模板
- 输出：1根+4叶共5 pattern节点 + `skill-research` 增Diátaxis四象限校验 + 全绿
- 不做：不重写存量 `research-diagram-methodology`（增量 `relates_to` 关联）

## 功能需求

1. 根本体：`scientific-research-methodology` 4 `composed_of` 叶，`islands:0` 可 `graph`
2. C4支：4层级+4补充图（dynamic/deployment）+ 边缘交叉<3靶
3. Diátaxis支：四象限 `tutorial/how-to/reference/explanation` 各1检验句，可 `grep Diátaxis` 命中
4. arc42支：12节 checklist 可 `grep arc42` 命中
5. I2S2支：生命周期 `proposal→peer-review→experiment→processing→publish` + 绿色保育（编目/存档/保存）+ `Source: primary` 溯源
6. 接入：`skill-research` 增 `Diátaxis` 四象限与 `arc42:10` 质量门禁（`grep` 可检）

## 非功能需求

- `validate 0 issues, islands:0`，5节点均 `scaffold` 可产

## 验收标准

- [ ] AC-1 根+4叶已创建且 `validate` 通过且 `composed_of` 4边可 `graph` 追溯
- [ ] AC-2 C4/Diátaxis/arc42/I2S2 各1叶 `attributes` 可 `scaffold` 且含 `mermaid`/`Diátaxis`/`arc42`/`I2S2`
- [ ] AC-3 接入：`skill-research` 含 `Diátaxis` 四象限与 `arc42` 可 `grep` 命中
- [ ] AC-4 全绿 `islands:0` 且 `5节点 scaffold` 可产
- [ ] AC-5 收敛 valid:true

## 关联本体节点

```
ontology:pattern/scientific-research-methodology
ontology:pattern/scientific-research-c4
ontology:pattern/scientific-research-diataxis
ontology:pattern/scientific-research-arc42
ontology:pattern/scientific-research-lifecycle
ontology:pattern/research-diagram-methodology
```

## 拆分映射

- 根与C4 -> ontology:pattern/scientific-research-c4
- Diátaxis -> ontology:pattern/scientific-research-diataxis
- arc42 -> ontology:pattern/scientific-research-arc42
- I2S2生命周期 -> ontology:pattern/scientific-research-lifecycle
