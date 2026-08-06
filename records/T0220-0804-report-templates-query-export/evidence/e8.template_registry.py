"""模板注册表（§8.2 固定模板注册表）。

- 启动时按 index.yaml 清单读取模板 YAML，以 code 去重并完成 YAML 校验。
- YAML 仅描述元数据（编码/标题/视图/列/筛选器/默认值/排序/导出格式），
  不包含 SQL/表名/关联/表达式。
- 查询接口不扫描目录、不读取 YAML，只读进程内注册表；模板随发布包更新，
  重启后生效。不使用 Redis、数据库或热更新缓存。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import yaml

from .errors import (
    TemplateNotFound,
    TemplateValidationError,
    UnknownFilterError,
    UnknownViewError,
)

_PAGE_SIZES = {5, 10, 20, 50}
_VIEW_ALIASES = {"table", "grouped_bar", "stacked_bar", "trend", "line", "summary"}
_EXPORT_FORMATS = {"csv", "pdf"}


@dataclass
class TemplateFilter:
    """模板允许的筛选器定义。"""

    name: str
    type: str
    required: bool = False
    modes: list[str] = field(default_factory=list)
    values: list[str] = field(default_factory=list)


@dataclass
class Template:
    """单套模板的对外元数据（YAML 声明）。"""

    code: str
    version: str
    title: str
    category: str
    query_handler: str
    views: list[str]
    columns: list[str]
    filters: list[TemplateFilter]
    default_filters: dict[str, Any]
    default_view: str
    default_sort: str
    default_page_size: int
    export_formats: list[str]
    file_path: str

    def to_meta(self) -> dict[str, Any]:
        """对外模板元数据（GET /report-templates 响应项）。"""
        return {
            "code": self.code,
            "version": self.version,
            "title": self.title,
            "category": self.category,
            "views": list(self.views),
            "columns": list(self.columns),
            "filters": [
                {
                    "name": f.name,
                    "type": f.type,
                    "required": f.required,
                    "modes": list(f.modes),
                    "values": list(f.values),
                }
                for f in self.filters
            ],
            "default_filters": dict(self.default_filters),
            "default_view": self.default_view,
            "default_sort": self.default_sort,
            "default_page_size": self.default_page_size,
            "export_formats": list(self.export_formats),
        }

    def filter_names(self) -> set[str]:
        return {f.name for f in self.filters}


class TemplateRegistry:
    """进程内模板注册表。启动加载后只读。"""

    def __init__(self, templates: Optional[list[Template]] = None) -> None:
        self._templates: dict[str, Template] = {}
        for t in templates or []:
            self._templates[t.code] = t

    # ---------- 加载与校验 ----------

    @classmethod
    def load(
        cls,
        root: str,
        *,
        index_name: str = "index.yaml",
    ) -> "TemplateRegistry":
        """按 index.yaml 清单加载全部模板，校验失败抛 TemplateValidationError。"""
        import pathlib

        root_path = pathlib.Path(root)
        index_path = root_path / index_name
        if not index_path.is_file():
            raise TemplateValidationError(f"index 文件缺失: {index_name}")
        raw = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
        listing = raw.get("templates")
        if not isinstance(listing, list) or not listing:
            raise TemplateValidationError(f"index 清单为空: {index_name}")

        templates: list[Template] = []
        seen: set[str] = set()
        for rel in listing:
            if not isinstance(rel, str):
                raise TemplateValidationError(f"index 条目非字符串: {rel!r}")
            tpath = root_path / rel
            if not tpath.is_file():
                raise TemplateValidationError(f"模板文件缺失: {rel}")
            tpl = cls._parse_template(tpath.read_text(encoding="utf-8"), str(rel))
            if tpl.code in seen:
                raise TemplateValidationError(f"模板 code 重复: {tpl.code}")
            seen.add(tpl.code)
            templates.append(tpl)
        return cls(templates)

    @staticmethod
    def _parse_template(text: str, file_path: str) -> Template:
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise TemplateValidationError(f"{file_path}: YAML 顶层须为映射")
        code = data.get("code")
        version = data.get("version")
        title = data.get("title")
        handler = data.get("query_handler")
        if not all(isinstance(v, str) and v for v in (code, version, title, handler)):
            raise TemplateValidationError(f"{file_path}: code/version/title/query_handler 缺失或非字符串")

        views = data.get("views", [])
        columns = data.get("columns", [])
        export_formats = data.get("export_formats", ["csv"])
        default_view = data.get("default_view")
        default_sort = data.get("default_sort", "")
        default_page_size = data.get("default_page_size", 20)
        if not isinstance(views, list) or not views:
            raise TemplateValidationError(f"{file_path}: views 缺失")
        if not isinstance(columns, list) or not columns:
            raise TemplateValidationError(f"{file_path}: columns 缺失")
        if not isinstance(export_formats, list) or not export_formats:
            raise TemplateValidationError(f"{file_path}: export_formats 缺失")
        for v in views:
            if v not in _VIEW_ALIASES:
                raise TemplateValidationError(f"{file_path}: 视图不合法 {v!r}")
        for fmt in export_formats:
            if fmt not in _EXPORT_FORMATS:
                raise TemplateValidationError(f"{file_path}: 导出格式不合法 {fmt!r}")
        if default_view not in views:
            raise TemplateValidationError(f"{file_path}: default_view 不在 views 内")
        if default_page_size not in _PAGE_SIZES:
            raise TemplateValidationError(f"{file_path}: default_page_size 须为 5/10/20/50")
        if not default_sort.endswith(("_asc", "_desc")):
            raise TemplateValidationError(f"{file_path}: default_sort 须以 _asc/_desc 结尾")

        raw_filters = data.get("filters", [])
        filters: list[TemplateFilter] = []
        if not isinstance(raw_filters, list):
            raise TemplateValidationError(f"{file_path}: filters 须为列表")
        for raw in raw_filters:
            if not isinstance(raw, dict) or "name" not in raw or "type" not in raw:
                raise TemplateValidationError(f"{file_path}: filter 缺 name/type")
            filters.append(
                TemplateFilter(
                    name=str(raw["name"]),
                    type=str(raw["type"]),
                    required=bool(raw.get("required", False)),
                    modes=[str(m) for m in raw.get("modes", [])],
                    values=[str(v) for v in raw.get("values", [])],
                )
            )

        default_filters = data.get("default_filters", {})
        if not isinstance(default_filters, dict):
            raise TemplateValidationError(f"{file_path}: default_filters 须为映射")

        category = file_path.split("/")[0] if "/" in file_path else "misc"
        return Template(
            code=code,
            version=version,
            title=title,
            category=category,
            query_handler=handler,
            views=views,
            columns=columns,
            filters=filters,
            default_filters=default_filters,
            default_view=default_view,
            default_sort=default_sort,
            default_page_size=default_page_size,
            export_formats=export_formats,
            file_path=file_path,
        )

    # ---------- 只读查询 ----------

    def get(self, code: str) -> Template:
        tpl = self._templates.get(code)
        if tpl is None:
            raise TemplateNotFound(code)
        return tpl

    def templates(self) -> list[Template]:
        return list(self._templates.values())

    def codes(self) -> list[str]:
        return list(self._templates.keys())

    def __contains__(self, code: str) -> bool:
        return code in self._templates

    def __len__(self) -> int:
        return len(self._templates)

    # ---------- 校验与解析 ----------

    def validate(
        self,
        template_code: str,
        version: str,
        filters: dict[str, Any],
        view: str,
    ) -> None:
        """T0219 TemplateRegistry 协议：模板/版本/筛选器/视图校验，非法抛错。"""
        tpl = self.get(template_code)
        if version != tpl.version:
            raise TemplateValidationError(
                f"模板版本不匹配: 期望 {tpl.version}, 收到 {version}"
            )
        self._validate_view(tpl, view)
        self._validate_filters(tpl, filters)

    def resolve(
        self, template_code: str, filters: dict[str, Any], view: str, page_size: int
    ) -> tuple[Template, dict[str, Any]]:
        """校验并规整 filters（合并默认值），返回 (模板, 规整后 filters)。"""
        tpl = self.get(template_code)
        self._validate_view(tpl, view)
        merged = dict(tpl.default_filters)
        for key, value in (filters or {}).items():
            merged[key] = value
        self._validate_filters(tpl, merged)
        if page_size not in _PAGE_SIZES:
            raise TemplateValidationError(f"页大小须为 5/10/20/50, 收到 {page_size}")
        return tpl, merged

    def _validate_view(self, tpl: Template, view: str) -> None:
        if view not in tpl.views:
            raise UnknownViewError(f"模板 {tpl.code} 不支持视图 {view!r}")

    def _validate_filters(self, tpl: Template, filters: dict[str, Any]) -> None:
        known = tpl.filter_names()
        for key in (filters or {}):
            if key not in known:
                raise UnknownFilterError(f"模板 {tpl.code} 不支持筛选器 {key!r}")
        for f in tpl.filters:
            if f.required and (not filters or filters.get(f.name) is None):
                raise UnknownFilterError(f"模板 {tpl.code} 缺必填筛选器 {f.name!r}")
