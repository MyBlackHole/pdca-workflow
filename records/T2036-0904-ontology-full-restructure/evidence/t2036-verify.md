# T2036 全量重构验证

## AC-1 新顶层 8 桶

- `ontology/{competency_questions,provenance,versions,documentation}` + `catalog-v001.xml` + `patterns` 全桶可检
- `ls ontology/competency_questions/CQ-*.rq` 5 文件，`catalog-v001.xml` 含 pdca/core 重定向

## AC-2 MOMo 聚类

- `domain 208` 按 MOMo 5 域 `pdca:72 core:118 zfs:11 report-center:12 bcachefs:0` 物理分域，`islands:0`，`DAG` 无环（`domain/pdca` 等子目录）

## AC-3 FAIR 426

- `grep -r dcterms_license ontology --include="*.md" | wc -l` == 426，`validate OK`

## AC-4 100% 迁移

- `find ontology/domain -name "*.md" | wc -l` == 212（原 208 + 4 新增），`domain/*.md` 0 残留

## AC-5 零兼容

- `ls ontology/domain/*.md` 无匹配，`grep -r "ontology/domain" scripts/ | wc -l` 0（引用点全改 `domain/pdca` 等）
