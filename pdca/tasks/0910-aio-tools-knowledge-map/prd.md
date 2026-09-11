# aio-tools 知识地图构建 PRD（T2154）

## 背景

`rdb-feature-design` 的知识地图已经建好（`references/` 内 00-index + 5 份分册，路由矩阵 + 领域→代码 + 数据库实现地图 + 新旧边界 + 跨仓契约）。
本任务学习其构建方式（重点 `03-aio-cdm-knowledge-map.md`，2385 行），为本项目
`/home/black/Public/aio/aio-tools/6200/release`（C/Go 混合备份工具集）生成同等导航能力的知识地图。

关键差异（已实证）：本项目无三代模型、无 `dag_id` 契约，技术栈为 C/Go（xmake 构建），
手法照搬但做本土化替换——统一阶段链路改为备份/挂载/恢复等任务链，契约核对改为
rpc/rdbcomm 协议字段核对。

## 范围

全量覆盖：`fs-backup`（fsdeamon/fsclient/kernel/tools）· `rpc` · `rdbcomm` ·
`libs` 公共库 · `s3-tool`/`s3tools` · `xbsa` · `libobk` · `bwlimit` · `dmsbtex` ·
`huanweicloun-sdk-s3-data-backup` · 构建装配（`xmake.lua`/`install`/`main.go`）。

## 方法（R3 修订：05 为主骨架，03 为辅）

1. 仿 00-index 建路由矩阵：需求类型 → 分册章节行号，支持 offset 精准 Read。
2. 每分册以 05 手法为骨架：能力总览表（能力 → 代码 → 使用方，含使用方引用统计）·
   继承/分层体系 · 复用/扩展判断流程 · 影响范围表 · 不该放入的边界 · 项目级机制
   （构建 xmake / 版本装配 / 加密分发等，按实际代码取舍）。
3. 吸收 03 手法：核心任务链（入口 → 分发 → 核心实现 → 回写）写法 + 新旧边界裁决清单 +
   协议契约核对表（rpc/rdbcomm 字段级核对）。
4. 铁律照搬：先路由再验证后输出；每条路径三项实证（存在 / 现行链路 / 逐字一致）；
   文档滞后以代码为准并记录差异；无法确认即标记，不猜测。
5. 产出落点（R2 修订，R4 确定）：`/home/black/Public/aio/rdb-skills/skills/rdb-tools-design/`
   （SKILL.md + `references/` 分册体系，与 `rdb-feature-design` 同构），
   分册命名沿 `NN-<模块>-knowledge-map.md` 规则（R3 确认）。
6. 版本划分（R4 确认）：每份分册头统一标注适用分支（6.2.0.0、目录 6200/release、
   实证 git commit），分支差异单列章节；后续新分支增量补分册，不重写。

## 验收标准

- [ ] AC-1：`rdb-tools-design/references/00-index.md` 路由矩阵覆盖全部子系统，每行可按行号 offset 定位；各分册头含适用分支标注（6.2.0.0）。
- [ ] AC-2：各分册领域→代码表逐条通过代码实证（路径存在 + 被现行链路引用 + 名称逐字核对），差异清单已记录。
- [ ] AC-3：新旧边界裁决清单与协议契约核对表完整，新增需求可按“参考谁、改哪里”直接定位。

## 关联本体节点

```
ontology:concept/pdca-task
ontology:process/flow-plan
ontology:process/flow-do
```

## 拆分映射

- research 单任务不拆分：路由勘测 + 分册撰写 + 代码实证均在 Do 内一次完成。
