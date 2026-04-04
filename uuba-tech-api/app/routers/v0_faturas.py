"""Router v0/faturas — endpoint de compatibilidade com CFO Automation API.

Aceita o payload CanonicalMessage (formato da CFO API) e encaminha ao n8n
webhook para processamento no ERP. Permite migracao transparente:
cliente muda URL + API key, zero mudanca no payload.

Lifecycle: deprecated quando cliente migrar para POST /api/v1/faturas.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request

from app.auth.api_key import require_permission, verify_api_key
from app.schemas.receivable import (
    CanonicalMessage,
    CustomerResult,
    OperationResult,
    OperationStatus,
    Receivable,
    ReceivableStatus,
)
from app.utils.ids import generate_id

logger = logging.getLogger("uuba")

router = APIRouter(
    prefix="/api/v0/faturas",
    tags=["v0-compat"],
    dependencies=[Depends(verify_api_key), Depends(require_permission("invoices:write"))],
)


async def _forward_to_n8n(
    tenant_id: str,
    payload: dict,
) -> dict:
    """Encaminha payload ao n8n webhook e retorna a resposta.

    TODO: Implementar chamada HTTP ao n8n webhook.
    - URL: configuravel via env N8N_RECEIVABLE_WEBHOOK_URL
    - Headers: X-Tenant-Id, X-Request-Id
    - Timeout: 30s
    - Retry: 1x com backoff
    """
    # PLACEHOLDER — retorna resposta simulada ate integrar com n8n
    logger.warning("v0/faturas: n8n integration not implemented — returning placeholder response")
    return {
        "status": "completed",
        "customer": {"id": f"cst_{generate_id()}", "created": True},
        "operations": [],
    }


@router.post(
    "",
    response_model=Receivable,
    status_code=201,
    summary="Criar fatura(s) via payload legado (v0)",
    description=(
        "Endpoint de compatibilidade com a CFO Automation API. "
        "Aceita o payload CanonicalMessage (customer + operations + payment_method) "
        "e encaminha ao n8n para processamento no ERP. "
        "Para o formato nativo, use `POST /api/v1/faturas`."
    ),
)
async def create_receivable(
    data: CanonicalMessage,
    request: Request,
):
    """Processa CanonicalMessage: valida, encaminha ao n8n, retorna Receivable."""
    tenant_id = request.state.tenant_id
    request_id = generate_id("recv")

    # Serializar payload pra enviar ao n8n
    payload = data.model_dump(mode="json")

    # Encaminhar ao n8n
    n8n_response = await _forward_to_n8n(tenant_id, payload)

    # Montar response no formato Receivable
    operations_results = []
    for i, op in enumerate(data.operations):
        is_sale = hasattr(op, "sale")
        op_id = generate_id("op")
        operations_results.append(
            OperationResult(
                id=op_id,
                type="sale" if is_sale else "contract",
                status=OperationStatus.CREATED,
            )
        )

    # Determinar ambiente a partir do prefixo da key
    key_id = getattr(request.state, "key_id", "")
    environment = "test" if "test" in key_id.lower() else "live"

    receivable = Receivable(
        id=request_id,
        status=ReceivableStatus(n8n_response.get("status", "completed")),
        customer=CustomerResult(**n8n_response["customer"]),
        operations=operations_results,
        environment=environment,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    logger.info(
        "v0/faturas: receivable created",
        extra={"request_id": request_id, "tenant_id": tenant_id, "ops": len(data.operations)},
    )

    return receivable
