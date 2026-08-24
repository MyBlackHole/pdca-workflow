---
schema: pdca.asset/v1
id: T0386-0824-analyze-last-commit
phase: check
source_ids: [research-report-final]
---

## 上下文

用户要求分析仓库最后一个提交【F-139】TLS/mTLS 全栈实现的修改内容。research 场景，产出调研报告。分析期间提交被 amend 重写（0e2d8c35 → dbc20b5e），Check 阶段 Grill 捕获该漂移并以新 HEAD 复核全部数据后修订报告。

## 假设与结果

- **假设**：最后提交内容稳定，可用 git 取证完整刻画。→ **部分修正**：提交在任务执行中被 amend；以 amend 后指纹 dbc20b5e 重新统计，数据两次复核一致。
- **假设**：统计口径可复现。→ **成立**：`--no-renames` 口径消除 rename 检测的预算相关波动。

## 分析

- **AC-1** ✅ 报告含规模与边界章节：openssl4 3857 文件 +1279668/-0、自研 266 文件 +34304/-2560、合计 4123/+1313972/-2560，与 `git show HEAD --numstat --no-renames` 复核一致（research-report-final）
- **AC-2** ✅ 模块级清单覆盖全部非第三方目录（oss/libs/rpc/rdbcomm/libobk/fs-backup/dmsbtex/根/s3tools/packages/xbsa/rpc-keygen/test 共 13 组），每模块附主题概括（research-report-final）
- **AC-3** ✅ 五条功能主线（OpenSSL4 国密/tls-keygen 多算法/mTLS 协商/证书缓存/xmake 构建版本管理）各附 commit 内文件与符号级证据（ADR-0001、hs_algorithm.c、tls_cert.h acquire/release、xmake 版本矩阵）（research-report-final）
- **AC-4** ✅ 报告为 Markdown 且落盘 evidence 目录（records/T0386-0824-analyze-last-commit/evidence/research-report-final.md，digest sha256:1e500226...）（convergence-map-final）

关键结论可复核途径：报告"参考资料"节含全部复现命令（含 HEAD 指纹预检）。

## 适用边界

- 结论仅适用于提交指纹 dbc20b5e；若提交再次 amend，需按报告参考资料重跑复核命令。
- 不构成代码质量评审结论；third_party/openssl4 上游源码未逐行解读。

## 下一轮建议

- 后续大型变更建议按主线拆分提交粒度，便于独立回滚与评审聚焦。
- 分析类任务可在 PRD 中预先声明"提交指纹锁定"验收前提，规避目标漂移。

## verdict

```json
{
  "outcome": "confirmed",
  "reason": "四条 AC 全部有证据支撑且数字经 --no-renames 独立复核一致；amend 漂移已捕获并修订",
  "verdict_id": "T0386-verdict-001",
  "at": "2026-08-24T10:34:00+08:00"
}
```
