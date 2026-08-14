// tde_decrypt.h — InnoDB 表空间加密(TDE) 物理解密 (MySQL 8.0.46 / keyring_file / AES)
//
// 经验证的解密链:
//   1. 主密钥:   keyring_file 中 INNODBKey 条目 data(32B) XOR 混淆串
//                '*305=Ljt0*!@$Hnm(*-9-w;:' (官方 8.0.46, 24 字符)
//   2. key_info: 页0 加密信息体("lCC" magic) -> 64B key_info
//                AES-256-ECB(主密钥) 解密 -> 前32B=表空间密钥, 后32B=IV
//   3. 页解密:   AES-256-CBC, IV 取表空间 IV 前 16B
//                两阶段: 尾32B(trailer) 先解, 拼接后解主区 16336B(main)
//                明文 FIL_PAGE_TYPE 存偏移28 original_type 恢复
//
// 内存注意: mysqlbin 集成方式为整文件一次性解密(明文缓冲 == .ibd 大小),
//           真实大表会占用等量物理内存, 必要时可批处理化(见 tde_decrypt.h TODO)。
#pragma once

#ifndef TDE_DECRYPT_H
#define TDE_DECRYPT_H

#include <cstddef>
#include <cstdint>

namespace tde {

// 表空间密钥 + IV (key_info 明文)
struct TableKeys {
  uint8_t key[32];  // 表空间密钥
  uint8_t iv[32];   // 表空间 IV (CBC 取前 16B)
};

// 从 keyring_file 提取主密钥(32B); 失败返回 false
bool master_key_from_keyring(const char *path, uint8_t mk[32]);

// 解析 .ibd 页0 的加密信息("lCC"), 用主密钥解密 key_info 得到表/IV
// p0: 明文页0首指针; len: 文件字节数; mk: 主密钥(32B)
bool tablespace_keys_from_page0(const uint8_t *p0, size_t len,
                                const uint8_t mk[32], TableKeys *out);

// 解密一页: enc -> plain(均为 16384B)。仅当文件态页 type==0x0F(加密) 才解密,
// 否则原样拷贝(如页0 FSP)。恢复 FIL_PAGE_TYPE(@24) 与清零 orig_type(@28)。
void decrypt_page(const uint8_t *enc, uint8_t *plain, const TableKeys &k);

// 页是否加密(文件态 type == FIL_PAGE_ENCRYPTED)
bool page_is_encrypted(const uint8_t *page);

}  // namespace tde

#endif  // TDE_DECRYPT_H