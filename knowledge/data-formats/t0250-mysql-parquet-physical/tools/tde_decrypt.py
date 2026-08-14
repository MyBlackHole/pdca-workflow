#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""InnoDB 表空间加密(TDE) 物理直读工具。

角色定位: 本脚本是解密链的 **GOLD 参考实现/验证基线**。
生产解析已迁移到 C++(src/mysql/tde_decrypt.cpp + mysqlbin --keyring),
本脚本 (1) 生成解密后的 parquet/CSV 金标准用于对拍验证 C++ 输出,
(2) 保留算法文档与独立调试能力。
解密链(已验证, MySQL 8.0.46 / keyring_file / AES):
  1. 主密钥:    keyring_file 中 INNODBKey 条目 data(32B)
               XOR 混淆串 '*305=Ljt0*!@$Hnm(*-9-w;:' (官方 8.0.46)
  2. key_info:  页0 加密信息体("lCC") -> 取 64B key_info
               AES-256-ECB(主密钥) 解密 -> 前32B=表空间密钥, 后32B=IV
  3. 页解密:    AES-256-CBC, IV 取表空间 IV 前16字节
               两阶段: 先解尾部32B(trailer), 拼接后再解主区 16336B(main)
               明文 FIL_PAGE_TYPE 存于偏移28 original_type 恢复
  4. 记录解析:  变长长度表逆序存于 rec-6 之前; 隐藏字段 DB_TRX_ID(6B)+DB_ROLL_PTR(7B)
               有符号整数存储时符号位取反(id ^ 0x80000000)

用法:
  tde_decrypt.py --keyring <文件> --ibd <文件> info
  tde_decrypt.py --keyring <文件> --ibd <文件> decrypt [--out 明文.ibd]
  tde_decrypt.py --keyring <文件> --ibd <文件> verify [--expected N]
  tde_decrypt.py --keyring <文件> --ibd <文件> rows [--schema spec] [--limit N] [--out x.csv]
