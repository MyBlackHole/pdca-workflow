---
type: Class
superClass: [[concept/domain-entity]]
domain: TLS/mTLS
docType: Entity
tags: [x509, cert]
---
# X509Certificate：证书实体

## 关系 (Relations)
- **继承父类 (subClassOf)**: [[concept/domain-entity]]
- **依赖组件 (dependsOn)**: [[entity/tls-session]]

## 核心属性 (Attributes)
- **序列号 (serialNumber)**: 数据类型 String
- **主体 (subject)**: 数据类型 String
- **证书链 (certificateChain)**: 对象属性，指向 [[entity/x509-certificate]]
- **是否自签名 (isSelfSigned)**: 数据类型 Boolean
