// tde_decrypt.cpp — InnoDB TDE 解密切片实现 (见 tde_decrypt.h)
#include "tde_decrypt.h"

#include <openssl/evp.h>

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

namespace tde {

namespace {

constexpr uint32_t kPageSize = 16384;
constexpr uint32_t kFilPageData = 38;
constexpr uint16_t kFilPageEncrypted = 0x000F;

// 官方 MySQL 8.0.46 keyring 混淆串（24 字符；xtrabackup 旧版多一个 '-' 不适用）
const char kObfuscate[] = "*305=Ljt0*!@$Hnm(*-9-w;:";

inline uint16_t be16(const uint8_t *p) {
  return static_cast<uint16_t>((p[0] << 8) | p[1]);
}

// 通用 OpenSSL EVP 对称加解密；cbc=true 用 AES-256-CBC(IV 前16B)，否则 AES-256-ECB
bool evp_crypt(const uint8_t *in, int inlen, uint8_t *out, const uint8_t key[32],
               const uint8_t *iv, int encrypt, bool cbc) {
  const EVP_CIPHER *cipher = cbc ? EVP_aes_256_cbc() : EVP_aes_256_ecb();
  EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
  if (!ctx) return false;
  int ok = 1;
  ok = EVP_CipherInit_ex(ctx, cipher, nullptr, key, iv, encrypt) == 1;
  EVP_CIPHER_CTX_set_padding(ctx, 0); /* 密文均为 block 整数倍, 关闭 PKCS#7 校验 */
  int olen = 0, final = 0;
  if (ok) ok = EVP_CipherUpdate(ctx, out, &olen, in, inlen) == 1;
  if (ok) ok = EVP_CipherFinal_ex(ctx, out + olen, &final) == 1;
  EVP_CIPHER_CTX_free(ctx);
  (void)olen;  // CBC 无 padding 输入为 16B 倍数, 输出长度 == 输入
  (void)final;
  return ok == 1;
}

inline bool evp_decrypt_cbc(const uint8_t *in, int inlen, uint8_t *out,
                            const uint8_t key[32], const uint8_t iv[16]) {
  return evp_crypt(in, inlen, out, key, iv, /*encrypt=*/0, /*cbc=*/true);
}
inline bool evp_decrypt_ecb(const uint8_t *in, int inlen, uint8_t *out,
                            const uint8_t key[32]) {
  return evp_crypt(in, inlen, out, key, nullptr, /*encrypt=*/0, /*cbc=*/false);
}

std::string read_file(const char *path) {
  FILE *f = std::fopen(path, "rb");
  if (!f) return {};
  std::string s;
  char buf[8192];
  for (;;) {
    size_t n = std::fread(buf, 1, sizeof buf, f);
    if (n == 0) break;
    s.append(buf, n);
  }
  std::fclose(f);
  return s;
}

}  // namespace

bool master_key_from_keyring(const char *path, uint8_t mk[32]) {
  // 局限: 仅支持 keyring_file v2 单条目 AES 主密钥(MySQL 8.0 默认场景)。
  //   find("AES") 命中首个键类型标记; 多条目/CHACHA20-POLY1305 需按 header 结构解析。
  std::string raw = read_file(path);
  size_t pos = raw.find("AES");
  if (pos == std::string::npos || pos + 3 + 32 > raw.size()) return false;
  size_t obf_len = std::strlen(kObfuscate);
  for (int j = 0; j < 32; ++j)
    mk[j] = static_cast<uint8_t>(raw[pos + 3 + j]) ^
            static_cast<uint8_t>(kObfuscate[j % obf_len]);
  return true;
}

bool tablespace_keys_from_page0(const uint8_t *p0, size_t len,
                                const uint8_t mk[32], TableKeys *out) {
  // 加密信息体: "lCC"(3) + master_key_id(4) + uuid(36) + key_info(64) + crc(4)
  const uint8_t magic[3] = {'l', 'C', 'C'};
  size_t hit = static_cast<size_t>(-1);
  size_t search = len > 20000 ? 20000 : len;  // 只扫页0 数据区
  for (size_t i = 0; i + 112 <= search; ++i)
    if (std::memcmp(p0 + i, magic, 3) == 0) {
      hit = i;
      break;
    }
  if (hit == static_cast<size_t>(-1)) return false;
  const uint8_t *ki = p0 + hit + 3 + 4 + 36;  // key_info 64B
  uint8_t plain[64];
  if (!evp_decrypt_ecb(ki, 64, plain, mk)) return false;
  std::memcpy(out->key, plain, 32);
  std::memcpy(out->iv, plain + 32, 32);
  return true;
}

bool page_is_encrypted(const uint8_t *page) {
  return be16(page + 24) == kFilPageEncrypted;
}

void decrypt_page(const uint8_t *enc, uint8_t *plain, const TableKeys &k) {
  std::memcpy(plain, enc, kPageSize);
  if (!page_is_encrypted(enc)) return;

  const int data_len = kPageSize - kFilPageData;    // 16346
  const int main_len = (data_len / 16) * 16;        // 16336
  const int remain_len = data_len - main_len;       // 10

  // 阶段1: 先解尾部 trailer(最后32B)
  uint8_t tplain[32];
  bool ok1 = evp_decrypt_cbc(enc + kFilPageData + data_len - 32, 32, tplain,
                             k.key, k.iv);

  // 拼接 main 密文: 前部(16314B) + trailer 解出前22B
  uint8_t tmp[16384];
  std::memcpy(tmp, enc + kFilPageData, data_len - 32);
  std::memcpy(tmp + data_len - 32, tplain, 32);

  // 阶段2: 解密 main 区
  bool ok2 = evp_decrypt_cbc(tmp, main_len, plain + kFilPageData, k.key, k.iv);
  if (!ok1 || !ok2) {
    // 解密失败(密钥/数据异常): 回退为原样密文, 不向解析层暴露垃圾明文
    std::memcpy(plain, enc, kPageSize);
    return;
  }

  // 余下 remain 明文(10B) = tplain 后10B
  std::memcpy(plain + kFilPageData + main_len, tplain + 22, remain_len);

  // 恢复 FIL_PAGE_TYPE(original_type 存 @28) 并清零
  uint16_t ot = be16(enc + 28);
  plain[24] = static_cast<uint8_t>(ot >> 8);
  plain[25] = static_cast<uint8_t>(ot & 0xFF);
  plain[28] = 0;
  plain[29] = 0;
}

}  // namespace tde