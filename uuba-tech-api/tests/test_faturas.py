from datetime import datetime, timezone, timedelta
from tests.conftest import AUTH, create_test_cliente, create_test_fatura


# --- POST /api/v1/faturas ---

async def test_create_fatura(client):
    cli = await create_test_cliente(client)
    venc = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    resp = await client.post("/api/v1/faturas", json={
        "cliente_id": cli["id"],
        "valor": 250000,
        "vencimento": venc,
        "descricao": "NF 1234",
    }, headers=AUTH)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"].startswith("fat_")
    assert body["object"] == "fatura"
    assert body["valor"] == 250000
    assert body["status"] == "pendente"
    assert body["moeda"] == "BRL"


async def test_create_fatura_valor_zero_returns_422(client):
    cli = await create_test_cliente(client)
    resp = await client.post("/api/v1/faturas", json={
        "cliente_id": cli["id"],
        "valor": 0,
        "vencimento": datetime.now(timezone.utc).isoformat(),
    }, headers=AUTH)
    assert resp.status_code == 422


async def test_create_fatura_valor_negative_returns_422(client):
    cli = await create_test_cliente(client)
    resp = await client.post("/api/v1/faturas", json={
        "cliente_id": cli["id"],
        "valor": -100,
        "vencimento": datetime.now(timezone.utc).isoformat(),
    }, headers=AUTH)
    assert resp.status_code == 422


async def test_create_fatura_missing_fields_returns_422(client):
    resp = await client.post("/api/v1/faturas", json={
        "valor": 100,
    }, headers=AUTH)
    assert resp.status_code == 422


# --- GET /api/v1/faturas ---

async def test_list_faturas_empty(client):
    resp = await client.get("/api/v1/faturas", headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["object"] == "list"
    assert body["data"] == []
    assert body["pagination"]["total"] == 0


async def test_list_faturas_with_data(client):
    cli = await create_test_cliente(client)
    await create_test_fatura(client, cli["id"])
    await create_test_fatura(client, cli["id"], valor=100000)
    resp = await client.get("/api/v1/faturas", headers=AUTH)
    body = resp.json()
    assert body["pagination"]["total"] == 2


async def test_list_faturas_filter_by_status(client):
    cli = await create_test_cliente(client)
    fat = await create_test_fatura(client, cli["id"])
    # Mark one as pago
    await client.patch(f"/api/v1/faturas/{fat['id']}", json={"status": "pago"}, headers=AUTH)
    await create_test_fatura(client, cli["id"], valor=50000)

    resp = await client.get("/api/v1/faturas?status=pendente", headers=AUTH)
    body = resp.json()
    assert body["pagination"]["total"] == 1
    assert body["data"][0]["status"] == "pendente"


async def test_list_faturas_filter_by_multiple_status(client):
    cli = await create_test_cliente(client)
    await create_test_fatura(client, cli["id"])
    fat2 = await create_test_fatura(client, cli["id"], valor=50000)
    await client.patch(f"/api/v1/faturas/{fat2['id']}", json={"status": "pago"}, headers=AUTH)

    resp = await client.get("/api/v1/faturas?status=pendente,pago", headers=AUTH)
    body = resp.json()
    assert body["pagination"]["total"] == 2


async def test_list_faturas_filter_by_cliente_id(client):
    cli1 = await create_test_cliente(client, documento="11111111000111")
    cli2 = await create_test_cliente(client, nome="Outro", documento="22222222000122")
    await create_test_fatura(client, cli1["id"])
    await create_test_fatura(client, cli2["id"], valor=50000)

    resp = await client.get(f"/api/v1/faturas?cliente_id={cli1['id']}", headers=AUTH)
    body = resp.json()
    assert body["pagination"]["total"] == 1


async def test_list_faturas_pagination(client):
    cli = await create_test_cliente(client)
    for i in range(5):
        await create_test_fatura(client, cli["id"], valor=(i + 1) * 10000)
    resp = await client.get("/api/v1/faturas?limit=2&offset=0", headers=AUTH)
    body = resp.json()
    assert len(body["data"]) == 2
    assert body["pagination"]["total"] == 5
    assert body["pagination"]["has_more"] is True


# --- GET /api/v1/faturas/{id} ---

async def test_get_fatura_exists(client):
    cli = await create_test_cliente(client)
    fat = await create_test_fatura(client, cli["id"])
    resp = await client.get(f"/api/v1/faturas/{fat['id']}", headers=AUTH)
    assert resp.status_code == 200
    assert resp.json()["id"] == fat["id"]


async def test_get_fatura_not_found(client):
    resp = await client.get("/api/v1/faturas/fat_naoexiste000", headers=AUTH)
    assert resp.status_code == 404
    body = resp.json()
    assert body["status"] == 404


# --- PATCH /api/v1/faturas/{id} ---

async def test_update_fatura_status_pago_sets_pago_em(client):
    cli = await create_test_cliente(client)
    fat = await create_test_fatura(client, cli["id"])
    assert fat["pago_em"] is None

    resp = await client.patch(
        f"/api/v1/faturas/{fat['id']}",
        json={"status": "pago"},
        headers=AUTH,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "pago"
    assert body["pago_em"] is not None


async def test_update_fatura_invalid_status_returns_422(client):
    cli = await create_test_cliente(client)
    fat = await create_test_fatura(client, cli["id"])
    resp = await client.patch(
        f"/api/v1/faturas/{fat['id']}",
        json={"status": "invalido"},
        headers=AUTH,
    )
    assert resp.status_code == 422


async def test_update_fatura_not_found(client):
    resp = await client.patch(
        "/api/v1/faturas/fat_naoexiste000",
        json={"status": "pago"},
        headers=AUTH,
    )
    assert resp.status_code == 404


async def test_update_fatura_promessa_pagamento(client):
    cli = await create_test_cliente(client)
    fat = await create_test_fatura(client, cli["id"])
    promessa = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    resp = await client.patch(
        f"/api/v1/faturas/{fat['id']}",
        json={"promessa_pagamento": promessa},
        headers=AUTH,
    )
    assert resp.status_code == 200
    assert resp.json()["promessa_pagamento"] is not None
