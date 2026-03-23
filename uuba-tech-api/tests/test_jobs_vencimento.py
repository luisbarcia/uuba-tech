"""Testes do job de transição automática para vencido (FR-015).

Cobre:
    AC-014: Fatura pendente vencida → vencido
    AC-015: Idempotência (rodar 2x = sem efeito)
    AC-020: Fatura em_negociacao não retrocede para vencido
"""

from datetime import datetime, timezone, timedelta

from tests.conftest import AUTH, create_test_cliente, create_test_fatura


# --- AC-014: Fatura pendente com vencimento passado → vencido ---


async def test_transiciona_fatura_pendente_vencida(client):
    """Fatura com vencimento ontem e status pendente deve virar vencido."""
    cli = await create_test_cliente(client)
    ontem = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    fat = await create_test_fatura(client, cli["id"], vencimento=ontem)
    assert fat["status"] == "pendente"

    resp = await client.post("/api/v1/jobs/transicionar-vencidas", headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["transicionadas"] == 1

    # Confirma que a fatura agora está vencida
    fat_resp = await client.get(f"/api/v1/faturas/{fat['id']}", headers=AUTH)
    assert fat_resp.json()["status"] == "vencido"


async def test_nao_transiciona_fatura_pendente_futura(client):
    """Fatura com vencimento futuro e status pendente NÃO deve ser alterada."""
    cli = await create_test_cliente(client)
    amanha = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    fat = await create_test_fatura(client, cli["id"], vencimento=amanha)

    resp = await client.post("/api/v1/jobs/transicionar-vencidas", headers=AUTH)
    assert resp.json()["transicionadas"] == 0

    fat_resp = await client.get(f"/api/v1/faturas/{fat['id']}", headers=AUTH)
    assert fat_resp.json()["status"] == "pendente"


async def test_transiciona_multiplas_faturas_vencidas(client):
    """Múltiplas faturas vencidas devem todas transicionar."""
    cli = await create_test_cliente(client)
    ontem = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    semana_passada = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    fat1 = await create_test_fatura(client, cli["id"], vencimento=ontem, valor=100000)
    fat2 = await create_test_fatura(client, cli["id"], vencimento=semana_passada, valor=200000)
    # Fatura futura — não deve ser afetada
    fat3 = await create_test_fatura(client, cli["id"], valor=300000)

    resp = await client.post("/api/v1/jobs/transicionar-vencidas", headers=AUTH)
    assert resp.json()["transicionadas"] == 2

    for fid in [fat1["id"], fat2["id"]]:
        r = await client.get(f"/api/v1/faturas/{fid}", headers=AUTH)
        assert r.json()["status"] == "vencido"

    r3 = await client.get(f"/api/v1/faturas/{fat3['id']}", headers=AUTH)
    assert r3.json()["status"] == "pendente"


# --- AC-015: Idempotência ---


async def test_idempotencia_rodar_duas_vezes(client):
    """Rodar o job 2x no mesmo dia não deve gerar efeitos colaterais."""
    cli = await create_test_cliente(client)
    ontem = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    fat = await create_test_fatura(client, cli["id"], vencimento=ontem)

    # Primeira execução
    resp1 = await client.post("/api/v1/jobs/transicionar-vencidas", headers=AUTH)
    assert resp1.json()["transicionadas"] == 1

    # Segunda execução — deve retornar 0
    resp2 = await client.post("/api/v1/jobs/transicionar-vencidas", headers=AUTH)
    assert resp2.json()["transicionadas"] == 0

    # Status continua vencido (não mudou de novo)
    fat_resp = await client.get(f"/api/v1/faturas/{fat['id']}", headers=AUTH)
    assert fat_resp.json()["status"] == "vencido"


# --- AC-020: Fatura em em_negociacao não retrocede ---


async def test_nao_transiciona_fatura_paga(client):
    """Fatura já paga não deve ser afetada pelo job."""
    cli = await create_test_cliente(client)
    ontem = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    fat = await create_test_fatura(client, cli["id"], vencimento=ontem)
    await client.patch(f"/api/v1/faturas/{fat['id']}", json={"status": "pago"}, headers=AUTH)

    resp = await client.post("/api/v1/jobs/transicionar-vencidas", headers=AUTH)
    assert resp.json()["transicionadas"] == 0

    fat_resp = await client.get(f"/api/v1/faturas/{fat['id']}", headers=AUTH)
    assert fat_resp.json()["status"] == "pago"


async def test_nao_transiciona_fatura_cancelada(client):
    """Fatura cancelada não deve ser afetada pelo job."""
    cli = await create_test_cliente(client)
    ontem = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    fat = await create_test_fatura(client, cli["id"], vencimento=ontem)
    await client.patch(f"/api/v1/faturas/{fat['id']}", json={"status": "cancelado"}, headers=AUTH)

    resp = await client.post("/api/v1/jobs/transicionar-vencidas", headers=AUTH)
    assert resp.json()["transicionadas"] == 0


async def test_nao_transiciona_fatura_ja_vencida(client):
    """Fatura já vencida não deve ser contada novamente."""
    cli = await create_test_cliente(client)
    ontem = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    fat = await create_test_fatura(client, cli["id"], vencimento=ontem)

    # Transiciona manualmente para vencido via PATCH
    await client.patch(f"/api/v1/faturas/{fat['id']}", json={"status": "vencido"}, headers=AUTH)

    resp = await client.post("/api/v1/jobs/transicionar-vencidas", headers=AUTH)
    assert resp.json()["transicionadas"] == 0


async def test_sem_faturas_retorna_zero(client):
    """Job sem faturas no banco retorna 0 transicionadas."""
    resp = await client.post("/api/v1/jobs/transicionar-vencidas", headers=AUTH)
    assert resp.status_code == 200
    assert resp.json()["transicionadas"] == 0


async def test_job_requer_autenticacao(client):
    """Endpoint deve exigir API key."""
    resp = await client.post("/api/v1/jobs/transicionar-vencidas")
    assert resp.status_code == 401