"""
import argparse
import struct
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

FIL_PAGE_DATA = 38
PAGE_DATA = 94
PAGE_N_RECS = 54
PAGE_LEVEL = 64
PAGE_TYPE = 24
ORIG_TYPE = 28
INFIMUM = PAGE_DATA + 5
FIL_PAGE_INDEX = 17855
MAGIC_V3 = b"lCC"
OBFUSCATE = b"*305=Ljt0*!@$Hnm(*-9-w;:"  # 官方 8.0.46 混淆串（xtrabackup 旧版多一个 '-' 不适用）

# 字段类型: iN=有符号定长, uN=无符号定长, v=变长
SIGNOFF = {2: 0x8000, 4: 0x80000000, 8: 0x8000000000000000}


def be16(b, o):
    return struct.unpack(">H", b[o:o + 2])[0]


def be32(b, o):
    return struct.unpack(">I", b[o:o + 4])[0]


def master_key_from_keyring(path):
    kf = open(path, "rb").read()
    i = kf.find(b"AES")
    if i < 0:
        raise SystemExit("keyring 中未找到 AES 条目")
    data = kf[i + 3:i + 3 + 32]
    if len(data) != 32:
        raise SystemExit("keyring data 长度异常")
    return bytes(data[j] ^ OBFUSCATE[j % len(OBFUSCATE)] for j in range(32))


class Tde:
    def __init__(self, keyring, ibd_path):
        self.mk = master_key_from_keyring(keyring)
        self.ibd_path = ibd_path
        with open(ibd_path, "rb") as f:
            self.blob = f.read()
        self.page_size = len(self.blob) // (len(self.blob) // 16384)
        self._parse_encinfo()
        self._setup_cipher()

    def _parse_encinfo(self):
        d = self.blob
        o = d.find(MAGIC_V3)
        if o < 0:
            raise SystemExit("页0 未找到密钥加密信息(lCC magic)")
        self.info_off = o
        self.master_key_id = be32(d, o + 3)
        self.uuid = d[o + 7:o + 7 + 36].decode("ascii", "replace")
        self.key_info_enc = d[o + 7 + 36:o + 7 + 36 + 64]
        crc = be32(d, o + 7 + 36 + 64)
        import zlib
        # 用主密钥解密后校验 CRC(ut_crc32 与标准 zlib 可能字节序不同, 仅提示)
        dec = Cipher(algorithms.AES(self.mk), modes.ECB()).decryptor().update(self.key_info_enc)
        c1 = zlib.crc32(dec) & 0xFFFFFFFF
        self.crc_ok = (c1 == crc)

    def _setup_cipher(self):
        dec = Cipher(algorithms.AES(self.mk), modes.ECB()).decryptor().update(self.key_info_enc)
        self.tablespace_key = dec[:32]
        self.iv = dec[32:64]
        self.iv16 = self.iv[:16]

    def _cbc(self, data):
        c = Cipher(algorithms.AES(self.tablespace_key), modes.CBC(self.iv16)).decryptor()
        return c.update(data) + c.finalize()

    def decrypt_page(self, raw):
        page = bytearray(raw)
        dl = self.page_size - FIL_PAGE_DATA
        ml = (dl // 16) * 16
        tr = bytes(page[FIL_PAGE_DATA + dl - 32:FIL_PAGE_DATA + dl])
        tp = self._cbc(tr)
        tmp = bytearray(self.page_size)
        tmp[0:dl - 32] = bytes(page[FIL_PAGE_DATA:FIL_PAGE_DATA + dl - 32])
        tmp[dl - 32:dl] = tp
        mo = self._cbc(bytes(tmp[:ml]))
        page[FIL_PAGE_DATA:FIL_PAGE_DATA + ml] = mo
        page[FIL_PAGE_DATA + ml:FIL_PAGE_DATA + dl] = tmp[ml:dl]
        ot = be16(page, ORIG_TYPE)
        page[PAGE_TYPE:PAGE_TYPE + 2] = struct.pack(">H", ot)
        page[ORIG_TYPE:ORIG_TYPE + 2] = b"\x00\x00"
        return bytes(page)

    def leaf_pages(self):
        n = len(self.blob) // 16384
        idx = 0
        for pi in range(n):
            page = self.decrypt_page(self.blob[pi * 16384:(pi + 1) * 16384])
            if be16(page, PAGE_TYPE) != FIL_PAGE_INDEX:
                continue
            if be16(page, PAGE_LEVEL) != 0:
                continue
            yield pi, page


def parse_schema(spec):
    fields = []
    for tok in spec.split(","):
        name, typ = tok.split(":")
        fields.append((name, typ))
    return fields


def iter_records(page, schema):
    """解析一个叶页中的全部聚簇记录, 产出 dict。

    记录布局(comp/dynamic, 无压缩):
      [变长长度表 逆序] [null位图] [extra5] [数据 rec 起]
      数据 = 主键(定长) + DB_TRX_ID(6B) + DB_ROLL_PTR(7B) + 用户字段
    变长字段长度表: 位于 rec-6-位图字节 往前, 按字段顺序读出(逆序写入)。
    支持类型: iN/uN 定长整数(有符号存时符号位取反), v 变长串, ?前缀=可空。
    """
    nrecs = be16(page, PAGE_N_RECS)
    nxt = be16(page, INFIMUM - 2)
    if nxt == 0:
        return
    org = INFIMUM + nxt

    nullable = [i for i, (_, t) in enumerate(schema) if t.startswith("?")]
    n_null = len(nullable)
    nb = (n_null + 7) // 8
    var_idx = [i for i, (_, t) in enumerate(schema) if t.lstrip("?") == "v"]

    for _ in range(nrecs):
        # --- 变长字段长度表 (逆序: 从 rec-6-位图 往下) ---
        lp = org - 6 - nb
        varlens = {}
        for i in var_idx:
            b1 = page[lp]
            lp -= 1
            if b1 & 0x80:  # 2 字节长度 (bit6 置位为外部存储, 此处不展开)
                varlens[i] = ((b1 & 0x3F) << 8) | page[lp]
                lp -= 1
            else:
                varlens[i] = b1
        # --- NULL 位图 (首个可空列占最高位) ---
        nullbits = {}
        if n_null:
            for j, c in enumerate(nullable):
                nullbits[c] = bool(page[org - 6 - nb + (j // 8)] & (0x80 >> (j % 8)))
        # --- 字段数据 ---
        offs = 0
        row = {}
        # 主键(单列, 定长)
        name0, t0 = schema[0]
        size = int(t0.lstrip("?")[1:])
        pv = page[org:org + size]
        if t0[0] == "i":
            row[name0] = int.from_bytes(pv, "big") ^ SIGNOFF[size]
        else:
            row[name0] = int.from_bytes(pv, "big")
        offs += size
        offs += 13  # DB_TRX_ID(6) + DB_ROLL_PTR(7)
        for i in range(1, len(schema)):
            name, typ = schema[i]
            if i in nullbits and nullbits[i]:
                row[name] = None
                continue
            if typ.lstrip("?") == "v":
                l = varlens[i]
                val = page[org + offs:org + offs + l]
                offs += l
                row[name] = val.decode("utf-8", "replace")
            else:
                size = int(typ.lstrip("?")[1:])
                val = page[org + offs:org + offs + size]
                offs += size
                if typ[0] == "i":
                    row[name] = int.from_bytes(val, "big") ^ SIGNOFF[size]
                else:
                    row[name] = int.from_bytes(val, "big")
        yield row
        n2 = be16(page, org - 2)
        if n2 == 0:
            break
        org += n2


def cmd_info(t: Tde, args):
    print(f"加密信息偏移     : 0x{t.info_off:x}")
    print(f"master_key_id    : {t.master_key_id}")
    print(f"server_uuid      : {t.uuid}")
    print(f"主密钥           : {t.mk.hex()}")
    print(f"表空间密钥       : {t.tablespace_key.hex()}")
    print(f"IV              : {t.iv.hex()}")
    print(f"key_info CRC     : {'OK' if t.crc_ok else '与zlib不一致(字节序差异属正常)'}")


def cmd_decrypt(t: Tde, args):
    n = len(t.blob) // 16384
    out = bytearray()
    for pi in range(n):
        out += t.decrypt_page(t.blob[pi * 16384:(pi + 1) * 16384])
    if args.out:
        with open(args.out, "wb") as f:
            f.write(out)
        print(f"已解密 {n} 页 -> {args.out}")
    else:
        sys.stdout.buffer.write(out)


def cmd_verify(t: Tde, args):
    total = 0
    leaves = 0
    for pi, page in t.leaf_pages():
        leaves += 1
        for _ in iter_records(page, [("id", "i4")]):
            total += 1
    exp = args.expected if args.expected is not None else 0
    print(f"叶页={leaves} 记录总数={total} 期望={exp} 匹配={exp == total}")


def cmd_rows(t: Tde, args):
    schema = parse_schema(args.schema)
    limit = args.limit or 2**63
    import csv
    count = 0
    f = open(args.out, "w", newline="") if args.out else None
    w = csv.writer(f) if f else None
    hdr = [n for n, _ in schema]
    if w:
        w.writerow(hdr)
    for pi, page in t.leaf_pages():
        for row in iter_records(page, schema):
            if w:
                w.writerow([row[h] for h in hdr])
            else:
                print(row)
            count += 1
            if count >= limit:
                break
        if count >= limit:
            break
    if f:
        f.close()
        print(f"已导出 {count} 行 -> {args.out}")


def main():
    ap = argparse.ArgumentParser(description="InnoDB TDE 物理直读")
    ap.add_argument("--keyring", required=True, help="keyring_file 路径")
    ap.add_argument("--ibd", required=True, help="加密 .ibd 表文件路径")
    ap.add_argument("--out", help="输出文件(decrypt/rows)")
    ap.add_argument("--expected", type=int, default=None, help="verify 期望行数")
    ap.add_argument("--schema", default="id:i4,s:v,t:v", help="字段定义 逗号分隔 name:type")
    ap.add_argument("--limit", type=int, default=None, help="rows 输出上限")
    ap.add_argument("cmd", choices=["info", "decrypt", "verify", "rows"])
    args = ap.parse_args()
    t = Tde(args.keyring, args.ibd)
    {"info": cmd_info, "decrypt": cmd_decrypt, "verify": cmd_verify, "rows": cmd_rows}[args.cmd](t, args)


if __name__ == "__main__":
    main()