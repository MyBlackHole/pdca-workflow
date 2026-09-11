---
schema: pdca.subject-snapshot/v1
protocol_revision: 3.4.10
snapshot_id: null
purpose: null
scope_source_ref: null
scope_statement: null
required_members: []
members: []
exclusions: []
captured_at: null
time_source_ref: null
---

# 固定对象集合草稿

EVIDENCE-01/CONTRACT-01的复合输入。purpose为protocol_baseline/subject_snapshot/review_run等明确用途；成员包含object_id、path/ref、source_revision、role、required和digest。required_members来自已确认范围，不根据实际搜到的文件反推。

先固定各成员，再哈希清单，由外层绑定。两个文件必须两项成员；一个文件的hash不是集合hash。ref可相对本清单目录或明确授权的固定根，但解析不能逃出授权范围。exclusions必须有范围依据，未知/不可读成员不能删掉。
