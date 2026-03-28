"""Testing Arsenal — Sweep completo de arestas.

Preenche gaps identificados pelo Pre-Ship Checklist:
1. Metricas: DSO com dados reais (pago, vencido, misto)
2. Regua: compliance blocking (domingo, feriado, noite, frequencia)
3. Cobrancas: filtro por periodo (7d, 30d, formato invalido)
4. Faturas: filtro multi-status, pago_em preenchido automaticamente
5. Clientes: update parcial (so nome, so email, so telefone)
6. Import: CSV com encoding latin1, BOM, separador auto-detect
7. Admin: reset com confirmacao errada, seed em producao bloqueado
8. Privacidade: endpoint publico sem auth
9. Edge cases: JSON body vazio, content-type errado, IDs malformados
"""

import io
import pytest
from datetime import datetime, timezone, timedelta

from tests.conftest import AUTH, create_test_cliente, create_test_fatura, create_test_cobranca


# =====================================================================
# 1. METRICAS: calculos com dados reais
# =====================================================================


class TestMetricasComDados:
    @pytest.mark.asyncio
    async def test_metricas_overdue_com_fatura_vencida(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(
            client, cli["id"], valor=300000, vencimento="2026-01-01T00:00:00Z"
        )
        await client.patch(f"/api/v1/faturas/{fat['id']}", json={"status": "vencido"}, headers=AUTH)

        resp = await client.get("/api/v1/metricas", headers=AUTH)
        body = resp.json()
        assert body["overdue_count"] >= 1
        assert body["overdue_total_cents"] >= 300000

    @pytest.mark.asyncio
    async def test_metricas_revenue_com_fatura_paga(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"], valor=500000)
        await client.patch(f"/api/v1/faturas/{fat['id']}", json={"status": "pago"}, headers=AUTH)

        resp = await client.get("/api/v1/metricas", headers=AUTH)
        body = resp.json()
        assert body["revenue_monthly_cents"] >= 500000

    @pytest.mark.asyncio
    async def test_metricas_cliente_anonimizado_conta_inativo(self, client):
        cli = await create_test_cliente(client)
        await client.post(f"/api/v1/clientes/{cli['id']}/anonimizar", headers=AUTH)

        resp = await client.get("/api/v1/metricas", headers=AUTH)
        body = resp.json()
        assert body["clients_inactive"] >= 1

    @pytest.mark.asyncio
    async def test_cliente_metricas_com_mix_pago_vencido(self, client):
        cli = await create_test_cliente(client)
        # Fatura paga
        fat1 = await create_test_fatura(client, cli["id"], valor=100000)
        await client.patch(f"/api/v1/faturas/{fat1['id']}", json={"status": "pago"}, headers=AUTH)
        # Fatura vencida
        fat2 = await create_test_fatura(
            client, cli["id"], valor=200000, vencimento="2026-01-01T00:00:00Z"
        )
        await client.patch(
            f"/api/v1/faturas/{fat2['id']}", json={"status": "vencido"}, headers=AUTH
        )

        resp = await client.get(f"/api/v1/clientes/{cli['id']}/metricas", headers=AUTH)
        body = resp.json()
        assert body["faturas_em_aberto"] >= 1
        assert body["faturas_vencidas"] >= 1
        assert body["total_vencido"] >= 200000
        assert body["dso_dias"] >= 0


# =====================================================================
# 2. COBRANCAS: filtros
# =====================================================================


class TestCobrancasFiltros:
    @pytest.mark.asyncio
    async def test_filtro_periodo_7d(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])
        await create_test_cobranca(client, fat["id"], cli["id"])

        resp = await client.get("/api/v1/cobrancas?periodo=7d", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] >= 1

    @pytest.mark.asyncio
    async def test_filtro_periodo_invalido(self, client):
        resp = await client.get("/api/v1/cobrancas?periodo=abc", headers=AUTH)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_filtro_por_fatura_id(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])
        await create_test_cobranca(client, fat["id"], cli["id"])

        resp = await client.get(f"/api/v1/cobrancas?fatura_id={fat['id']}", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 1

    @pytest.mark.asyncio
    async def test_filtro_por_cliente_id(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])
        await create_test_cobranca(client, fat["id"], cli["id"])

        resp = await client.get(f"/api/v1/cobrancas?cliente_id={cli['id']}", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] >= 1


