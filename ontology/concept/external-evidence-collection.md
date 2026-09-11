---
schema: pdca.asset/v2
id: ontology:concept/external-evidence-collection
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 外部证据导入边界
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-evidence
  - ontology:concept/pdca-task
---

# 外部证据导入边界

仅导入用户授权且与当前契约相关的材料。先核验来源、版本和读取权限，检查路径规范化及符号链接目标；超出授权范围时停止。

复制到当前任务artifacts的具名位置，记录原来源locator、源版本/摘要、副本摘要与导入理由。原位置可变时以固定副本为后续审查依据。无法复制的在线源保存实际取得的内容和获取来源，不能伪造抓取成功。

按EVIDENCE-01登记；复制文件不等于验证内容真实。不得借导入遍历其他任务工作目录或绕过权限。来自依赖的摘要结论仍需在当前任务验证其适用性。
