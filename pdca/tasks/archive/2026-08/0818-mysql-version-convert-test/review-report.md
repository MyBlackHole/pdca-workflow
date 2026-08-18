# T0300 Do 阶段代码审查（双轴）

审查范围：本轮新增 `bench/extract_version_ibd.sh`、`bench/verify_version_convert.py`（无 src/ 变更，
版本拆分源码在 T0250 已审查；本轮四版本转换测试即对其运行验证）。

## 标准轴（编码规范 + 坏味）
- `extract_version_ibd.sh`：`set -euo pipefail`、容器/volume/版本映射显式声明、
  innodb_fast_shutdown=0 干净关闭后再提取（避免脏页/重做日志干扰快照一致性）、
  unshare 内 `chown 0:0`（命名空间根 = 宿主调用者）——修复了首版 `chown $(id -u)` 在 unshare
  uid 映射下落到 100999 的权限坑。无重复代码、无魔法值。
- `verify_version_convert.py`：列序与规范化约定（amount 定长 2 位、created_at DATETIME(6) 文本、
  active 0/1、NULL="NULL"）显式注释，与 `mysql -N -B` 输出对齐；三路验证（行数 + 全量逐字段 + 聚合）；
  以 id 排序消除对物理页序的依赖（重要发现：56/57/84 页序≠主键序）。失败路径 exit 1，输出差异样本。
- 坏味：无。Python 侧 pyarrow 导入在无 venv 环境下报"could not be resolved"，属环境配置，
  非代码缺陷（已验证 venv 内可运行）。

## 规范轴（对照 prd.md AC）
- AC-1（四版本 .ibd 提取）：extract_version_ibd.sh 覆盖 56/57/80/84 四个 volume → 达标
- AC-2（转换 rows=1M）：mysqlbin 四版本实测 rows=1,000,000 → 达标
- AC-3（全量逐字段差异=0）：verify_version_convert.py 四版本实测差异=0 → 达标
- AC-4（8.0 聚合补齐）：聚合对照 PASS，ac1_four_versions.md 已补 8.0 列 → 达标
- AC-5（记录+manifest）：T0300_version_convert.md + 源项目 evidence/manifest.jsonl 登记 → 达标
- AC-6（版本拆分无回归）：四版本经拆分后的解析路径全部 PASS → 达标

## 风险评级
LOW。无 Blocking。

## 建议
- 吞吐测量受四实例并行争用影响（277K/s 低于 AC-1 单实例），后续基准请单实例运行（已在记录中注明）。
- `bench/extract_version_ibd.sh` 依赖宿主 volume 路径与容器名，属一次性数据获取工具；
  如需复用建议参数化（当前以注释 + 映射表形式显式化，可接受）。