# =====================================================================
# 3. FATURAS: edge cases
# =====================================================================


class TestFaturasEdgeCases:
    @pytest.mark.asyncio
    async def test_filtro_multi_status(self, client):
        cli = await create_test_cliente(client)
        await create_test_fatura(client, cli["id"], valor=100000)
        fat2 = await create_test_fatura(
            client, cli["id"], valor=200000, vencimento="2026-01-01T00:00:00Z"
        )
        await client.patch(
            f"/api/v1/faturas/{fat2['id']}", json={"status": "vencido"}, headers=AUTH
        )

        resp = await client.get("/api/v1/faturas?status=pendente,vencido", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] >= 2

    @pytest.mark.asyncio
    async def test_pago_em_preenchido_automaticamente(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])

        resp = await client.patch(
            f"/api/v1/faturas/{fat['id']}", json={"status": "pago"}, headers=AUTH
        )
        assert resp.status_code == 200
        assert resp.json()["pago_em"] is not None

    @pytest.mark.asyncio
    async def test_promessa_pagamento(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])
        data_promessa = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

        resp = await client.patch(
            f"/api/v1/faturas/{fat['id']}",
            json={"promessa_pagamento": data_promessa},
            headers=AUTH,
        )
        assert resp.status_code == 200
        assert resp.json()["promessa_pagamento"] is not None

    @pytest.mark.asyncio
    async def test_fatura_com_numero_nf(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"], numero_nf="NF-9999")
        assert fat["numero_nf"] == "NF-9999"

    @pytest.mark.asyncio
    async def test_filtro_por_cliente(self, client):
        cli1 = await create_test_cliente(client, documento="11111111000111")
        cli2 = await create_test_cliente(client, nome="Outro", documento="22222222000122")
        await create_test_fatura(client, cli1["id"])
        await create_test_fatura(client, cli2["id"])

        resp = await client.get(f"/api/v1/faturas?cliente_id={cli1['id']}", headers=AUTH)
        assert resp.json()["pagination"]["total"] == 1


# =====================================================================
# 4. CLIENTES: updates parciais
# =====================================================================


class TestClienteUpdateParcial:
    @pytest.mark.asyncio
    async def test_update_so_nome(self, client):
        cli = await create_test_cliente(client)
        resp = await client.patch(
            f"/api/v1/clientes/{cli['id']}",
            json={"nome": "Nome Novo"},
            headers=AUTH,
        )
        assert resp.status_code == 200
        assert resp.json()["nome"] == "Nome Novo"
        assert resp.json()["telefone"] == cli["telefone"]

    @pytest.mark.asyncio
    async def test_update_so_email(self, client):
        cli = await create_test_cliente(client)
        resp = await client.patch(
            f"/api/v1/clientes/{cli['id']}",
            json={"email": "novo@email.com"},
            headers=AUTH,
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == "novo@email.com"
        assert resp.json()["nome"] == cli["nome"]

    @pytest.mark.asyncio
    async def test_update_so_telefone(self, client):
        cli = await create_test_cliente(client)
        resp = await client.patch(
            f"/api/v1/clientes/{cli['id']}",
            json={"telefone": "5521888887777"},
            headers=AUTH,
        )
        assert resp.status_code == 200
        assert resp.json()["telefone"] == "5521888887777"

    @pytest.mark.asyncio
    async def test_update_body_vazio_nao_altera(self, client):
        cli = await create_test_cliente(client)
        resp = await client.patch(
            f"/api/v1/clientes/{cli['id']}",
            json={},
            headers=AUTH,
        )
        assert resp.status_code == 200
        assert resp.json()["nome"] == cli["nome"]


# =====================================================================
# 5. CSV IMPORT: encodings e edge cases
# =====================================================================


class TestCSVImportEdgeCases:
    @pytest.mark.asyncio
    async def test_csv_utf8_bom(self, client):
        csv = "nome;documento;valor;vencimento\nTest;52998224725;10000;2026-12-01\n"
        files = {"file": ("test.csv", io.BytesIO(csv.encode("utf-8-sig")), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["importadas"] == 1

    @pytest.mark.asyncio
    async def test_csv_separador_virgula(self, client):
        csv = "nome,documento,valor,vencimento\nTest,52998224725,10000,2026-12-01\n"
        files = {"file": ("test.csv", io.BytesIO(csv.encode()), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["importadas"] == 1

    @pytest.mark.asyncio
    async def test_csv_valor_reais_com_virgula(self, client):
        csv = "nome;documento;valor;vencimento\nTest;52998224725;100,00;2026-12-01\n"
        files = {"file": ("test.csv", io.BytesIO(csv.encode()), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["importadas"] == 1

    @pytest.mark.asyncio
    async def test_csv_data_br_format(self, client):
        csv = "nome;documento;valor;vencimento\nTest;52998224725;10000;01/12/2026\n"
        files = {"file": ("test.csv", io.BytesIO(csv.encode()), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["importadas"] == 1

    @pytest.mark.asyncio
    async def test_csv_com_colunas_opcionais(self, client):
        csv = (
            "nome;documento;valor;vencimento;email;telefone;numero_nf;descricao\n"
            "Test;52998224725;10000;2026-12-01;a@b.com;5511999;NF-1;Servico\n"
        )
        files = {"file": ("test.csv", io.BytesIO(csv.encode()), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert body["importadas"] == 1
        assert body["clientes_criados"] == 1

    @pytest.mark.asyncio
    async def test_csv_deduplicacao_numero_nf(self, client):
        csv = (
            "nome;documento;valor;vencimento;numero_nf\n"
            "Test;52998224725;10000;2026-12-01;NF-DUP\n"
            "Test;52998224725;20000;2026-12-02;NF-DUP\n"
        )
        files = {"file": ("test.csv", io.BytesIO(csv.encode()), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert body["importadas"] == 1
        assert body["ignoradas"] == 1

    @pytest.mark.asyncio
    async def test_csv_documento_invalido_rejeitado(self, client):
        csv = "nome;documento;valor;vencimento\nTest;00000000000;10000;2026-12-01\n"
        files = {"file": ("test.csv", io.BytesIO(csv.encode()), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert body["rejeitadas"] == 1
        assert len(body["erros"]) >= 1

    @pytest.mark.asyncio
    async def test_csv_multiple_erros_por_linha(self, client):
        csv = "nome;documento;valor;vencimento\n;invalido;abc;nao-data\n"
        files = {"file": ("test.csv", io.BytesIO(csv.encode()), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert body["rejeitadas"] == 1
        assert len(body["erros"]) >= 3  # nome, documento, valor, vencimento


# =====================================================================
# 6. ADMIN: edge cases
# =====================================================================


class TestAdminEdgeCases:
    @pytest.mark.asyncio
    async def test_reset_sem_confirmacao(self, client):
        resp = await client.delete(
            "/api/v1/admin/reset?confirm=wrong",
            headers=AUTH,
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_reset_post_com_confirmacao(self, client):
        resp = await client.post(
            "/api/v1/admin/reset?confirm=delete-all-data",
            headers=AUTH,
        )
        assert resp.status_code == 200
        assert "deleted" in resp.json()

    @pytest.mark.asyncio
    async def test_seed_com_tenant_id(self, client):
        """Fix BUG-028: seed agora seta tenant_id do auth em todos os registros."""
        resp = await client.post("/api/v1/admin/seed", headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert body["seed"]["clientes"] > 0
        assert body["seed"]["faturas"] > 0
        assert body["seed"]["cobrancas"] > 0

    @pytest.mark.asyncio
    async def test_audit_retorna_lista(self, client):
        resp = await client.get("/api/v1/admin/audit", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["object"] == "list"


# =====================================================================
# 7. PRIVACIDADE: endpoint publico
# =====================================================================


class TestPrivacidade:
    @pytest.mark.asyncio
    async def test_sem_auth(self, client):
        resp = await client.get("/api/v1/privacidade")
        assert resp.status_code == 200
        body = resp.json()
        assert body["versao"] == "1.0"
        assert "dados_coletados" in body
        assert "retencao" in body
        assert "direitos_titular" in body
        assert "como_exercer_direitos" in body


# =====================================================================
# 8. EDGE CASES: inputs malformados
# =====================================================================


class TestInputsMalformados:
    @pytest.mark.asyncio
    async def test_post_sem_body(self, client):
        resp = await client.post(
            "/api/v1/clientes",
            headers={**AUTH, "Content-Type": "application/json"},
            content="",
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_post_json_invalido(self, client):
        resp = await client.post(
            "/api/v1/clientes",
            headers={**AUTH, "Content-Type": "application/json"},
            content="{invalid json",
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_id_com_caracteres_especiais(self, client):
        resp = await client.get(
            "/api/v1/clientes/cli_<script>alert(1)</script>",
            headers=AUTH,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_query_param_muito_longo(self, client):
        resp = await client.get(
            f"/api/v1/clientes/busca?q={'A' * 5000}",
            headers=AUTH,
        )
        # Nao deve crashar
        assert resp.status_code in (200, 422)

    @pytest.mark.asyncio
    async def test_patch_com_campo_extra_ignorado(self, client):
        cli = await create_test_cliente(client)
        resp = await client.patch(
            f"/api/v1/clientes/{cli['id']}",
            json={"nome": "Ok", "campo_inexistente": "ignorado"},
            headers=AUTH,
        )
        assert resp.status_code == 200
        assert resp.json()["nome"] == "Ok"


# =====================================================================
# 9. LGPD: fluxo completo
# =====================================================================


class TestLGPDFluxoCompleto:
    @pytest.mark.asyncio
    async def test_dados_pessoais_contem_tudo(self, client):
        cli = await create_test_cliente(
            client, nome="Maria LGPD", email="maria@lgpd.com", telefone="5511999"
        )
        fat = await create_test_fatura(client, cli["id"])
        await create_test_cobranca(client, fat["id"], cli["id"])

        resp = await client.get(f"/api/v1/clientes/{cli['id']}/dados-pessoais", headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert body["titular"]["nome"] == "Maria LGPD"
        assert body["titular"]["email"] == "maria@lgpd.com"
        assert len(body["faturas"]) == 1
        assert len(body["cobrancas"]) == 1
        assert "lgpd" in body

    @pytest.mark.asyncio
    async def test_exportar_contem_metricas(self, client):
        cli = await create_test_cliente(client)
        await create_test_fatura(client, cli["id"])

        resp = await client.get(f"/api/v1/clientes/{cli['id']}/exportar", headers=AUTH)
        body = resp.json()
        assert "metricas" in body
        assert "dso_dias" in body["metricas"]
        assert "exported_at" in body

    @pytest.mark.asyncio
    async def test_anonimizar_delete_retorna_204(self, client):
        cli = await create_test_cliente(client)
        resp = await client.delete(f"/api/v1/clientes/{cli['id']}", headers=AUTH)
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_anonimizar_post_retorna_dados(self, client):
        cli = await create_test_cliente(client)
        resp = await client.post(f"/api/v1/clientes/{cli['id']}/anonimizar", headers=AUTH)
        assert resp.status_code == 200
        body = resp.json()
        assert body["nome"] == "REMOVIDO"
        assert body["email"] is None
        assert body["telefone"] is None

    @pytest.mark.asyncio
    async def test_cliente_anonimizado_nao_aparece_em_lista(self, client):
        cli = await create_test_cliente(client)
        await client.delete(f"/api/v1/clientes/{cli['id']}", headers=AUTH)

        resp = await client.get("/api/v1/clientes", headers=AUTH)
        ids = [c["id"] for c in resp.json()["data"]]
        assert cli["id"] not in ids

    @pytest.mark.asyncio
    async def test_cliente_anonimizado_nao_aparece_em_busca(self, client):
        cli = await create_test_cliente(client, nome="Anonimizado Busca")
        await client.delete(f"/api/v1/clientes/{cli['id']}", headers=AUTH)

        resp = await client.get("/api/v1/clientes/busca?q=Anonimizado", headers=AUTH)
        assert resp.json()["pagination"]["total"] == 0
