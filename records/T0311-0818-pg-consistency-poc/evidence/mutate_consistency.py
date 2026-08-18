#!/usr/bin/env python3
# T0311 全面数据一致性校验 POC — mutation 注入测试
#
# 对基准 tsv 逐一注入 12 种变异，调用 verify_consistency.py 验证必须 FAIL（被捕获）。
# 捕获率 = 100% 即证明校验方法对该变异类敏感。
#
# 用法:
#   python3 bench/mutate_consistency.py <parquet> <sql_tsv> <out_dir> [--pg-dsn ...] [--show-diff 2]
import argparse
import os
import subprocess
import sys

VERIFY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_consistency.py")


def load(path):
    with open(path) as f:
        return f.read().splitlines()


def save(rows, path):
    with open(path, "w") as f:
        f.write("\n".join(rows))
        if rows:
            f.write("\n")


def split(row):
    return row.split("\t")


def join(fields):
    return "\t".join(fields)


def mutations():
    """返回 [(name, fn(rows) -> rows)]，fn 在 rows 副本上注入单种变异。"""
    def m01(rows):
        # 改值：amount 数值 +0.01
        r = rows[:]
        f = split(r[999]); f[2] = "10.01"; r[999] = join(f)
        return r

    def m02(rows):
        # 值->NULL：status 改 'NULL'
        r = rows[:]
        f = split(r[4999]); f[4] = "NULL"; r[4999] = join(f)
        return r

    def m03(rows):
        # 时间精度丢失：created_at 去掉微秒
        r = rows[:]
        f = split(r[2999]); f[3] = f[3][:19]; r[2999] = join(f)
        return r

    def m04(rows):
        # 删行
        r = rows[:]
        del r[9998]
        return r

    def m05(rows):
        # 重复行（插入既有 id 行到末尾）
        r = rows[:]
        r.append(rows[1233])
        return r

    def m06(rows):
        # 换列序：id <-> customer_id 互换
        r = rows[:]
        f = split(r[499]); f[0], f[1] = f[1], f[0]; r[499] = join(f)
        return r

    def m07(rows):
        # decimal 精度：'80.00' -> '80'
        r = rows[:]
        f = split(r[7999]); f[2] = "80"; r[7999] = join(f)
        return r

    def m08(rows):
        # bool 翻转
        r = rows[:]
        f = split(r[5999]); f[6] = "0" if f[6] == "1" else "1"; r[5999] = join(f)
        return r

    def m09(rows):
        # NULL <-> 空串：把某 NULL status 改成空串
        r = rows[:]
        for idx, row in enumerate(r):
            f = split(row)
            if f[4] == "NULL":
                f[4] = ""; r[idx] = join(f)
                break
        return r

    def m10(rows):
        # payload 截断（选非 TOAST 行）
        r = rows[:]
        f = split(r[4001]); f[5] = f[5][:32]; r[4001] = join(f)
        return r

    def m11(rows):
        # id 错位/跳号
        r = rows[:]
        f = split(r[6999]); f[0] = "70000"; r[6999] = join(f)
        return r

    def m12(rows):
        # payload 尾随空格（非 TOAST 行）
        r = rows[:]
        f = split(r[4002]); f[5] = f[5] + " "; r[4002] = join(f)
        return r

    return [
        ("m01_change_value", m01),
        ("m02_value_to_null", m02),
        ("m03_ts_precision_loss", m03),
        ("m04_delete_row", m04),
        ("m05_dup_row", m05),
        ("m06_swap_id_customer", m06),
        ("m07_amount_precision", m07),
        ("m08_bool_flip", m08),
        ("m09_null_to_empty", m09),
        ("m10_payload_truncate", m10),
        ("m11_id_shift", m11),
        ("m12_trailing_space", m12),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parquet")
    ap.add_argument("sql_tsv")
    ap.add_argument("out_dir")
    ap.add_argument("--pg-dsn", default="")
    ap.add_argument("--show-diff", type=int, default=2)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    base = load(args.sql_tsv)

    # 基线：未变异必须 PASS（防止假阴性）
    base_path = os.path.join(args.out_dir, "base.tsv")
    save(base, base_path)
    bp = subprocess.run([sys.executable, VERIFY, args.parquet, base_path,
                         "--show-diff", str(args.show_diff),
                         *(["--pg-dsn", args.pg_dsn] if args.pg_dsn else [])],
                        capture_output=True, text=True)
    base_ok = (bp.returncode == 0)
    print("基线(未变异) verify: %s" % ("PASS" if base_ok else "FAIL(异常!)"))

    caught = 0
    total = 0
    results = []
    for name, fn in mutations():
        rows = fn(base[:])
        p = os.path.join(args.out_dir, name + ".tsv")
        save(rows, p)
        r = subprocess.run([sys.executable, VERIFY, args.parquet, p,
                            "--show-diff", str(args.show_diff),
                            *(["--pg-dsn", args.pg_dsn] if args.pg_dsn else [])],
                           capture_output=True, text=True)
        captured = (r.returncode != 0)
        total += 1
        if captured:
            caught += 1
        results.append((name, captured, r.returncode))
        if not captured:
            print("  MISS: %s (exit=%d)" % (name, r.returncode))
            for line in r.stdout.strip().splitlines()[-8:]:
                print("    " + line)
        else:
            print("  caught: %s" % name)

    print("\n== mutation 捕获汇总: %d/%d ==" % (caught, total))
    if not base_ok or caught < total:
        print("基线或捕获未达 100% -> FAIL")
        sys.exit(1)
    print("捕获率 100% -> PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
