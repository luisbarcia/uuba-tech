from tests.conftest import AUTH, create_test_cliente, create_test_fatura


# --- POST /api/v1/clientes ---

async def test_create_cliente(client):
    resp = await client.post("/api/v1/clientes", json={
        "nome": "Padaria Bom Pao",
        "documento": "12345678000190",
        "telefone": "5511999001234",
    }, headers=AUTH)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"].startswith("cli_")
    assert body["object"] == "cliente"
    assert body["nome"] == "Padaria Bom Pao"
    assert body["documento"] == "12345678000190"
    assert "created_at" in body
    assert "updated_at" in body


async def test_create_cliente_missing_nome_returns_422(client):
    resp = await client.post("/api/v1/clientes", json={
        "documento": "12345678000190",
    }, headers=AUTH)
    assert resp.status_code == 422


async def test_create_cliente_missing_documento_returns_422(client):
    resp = await client.post("/api/v1/clientes", json={
        "nome": "Padaria",
    }, headers=AUTH)
    assert resp.status_code == 422


async def test_create_cliente_duplicate_documento_returns_409(client):
    await create_test_cliente(client, documento="99999999000199")
    resp = await client.post("/api/v1/clientes", json={
        "nome": "Outro Nome",
        "documento": "99999999000199",
    }, headers=AUTH)
    assert resp.status_code == 409


# --- GET /api/v1/clientes ---

async def test_list_clientes_empty(client):
    resp = await client.get("/api/v1/clientes", headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["object"] == "list"
    assert body["data"] == []
    assert body["pagination"]["total"] == 0


async def test_list_clientes_with_data(client):
    await create_test_cliente(client, documento="11111111000111")
    await create_test_cliente(client, nome="Loja B", documento="22222222000122")
    resp = await client.get("/api/v1/clientes", headers=AUTH)
    body = resp.json()
    assert body["pagination"]["total"] == 2
    assert len(body["data"]) == 2


async def test_list_clientes_filter_by_telefone(client):
    await create_test_cliente(client, documento="33333333000133", telefone="5511888887777")
    await create_test_cliente(client, nome="Outro", documento="44444444000144", telefone="5521999990000")
    resp = await client.get("/api/v1/clientes?telefone=5511888887777", headers=AUTH)
    body = resp.json()
    assert body["pagination"]["total"] == 1
    assert body["data"][0]["telefone"] == "5511888887777"


async def test_list_clientes_pagination(client):
    for i in range(5):
        await create_test_cliente(client, nome=f"Cliente {i}", documento=f"0000000000{i:04d}")
    resp = await client.get("/api/v1/clientes?limit=2&offset=0", headers=AUTH)
    body = resp.json()
    assert len(body["data"]) == 2
    assert body["pagination"]["total"] == 5
    assert body["pagination"]["has_more"] is True

    resp2 = await client.get("/api/v1/clientes?limit=2&offset=4", headers=AUTH)
    body2 = resp2.json()
    assert len(body2["data"]) == 1
    assert body2["pagination"]["has_more"] is False


# --- GET /api/v1/clientes/{id} ---

async def test_get_cliente_exists(client):
    created = await create_test_cliente(client)
    resp = await client.get(f"/api/v1/clientes/{created['id']}", headers=AUTH)
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


async def test_get_cliente_not_found(client):
    resp = await client.get("/api/v1/clientes/cli_naoexiste000", headers=AUTH)
    assert resp.status_code == 404
    body = resp.json()
    assert body["status"] == 404
    assert "type" in body


# --- PATCH /api/v1/clientes/{id} ---

async def test_update_cliente(client):
    created = await create_test_cliente(client)
    resp = await client.patch(
        f"/api/v1/clientes/{created['id']}",
        json={"nome": "Novo Nome"},
        headers=AUTH,
    )
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Novo Nome"


async def test_update_cliente_not_found(client):
    resp = await client.patch(
        "/api/v1/clientes/cli_naoexiste000",
        json={"nome": "Teste"},
        headers=AUTH,
    )
    assert resp.status_code == 404


# --- GET /api/v1/clientes/{id}/metricas ---

async def test_get_metricas_empty(client):
    created = await create_test_cliente(client)
    resp = await client.get(f"/api/v1/clientes/{created['id']}/metricas", headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["dso_dias"] == 0.0
    assert body["total_em_aberto"] == 0
    assert body["total_vencido"] == 0
    assert body["faturas_em_aberto"] == 0
    assert body["faturas_vencidas"] == 0


async def test_get_metricas_with_faturas(client):
    cli = await create_test_cliente(client)
    await create_test_fatura(client, cli["id"], valor=100000)
    resp = await client.get(f"/api/v1/clientes/{cli['id']}/metricas", headers=AUTH)
    body = resp.json()
    assert body["faturas_em_aberto"] == 1
    assert body["total_em_aberto"] == 100000


async def test_get_metricas_not_found(client):
    resp = await client.get("/api/v1/clientes/cli_naoexiste000/metricas", headers=AUTH)
    assert resp.status_code == 404
