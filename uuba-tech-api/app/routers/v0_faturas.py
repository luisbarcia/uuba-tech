"""Router v0/faturas — endpoint de compatibilidade com CFO Automation API.

Aceita o payload CanonicalMessage (formato da CFO API) e encaminha ao n8n
webhook para processamento no ERP. Permite migracao transparente:
cliente muda URL + API key, zero mudanca no payload.

Features:
- ?dry_run=true → valida payload sem enviar ao ERP
- Idempotency-Key header → dedup via DB cache (24h TTL)

Lifecycle: deprecated quando cliente migrar para POST /api/v1/faturas.

n8n Webhook Headers (convencao obrigatoria):
    Todo forward da API para webhooks n8n DEVE incluir:
    - X-Tenant-Id: ID do tenant que originou o request
    - X-Request-Id: ID unico do request para rastreamento
    - X-API-Base-URL: Base URL da API (ex: https://api.uuba.tech)
    - X-API-Endpoint: URL completa do endpoint que originou (ex: https://api.uuba.tech/api/v0/faturas)
    Isso permite que workflows n8n facam callbacks para a API sem hardcode de URLs.
"""

import json
import logging
import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Body, Depends, Header, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key import require_permission, verify_api_key
from app.auth.idempotency import check_idempotency, save_idempotency
from app.database import get_db
from app.exceptions import APIError
from app.schemas.receivable import (
    CanonicalMessage,
    CustomerResult,
    OperationResult,
    OperationStatus,
    ProblemDetails,
    Receivable,
    ReceivableStatus,
    SaleOperation,
    ValidationResult,
    ValidationWarning,
)
from app.utils.ids import generate_id

logger = logging.getLogger("uuba")

N8N_WEBHOOK_URL = os.environ.get(
    "N8N_RECEIVABLE_WEBHOOK_URL",
    "https://n8n.srv921702.hstgr.cloud/webhook/cfo/v1/receivables",
)
N8N_TIMEOUT = float(os.environ.get("N8N_WEBHOOK_TIMEOUT", "30"))
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.uuba.tech")

router = APIRouter(
    prefix="/api/v0/faturas",
    tags=["v0-compat"],
    dependencies=[Depends(verify_api_key), Depends(require_permission("receivables:write"))],
)


async def _forward_to_n8n(
    tenant_id: str,
    request_id: str,
    payload: dict,
) -> dict:
    """Encaminha payload ao n8n webhook e retorna a resposta."""
    try:
        async with httpx.AsyncClient(timeout=N8N_TIMEOUT) as client:
            response = await client.post(
                N8N_WEBHOOK_URL,
                json=payload,
                headers={
                    "X-Tenant-Id": tenant_id,
                    "X-Request-Id": request_id,
                    "X-API-Base-URL": API_BASE_URL,
                    "X-API-Endpoint": f"{API_BASE_URL}/api/v0/faturas",
                    "Content-Type": "application/json",
                },
            )
        if response.status_code >= 400:
            logger.error(
                "n8n webhook error: %d %s",
                response.status_code,
                response.text[:500],
            )
            raise APIError(
                502,
                "n8n-error",
                "Erro no processamento",
                f"n8n retornou {response.status_code}. Tente novamente.",
            )
        return response.json()
    except httpx.TimeoutException:
        logger.error("n8n webhook timeout after %ss", N8N_TIMEOUT)
        raise APIError(
            504,
            "n8n-timeout",
            "Timeout no processamento",
            "O processamento demorou mais que o esperado. Tente novamente.",
        )
    except httpx.HTTPError as exc:
        logger.error("n8n webhook connection error: %s", exc)
        raise APIError(
            502,
            "n8n-unavailable",
            "Servico de processamento indisponivel",
            "Nao foi possivel conectar ao processador. Tente novamente.",
        )


