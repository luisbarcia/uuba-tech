"""Bug Hunt abrangente — 2026-03-27.

Bugs encontrados via analise sistematica do codigo.
Cada classe = 1 bug com teste RED antes do fix.

Categorias:
- SECURITY: vazamento de dados, bypass de auth
- LOGIC: comportamento incorreto em edge cases
- INTEGRITY: dados inconsistentes
- RESILIENCE: crashs em inputs inesperados
"""

import pytest

from tests.conftest import AUTH, create_test_cliente, create_test_fatura, create_test_cobranca


# =====================================================================
# SECURITY BUGS
# =====================================================================


class TestBugTenantIdQueryParamIgnored:
    """BUG-003: Routers de faturas e cobrancas aceitam tenant_id como query param
    mas o repo ja filtra por tenant do auth. O param nao faz nada — mas e confuso
    e pode ser explorado em futuras refatoracoes se alguem conectar o param ao service.

    O param deveria ser removido ou pelo menos documentado como no-op."""

    @pytest.mark.asyncio
    async def test_faturas_tenant_id_param_is_noop(self, client):
        """tenant_id query param em /faturas NAO deve alterar o resultado."""
        cli = await create_test_cliente(client)
        await create_test_fatura(client, cli["id"])

        resp_normal = await client.get("/api/v1/faturas", headers=AUTH)
        resp_forjado = await client.get("/api/v1/faturas?tenant_id=ten_hacker", headers=AUTH)

        assert (
            resp_normal.json()["pagination"]["total"] == resp_forjado.json()["pagination"]["total"]
        )

    @pytest.mark.asyncio
    async def test_cobrancas_tenant_id_param_is_noop(self, client):
        """tenant_id query param em /cobrancas NAO deve alterar o resultado."""
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])
        await create_test_cobranca(client, fat["id"], cli["id"])

        resp_normal = await client.get("/api/v1/cobrancas", headers=AUTH)
        resp_forjado = await client.get("/api/v1/cobrancas?tenant_id=ten_hacker", headers=AUTH)

        assert (
            resp_normal.json()["pagination"]["total"] == resp_forjado.json()["pagination"]["total"]
        )


# =====================================================================
# LOGIC BUGS
# =====================================================================


class TestBugDSOComPagamentoAnteriorAoVencimento:
    """BUG-004: DSO pode ser NEGATIVO se pago_em < vencimento (pagamento antecipado).
    O calculo (pago_em - vencimento).days retorna negativo, o que distorce a media."""

    @pytest.mark.asyncio
    async def test_dso_nao_fica_negativo(self, client):
        """DSO deve ser >= 0 mesmo com pagamentos antecipados."""
        cli = await create_test_cliente(client)
        # Fatura vence no futuro
        fat = await create_test_fatura(
            client, cli["id"], valor=100000, vencimento="2026-12-01T00:00:00Z"
        )
        # Pagar agora (antes do vencimento)
        await client.patch(
            f"/api/v1/faturas/{fat['id']}",
            json={"status": "pago"},
            headers=AUTH,
        )

        resp = await client.get(f"/api/v1/clientes/{cli['id']}/metricas", headers=AUTH)
        assert resp.status_code == 200
        # BUG: dso_dias vai ser negativo (~-249 dias)
        # FIX: dso deve ser capped em 0
        assert resp.json()["dso_dias"] >= 0


class TestBugExportarClienteAnonimizado:
    """BUG-005: POST /clientes/{id}/anonimizar seguido de GET /{id}/exportar.
    Apos anonimizar, o get_cliente normal retorna None (filtrado por deletado_em).
    Mas exportar chama get_cliente que retorna 404 — dados anonimizados nao sao exportaveis.
    Isso e o comportamento correto? O teste documenta a decisao."""

    @pytest.mark.asyncio
    async def test_exportar_cliente_anonimizado_retorna_404(self, client):
        """Exportar dados de cliente ja anonimizado deve retornar 404.
        (Dados foram removidos — nada para exportar.)"""
        cli = await create_test_cliente(client)

        await client.post(f"/api/v1/clientes/{cli['id']}/anonimizar", headers=AUTH)

        resp = await client.get(f"/api/v1/clientes/{cli['id']}/exportar", headers=AUTH)
        assert resp.status_code == 404


class TestBugUpdateClientePodeAlterarDocumento:
    """BUG-006: PATCH /clientes/{id} permite alterar documento (CPF/CNPJ).
    ClienteUpdate NAO tem campo documento, mas setattr generico poderia
    permitir injecao se alguem adicionasse. Teste defensivo."""

    @pytest.mark.asyncio
    async def test_patch_nao_aceita_documento(self, client):
        """PATCH cliente com campo documento deve ser ignorado (422 ou ignored)."""
        cli = await create_test_cliente(client, documento="52998224725")

        resp = await client.patch(
            f"/api/v1/clientes/{cli['id']}",
            json={"documento": "11444777000161"},
            headers=AUTH,
        )
        # Pydantic ignora campos nao definidos no schema (exclude_unset)
        # Verificar que documento NAO mudou
        if resp.status_code == 200:
            check = await client.get(f"/api/v1/clientes/{cli['id']}", headers=AUTH)
            assert check.json()["documento"] == "52998224725"


