"""Router v0/faturas — endpoint de compatibilidade com CFO Automation API.

Aceita o payload CanonicalMessage (formato da CFO API) e encaminha ao n8n
webhook para processamento no ERP. Permite migracao transparente:
cliente muda URL + API key, zero mudanca no payload.

Features:
- ?dry_run=true → valida payload sem enviar ao ERP
- Idempotency-Key header (TODO: implementar KV)

Lifecycle: deprecated quando cliente migrar para POST /api/v1/faturas.

n8n Webhook Headers (convencao obrigatoria):
    Todo forward da API para webhooks n8n DEVE incluir:
    - X-Tenant-Id: ID do tenant que originou o request
    - X-Request-Id: ID unico do request para rastreamento
    - X-API-Base-URL: Base URL da API (ex: https://api.uuba.tech)
    - X-API-Endpoint: URL completa do endpoint que originou (ex: https://api.uuba.tech/api/v0/faturas)
    Isso permite que workflows n8n facam callbacks para a API sem hardcode de URLs.
"""

import logging
import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, Header, Query, Request
from fastapi.responses import JSONResponse

from app.auth.api_key import require_permission, verify_api_key
from app.exceptions import APIError
from app.schemas.receivable import (
    CanonicalMessage,
    CustomerResult,
    OperationResult,
    OperationStatus,
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
    summary="Criar fatura(s) via payload legado (v0)",
    description=(
        "Endpoint de compatibilidade com a CFO Automation API. "
        "Aceita o payload CanonicalMessage (customer + operations + payment_method) "
        "e encaminha ao n8n para processamento no ERP.\n\n"
        "Use `?dry_run=true` para validar o payload sem enviar ao ERP. "
        "Retorna `ValidationResult` em vez de `Receivable`.\n\n"
        "Para o formato nativo, use `POST /api/v1/faturas`."
    ),
)
async def create_receivable(
    data: CanonicalMessage,
    request: Request,
    dry_run: bool = Query(default=False, description="Validar sem enviar ao ERP"),
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
        description="UUID v4 para idempotencia (TODO)",
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

    # Determinar ambiente a partir do prefixo da key
    key_id = getattr(request.state, "key_id", "")
    environment = "test" if "test" in key_id.lower() else "live"

    receivable = Receivable(
        id=request_id,
        status=status,
        customer=customer,
        operations=operations,
        environment=environment,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    logger.info(
        "v0/faturas: receivable %s tenant=%s ops=%d status=%s",
        request_id,
        tenant_id,
        len(data.operations),
        status.value,
    )

    return JSONResponse(
        content=receivable.model_dump(),
        status_code=201 if status != ReceivableStatus.FAILED else 200,
        headers={"X-Request-Id": request_id},
    )