def _validate_payload(data: CanonicalMessage) -> ValidationResult:
    """Valida o payload sem enviar ao ERP. Retorna ValidationResult."""
    warnings: list[ValidationWarning] = []

    # Verificar campos recomendados
    if not data.customer.email:
        warnings.append(
            ValidationWarning(
                pointer="/customer/email",
                code="missing_email",
                detail="Customer has no email. Recommended for ERP contact sync.",
            )
        )
    if not data.customer.mobile and not data.customer.phone:
        warnings.append(
            ValidationWarning(
                pointer="/customer/mobile",
                code="missing_phone",
                detail="Customer has no phone number. Recommended for ERP contact sync.",
            )
        )

    total_sales = 0
    total_contracts = 0
    total_value = 0.0

    for op in data.operations:
        if isinstance(op, SaleOperation):
            total_sales += 1
            total_value += op.sale.amount
        else:
            total_contracts += 1
            if op.service.price:
                total_value += op.service.price

    return ValidationResult(
        valid=True,
        customer_type=data.customer.type.value,
        operations_count=len(data.operations),
        total_sales=total_sales,
        total_contracts=total_contracts,
        total_value=total_value,
        warnings=warnings,
    )


@router.post(
    "",
    status_code=200,
    summary="Criar fatura(s) via Canonical Data Model",
    description=(
        "Endpoint de compatibilidade com a CFO Automation API. "
        "Aceita o payload CanonicalMessage (customer + operations + payment_method) "
        "e encaminha ao n8n para processamento no ERP.\n\n"
        "**Responses:**\n"
        "- `201` — Receivable criado (dry_run=false)\n"
        "- `200` — ValidationResult (dry_run=true)\n\n"
        "**Idempotency:** Envie `Idempotency-Key: <UUID>` para dedup. "
        "Mesmo key + mesmo body em 24h retorna a resposta original. "
        "Mesmo key + body diferente retorna 422.\n\n"
        "Para o formato nativo, use `POST /api/v1/faturas`."
    ),
    responses={
        201: {
            "model": Receivable,
            "description": "Receivable criado com sucesso no ERP",
            "content": {
                "application/json": {
                    "example": {
                        "id": "recv_abc123def456",
                        "object": "receivable",
                        "status": "completed",
                        "customer": {"id": "cst_abc123", "created": True},
                        "operations": [
                            {
                                "id": "op_abc123",
                                "object": "operation",
                                "type": "sale",
                                "status": "created",
                                "external_id": "12345",
                            }
                        ],
                        "environment": "live",
                        "created_at": "2026-04-09T14:30:00-03:00",
                    }
                }
            },
        },
        200: {
            "model": ValidationResult,
            "description": "Resultado da validacao (dry_run=true)",
            "content": {
                "application/json": {
                    "example": {
                        "object": "validation_result",
                        "valid": True,
                        "customer_type": "PJ",
                        "operations_count": 2,
                        "total_sales": 2,
                        "total_contracts": 0,
                        "total_value": 3500.0,
                        "warnings": [
                            {
                                "pointer": "/customer/email",
                                "code": "missing_email",
                                "detail": "Customer has no email. Recommended for ERP contact sync.",
                            }
                        ],
                    }
                }
            },
        },
        401: {
            "model": ProblemDetails,
            "description": "API key ausente ou invalida",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.uuba.tech/errors/auth-invalida",
                        "title": "Autenticacao invalida",
                        "status": 401,
                        "detail": "API key ausente ou invalida",
                        "instance": "/api/v0/faturas",
                        "request_id": "req_abc123",
                        "errors": [],
                    }
                }
            },
        },
        422: {
            "model": ProblemDetails,
            "description": "Erro de validacao ou Idempotency mismatch",
            "content": {
                "application/json": {
                    "examples": {
                        "validation_error": {
                            "summary": "Erro de validacao do payload",
                            "value": {
                                "type": "https://api.uuba.tech/errors/validacao",
                                "title": "Erro de validacao",
                                "status": 422,
                                "detail": "2 campo(s) com erro de validacao.",
                                "instance": "/api/v0/faturas",
                                "request_id": "req_abc123",
                                "errors": [
                                    {
                                        "pointer": "/customer/document",
                                        "code": "string_too_short",
                                        "detail": "String should have at least 11 characters",
                                    },
                                    {
                                        "pointer": "/operations/0/sale/amount",
                                        "code": "greater_than",
                                        "detail": "Input should be greater than 0",
                                    },
                                ],
                            },
                        },
                        "idempotency_mismatch": {
                            "summary": "Idempotency-Key reutilizada com body diferente",
                            "value": {
                                "type": "https://api.uuba.tech/errors/idempotency-mismatch",
                                "title": "Idempotency key reutilizada com body diferente",
                                "status": 422,
                                "detail": "A key 'uuid' ja foi usada com um payload diferente.",
                                "instance": "/api/v0/faturas",
                                "request_id": "req_abc123",
                                "errors": [],
                            },
                        },
                    }
                }
            },
        },
        502: {
            "model": ProblemDetails,
            "description": "Erro no processamento (n8n indisponivel)",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.uuba.tech/errors/n8n-error",
                        "title": "Erro no processamento",
                        "status": 502,
                        "detail": "n8n retornou 500. Tente novamente.",
                        "instance": "/api/v0/faturas",
                        "request_id": "req_abc123",
                        "errors": [],
                    }
                }
            },
        },
        504: {
            "model": ProblemDetails,
            "description": "Timeout no processamento",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.uuba.tech/errors/n8n-timeout",
                        "title": "Timeout no processamento",
                        "status": 504,
                        "detail": "O processamento demorou mais que o esperado. Tente novamente.",
                        "instance": "/api/v0/faturas",
                        "request_id": "req_abc123",
                        "errors": [],
                    }
                }
            },
        },
    },
)
async def create_receivable(
    request: Request,
    data: CanonicalMessage = Body(
        ...,
        openapi_examples={
            "sale_pj": {
                "summary": "Venda avulsa (PJ)",
                "description": "Registro de venda para empresa com CNPJ",
                "value": {
                    "customer": {
                        "type": "PJ",
                        "document": "12345678000190",
                        "name": "Startup ABC Ltda",
                        "trade_name": "Startup ABC",
                        "email": "financeiro@startup.com",
                        "mobile": "(11) 99999-8888",
                    },
                    "operations": [
                        {
                            "service": {
                                "code": "CONSULT-01",
                                "description": "Consultoria em gestao financeira",
                                "price": 2500.00,
                            },
                            "sale": {
                                "amount": 2500.00,
                                "due_date": "2026-05-15",
                                "description": "Parcela unica",
                            },
                        }
                    ],
                    "payment_method": "BOLETO_BANCARIO",
                },
            },
            "sale_pf": {
                "summary": "Venda avulsa (PF)",
                "description": "Registro de venda para pessoa fisica com CPF",
                "value": {
                    "customer": {
                        "type": "PF",
                        "document": "12345678900",
                        "name": "Joao Silva",
                        "email": "joao@email.com",
                        "mobile": "(11) 98765-4321",
                    },
                    "operations": [
                        {
                            "service": {
                                "code": "TRAIN-01",
                                "description": "Treinamento individual",
                                "price": 500.00,
                            },
                            "sale": {
                                "amount": 500.00,
                                "due_date": "2026-05-01",
                            },
                        }
                    ],
                    "payment_method": "BOLETO_BANCARIO",
                },
            },
            "contract_mensal": {
                "summary": "Contrato mensal (assinatura)",
                "description": "Contrato recorrente open-ended (cycles=null)",
                "value": {
                    "customer": {
                        "type": "PJ",
                        "document": "98765432000199",
                        "name": "Empresa XYZ Ltda",
                        "email": "admin@xyz.com",
                        "contacts": [
                            {
                                "name": "Ana Costa",
                                "email": "ana@xyz.com",
                                "role": "CFO",
                            }
                        ],
                    },
                    "operations": [
                        {
                            "service": {
                                "code": "SAAS-PRO",
                                "description": "Plano Pro - SaaS mensal",
                                "price": 499.00,
                            },
                            "contract": {
                                "start_date": "2026-05-01",
                                "cycles": None,
                                "frequency": "MENSAL",
                                "due_day": 5,
                                "emission_day": 1,
                            },
                        }
                    ],
                    "payment_method": "BOLETO_BANCARIO",
                },
            },
            "parcelamento_3x": {
                "summary": "Parcelamento em 3x",
                "description": "3 operacoes de venda com datas de vencimento sequenciais",
                "value": {
                    "customer": {
                        "type": "PJ",
                        "document": "11222333000181",
                        "name": "Industria Beta SA",
                        "email": "financeiro@beta.com",
                    },
                    "operations": [
                        {
                            "service": {"code": "IMPL-01", "description": "Implantacao do sistema"},
                            "sale": {"amount": 5000.00, "due_date": "2026-05-15", "description": "Parcela 1/3"},
                        },
                        {
                            "service": {"code": "IMPL-01", "description": "Implantacao do sistema"},
                            "sale": {"amount": 5000.00, "due_date": "2026-06-15", "description": "Parcela 2/3"},
                        },
                        {
                            "service": {"code": "IMPL-01", "description": "Implantacao do sistema"},
                            "sale": {"amount": 5000.00, "due_date": "2026-07-15", "description": "Parcela 3/3"},
                        },
                    ],
                    "payment_method": "BOLETO_BANCARIO",
                },
            },
        },
    ),
    db: AsyncSession = Depends(get_db),
    dry_run: bool = Query(default=False, description="Validar sem enviar ao ERP"),
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
        description="UUID v4 para idempotencia (24h TTL)",
    ),
):
    """Processa CanonicalMessage: valida, encaminha ao n8n, retorna Receivable."""
    tenant_id = request.state.tenant_id
    request_id = generate_id("recv")

    # --- Dry-run: valida e retorna sem processar ---
    if dry_run:
        result = _validate_payload(data)
        logger.info(
            "v0/faturas: dry-run tenant=%s ops=%d valid=%s",
            tenant_id,
            len(data.operations),
            result.valid,
        )
        return JSONResponse(
            content=result.model_dump(),
            headers={"X-Request-Id": request_id},
        )

    # --- Idempotency check (antes de encaminhar ao n8n) ---
    body_bytes = data.model_dump_json().encode()

    if idempotency_key:
        cached = await check_idempotency(db, tenant_id, idempotency_key, body_bytes)
        if cached:
            logger.info(
                "v0/faturas: idempotency hit key=%s tenant=%s",
                idempotency_key,
                tenant_id,
            )
            return JSONResponse(
                content=json.loads(cached.response_body),
                status_code=cached.response_status,
                headers={
                    "X-Request-Id": request_id,
                    "X-Idempotent-Replayed": "true",
                },
            )

    # --- Processamento real: encaminhar ao n8n ---
    payload = data.model_dump(mode="json")
    n8n_response = await _forward_to_n8n(tenant_id, request_id, payload)

    # Se n8n retornou response no formato Receivable, usar diretamente
    if "customer" in n8n_response and "operations" in n8n_response:
        customer = CustomerResult(**n8n_response["customer"])
        operations = [OperationResult(**op) for op in n8n_response.get("operations", [])]
        status = ReceivableStatus(n8n_response.get("status", "completed"))
    else:
        # Fallback: montar response a partir do payload original
        customer = CustomerResult(
            id=n8n_response.get("customer_id", generate_id("cst")),
            created=n8n_response.get("customer_created", True),
        )
        operations = []
        for i, op in enumerate(data.operations):
            is_sale = isinstance(op, SaleOperation)
            op_ids = n8n_response.get("operation_ids", [])
            operations.append(
                OperationResult(
                    id=op_ids[i] if i < len(op_ids) else generate_id("op"),
                    type="sale" if is_sale else "contract",
                    status=OperationStatus.CREATED,
                )
            )
        status = ReceivableStatus(n8n_response.get("status", "completed"))

    # Environment definido por verify_api_key com base no prefixo da key
    environment = getattr(request.state, "environment", "live")

    receivable = Receivable(
        id=request_id,
        status=status,
        customer=customer,
        operations=operations,
        environment=environment,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    response_status = 201 if status != ReceivableStatus.FAILED else 200
    response_body = receivable.model_dump()

    # --- Idempotency save (apos resposta construida) ---
    if idempotency_key:
        await save_idempotency(
            db,
            tenant_id,
            idempotency_key,
            body_bytes,
            response_status,
            json.dumps(response_body),
        )

    logger.info(
        "v0/faturas: receivable %s tenant=%s ops=%d status=%s",
        request_id,
        tenant_id,
        len(data.operations),
        status.value,
    )

    return JSONResponse(
        content=response_body,
        status_code=response_status,
        headers={"X-Request-Id": request_id},
    )
