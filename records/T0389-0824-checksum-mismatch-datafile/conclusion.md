---
schema: pdca.asset/v1
id: T0389-0824-checksum-mismatch-datafile
phase: check
source_ids: [research-report, prod-error-log]
---

## 上下文

GoldenDB 定制版 Percona XtraBackup 8.0.25-17 在 `--backup` 阶段对分区文件
`./usercdb/ur_usergoods_info_his_06#p#p2026.ibd`（Space ID:520513, Flags:16417）
报 `Checksum mismatch in datafile`。任务为 research 场景根因分析，
用户核心追问：**该报错是否影响备份**。

## 假设与结果

- 假设 H1（Plan 提出）：报错精确对应表空间首页校验路径 → **成立**，拼接点唯一
  （fsp0file.cc:638+657），验证：`grep -rn "Checksum mismatch" storage/innobase/`。
- 假设 H2（Plan 提出）：加密/压缩可能是诱因之一 → **被证据否定**：
  Flags=16417 解码 ENCRYPTION=0、ZIP_SSIZE=0（fsp0types.h 位布局）。
- 假设 H3（Do 中形成）：报错后备份静默缺失该分区文件 → **成立**，
  因果链四跳全部代码实证（提前 return→不注册 fil_system→拷贝枚举只遍历
  fil_system→open_ibds 忽略返回值照常结束）。

## 分析

- **AC-1** ✅ 报错拼接点与所在函数已定位并给出可复现 grep（research-report F1）（research-report）
- **AC-2** ✅ 判定内核 B1-B6 全部 6 类分支附 checksum.cc 行号（research-report F2）（research-report）
- **AC-3** ✅ --backup 完整调用链含 DB_PAGE_IS_BLANK 豁免与 UNIV_HOTBACKUP 条件编译差异（research-report F3）（research-report）
- **AC-4** ✅ R1-R9 共 9 条根因假设，各附代码依据与现场观测特征（research-report F6）（research-report）
- **AC-5** ✅ 决策树 D0-D6 含 innochecksum/xxd/keyring 可执行命令与判读说明，R3/R5 有独立子路径 D6（research-report F7）（research-report）
- **AC-6** ✅ 文案辨析表区分首页校验路径与逐页复制/copy-back/mysqld 路径（research-report F8）（research-report）
- **AC-7** ✅ 生产案例逐位解码 + 主因排序（R9≈R2>R1，排除 R3/R5）+ 验证步骤 D1-D3（research-report F5；prod-error-log）（research-report, prod-error-log）
- **AC-8** ✅ 报错后行为因果链 + 备份集确认方法 D0 + 补救建议（补备/后置核对检查）（research-report F4、结论 3a/3d）（research-report）

关键结论可复核途径汇总：报告每节末尾"验证途径"命令块；
核心一跳复核：`sed -n '496,509p' storage/innobase/xtrabackup/src/xtrabackup.cc`
（拷贝枚举来源）与 `sed -n '11727,11736p' storage/innobase/fil/fil0fil.cc`
（校验失败提前返回）。

## 适用边界

- 结论基于 8.0.25-17 源码树；其他版本判定分支可能增删（如更低版本无 SDI 位）。
- "静默缺文件"结论适用于走 fil_scan_for_tablespaces 扫描注册的 .ibd；
  ibdata/undo 走独立路径不受此影响（ibdata 首页校验在 HOTBACKUP 下不编译）。
- 根因排序是概率判断而非实锤：R9/R2/R1 的最终裁决需现场执行 D1-D3。
- R8（GoldenDB 定制偏差）无 git 历史可比对，保持低置信度待验证。

## 下一轮建议

1. 若现场确认备份集缺文件且需追责存储层，另立 bugfix 任务实现
   "xtrabackup_tablespaces 元数据 vs 实际拷贝文件"一致性后置检查，
   把静默缺文件变为显式失败（报告结论 3d 已给出需求雏形）。
2. 分区维护任务与备份窗口互斥可在 GoldenDB 调度层落地，作为运维规范沉淀。
3. 若获得上游 git 仓库访问能力，回补 R8 的 diff 验证闭环本任务唯一遗留假设。

## verdict

```json
{
  "outcome": "confirmed",
  "reason": "全部关键结论锚定一手源码 file:line 且附可重跑验证命令；AC-1~AC-8 全部 ✅ 有证据支撑",
  "verdict_id": "T0389-verdict-check-001",
  "at": "2026-08-24T12:18:00+08:00"
}
```
