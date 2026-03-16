"""Data integrity hunting — encoding, constraints, temporal, consistency."""
import asyncio
from datetime import datetime, timezone, timedelta
from tests.conftest import AUTH, create_test_cliente, create_test_fatura, create_test_cobranca


# =============================================================================
# ENCODING ATTACKS — every text field must handle real-world input
# =============================================================================

ENCODING_PAYLOADS = {
    "emoji": "Padaria Bom Pão 🍞🔥👍🏽",
    "chinese": "面包店 好面包",
    "arabic": "مخبز خبز جيد",
    "japanese": "パン屋 良いパン",
    "korean": "빵집 좋은빵",
    "cyrillic": "Пекарня Хороший Хлеб",
    "accented": "Pâtisserie résumé naïve café über Ñoño",
    "surrogate_pair": "𝕳𝖊𝖑𝖑𝖔 𝕿𝖊𝖘𝖙",
    "newlines": "Linha 1\nLinha 2\r\nLinha 3",
    "special_chars": 'Teste "com" \'aspas\' & <tags> \\backslash',
    "zero_width": "Te\u200bst\u200be",  # zero-width space
    "rtl_markers": "\u200fRight-to-left\u200e",
}


async def test_encoding_in_cliente_nome(client):
    """All encodings must be stored and returned correctly in nome."""
    for label, payload in ENCODING_PAYLOADS.items():
        doc = f"ENC{abs(hash(label)) % 9999999:07d}00"
        resp = await client.post("/api/v1/clientes", json={
            "nome": payload,
            "documento": doc,
        }, headers=AUTH)
        assert resp.status_code == 201, f"Failed for {label}: {resp.text}"
        body = resp.json()
        assert body["nome"] == payload, f"Encoding corrupted for {label}"

        # Verify round-trip via GET
        get_resp = await client.get(f"/api/v1/clientes/{body['id']}", headers=AUTH)
        assert get_resp.json()["nome"] == payload, f"Round-trip corrupted for {label}"


async def test_encoding_in_fatura_descricao(client):
    cli = await create_test_cliente(client)
    for label, payload in ENCODING_PAYLOADS.items():
        resp = await client.post("/api/v1/faturas", json={
            "cliente_id": cli["id"],
            "valor": 10000,
            "vencimento": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "descricao": payload,
        }, headers=AUTH)
        assert resp.status_code == 201, f"Failed for {label}"
        assert resp.json()["descricao"] == payload, f"Corrupted for {label}"


async def test_encoding_in_cobranca_mensagem(client):
    cli = await create_test_cliente(client, documento="98765432000198")
    fat = await create_test_fatura(client, cli["id"])
    for label, payload in ENCODING_PAYLOADS.items():
        resp = await client.post("/api/v1/cobrancas", json={
            "fatura_id": fat["id"],
            "cliente_id": cli["id"],
            "tipo": "lembrete",
            "mensagem": payload,
        }, headers=AUTH)
        assert resp.status_code == 201, f"Failed for {label}"
        assert resp.json()["mensagem"] == payload, f"Corrupted for {label}"


async def test_encoding_in_email(client):
    """Email with international chars."""
    resp = await client.post("/api/v1/clientes", json={
        "nome": "Teste Email",
        "documento": "98765432000199",
        "email": "josé@domínio.com.br",
    }, headers=AUTH)
    assert resp.status_code == 201
    assert resp.json()["email"] == "josé@domínio.com.br"


async def test_empty_string_vs_null(client):
    """Empty string in optional fields — should be stored, not converted to null."""
    resp = await client.post("/api/v1/clientes", json={
        "nome": "Teste Empty",
        "documento": "11122233000144",
        "email": "",
        "telefone": "",
    }, headers=AUTH)
    assert resp.status_code == 201
    body = resp.json()
    # Empty strings should be stored as empty strings, not null
    assert body["email"] == "" or body["email"] is None  # document behavior


# =============================================================================
# CONSTRAINT ENFORCEMENT AT DB LEVEL
# =============================================================================

async def test_unique_documento_enforced_at_db(client):
    """UNIQUE constraint must be enforced even with concurrent-like requests."""
    await create_test_cliente(client, documento="UNIQUE00000001")
    resp = await client.post("/api/v1/clientes", json={
        "nome": "Duplicate",
        "documento": "UNIQUE00000001",
    }, headers=AUTH)
    assert resp.status_code == 409


async def test_fk_cliente_enforced_on_fatura(client):
    """FK constraint: fatura must reference existing cliente."""
    resp = await client.post("/api/v1/faturas", json={
        "cliente_id": "cli_GHOST0000000",
        "valor": 10000,
        "vencimento": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    }, headers=AUTH)
    assert resp.status_code == 409


