---
schema: pdca.knowledge-catalog/v1
state: draft
protocol_revision: 3.4.11
library_id: null
generation: null
previous_catalog_digest: null
authority_source_ref: null
writer_ref: null
commit_log_ref: null
entries: []
adoption_index_ref: null
adoption_coverage: null
notice_view_ref: null
notice_generation: null
sync_limitations: []
---

# 知识库发现目录与索引视图

EVOLVE-01/ADOPT-01。entries每项含definition_id、当前head_revision/head_digest/head_manifest_ref/head_manifest_digest、publication_ref以及版本store位置。projection路径只用于发现，运行只消费固定manifest。

此文件是可重建视图而非自己授予权威。generation必须由真实单写者/后端提交维护；任何声明的CAS或fencing都需实际能力。adoption_coverage写known_works/scan_cursor或事件水位、未访问区域及complete/incomplete依据，空列表不代表无人使用。

本项目无自动跨主机同步服务。未配置共享库的项目可以按REUSE-01使用授权snapshot；不得因此宣称全局catalog或全部采用者已同步。
