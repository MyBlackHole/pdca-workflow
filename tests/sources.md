# 固定来源与核验边界

以下版本在本轮通过公开网页核对，不声称为当前最新版本；原文件未成功下载到执行容器，不提供伪造的原文件摘要。向量作为固定事实转写到本包测试数据，转写文件有自己的校验。源码核对不是实际文件系统运行。

- GCM: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf
- CCM: https://www.rfc-editor.org/rfc/rfc3610.txt
- XTS: https://raw.githubusercontent.com/torvalds/linux/v6.12/crypto/xts.c
- FSC: https://www.kernel.org/doc/html/v6.12/filesystems/fscrypt.html
- BRT: https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/module/zfs/brt.c
- DDT: https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/module/zfs/ddt.c
- ZIO: https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/module/zfs/zio.c
- DDTH: https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/include/sys/ddt.h
- ZPROP: https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/man/man7/zfsprops.7
- VEC: https://raw.githubusercontent.com/openssl/openssl/openssl-3.0.16/test/recipes/30-test_evp_data/evpciph_aes_common.txt