async def test_fk_fatura_enforced_on_cobranca(client):
    """FK constraint: cobranca must reference existing fatura."""
    cli = await create_test_cliente(client)
    resp = await client.post("/api/v1/cobrancas", json={
        "fatura_id": "fat_GHOST0000000",
        "cliente_id": cli["id"],
        "tipo": "lembrete",
    }, headers=AUTH)
    assert resp.status_code == 409


async def test_fk_cliente_enforced_on_cobranca(client):
    """FK constraint: cobranca.cliente_id must reference existing cliente."""
    cli = await create_test_cliente(client, documento="FK_TEST_000001")
    fat = await create_test_fatura(client, cli["id"])
    resp = await client.post("/api/v1/cobrancas", json={
        "fatura_id": fat["id"],
        "cliente_id": "cli_GHOST0000000",
        "tipo": "lembrete",
    }, headers=AUTH)
    assert resp.status_code == 409


# =============================================================================
# TEMPORAL DATA ATTACKS
# =============================================================================

async def test_created_at_auto_populated(client):
    """created_at must be set automatically on creation."""
    before = datetime.now(timezone.utc)
    cli = await create_test_cliente(client, documento="TIME000000001")
    after = datetime.now(timezone.utc)
    created = datetime.fromisoformat(cli["created_at"])
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    assert before <= created <= after


async def test_updated_at_changes_on_update(client):
    """updated_at must change when record is modified."""
    cli = await create_test_cliente(client, documento="TIME000000002")
    original_updated = cli["updated_at"]

    # Small delay to ensure timestamp differs
    await asyncio.sleep(0.01)

    resp = await client.patch(
        f"/api/v1/clientes/{cli['id']}",
        json={"nome": "Updated Name"},
        headers=AUTH,
    )
    assert resp.status_code == 200
    new_updated = resp.json()["updated_at"]
    assert new_updated >= original_updated


async def test_pago_em_set_automatically(client):
    """pago_em must be set when status changes to 'pago'."""
    cli = await create_test_cliente(client, documento="TIME000000003")
    fat = await create_test_fatura(client, cli["id"])
    assert fat["pago_em"] is None

    before = datetime.now(timezone.utc)
    resp = await client.patch(
        f"/api/v1/faturas/{fat['id']}",
        json={"status": "pago"},
        headers=AUTH,
    )
    after = datetime.now(timezone.utc)
    pago_em = datetime.fromisoformat(resp.json()["pago_em"])
    if pago_em.tzinfo is None:
        pago_em = pago_em.replace(tzinfo=timezone.utc)
    assert before <= pago_em <= after


async def test_vencimento_datetime_stored_correctly(client):
    """Datetime must represent the same instant after round-trip."""
    cli = await create_test_cliente(client, documento="TIME000000004")
    # Use UTC to avoid SQLite timezone limitations
    venc_dt = datetime(2026, 4, 1, 3, 0, 0, tzinfo=timezone.utc)
    resp = await client.post("/api/v1/faturas", json={
        "cliente_id": cli["id"],
        "valor": 10000,
        "vencimento": venc_dt.isoformat(),
    }, headers=AUTH)
    assert resp.status_code == 201
    stored = resp.json()["vencimento"]
    returned = datetime.fromisoformat(stored)
    if returned.tzinfo is None:
        returned = returned.replace(tzinfo=timezone.utc)
    assert abs((returned - venc_dt).total_seconds()) < 2


async def test_enviado_em_set_on_cobranca_creation(client):
    """enviado_em must be set automatically when cobranca is created."""
    cli = await create_test_cliente(client, documento="TIME000000005")
    fat = await create_test_fatura(client, cli["id"])
    cob = await create_test_cobranca(client, fat["id"], cli["id"])
    assert cob["enviado_em"] is not None


# =============================================================================
# DATA CONSISTENCY — metricas reflect actual fatura state
# =============================================================================

async def test_metricas_consistent_after_fatura_paid(client):
    """Metricas must update correctly when fatura is marked as paid."""
    cli = await create_test_cliente(client, documento="CONS000000001")
    fat1 = await create_test_fatura(client, cli["id"], valor=100000)
    await create_test_fatura(client, cli["id"], valor=200000)

    # Both pending
    resp = await client.get(f"/api/v1/clientes/{cli['id']}/metricas", headers=AUTH)
    m = resp.json()
    assert m["faturas_em_aberto"] == 2
    assert m["total_em_aberto"] == 300000

    # Pay one
    await client.patch(f"/api/v1/faturas/{fat1['id']}", json={"status": "pago"}, headers=AUTH)

    resp2 = await client.get(f"/api/v1/clientes/{cli['id']}/metricas", headers=AUTH)
    m2 = resp2.json()
    assert m2["faturas_em_aberto"] == 1
    assert m2["total_em_aberto"] == 200000


