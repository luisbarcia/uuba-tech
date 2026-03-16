"""Mass assignment attacks — attempt to overwrite protected fields."""
from tests.conftest import AUTH, create_test_cliente, create_test_fatura, create_test_cobranca


# --- Cliente mass assignment ---

async def test_cannot_set_id_on_create_cliente(client):
    resp = await client.post("/api/v1/clientes", json={
        "nome": "Hacker Inc",
        "documento": "55555555000155",
        "id": "cli_HACKED000000",
    }, headers=AUTH)
    assert resp.status_code == 201
    assert resp.json()["id"] != "cli_HACKED000000"
    assert resp.json()["id"].startswith("cli_")


async def test_cannot_set_created_at_on_create_cliente(client):
    resp = await client.post("/api/v1/clientes", json={
        "nome": "Hacker Inc",
        "documento": "55555555000156",
        "created_at": "2020-01-01T00:00:00Z",
    }, headers=AUTH)
    assert resp.status_code == 201
    assert "2020" not in resp.json()["created_at"]


async def test_cannot_set_object_field_on_create_cliente(client):
    resp = await client.post("/api/v1/clientes", json={
        "nome": "Hacker Inc",
        "documento": "55555555000157",
        "object": "admin",
    }, headers=AUTH)
    assert resp.status_code == 201
    assert resp.json()["object"] == "cliente"


async def test_cannot_set_documento_on_update_cliente(client):
    """documento should not be updatable via PATCH."""
    created = await create_test_cliente(client, documento="88888888000188")
    resp = await client.patch(f"/api/v1/clientes/{created['id']}", json={
        "documento": "99999999000199",
    }, headers=AUTH)
    # Should either 422 (field not in update schema) or ignore the field
    assert resp.status_code == 200
    # Verify documento was NOT changed
    get_resp = await client.get(f"/api/v1/clientes/{created['id']}", headers=AUTH)
    assert get_resp.json()["documento"] == "88888888000188"


# --- Fatura mass assignment ---

async def test_cannot_set_id_on_create_fatura(client):
    cli = await create_test_cliente(client)
    from datetime import datetime, timezone, timedelta
    resp = await client.post("/api/v1/faturas", json={
        "cliente_id": cli["id"],
        "valor": 10000,
        "vencimento": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "id": "fat_HACKED000000",
    }, headers=AUTH)
    assert resp.status_code == 201
    assert resp.json()["id"] != "fat_HACKED000000"


async def test_cannot_set_status_on_create_fatura(client):
    """New faturas should always start as 'pendente'."""
    cli = await create_test_cliente(client, documento="66666666000166")
    from datetime import datetime, timezone, timedelta
    resp = await client.post("/api/v1/faturas", json={
        "cliente_id": cli["id"],
        "valor": 10000,
        "vencimento": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "status": "pago",
    }, headers=AUTH)
    assert resp.status_code == 201
    assert resp.json()["status"] == "pendente"


async def test_cannot_set_pago_em_on_create_fatura(client):
    cli = await create_test_cliente(client, documento="66666666000167")
    from datetime import datetime, timezone, timedelta
    resp = await client.post("/api/v1/faturas", json={
        "cliente_id": cli["id"],
        "valor": 10000,
        "vencimento": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "pago_em": "2020-01-01T00:00:00Z",
    }, headers=AUTH)
    assert resp.status_code == 201
    assert resp.json()["pago_em"] is None


async def test_cannot_set_moeda_on_create_fatura(client):
    cli = await create_test_cliente(client, documento="66666666000168")
    from datetime import datetime, timezone, timedelta
    resp = await client.post("/api/v1/faturas", json={
        "cliente_id": cli["id"],
        "valor": 10000,
        "vencimento": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "moeda": "USD",
    }, headers=AUTH)
    assert resp.status_code == 201
    assert resp.json()["moeda"] == "BRL"


async def test_cannot_change_valor_on_update_fatura(client):
    """PATCH fatura should not allow changing valor."""
    cli = await create_test_cliente(client, documento="66666666000169")
    fat = await create_test_fatura(client, cli["id"], valor=50000)
    resp = await client.patch(f"/api/v1/faturas/{fat['id']}", json={
        "valor": 1,
    }, headers=AUTH)
    # Should ignore or 422
    get_resp = await client.get(f"/api/v1/faturas/{fat['id']}", headers=AUTH)
    assert get_resp.json()["valor"] == 50000


async def test_cannot_change_cliente_id_on_update_fatura(client):
    cli = await create_test_cliente(client, documento="66666666000170")
    fat = await create_test_fatura(client, cli["id"])
    resp = await client.patch(f"/api/v1/faturas/{fat['id']}", json={
        "cliente_id": "cli_HACKED000000",
    }, headers=AUTH)
    get_resp = await client.get(f"/api/v1/faturas/{fat['id']}", headers=AUTH)
    assert get_resp.json()["cliente_id"] == cli["id"]


# --- Cobranca mass assignment ---

async def test_cannot_set_id_on_create_cobranca(client):
    cli = await create_test_cliente(client, documento="77777777000178")
    fat = await create_test_fatura(client, cli["id"])
    resp = await client.post("/api/v1/cobrancas", json={
        "fatura_id": fat["id"],
        "cliente_id": cli["id"],
        "tipo": "lembrete",
        "id": "cob_HACKED000000",
    }, headers=AUTH)
    assert resp.status_code == 201
    assert resp.json()["id"] != "cob_HACKED000000"


async def test_cannot_set_status_on_create_cobranca(client):
    cli = await create_test_cliente(client, documento="77777777000179")
    fat = await create_test_fatura(client, cli["id"])
    resp = await client.post("/api/v1/cobrancas", json={
        "fatura_id": fat["id"],
        "cliente_id": cli["id"],
        "tipo": "lembrete",
        "status": "lido",
    }, headers=AUTH)
    assert resp.status_code == 201
    assert resp.json()["status"] == "enviado"


async def test_cannot_set_pausado_on_create_cobranca(client):
    cli = await create_test_cliente(client, documento="77777777000180")
    fat = await create_test_fatura(client, cli["id"])
    resp = await client.post("/api/v1/cobrancas", json={
        "fatura_id": fat["id"],
        "cliente_id": cli["id"],
        "tipo": "lembrete",
        "pausado": True,
    }, headers=AUTH)
    assert resp.status_code == 201
    assert resp.json()["pausado"] is False
