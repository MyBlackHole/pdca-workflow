"""同步导出（§8.5）：CSV 流式导出与 PDF 离线渲染实现层。

- CSV：按 Keyset 小批读取并写入，`csv_max_rows + 1` 条探测截断；每批短事务，
  不持有跨 HTTP 请求的长事务。表格式模板导出页面同列同序的原始值；图表模板
  导出支撑图表的底层聚合行，不导出图片。
- PDF：reportlab 渲染当前筛选形态。表格按 `pdf_table_rows_per_page` 分页且页首
  重复列头；图表模板按底层汇总行渲染为多页表格（每页重复表头表列）。PDF 不落盘，
  请求内生成 bytes 返回。数据行上限 `pdf_max_tabular_rows`，超出在末页脚+响应头标注。

本模块不持有连接池配额（BoundedSemaphore 由上层 Web/适配器注入），只负责
“逐批读取数据 → 写入 text/csv 或 PDF bytes”。
"""

from __future__ import annotations

import csv
import io
import math
from typing import Iterable, Optional

from .errors import ReportError
from .query_service import QueryService

# 默认配置（与 report-web.yaml 对应键同默认）
DEFAULT_CSV_MAX_ROWS = 4000
DEFAULT_PDF_ROWS_PER_PAGE = 50
DEFAULT_PDF_MAX_TABULAR_ROWS = DEFAULT_CSV_MAX_ROWS

# 读取批大小（Keyset 小批，须为合法页大小 5/10/20/50；50 兼顾吞吐与短事务）
_BATCH_SIZE = 50


class ExportConfig:
    """导出配置（对标 report-web.yaml 的 export.* 键）。"""

    def __init__(
        self,
        csv_max_rows: int = DEFAULT_CSV_MAX_ROWS,
        pdf_table_rows_per_page: int = DEFAULT_PDF_ROWS_PER_PAGE,
        pdf_max_tabular_rows: Optional[int] = None,
    ) -> None:
        if csv_max_rows < 1:
            raise ReportError("export.csv_max_rows 必须为正整数")
        if pdf_table_rows_per_page < 1:
            raise ReportError("export.pdf_table_rows_per_page 必须为正整数")
        self.csv_max_rows = csv_max_rows
        self.pdf_table_rows_per_page = pdf_table_rows_per_page
        self.pdf_max_tabular_rows = pdf_max_tabular_rows or csv_max_rows


class ExportResult:
    def __init__(
        self,
        format: str,
        content: bytes,
        columns: list[str],
        row_count: int,
        truncated: bool,
        row_limit: int,
    ) -> None:
        self.format = format
        self.content = content
        self.columns = columns
        self.row_count = row_count
        self.truncated = truncated
        self.row_limit = row_limit

    @property
    def content_type(self) -> str:
        if self.format == "csv":
            return "text/csv; charset=utf-8"
        return "application/pdf"


class ExportService:
    """面向 CSV/PDF 的逐批导出服务（复用 QueryService 的 Keyset 分页）。"""

    def __init__(self, qsvc: QueryService, config: Optional[ExportConfig] = None) -> None:
        self._qsvc = qsvc
        self._config = config or ExportConfig()

    # ---------- 行上限内逐批拉取（Keyset 分页） ----------

    def _iter_all(
        self,
        template_code: str,
        filters: Optional[dict],
        view: str,
        limit: int,
    ) -> tuple[list[str], list[dict], bool]:
        """逐批读取至多 limit 行；超出 limit 时 truncated=True。

        返回 (columns, records, truncated)。records 最多 limit 条。
        """
        columns: list[str] = []
        records: list[dict] = []
        cursor: Optional[str] = None
        truncated = False
        # 探测上限：多读 limit+1 条判断是否截断（批固定为合法页大小）
        probe = limit + 1 if limit is not None else None
        while True:
            if probe is not None and len(records) >= probe:
                truncated = True
                break
            res = self._qsvc.query(
                template_code,
                filters=filters,
                view=view,
                page_size=_BATCH_SIZE,
                cursor_token=cursor,
            )
            if not columns:
                columns = res.columns
            records.extend(res.records)
            if not res.has_more:
                break
            cursor = res.next_cursor
        if probe is not None and len(records) > limit:
            records = records[:limit]
            truncated = True
        return columns, records, truncated

    # ---------- CSV ----------

    def export_csv(
        self,
        template_code: str,
        filters: Optional[dict],
        view: str,
    ) -> ExportResult:
        columns, records, truncated = self._iter_all(
            template_code, filters, view, self._config.csv_max_rows,
        )
        buf = io.StringIO(newline="")
        writer = csv.writer(buf)
        writer.writerow(columns)
        for rec in records:
            writer.writerow([rec.get(c, "") for c in columns])
        return ExportResult(
            format="csv",
            content=buf.getvalue().encode("utf-8"),
            columns=columns,
            row_count=len(records),
            truncated=truncated,
            row_limit=self._config.csv_max_rows,
        )

    # ---------- PDF ----------

    def export_pdf(
        self,
        template_code: str,
        filters: Optional[dict],
        view: str,
    ) -> ExportResult:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import mm
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        columns, records, truncated = self._iter_all(
            template_code, filters, view, self._config.pdf_max_tabular_rows,
        )
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm,
            topMargin=12 * mm, bottomMargin=14 * mm,
            title=f"Report {template_code}",
        )
        story: list = []
        styles = getSampleStyleSheet()
        story.append(Paragraph(f"Template: {template_code}", styles["Title"]))
        story.append(Paragraph(
            f"View: {view} · Rows: {len(records)}{' · TRUNCATED at ' + str(self._config.pdf_max_tabular_rows) if truncated else ''}",
            styles["Normal"],
        ))
        story.append(Spacer(1, 4 * mm))

        rows_per_page = self._config.pdf_table_rows_per_page
        header = [str(c) for c in columns]
        data_rows = [
            [str(rec.get(c, "")) for c in columns]
            for rec in records
        ]
        # 分页 + 页首重复列头
        chunks = [
            [header] + data_rows[i:i + rows_per_page]
            for i in range(0, len(data_rows), rows_per_page)
        ]
        if not chunks:
            chunks = [[header]]
        for idx, chunk in enumerate(chunks):
            table = Table(chunk, repeatRows=1)
            table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.9, 0.92, 0.95)),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            story.append(table)
            if idx < len(chunks) - 1:
                story.append(Spacer(1, 6 * mm))
        # 末页脚截断标注
        if truncated:
            story.append(Spacer(1, 4 * mm))
            story.append(Paragraph(
                f"Result truncated at {self._config.pdf_max_tabular_rows} rows.",
                styles["Normal"],
            ))
        doc.build(story)
        return ExportResult(
            format="pdf",
            content=buf.getvalue(),
            columns=columns,
            row_count=len(records),
            truncated=truncated,
            row_limit=self._config.pdf_max_tabular_rows,
        )