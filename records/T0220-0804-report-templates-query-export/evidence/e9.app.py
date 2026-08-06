"""report-web FastAPI 应用（子方案 §2–§5 HTTP 契约）。

- 认证：验证码/登录/改密/登出/系统设置。
- 备份域管理：CRUD/启停/删除/连通性。
- 保存报告：CRUD + sub 隔离。
所有业务依赖（repository/service/client）通过 create_app 注入，便于测试替换。
"""

from __future__ import annotations

import fakeredis
import redis
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel

from report_center_db.postgres.connection import PostgreSQLConnectionFactory
from report_center_db.postgres.preference import PostgreSQLReportPreferenceRepository
from report_center_db.postgres.user import PostgreSQLReportUserRepository
from report_center_db.security.aes import AESCipher
from report_center_db.security.jwt import TokenSigner, TokenType, TokenVerifier
from report_center_db.security.password import PasswordHasher, PasswordPolicyViolation
from report_center_db.services.auth_service import (
    AuthError,
    AuthService,
    CaptchaService,
    LoginLockedError,
    RedisTokenStore,
    TokenRevokedError,
)
from report_center_db.services.domain_repository import (
    BackupDomainLimitReached,
    DomainError,
    DomainNameInvalid,
    PostgreSQLDomainRepository,
)
from report_center_db.services.domain_service import (
    DomainNotDisabled,
    DomainService,
    DomainServiceError,
)
from report_center_db.services.redis_store import RedisKeyStore
from report_center_db.services.rpc_clients import CDMRpcConnectivityClient
from report_center_db.services.saved_report_service import (
    SavedReportError,
    SavedReportNameInvalid,
    SavedReportService,
    TemplateRegistry,
    TemplateUnknown,
)
from report_web.report.errors import (
    ExportBusyError,
    QueryBusyError,
    QueryTimeoutError,
    ReportError,
    TemplateNotFound,
    TemplateValidationError,
)
from report_web.report.export_service import ExportConfig, ExportService
from report_web.report.query_handlers import ReportQueryHandlerRegistry
from report_web.report.query_service import QueryService
from report_web.report.quota import ReadPoolQuota

_ERROR_HTTP = {
    "INVALID_CREDENTIALS": 401,
    "INVALID_CAPTCHA": 400,
    "LOGIN_LOCKED": 429,
    "TOKEN_INVALID": 401,
    "PASSWORD_POLICY_VIOLATION": 400,
    "SETTING_INVALID": 400,
    "DOMAIN_NAME_INVALID": 400,
    "DOMAIN_NAME_DUPLICATED": 409,
    "PASSWORD_ENCRYPT_FAILED": 400,
    "BACKUP_DOMAIN_LIMIT_REACHED": 429,
    "DOMAIN_NOT_DISABLED": 409,
    "DOMAIN_NOT_FOUND": 404,
    "RPC_CONNECT_FAILED": 502,
    "RPC_TIMEOUT": 502,
    "RPC_CLI_AUTH_FAILED": 502,
    "RPC_EXEC_FAILED": 502,
    "TEMPLATE_UNKNOWN": 400,
    "SAVED_REPORT_NAME_INVALID": 400,
    "SAVED_REPORT_NAME_DUPLICATED": 409,
    "SAVED_REPORT_NOT_FOUND": 404,
    "TEMPLATE_NOT_FOUND": 404,
    "TEMPLATE_VALIDATION_ERROR": 400,
    "QUERY_BUSY": 429,
    "EXPORT_BUSY": 429,
    "QUERY_TIMEOUT": 503,
}


class _LoginRequest(BaseModel):
    session_id: str
    username: str
    password: str
    captcha: str


class _ChangePasswordRequest(BaseModel):
    new_password: str


class _TtlRequest(BaseModel):
    value: int
    unit: str


class _DomainCreate(BaseModel):
    domain_name: str
    web_ip: str
    web_port: int
    rpc_port: int = 6611
    username: str
    password: str


class _DomainUpdate(BaseModel):
    domain_name: str | None = None
    web_ip: str | None = None
    web_port: int | None = None
    rpc_port: int | None = None
    username: str | None = None
    password: str | None = None


class _SavedReportCreate(BaseModel):
    report_name: str
    template_code: str
    template_version: str
    filters_snapshot: dict
    view_snapshot: str | None = None


class _SavedReportUpdate(BaseModel):
    report_name: str | None = None
    filters_snapshot: dict | None = None
    view_snapshot: str | None = None


