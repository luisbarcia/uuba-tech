import logging
import json as json_lib

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.ids import generate_id
from app.exceptions import APIError
from app.database import get_db


# --- Structured logging ---
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "msg": record.getMessage(),
            "module": record.module,
        }
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        return json_lib.dumps(log_data, ensure_ascii=False)


handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
logger = logging.getLogger("uuba")


# --- App ---
app = FastAPI(
    title="Uúba Tech API",
    version="0.1.0",
    description="API de cobrança inteligente para PMEs brasileiras",
    docs_url=None,
    redoc_url=None,
)


# --- Scalar API Docs ---
@app.get("/docs", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


# --- Exception handlers ---
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.status,
        content={
            "type": f"https://api.uubatech.com/errors/{exc.error_type}",
            "title": exc.title,
            "status": exc.status,
            "detail": exc.detail,
            "instance": str(request.url.path),
            "request_id": getattr(request.state, "request_id", ""),
            "errors": [],
        },
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    from sqlalchemy.exc import IntegrityError
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=409,
            content={
                "type": "https://api.uubatech.com/errors/integridade",
                "title": "Erro de integridade",
                "status": 409,
                "detail": str(exc.orig) if exc.orig else "Constraint violation",
                "instance": str(request.url.path),
                "request_id": getattr(request.state, "request_id", ""),
                "errors": [],
            },
        )
    return JSONResponse(
        status_code=500,
        content={
            "type": "https://api.uubatech.com/errors/interno",
            "title": "Erro interno",
            "status": 500,
            "detail": "Erro inesperado no servidor",
            "instance": str(request.url.path),
            "request_id": getattr(request.state, "request_id", ""),
            "errors": [],
        },
    )


# --- Middleware ---
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = generate_id("req")
    request.state.request_id = request_id
    logger.info(f"{request.method} {request.url.path}", extra={"request_id": request_id})
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response


# --- Routers ---
from app.routers import clientes, faturas, cobrancas
app.include_router(clientes.router)
app.include_router(faturas.router)
app.include_router(cobrancas.router)


# --- Health ---
@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}