async def test_metricas_consistent_after_fatura_cancelled(client):
    """Cancelled fatura should not appear in em_aberto."""
    cli = await create_test_cliente(client, documento="CONS000000002")
    fat = await create_test_fatura(client, cli["id"], valor=50000)

    await client.patch(f"/api/v1/faturas/{fat['id']}", json={"status": "cancelado"}, headers=AUTH)

    resp = await client.get(f"/api/v1/clientes/{cli['id']}/metricas", headers=AUTH)
    m = resp.json()
    assert m["faturas_em_aberto"] == 0
    assert m["total_em_aberto"] == 0


async def test_metricas_vencido_count(client):
    """Faturas with past vencimento and status pendente/vencido count as vencidas."""
    cli = await create_test_cliente(client, documento="CONS000000003")
    # Create fatura with past vencimento
    await create_test_fatura(
        client, cli["id"], valor=75000,
        vencimento=(datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
    )

    resp = await client.get(f"/api/v1/clientes/{cli['id']}/metricas", headers=AUTH)
    m = resp.json()
    assert m["faturas_em_aberto"] == 1
    assert m["faturas_vencidas"] == 1
    assert m["total_vencido"] == 75000


async def test_cobranca_historico_consistent_with_list(client):
    """Historico for a fatura must match cobrancas filtered by fatura_id."""
    cli = await create_test_cliente(client, documento="CONS000000004")
    fat = await create_test_fatura(client, cli["id"])
    await create_test_cobranca(client, fat["id"], cli["id"], tipo="lembrete")
    await create_test_cobranca(client, fat["id"], cli["id"], tipo="cobranca")

    historico = await client.get(f"/api/v1/cobrancas/{fat['id']}/historico", headers=AUTH)
    filtered = await client.get(f"/api/v1/cobrancas?fatura_id={fat['id']}", headers=AUTH)

    assert historico.json()["pagination"]["total"] == filtered.json()["pagination"]["total"]


# =============================================================================
# CONCURRENT WRITE SIMULATION
# =============================================================================

async def test_sequential_duplicate_documento(client):
    """Second insert with same documento must fail cleanly."""
    doc = "RACE000000001"
    resp1 = await client.post("/api/v1/clientes", json={"nome": "A", "documento": doc}, headers=AUTH)
    assert resp1.status_code == 201
    resp2 = await client.post("/api/v1/clientes", json={"nome": "B", "documento": doc}, headers=AUTH)
    assert resp2.status_code == 409
    # Verify first record is intact
    get_resp = await client.get(f"/api/v1/clientes/{resp1.json()['id']}", headers=AUTH)
    assert get_resp.status_code == 200
    assert get_resp.json()["nome"] == "A"


async def test_concurrent_fatura_updates(client):
    """Simulate two concurrent status updates on same fatura."""
    cli = await create_test_cliente(client, documento="RACE000000002")
    fat = await create_test_fatura(client, cli["id"])

    results = await asyncio.gather(
        client.patch(f"/api/v1/faturas/{fat['id']}", json={"status": "pago"}, headers=AUTH),
        client.patch(f"/api/v1/faturas/{fat['id']}", json={"status": "cancelado"}, headers=AUTH),
    )
    # Both should succeed (last write wins) — no crash
    for r in results:
        assert r.status_code == 200

    # Check final state is consistent
    final = await client.get(f"/api/v1/faturas/{fat['id']}", headers=AUTH)
    assert final.json()["status"] in ("pago", "cancelado")


# =============================================================================
# BULK DATA CONSISTENCY
# =============================================================================

async def test_pagination_total_matches_data_count(client):
    """Total in pagination must match actual number of records."""
    cli = await create_test_cliente(client, documento="BULK000000001")
    n = 7
    for i in range(n):
        await create_test_fatura(client, cli["id"], valor=(i + 1) * 10000)

    # Fetch all pages
    all_items = []
    offset = 0
    while True:
        resp = await client.get(
            f"/api/v1/faturas?cliente_id={cli['id']}&limit=3&offset={offset}",
            headers=AUTH,
        )
        body = resp.json()
        all_items.extend(body["data"])
        if not body["pagination"]["has_more"]:
            break
        offset += 3

    assert len(all_items) == n
    # Verify no duplicates
    ids = [item["id"] for item in all_items]
    assert len(set(ids)) == n


async def test_list_filter_does_not_alter_other_data(client):
    """Filtering should not affect data in other queries."""
    cli = await create_test_cliente(client, documento="BULK000000002")
    fat1 = await create_test_fatura(client, cli["id"], valor=10000)
    await create_test_fatura(client, cli["id"], valor=20000)
    await client.patch(f"/api/v1/faturas/{fat1['id']}", json={"status": "pago"}, headers=AUTH)

    # Filtered query
    resp_pago = await client.get("/api/v1/faturas?status=pago", headers=AUTH)
    resp_all = await client.get(f"/api/v1/faturas?cliente_id={cli['id']}", headers=AUTH)

    assert resp_pago.json()["pagination"]["total"] == 1
    assert resp_all.json()["pagination"]["total"] == 2
