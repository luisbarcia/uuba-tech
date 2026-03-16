"""Injection attacks — SQL, XSS, command injection, path traversal."""
from tests.conftest import AUTH, create_test_cliente, create_test_fatura


SQL_PAYLOADS = [
    "' OR 1=1--",
    "'; DROP TABLE clientes;--",
    "1 UNION SELECT * FROM clientes--",
    "1; SELECT pg_sleep(5)--",
    "' OR ''='",
    "admin'--",
]

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)",
    '"><script>alert(1)</script>',
]

COMMAND_PAYLOADS = [
    "; ls -la",
    "| cat /etc/passwd",
    "$(whoami)",
    "`id`",
]


# --- SQL injection in query parameters ---

async def test_sql_injection_in_telefone_filter(client):
    for payload in SQL_PAYLOADS:
        resp = await client.get(f"/api/v1/clientes?telefone={payload}", headers=AUTH)
        assert resp.status_code in (200, 422), f"Payload {payload!r} returned {resp.status_code}"
        if resp.status_code == 200:
            body = resp.json()
            assert body["pagination"]["total"] == 0


async def test_sql_injection_in_status_filter(client):
    for payload in SQL_PAYLOADS:
        resp = await client.get(f"/api/v1/faturas?status={payload}", headers=AUTH)
        assert resp.status_code in (200, 422), f"Payload {payload!r} returned {resp.status_code}"


async def test_sql_injection_in_cliente_id_filter(client):
    for payload in SQL_PAYLOADS:
        resp = await client.get(f"/api/v1/faturas?cliente_id={payload}", headers=AUTH)
        assert resp.status_code in (200, 422)


async def test_sql_injection_in_periodo_filter(client):
    """periodo param validated with regex — SQL injection returns 422."""
    resp = await client.get("/api/v1/cobrancas?periodo=' OR 1=1--", headers=AUTH)
    assert resp.status_code == 422


# --- SQL injection in path parameters ---

async def test_sql_injection_in_path_cliente_id(client):
    for payload in SQL_PAYLOADS:
        resp = await client.get(f"/api/v1/clientes/{payload}", headers=AUTH)
        assert resp.status_code in (404, 422)


async def test_sql_injection_in_path_fatura_id(client):
    for payload in SQL_PAYLOADS:
        resp = await client.get(f"/api/v1/faturas/{payload}", headers=AUTH)
        assert resp.status_code in (404, 422)


# --- SQL injection in JSON body ---

async def test_sql_injection_in_cliente_nome(client):
    for payload in SQL_PAYLOADS:
        resp = await client.post("/api/v1/clientes", json={
            "nome": payload,
            "documento": "99999999000100",
        }, headers=AUTH)
        # Should succeed (store the string literally) or 422
        assert resp.status_code in (201, 409, 422)
        if resp.status_code == 201:
            body = resp.json()
            assert body["nome"] == payload  # stored literally, not executed


async def test_sql_injection_in_fatura_descricao(client):
    cli = await create_test_cliente(client)
    from datetime import datetime, timezone, timedelta
    for payload in SQL_PAYLOADS:
        resp = await client.post("/api/v1/faturas", json={
            "cliente_id": cli["id"],
            "valor": 10000,
            "vencimento": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "descricao": payload,
        }, headers=AUTH)
        assert resp.status_code == 201
        assert resp.json()["descricao"] == payload


# --- XSS stored in responses ---

async def test_xss_in_cliente_nome_returned_literally(client):
    """XSS payload stored and returned as-is (not HTML-encoded in JSON API)."""
    for payload in XSS_PAYLOADS:
        resp = await client.post("/api/v1/clientes", json={
            "nome": payload,
            "documento": f"XSS{hash(payload) % 99999:05d}000100",
        }, headers=AUTH)
        if resp.status_code == 201:
            assert resp.json()["nome"] == payload


async def test_xss_in_cobranca_mensagem(client):
    cli = await create_test_cliente(client, documento="77777777000177")
    fat = await create_test_fatura(client, cli["id"])
    for payload in XSS_PAYLOADS:
        resp = await client.post("/api/v1/cobrancas", json={
            "fatura_id": fat["id"],
            "cliente_id": cli["id"],
            "tipo": "lembrete",
            "mensagem": payload,
        }, headers=AUTH)
        assert resp.status_code == 201
        assert resp.json()["mensagem"] == payload


# --- Command injection ---

async def test_command_injection_in_nome(client):
    for payload in COMMAND_PAYLOADS:
        resp = await client.post("/api/v1/clientes", json={
            "nome": payload,
            "documento": f"CMD{abs(hash(payload)) % 99999:05d}000100",
        }, headers=AUTH)
        assert resp.status_code in (201, 422)
        if resp.status_code == 201:
            assert resp.json()["nome"] == payload


# --- Path traversal ---

async def test_path_traversal_in_id(client):
    traversal_payloads = [
        "../../etc/passwd",
        "..%2f..%2fetc%2fpasswd",
        "....//....//etc/passwd",
        "%00",
        "cli_abc/../../../etc/passwd",
    ]
    for payload in traversal_payloads:
        resp = await client.get(f"/api/v1/clientes/{payload}", headers=AUTH)
        assert resp.status_code in (404, 422, 400)


# --- Error responses don't leak internals ---

async def test_error_no_stack_trace(client):
    """Error responses should not expose stack traces."""
    # periodo with invalid format now returns 422 with clean message
    resp = await client.get("/api/v1/cobrancas?periodo=invalid", headers=AUTH)
    body = resp.json()
    assert "Traceback" not in str(body)
    assert "File" not in body.get("detail", "")
    assert ".py" not in body.get("detail", "")

    # 404 errors
    resp2 = await client.get("/api/v1/clientes/cli_fake", headers=AUTH)
    body2 = resp2.json()
    assert "Traceback" not in str(body2)


async def test_error_no_db_schema_leak(client):
    """Errors should not expose table/column names."""
    resp = await client.get("/api/v1/clientes/cli_fake", headers=AUTH)
    body = resp.json()
    detail = str(body)
    assert "__tablename__" not in detail

    # FK violation error
    from datetime import datetime, timezone, timedelta
    resp2 = await client.post("/api/v1/faturas", json={
        "cliente_id": "cli_DOESNOTEXIST",
        "valor": 10000,
        "vencimento": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    }, headers=AUTH)
    body2 = resp2.json()
    assert "SELECT" not in str(body2)
    assert "INSERT" not in str(body2)