class _QueryRequest(BaseModel):
    filters: dict | None = None
    view: str = "table"
    page_size: int = 20
    cursor: str | None = None


class _ExportRequest(BaseModel):
    filters: dict | None = None
    view: str = "table"
    format: str = "csv"


def _error_to_http(error_code: str, message: str, request_id: str) -> JSONResponse:
    http_code = _ERROR_HTTP.get(error_code, 500)
    return JSONResponse(
        status_code=http_code,
        content={"error_code": error_code, "message": message, "request_id": request_id},
    )


def create_app(
    *,
    factory: PostgreSQLConnectionFactory,
    aes_key_base64: str,
    private_key_pem: str,
    redis_url: str | None,
    scheduler_factory,
    template_registry: TemplateRegistry | None = None,
    connectivity_factory=None,
    captcha_enabled: bool = True,
    bootstrap_admin: bool = True,
    query_quota: int = 16,
    export_quota: int = 2,
    metric_quota: int = 2,
    csv_max_rows: int = 4000,
    pdf_table_rows_per_page: int = 50,
) -> FastAPI:
    cipher = AESCipher(aes_key_base64)
    users = PostgreSQLReportUserRepository(factory)
    prefs = PostgreSQLReportPreferenceRepository(factory)
    hasher = PasswordHasher()
    if bootstrap_admin:
        users.ensure_bootstrap_admin("admin", hasher.hash("admin"))
    signer = TokenSigner(private_key_pem)
    verifier = TokenVerifier(signer.public_key_pem())

    if redis_url:
        redis_client = redis.Redis.from_url(redis_url)
    else:
        redis_client = fakeredis.FakeStrictRedis()
    store = RedisKeyStore(redis_client)
    captcha_service = CaptchaService(store)
    token_store = RedisTokenStore(store)
    auth = AuthService(
        users,
        hasher,
        signer,
        token_store,
        token_ttl_seconds=1800,
        store=store,
        ttl_provider=lambda: int(prefs.get_token_ttl().setting_value),
    )

    domain_repo = PostgreSQLDomainRepository(factory, cipher)
    domain_service = DomainService(domain_repo, scheduler_factory, connectivity_factory)

    saved_repo = SavedReportService(prefs, template_registry)

    # T0220 报表查询/导出服务（模板注册表、固定 Handler、Keyset 分页、读池配额）
    handlers = ReportQueryHandlerRegistry()
    qsvc = QueryService(factory, template_registry, handlers)
    # 导出查询使用独立 statement_timeout=30s（§8.5），页面查询保持 2s
    export_qsvc = QueryService(factory, template_registry, handlers, statement_timeout_ms=30000)
    quota = ReadPoolQuota(query=query_quota, export=export_quota, metric=metric_quota)
    export_svc = ExportService(
        export_qsvc,
        ExportConfig(csv_max_rows=csv_max_rows, pdf_table_rows_per_page=pdf_table_rows_per_page),
    )

    app = FastAPI(title="report-web")

    @app.middleware("http")
    async def _request_id(request: Request, call_next):
        import uuid as _uuid

        request.state.request_id = str(_uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-Id"] = request.state.request_id
        return response

    def _principal(authorization: str | None = Header(default=None)) -> dict:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="缺少访问 Token")
        token = authorization.split(" ", 1)[1]
        try:
            return auth.validate(token, verifier)
        except TokenRevokedError as exc:
            raise HTTPException(status_code=401, detail=exc.code) from exc

    def _admin_required(principal: dict = Depends(_principal)) -> dict:
        if not principal.get("is_admin"):
            raise HTTPException(status_code=403, detail="需要管理员权限")
        return principal

    # ---- 认证 ----

    @app.get("/auth/captcha")
    def get_captcha():
        session_id, image, _ = captcha_service.generate()
        return {"session_id": session_id, "captcha_image": image}

    @app.post("/auth/login")
    def login(body: _LoginRequest, request: Request):
        if captcha_enabled:
            captcha_ok = captcha_service.verify(body.session_id, body.captcha)
            if not captcha_ok:
                return _error_to_http("INVALID_CAPTCHA", "验证码错误", request.state.request_id)
        try:
            result = auth.login(body.username, body.password, captcha_ok=True)
        except LoginLockedError as exc:
            return _error_to_http(exc.code, "登录失败次数过多", str(request.state.request_id or ""))
        except AuthError as exc:
            return _error_to_http(exc.code, "用户名或密码错误", str(request.state.request_id or ""))
        return result

    @app.post("/auth/change-password")
    def change_password(body: _ChangePasswordRequest, authorization: str | None = Header(default=None), request: Request = None):
        if not authorization or not authorization.startswith("Bearer "):
            return _error_to_http("TOKEN_INVALID", "缺少 Token", "")
        token = authorization.split(" ", 1)[1]
        try:
            auth.change_password(token, body.new_password, verifier)
        except PasswordPolicyViolation as exc:
            return _error_to_http("PASSWORD_POLICY_VIOLATION", str(exc), "")
        except AuthError as exc:
            return _error_to_http("TOKEN_INVALID", str(exc), "")
        return JSONResponse(status_code=204, content=None)

    @app.post("/auth/logout")
    def logout(principal: dict = Depends(_principal)):
        auth.logout(principal["subject_id"])
        return JSONResponse(status_code=204, content=None)

    @app.get("/system-settings/report-access-token-ttl")
    def get_ttl(principal: dict = Depends(_principal)):
        setting = prefs.get_token_ttl()
        return {"setting_key": setting.setting_key, "setting_value": setting.setting_value}

    @app.put("/system-settings/report-access-token-ttl")
    def put_ttl(body: _TtlRequest, principal: dict = Depends(_admin_required)):
        seconds = _parse_ttl_seconds(body.value, body.unit)
        if seconds is None:
            return _error_to_http("SETTING_INVALID", "非法 TTL 值", "")
        prefs.set_token_ttl(seconds, principal["subject_id"])
        return {"setting_key": "report_access_token_ttl_seconds", "setting_value": str(seconds)}

    # ---- 备份域 ----

    @app.get("/backup-domains")
    def list_domains(keyword: str | None = None, principal: dict = Depends(_principal)):
        page = domain_service.list_domains(keyword)
        return {
            "records": [_domain_public(d) for d in page.records],
            "total": page.total,
            "next_cursor": page.next_cursor,
            "has_more": page.has_more,
        }

    @app.post("/backup-domains")
    def create_domain(body: _DomainCreate, principal: dict = Depends(_admin_required)):
        from report_center_db.postgres.errors import UniqueViolationError

        try:
            domain = domain_service.create_domain(
                domain_name=body.domain_name,
                web_ip=body.web_ip,
                web_port=body.web_port,
                rpc_port=body.rpc_port,
                username=body.username,
                password=body.password,
            )
        except DomainNameInvalid as exc:
            return _error_to_http("DOMAIN_NAME_INVALID", str(exc), "")
        except BackupDomainLimitReached as exc:
            return _error_to_http("BACKUP_DOMAIN_LIMIT_REACHED", str(exc), "")
        except UniqueViolationError as exc:
            return _error_to_http("DOMAIN_NAME_DUPLICATED", "域名已存在", "")
        except DomainError as exc:
            return _error_to_http("PASSWORD_ENCRYPT_FAILED", "密码加密失败", "")
        return JSONResponse(status_code=201, content=_domain_public(domain))

    @app.patch("/backup-domains/{domain_id}")
    def update_domain(domain_id: int, body: _DomainUpdate, principal: dict = Depends(_admin_required)):
        from report_center_db.services.domain_repository import DomainNotFound

        try:
            domain = domain_repo.update(
                domain_id,
                domain_name=body.domain_name,
                web_ip=body.web_ip,
                web_port=body.web_port,
                rpc_port=body.rpc_port,
                username=body.username,
                password=body.password,
            )
        except DomainNotFound as exc:
            return _error_to_http("DOMAIN_NOT_FOUND", str(exc), "")
        except DomainNameInvalid as exc:
            return _error_to_http("DOMAIN_NAME_INVALID", str(exc), "")
        return _domain_public(domain)

    @app.post("/backup-domains/{domain_id}/enable")
    def enable_domain(domain_id: int, principal: dict = Depends(_admin_required)):
        try:
            domain_service.enable_domain(domain_id)
        except Exception as exc:
            return _error_to_http("RPC_EXEC_FAILED", str(exc), "")
        return {"id": domain_id, "collection_enabled": True}

    @app.post("/backup-domains/{domain_id}/disable")
    def disable_domain(domain_id: int, principal: dict = Depends(_admin_required)):
        try:
            domain_service.disable_domain(domain_id)
        except Exception as exc:
            return _error_to_http("RPC_EXEC_FAILED", str(exc), "")
        return {"id": domain_id, "collection_enabled": False}

    @app.delete("/backup-domains/{domain_id}")
    def delete_domain(domain_id: int, principal: dict = Depends(_admin_required)):
        try:
            domain_service.delete_domain(domain_id)
        except DomainNotDisabled as exc:
            return _error_to_http("DOMAIN_NOT_DISABLED", str(exc), "")
        except DomainError as exc:
            return _error_to_http("DOMAIN_NOT_FOUND", str(exc), "")
        return JSONResponse(status_code=204, content=None)

    @app.post("/backup-domains/{domain_id}/test-connection")
    def test_connection(domain_id: int, principal: dict = Depends(_admin_required)):
        domain = domain_repo.get_active_by_id(domain_id)
        if domain is None:
            return _error_to_http("DOMAIN_NOT_FOUND", "域不存在", "")
        channel = connectivity_factory() if connectivity_factory else None
        if channel is None:
            return _error_to_http("RPC_EXEC_FAILED", "连通性通道未配置", "")
        client = CDMRpcConnectivityClient(channel)
        result = client.test(
            web_ip=domain.web_ip,
            rpc_port=domain.rpc_port,
            username=domain.username,
            password=_decrypt_password(domain.password, cipher),
        )
        return {"result_code": result.result_code, "latency_ms": result.latency_ms}

    # ---- 保存报告 ----

    @app.post("/saved-reports")
    def save_report(body: _SavedReportCreate, principal: dict = Depends(_principal)):
        try:
            saved = saved_repo.save_report(
                owner_subject_id=principal["subject_id"],
                report_name=body.report_name,
                template_code=body.template_code,
                template_version=body.template_version,
                filters_snapshot=body.filters_snapshot,
                view_snapshot=body.view_snapshot,
            )
        except TemplateUnknown as exc:
            return _error_to_http("TEMPLATE_UNKNOWN", str(exc), "")
        except SavedReportNameInvalid as exc:
            return _error_to_http("SAVED_REPORT_NAME_INVALID", str(exc), "")
        except SavedReportError as exc:
            return _error_to_http("SAVED_REPORT_NAME_DUPLICATED", str(exc), "")
        return JSONResponse(status_code=201, content={"saved_report_id": str(saved.saved_report_id)})

    @app.get("/saved-reports")
    def list_reports(keyword: str | None = None, template_code: str | None = None, principal: dict = Depends(_principal)):
        records = saved_repo.list_reports(
            principal["subject_id"], keyword=keyword, template_code=template_code
        )
        return {"records": [_report_public(r) for r in records]}

    @app.get("/saved-reports/{report_id}")
    def get_report(report_id: str, principal: dict = Depends(_principal)):
        import uuid as _uuid

        try:
            report_uuid = _uuid.UUID(report_id)
        except ValueError:
            return _error_to_http("SAVED_REPORT_NOT_FOUND", "报告不存在", "")
        report = saved_repo.get_report(principal["subject_id"], report_uuid)
        if report is None:
            return _error_to_http("SAVED_REPORT_NOT_FOUND", "报告不存在", "")
        return _report_public(report)

    @app.patch("/saved-reports/{report_id}")
    def update_report(report_id: str, body: _SavedReportUpdate, principal: dict = Depends(_principal)):
        import uuid as _uuid

        try:
            report_uuid = _uuid.UUID(report_id)
        except ValueError:
            return _error_to_http("SAVED_REPORT_NOT_FOUND", "报告不存在", "")
        from report_center_db.services.saved_report_service import SavedReportNotFound

        try:
            updated = saved_repo.update_report(
                principal["subject_id"],
                report_uuid,
                report_name=body.report_name,
                filters_snapshot=body.filters_snapshot,
                view_snapshot=body.view_snapshot,
            )
        except SavedReportNotFound as exc:
            return _error_to_http("SAVED_REPORT_NOT_FOUND", str(exc), "")
        except TemplateUnknown as exc:
            return _error_to_http("TEMPLATE_UNKNOWN", str(exc), "")
        except SavedReportNameInvalid as exc:
            return _error_to_http("SAVED_REPORT_NAME_INVALID", str(exc), "")
        return _report_public(updated)

    @app.delete("/saved-reports/{report_id}")
    def delete_report(report_id: str, principal: dict = Depends(_principal)):
        import uuid as _uuid

        deleted = saved_repo.delete_report(principal["subject_id"], _uuid.UUID(report_id))
        if not deleted:
            return _error_to_http("SAVED_REPORT_NOT_FOUND", "报告不存在", "")
        return JSONResponse(status_code=204, content=None)

    # ---------- 报表查询与导出（§4） ----------

    def _report_error_response(request: Request, exc: ReportError) -> JSONResponse:
        return _error_to_http(exc.code, str(exc), getattr(request.state, "request_id", ""))

    @app.get("/report-templates")
    def list_templates(principal: dict = Depends(_principal), request: Request = None):
        try:
            return {"templates": [t.to_meta() for t in template_registry.templates()]}
        except ReportError as exc:
            return _report_error_response(request, exc)

    @app.post("/report-templates/{template_code}/query")
    def report_query(template_code: str, body: _QueryRequest, principal: dict = Depends(_principal), request: Request = None):
        try:
            with quota.query_guard():
                result = qsvc.query(
                    template_code,
                    filters=body.filters,
                    view=body.view,
                    page_size=body.page_size,
                    cursor_token=body.cursor,
                )
            return result.to_dict()
        except TemplateValidationError as exc:
            return _error_to_http("TEMPLATE_VALIDATION_ERROR", str(exc), getattr(request.state, "request_id", ""))
        except TemplateNotFound as exc:
            return _error_to_http("TEMPLATE_NOT_FOUND", str(exc), getattr(request.state, "request_id", ""))
        except QueryBusyError as exc:
            return _error_to_http("QUERY_BUSY", str(exc), getattr(request.state, "request_id", ""))
        except QueryTimeoutError as exc:
            return _error_to_http("QUERY_TIMEOUT", str(exc), getattr(request.state, "request_id", ""))
        except ReportError as exc:
            return _report_error_response(request, exc)

    @app.post("/report-templates/{template_code}/export")
    def report_export(template_code: str, body: _ExportRequest, principal: dict = Depends(_principal), request: Request = None):
        try:
            with quota.export_guard():
                if body.format == "pdf":
                    result = export_svc.export_pdf(template_code, filters=body.filters, view=body.view)
                    return Response(
                        content=result.content,
                        media_type="application/pdf",
                        headers={"X-Report-Truncated": str(result.truncated).lower(),
                                 "X-Report-Row-Limit": str(result.row_limit)},
                    )
                result = export_svc.export_csv(template_code, filters=body.filters, view=body.view)
                return StreamingResponse(
                    iter([result.content]),
                    media_type="text/csv; charset=utf-8",
                    headers={"X-Report-Truncated": str(result.truncated).lower(),
                             "X-Report-Row-Limit": str(result.row_limit)},
                )
        except ExportBusyError as exc:
            return _error_to_http("EXPORT_BUSY", str(exc), getattr(request.state, "request_id", ""))
        except QueryTimeoutError as exc:
            return _error_to_http("QUERY_TIMEOUT", str(exc), getattr(request.state, "request_id", ""))
        except ReportError as exc:
            return _report_error_response(request, exc)

    return app


def _parse_ttl_seconds(value: int, unit: str) -> int | None:
    if value <= 0:
        return None
    factor = {"minute": 60, "hour": 3600}.get(unit)
    if factor is None:
        return None
    return value * factor


def _domain_public(domain) -> dict:
    return {
        "id": domain.id,
        "domain_name": domain.domain_name,
        "web_ip": domain.web_ip,
        "web_port": domain.web_port,
        "rpc_port": domain.rpc_port,
        "username": domain.username,
        "collection_enabled": domain.collection_enabled,
        "is_deleted": domain.is_deleted,
        "created_at": str(domain.created_at) if domain.created_at else None,
        "updated_at": str(domain.updated_at) if domain.updated_at else None,
    }


def _report_public(report) -> dict:    return {
        "saved_report_id": str(report.saved_report_id),
        "report_name": report.report_name,
        "template_code": report.template_code,
        "template_version": report.template_version,
        "filters_snapshot": report.filters_snapshot,
        "view_snapshot": report.view_snapshot,
        "created_at": str(report.created_at) if report.created_at else None,
        "updated_at": str(report.updated_at) if report.updated_at else None,
    }


def _decrypt_password(ciphertext: str, cipher: AESCipher) -> str:
    return cipher.decrypt(ciphertext)
