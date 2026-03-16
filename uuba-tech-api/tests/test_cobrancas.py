from tests.conftest import AUTH, create_test_cliente, create_test_fatura, create_test_cobranca


# --- POST /api/v1/cobrancas ---

async def test_create_cobranca(client):
    cli = await create_test_cliente(client)
    fat = await create_test_fatura(client, cli["id"])
    resp = await client.post("/api/v1/cobrancas", json={
        "fatura_id": fat["id"],
        "cliente_id": cli["id"],
        "tipo": "lembrete",
        "canal": "whatsapp",
        "tom": "amigavel",
        "mensagem": "Ola, sua fatura vence em breve!",
    }, headers=AUTH)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"].startswith("cob_")
    assert body["object"] == "cobranca"
    assert body["tipo"] == "lembrete"
    assert body["canal"] == "whatsapp"
    assert body["tom"] == "amigavel"
    assert body["pausado"] is False
    assert body["enviado_em"] is not None


async def test_create_cobranca_invalid_tipo_returns_422(client):
    cli = await create_test_cliente(client)
    fat = await create_test_fatura(client, cli["id"])
    resp = await client.post("/api/v1/cobrancas", json={
        "fatura_id": fat["id"],
        "cliente_id": cli["id"],
        "tipo": "invalido",
    }, headers=AUTH)
    assert resp.status_code == 422


async def test_create_cobranca_default_canal(client):
    cli = await create_test_cliente(client)
    fat = await create_test_fatura(client, cli["id"])
    resp = await client.post("/api/v1/cobrancas", json={
        "fatura_id": fat["id"],
        "cliente_id": cli["id"],
        "tipo": "cobranca",
    }, headers=AUTH)
    assert resp.status_code == 201
    assert resp.json()["canal"] == "whatsapp"


# --- GET /api/v1/cobrancas ---

async def test_list_cobrancas_empty(client):
    resp = await client.get("/api/v1/cobrancas", headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []
    assert body["pagination"]["total"] == 0


async def test_list_cobrancas_with_data(client):
    cli = await create_test_cliente(client)
    fat = await create_test_fatura(client, cli["id"])
    await create_test_cobranca(client, fat["id"], cli["id"])
    await create_test_cobranca(client, fat["id"], cli["id"], tipo="cobranca")
    resp = await client.get("/api/v1/cobrancas", headers=AUTH)
    body = resp.json()
    assert body["pagination"]["total"] == 2


async def test_list_cobrancas_filter_by_fatura_id(client):
    cli = await create_test_cliente(client)
    fat1 = await create_test_fatura(client, cli["id"])
    fat2 = await create_test_fatura(client, cli["id"], valor=50000)
    await create_test_cobranca(client, fat1["id"], cli["id"])
    await create_test_cobranca(client, fat2["id"], cli["id"])

    resp = await client.get(f"/api/v1/cobrancas?fatura_id={fat1['id']}", headers=AUTH)
    body = resp.json()
    assert body["pagination"]["total"] == 1


async def test_list_cobrancas_filter_by_cliente_id(client):
    cli1 = await create_test_cliente(client, documento="11111111000111")
    cli2 = await create_test_cliente(client, nome="Outro", documento="22222222000122")
    fat1 = await create_test_fatura(client, cli1["id"])
    fat2 = await create_test_fatura(client, cli2["id"], valor=50000)
    await create_test_cobranca(client, fat1["id"], cli1["id"])
    await create_test_cobranca(client, fat2["id"], cli2["id"])

    resp = await client.get(f"/api/v1/cobrancas?cliente_id={cli1['id']}", headers=AUTH)
    body = resp.json()
    assert body["pagination"]["total"] == 1


# --- GET /api/v1/cobrancas/{fatura_id}/historico ---

async def test_get_historico(client):
    cli = await create_test_cliente(client)
    fat = await create_test_fatura(client, cli["id"])
    await create_test_cobranca(client, fat["id"], cli["id"], tipo="lembrete")
    await create_test_cobranca(client, fat["id"], cli["id"], tipo="cobranca")
    await create_test_cobranca(client, fat["id"], cli["id"], tipo="follow_up")

    resp = await client.get(f"/api/v1/cobrancas/{fat['id']}/historico", headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["pagination"]["total"] == 3


async def test_get_historico_empty(client):
    resp = await client.get("/api/v1/cobrancas/fat_naoexiste000/historico", headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []
    assert body["pagination"]["total"] == 0


# --- PATCH /api/v1/cobrancas/{id}/pausar ---

async def test_pausar_cobranca(client):
    cli = await create_test_cliente(client)
    fat = await create_test_fatura(client, cli["id"])
    cob = await create_test_cobranca(client, fat["id"], cli["id"])
    assert cob["pausado"] is False

    resp = await client.patch(f"/api/v1/cobrancas/{cob['id']}/pausar", headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["pausado"] is True
    assert body["status"] == "pausado"


async def test_pausar_cobranca_not_found(client):
    resp = await client.patch("/api/v1/cobrancas/cob_naoexiste000/pausar", headers=AUTH)
    assert resp.status_code == 404


# --- PATCH /api/v1/cobrancas/{id}/retomar ---

async def test_retomar_cobranca(client):
    cli = await create_test_cliente(client)
    fat = await create_test_fatura(client, cli["id"])
    cob = await create_test_cobranca(client, fat["id"], cli["id"])
    # Pausar primeiro
    await client.patch(f"/api/v1/cobrancas/{cob['id']}/pausar", headers=AUTH)

    resp = await client.patch(f"/api/v1/cobrancas/{cob['id']}/retomar", headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["pausado"] is False
    assert body["status"] == "enviado"


async def test_retomar_cobranca_not_found(client):
    resp = await client.patch("/api/v1/cobrancas/cob_naoexiste000/retomar", headers=AUTH)
    assert resp.status_code == 404