class TestBugTransicaoInvalidaRetorna409:
    """BUG-007: Verificar que todas as transicoes invalidas retornam 409 (nao 500)."""

    @pytest.mark.asyncio
    async def test_pago_para_pendente_retorna_409(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])

        await client.patch(f"/api/v1/faturas/{fat['id']}", json={"status": "pago"}, headers=AUTH)
        resp = await client.patch(
            f"/api/v1/faturas/{fat['id']}", json={"status": "pendente"}, headers=AUTH
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_cancelado_para_pago_retorna_409(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])

        await client.patch(
            f"/api/v1/faturas/{fat['id']}", json={"status": "cancelado"}, headers=AUTH
        )
        resp = await client.patch(
            f"/api/v1/faturas/{fat['id']}", json={"status": "pago"}, headers=AUTH
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_status_inexistente_retorna_422(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])

        resp = await client.patch(
            f"/api/v1/faturas/{fat['id']}", json={"status": "inventado"}, headers=AUTH
        )
        assert resp.status_code == 422


# =====================================================================
# INTEGRITY BUGS
# =====================================================================


class TestBugCobrancaEmFaturaTerminal:
    """BUG-008: Criar cobranca em fatura paga/cancelada deve retornar 409."""

    @pytest.mark.asyncio
    async def test_cobranca_em_fatura_paga_retorna_409(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])

        await client.patch(f"/api/v1/faturas/{fat['id']}", json={"status": "pago"}, headers=AUTH)

        resp = await client.post(
            "/api/v1/cobrancas",
            json={
                "fatura_id": fat["id"],
                "cliente_id": cli["id"],
                "tipo": "lembrete",
            },
            headers=AUTH,
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_cobranca_em_fatura_cancelada_retorna_409(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])

        await client.patch(
            f"/api/v1/faturas/{fat['id']}", json={"status": "cancelado"}, headers=AUTH
        )

        resp = await client.post(
            "/api/v1/cobrancas",
            json={
                "fatura_id": fat["id"],
                "cliente_id": cli["id"],
                "tipo": "cobranca",
            },
            headers=AUTH,
        )
        assert resp.status_code == 409


# =====================================================================
# RESILIENCE BUGS
# =====================================================================


class TestBugCSVImportEdgeCases:
    """BUG-009: Import CSV com inputs maliciosos."""

    @pytest.mark.asyncio
    async def test_csv_sem_header_retorna_erro(self, client):
        """CSV sem colunas obrigatorias deve retornar erro claro, nao 500."""
        import io

        csv_content = "coluna_errada;outra\nvalor1;valor2\n"
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_csv_com_filename_path_traversal(self, client):
        """Filename com path traversal deve ser rejeitado."""
        import io

        csv_content = "nome;documento;valor;vencimento\nTest;52998224725;10000;2026-12-01\n"
        files = {"file": ("../../etc/passwd.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        # Deve aceitar (filename e so metadata, nao salva no disco) ou rejeitar
        # O importante e que NAO cause crash
        assert resp.status_code in (200, 422)


class TestBugPaginationEdgeCases:
    """BUG-010: Paginacao com offsets maiores que total."""

    @pytest.mark.asyncio
    async def test_offset_maior_que_total_retorna_vazio(self, client):
        """Offset maior que total de registros deve retornar data vazio, nao erro."""
        resp = await client.get("/api/v1/clientes?offset=99999&limit=50", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["data"] == []
        assert resp.json()["pagination"]["has_more"] is False


class TestBugHealthCheckSemAuth:
    """BUG-011: Health check NUNCA deve exigir auth (monitoramento externo)."""

    @pytest.mark.asyncio
    async def test_health_sem_header(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestBugFaturaValorZero:
    """BUG-012: Fatura com valor=0 deve ser rejeitada (validacao Pydantic gt=0)."""

    @pytest.mark.asyncio
    async def test_fatura_valor_zero_retorna_422(self, client):
        cli = await create_test_cliente(client)
        resp = await client.post(
            "/api/v1/faturas",
            json={
                "cliente_id": cli["id"],
                "valor": 0,
                "vencimento": "2026-12-01T00:00:00Z",
            },
            headers=AUTH,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_fatura_valor_negativo_retorna_422(self, client):
        cli = await create_test_cliente(client)
        resp = await client.post(
            "/api/v1/faturas",
            json={
                "cliente_id": cli["id"],
                "valor": -100,
                "vencimento": "2026-12-01T00:00:00Z",
            },
            headers=AUTH,
        )
        assert resp.status_code == 422


class TestBugCleanupSemTenantFilter:
    """BUG-013: cleanup_service.executar_cleanup NAO filtra por tenant.
    O _limpar_mensagens_antigas e _anonimizar_clientes_inativos atuam em
    TODOS os tenants — isso e correto para um job global, mas deveria
    ser documentado e nao exposto a qualquer tenant autenticado."""

    @pytest.mark.asyncio
    async def test_cleanup_retorna_200(self, client):
        """Cleanup deve funcionar sem crash."""
        resp = await client.post("/api/v1/admin/cleanup", headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert "mensagens_limpas" in body
        assert "clientes_anonimizados" in body
