---
schema: pdca.asset/v1
id: ontology:pattern/sm4-zfs-encryption
type: pattern
layer: Knowledge
status: active
summary: SM4 ZFS 块存储加密子模式（内核级 SM4-GCM 透明加密，ZFS 块设备）
relations:
  specializes:
    - ontology:pattern/sm4-storage-encryption
  relates_to:
    - ontology:entity/zfs-system
attributes:
  - name: zfs_sm4_gcm
    desc: ZFS 块存储 SM4-GCM 透明加密
    constraint: ZFS 块存储的内核级 SM4-GCM 透明加密，数据落盘即加密，读取即解密，国产 CPU SM4 指令加速
    testable_signal: "运行 grep -q 'SM4-GCM' /home/black/Public/aio/aio-tools/6200/F/139/备份传输存储国密SM4全流程加密方案.md 且 grep -q 'zfs' /home/black/Public/aio/aio-tools/6200/F/139/备份传输存储国密SM4全流程加密方案.md 命中"
---

# SM4 ZFS 块存储加密子模式

> 源：`sm4-storage-encryption` 的 `ZFS` 四场景之一，`F/139` 的 `SM4` 方案

## 架构

```mermaid
flowchart TD
    A[ZFS 块设备] --> B[SM4-GCM 内核加密]
    B --> C[落盘]
```
Source: `file: F/139/备份传输存储国密SM4全流程加密方案.md:1`
