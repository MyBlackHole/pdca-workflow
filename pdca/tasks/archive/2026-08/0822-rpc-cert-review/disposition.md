# T0348 审查结论处置 — rpc 证书实现审查

## 审查产出

- `review-report.md`：5 项发现（F1 高 / F2 中 / F3 中 / F4 低 / F5 信息）+ 6 项通过项

## 处置

- **F1（client 静默降级）/ F2（空 ca_cn 下发）/ F3（mtls=0 坏证书阻止启动）**
  → 立跟进任务 **T0349-0822-rpc-mtls-degrade-fix**（development）
- **F4**（AC-2 补 cert_dir/<ca_cn>/host.* 存在性断言）→ 并入 T0349
- **F5**（GET_TIME 明文放行窗口）→ 文档化，无代码动作
