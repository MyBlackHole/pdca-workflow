---
schema: pdca.asset/v2
id: ontology:concept/ontology-creation-gate
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.0
summary: 本体创建与发布审查
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/ontology-asset
  - ontology:concept/ontology-rule-type-controlled
  - ontology:concept/ontology-rule-non-dangling
  - ontology:concept/ontology-rule-acyclic
  - ontology:concept/ontology-rule-attr-testable
  - ontology:concept/ontology-rule-richness
  - ontology:concept/ontology-rule-guides-range
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-evolution
  - ontology:concept/ontology-adoption
  - ontology:concept/task-decomposition
---

# 本体创建与发布审查

## 适用条件

新建/修订候选并准备发布为活动本体时执行；普通任务未改本体不强制全库扫描。

## 输入

候选内容、原版本、来源证据、任务基线及变更理由。按需读取关联ontology-rule节点。

## 动作

1. 检查首段YAML、必需字段、唯一身份、目录分组、受控词表和版本差异。
2. 递归检查引用和受影响的反向依赖；类/实例关系范围、按关系区分的循环、属性可验证性及有意义关联逐项审查。
3. 验证行为主张的真实证据、正反例与适用边界。结构检查通过不自动批准内容真实；外部源码未提供时不能宣称重跑通过。
4. 比较已有知识和当前活动规则，记录重复、冲突、兼容性和候选处置；涉及核心规则发布需独立授权，不能自行修改本任务验收。
5. 写发布审查记录和版本引用；只有获准发布的内容进入active。未通过则保留candidate并给出具体问题。

## 输出与完成判据

逐规则通过/失败/未执行清单、受影响节点及证据、发布决定。可以使用宿主通用YAML/图/摘要工具提高确定性，但本仓库不捆绑脚本，也不宣称配置了CI/hook硬门禁。

## 工作目标节点的额外要求

工作树冻结还必须满足TREE-01/NODE-01/TEST-01：父需求覆盖、唯一组成归属、组合不变量、三场景测试契约、正反例oracle与上下文预算。建模时可审候选产物，不能把候选当当前任务验收规则。

## 3.3：内容审查与提交分工

本节点只负责内容/来源/语义/案例审查，EVOLVE-01负责候选base、不可变版本和发布提交；不能用本节点“内容合格”回执代替资源所有权或用户发布许可。审查对象须为最终payload/manifest，作者与独立审查任务身份分开，普通节点自检不自动充当共享发布审查。

检查：REUSE检索与分类理由；旧新允许行为/适用域/接口/错误/状态及case差异；所有适用必需base约束未被局部排除；编辑性变更无行为漂移；真实来源和错误定义负控制；ADOPT影响范围及索引缺口。候选基于旧head或合并后字节改变，则旧审查/授权不得继续使用。

## 建模和入库的新增审查项

DECOMP-01：每个节点有真实分解理由，不用children空自证；scope覆盖全部用户/父义务，跨分片事实审查不得无人负责。NODE-01：协议、被审对象、业务实体分离；定义不等于本次草稿目录。REUSE-01：知识与实例新建独立决策，明确现有采用/本地差异/必需或延期发布；可复用payload独立可读且不泄露任务隐私。

分别执行合法叶、应拆分、无进展递归、共享只读、没有历史records但已有定义、缺反例运行与错误判定器控制。共享审查不只数文件/关键词，所有必需case要在其suite内解析；缺任何必需定义/oracle时不能给“全库已通过”。
