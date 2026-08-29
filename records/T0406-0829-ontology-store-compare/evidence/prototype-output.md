# T0406 原型转 OWL/TTL 对比输出


## SSOT v3 样本：ontology/entity/x509-certificate.md
```turtle
<http://pdca.local/ontology/entity/x509-certificate> a owl:Class .
<http://pdca.local/ontology/entity/x509-certificate> rdfs:subClassOf <http://pdca.local/ontology/concept/domain-entity> .
```

## SSOT v3 样本：ontology/pattern/mtls-handshake-enum-unify.md
```turtle
<http://pdca.local/ontology/pattern/mtls-handshake-enum-unify> a owl:Class .
<http://pdca.local/ontology/pattern/mtls-handshake-enum-unify> rdfs:subClassOf <http://pdca.local/ontology/pattern> .
<http://pdca.local/ontology/pattern/mtls-handshake-enum-unify> pdca:guides <http://pdca.local/ontology/entity/mtls-handshake> .
<http://pdca.local/ontology/pattern/mtls-handshake-enum-unify> pdca:attr/applicability "多模块各自定义同一组算法枚举与映射的工程" .
```

## SSOT v3 样本：ontology/principle/structured-mtls-failure-diagnostics.md
```turtle
<http://pdca.local/ontology/principle/structured-mtls-failure-diagnostics> a owl:Class .
<http://pdca.local/ontology/principle/structured-mtls-failure-diagnostics> rdfs:subClassOf <http://pdca.local/ontology/principle> .
<http://pdca.local/ontology/principle/structured-mtls-failure-diagnostics> pdca:guides <http://pdca.local/ontology/entity/tls-session> .
<http://pdca.local/ontology/principle/structured-mtls-failure-diagnostics> pdca:attr/applicability "TLS/mTLS 初始化和握手失败日志场景" .
```

## SSOT v3 样本：ontology/concept/pdca.md
```turtle
<http://pdca.local/ontology/concept/pdca> a owl:Class .
```

## 提案风格样本：samples/proposal/mtls-handshake-enum-unify.md
```turtle
<http://pdca.local/ontology/proposal/mtls-handshake-enum-unify> a owl:Class .
<http://pdca.local/ontology/proposal/mtls-handshake-enum-unify> rdfs:subClassOf <http://pdca.local/ontology/pattern> .
<http://pdca.local/ontology/proposal/mtls-handshake-enum-unify> pdca:subClassOf <http://pdca.local/ontology/pattern> .
<http://pdca.local/ontology/proposal/mtls-handshake-enum-unify> pdca:guidedBy <http://pdca.local/ontology/entity/mtls-handshake> .
<http://pdca.local/ontology/proposal/mtls-handshake-enum-unify> pdca:attr/applicability ""^^xsd:string .
<http://pdca.local/ontology/proposal/mtls-handshake-enum-unify> pdca:attr/testableSignal ""^^xsd:string .
```
- 模糊谓词(需归一化): ['subClassOf', 'guidedBy']
- 属性类型丢失项: 无

## 提案风格样本：samples/proposal/structured-mtls-failure-diagnostics.md
```turtle
<http://pdca.local/ontology/proposal/structured-mtls-failure-diagnostics> a owl:Class .
<http://pdca.local/ontology/proposal/structured-mtls-failure-diagnostics> rdfs:subClassOf <http://pdca.local/ontology/principle> .
<http://pdca.local/ontology/proposal/structured-mtls-failure-diagnostics> pdca:subClassOf <http://pdca.local/ontology/principle> .
<http://pdca.local/ontology/proposal/structured-mtls-failure-diagnostics> pdca:guidedBy <http://pdca.local/ontology/entity/tls-session> .
<http://pdca.local/ontology/proposal/structured-mtls-failure-diagnostics> pdca:attr/applicability ""^^xsd:string .
<http://pdca.local/ontology/proposal/structured-mtls-failure-diagnostics> pdca:attr/testableSignal ""^^xsd:string .
```
- 模糊谓词(需归一化): ['subClassOf', 'guidedBy']
- 属性类型丢失项: 无

## 提案风格样本：samples/proposal/x509-certificate.md
```turtle
<http://pdca.local/ontology/proposal/x509-certificate> a owl:Class .
<http://pdca.local/ontology/proposal/x509-certificate> rdfs:subClassOf <http://pdca.local/ontology/concept/domain-entity> .
<http://pdca.local/ontology/proposal/x509-certificate> pdca:subClassOf <http://pdca.local/ontology/concept/domain-entity> .
<http://pdca.local/ontology/proposal/x509-certificate> pdca:dependsOn <http://pdca.local/ontology/entity/tls-session> .
<http://pdca.local/ontology/proposal/x509-certificate> pdca:certificateChain <http://pdca.local/ontology/entity/x509-certificate> .
<http://pdca.local/ontology/proposal/x509-certificate> pdca:attr/serialNumber ""^^xsd:string .
<http://pdca.local/ontology/proposal/x509-certificate> pdca:attr/subject ""^^xsd:string .
<http://pdca.local/ontology/proposal/x509-certificate> pdca:attr/isSelfSigned ""^^xsd:boolean .
```
- 模糊谓词(需归一化): ['subClassOf', 'dependsOn', 'certificateChain']
- 属性类型丢失项: 无

## 映射完整度与脆弱度对比

- SSOT v3：谓词受控(specializes/guides/...)、关系 range 由 ontology-validate 强制校验 → OWL 映射**无损且可机器验证**；代价是目录耦合(type==dir)、对人类可读性较弱。
- 提案风格：谓词为自由文本(subClassOf/dependsOn/guidedBy) → OWL 映射需**谓词归一化**(否则属性爆炸/语义歧义)；属性类型仅标注中文'数据类型 X' → 非受控类型会**丢失 datatype**；wikilink 拼写错误会静默断图，无内置校验。
