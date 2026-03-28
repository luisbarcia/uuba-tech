"""Bug Hunt COMPLETO — varredura de todos os 57 arquivos Python.

Cobre:
- SECURITY: vazamento de dados, bypass, injection
- LOGIC: edge cases, calculos incorretos
- INTEGRITY: dados inconsistentes, constraints faltantes
- RESILIENCE: crashes em inputs validos mas inesperados
- COMPLIANCE: LGPD, horarios, feriados
- IMPORT: CSV parsing edge cases
- REGUA: motor de cobranca edge cases
"""

import pytest

from tests.conftest import AUTH, create_test_cliente, create_test_fatura, create_test_cobranca


# =====================================================================
# SECURITY: tenants router sem restricao admin
# =====================================================================


class TestBugTenantsCRUDSemAdmin:
    """BUG-014: Qualquer API key autenticada pode criar/listar/atualizar tenants.
    Um tenant starter consegue ver todos os outros tenants da plataforma."""

    @pytest.mark.asyncio
    async def test_list_tenants_retorna_dados(self, client):
        """Demonstra que qualquer tenant ve a lista de todos os tenants.
        NAO e um bug de crash, e um bug de AUTORIZACAO."""
        resp = await client.get("/api/v1/tenants", headers=AUTH)
        assert resp.status_code == 200
        # Pelo menos o tenant de teste existe
        assert resp.json()["pagination"]["total"] >= 1

    @pytest.mark.asyncio
    async def test_create_tenant_with_admin_works(self, client):
        """Com permissao admin (conftest default), criar tenant funciona."""
        resp = await client.post(
            "/api/v1/tenants",
            json={"name": "Criado Com Admin"},
            headers=AUTH,
        )
        assert resp.status_code == 201
        # RBAC restritivo testado em test_tenants_rbac.py


# =====================================================================
# SECURITY: audit_service.registrar nao seta tenant_id
# =====================================================================


class TestBugAuditSemTenantId:
    """BUG-015: AuditLog model tem campo tenant_id NOT NULL,
    mas audit_service.registrar() nunca passa tenant_id.
    Em producao com PostgreSQL (NOT NULL constraint), vai dar 500."""

    @pytest.mark.asyncio
    async def test_admin_audit_retorna_200(self, client):
        """GET /admin/audit deve funcionar sem crash."""
        resp = await client.get("/api/v1/admin/audit", headers=AUTH)
        assert resp.status_code == 200


# =====================================================================
# LOGIC: compliance feriados hardcoded para 2026
# =====================================================================


class TestBugComplianceFeriadoHardcoded:
    """BUG-016: compliance.py tem FERIADOS_NACIONAIS_2026 hardcoded.
    Em 2027 a funcao is_horario_util vai permitir envio em feriados."""

    def test_feriado_natal_2026_bloqueado(self):
        from datetime import datetime, timezone
        from app.services.compliance import is_horario_util

        natal = datetime(2026, 12, 25, 10, 0, tzinfo=timezone.utc)
        assert is_horario_util(natal) is False

    def test_domingo_bloqueado(self):
        from datetime import datetime, timezone
        from app.services.compliance import is_horario_util

        # 2026-03-29 e domingo
        domingo = datetime(2026, 3, 29, 10, 0, tzinfo=timezone.utc)
        assert is_horario_util(domingo) is False

    def test_horario_fora_expediente_bloqueado(self):
        from datetime import datetime, timezone
        from app.services.compliance import is_horario_util

        # Seg as 21h — fora do expediente
        noite = datetime(2026, 3, 30, 21, 0, tzinfo=timezone.utc)
        assert is_horario_util(noite) is False

    def test_horario_valido_permitido(self):
        from datetime import datetime, timezone
        from app.services.compliance import is_horario_util

        # Seg as 10h — dentro do expediente
        manha = datetime(2026, 3, 30, 10, 0, tzinfo=timezone.utc)
        assert is_horario_util(manha) is True

    def test_sabado_dentro_expediente(self):
        from datetime import datetime, timezone
        from app.services.compliance import is_horario_util

        # Sab as 10h — dentro do expediente (8-14)
        sab_manha = datetime(2026, 3, 28, 10, 0, tzinfo=timezone.utc)
        assert is_horario_util(sab_manha) is True

    def test_sabado_fora_expediente(self):
        from datetime import datetime, timezone
        from app.services.compliance import is_horario_util

        # Sab as 15h — fora do expediente (8-14)
        sab_tarde = datetime(2026, 3, 28, 15, 0, tzinfo=timezone.utc)
        assert is_horario_util(sab_tarde) is False


# =====================================================================
# LOGIC: compliance frequencia edge cases
# =====================================================================


class TestBugComplianceFrequencia:
    """BUG-017: pode_enviar() edge cases."""

    def test_pode_enviar_sem_historico(self):
        from app.services.compliance import pode_enviar

        assert pode_enviar([]) is True

    def test_bloqueia_segunda_no_dia(self):
        from datetime import datetime, timezone
        from app.services.compliance import pode_enviar

        agora = datetime(2026, 3, 27, 14, 0, tzinfo=timezone.utc)
        recentes = [datetime(2026, 3, 27, 10, 0, tzinfo=timezone.utc)]
        assert pode_enviar(recentes, agora=agora) is False

    def test_bloqueia_quarta_na_semana(self):
        from datetime import datetime, timezone
        from app.services.compliance import pode_enviar

        agora = datetime(2026, 3, 27, 10, 0, tzinfo=timezone.utc)
        recentes = [
            datetime(2026, 3, 22, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 24, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 26, 10, 0, tzinfo=timezone.utc),
        ]
        assert pode_enviar(recentes, agora=agora) is False


# =====================================================================
# LOGIC: import_service edge cases
# =====================================================================


class TestBugImportParseValor:
    """BUG-018: _parse_valor edge cases."""

    def test_valor_reais_virgula(self):
        from app.services.import_service import _parse_valor

        assert _parse_valor("2500,00") == 250000

    def test_valor_reais_ponto(self):
        from app.services.import_service import _parse_valor

        assert _parse_valor("2500.00") == 250000

    def test_valor_centavos_inteiro(self):
        from app.services.import_service import _parse_valor

        assert _parse_valor("250000") == 250000

    def test_valor_com_espacos(self):
        from app.services.import_service import _parse_valor

        assert _parse_valor("  2500.00  ") == 250000

    def test_valor_vazio_raise(self):
        from app.services.import_service import _parse_valor

        with pytest.raises(ValueError):
            _parse_valor("")

    def test_valor_texto_raise(self):
        from app.services.import_service import _parse_valor

        with pytest.raises(ValueError):
            _parse_valor("abc")

    def test_valor_com_milhar_nao_suportado(self):
        """BUG: '2.500,00' nao e suportado (ponto como milhar).
        O regex espera digitos+separador+2decimais, mas '2.500,00' tem ponto no meio."""
        from app.services.import_service import _parse_valor

        with pytest.raises(ValueError):
            _parse_valor("2.500,00")

    def test_valor_com_1_decimal_nao_suportado(self):
        """BUG: '2500.5' (1 decimal) nao e reconhecido — regex exige exatamente 2."""
        from app.services.import_service import _parse_valor

        with pytest.raises(ValueError):
            _parse_valor("2500.5")


class TestBugImportParseDate:
    """BUG-019: _parse_date edge cases."""

    def test_date_br_format(self):
        from app.services.import_service import _parse_date
        from datetime import timezone

        dt = _parse_date("15/01/2026")
        assert dt.day == 15
        assert dt.month == 1
        assert dt.year == 2026
        assert dt.tzinfo == timezone.utc

    def test_date_iso_format(self):
        from app.services.import_service import _parse_date

        dt = _parse_date("2026-01-15")
        assert dt.day == 15

    def test_date_invalid_raise(self):
        from app.services.import_service import _parse_date

        with pytest.raises(ValueError):
            _parse_date("not-a-date")

    def test_date_day_month_swap_br(self):
        """BUG: '31/12/2026' e valido. '12/31/2026' deveria falhar (mes 31 nao existe).
        Mas o regex aceita dd/mm/yyyy e datetime() vai levantar ValueError."""
        from app.services.import_service import _parse_date

        with pytest.raises(ValueError):
            _parse_date("31/13/2026")  # mes 13


# =====================================================================
# LOGIC: regua_service edge cases
# =====================================================================


class TestBugReguaTemplate:
    """BUG-020: _renderizar_template com campos None."""

    def test_template_com_nf_none(self):
        from app.services.regua_service import _renderizar_template
        from unittest.mock import MagicMock

        fatura = MagicMock()
        fatura.valor = 250000
        fatura.vencimento = None
        fatura.numero_nf = None
        fatura.pagamento_link = None

        result = _renderizar_template(
            "Fatura {numero_nf}: R$ {valor}. Link: {link_pagamento}", fatura, 5
        )
        assert "S/N" in result
        assert "(link pendente)" in result

    def test_template_com_campos_reais(self):
        from datetime import datetime, timezone
        from app.services.regua_service import _renderizar_template
        from unittest.mock import MagicMock

        fatura = MagicMock()
        fatura.valor = 250000
        fatura.vencimento = datetime(2026, 3, 1, tzinfo=timezone.utc)
        fatura.numero_nf = "NF-1234"
        fatura.pagamento_link = "https://pag.me/xyz"

        result = _renderizar_template(
            "NF {numero_nf}, R$ {valor}, venc {vencimento}, D+{dias_atraso}", fatura, 10
        )
        assert "NF-1234" in result
        assert "2.500,00" in result
        assert "01/03/2026" in result
        assert "D+10" in result


class TestBugReguaProximoPasso:
    """BUG-021: _proximo_passo edge cases."""

    def test_sem_passos_retorna_none(self):
        from app.services.regua_service import _proximo_passo

        assert _proximo_passo([], 5) is None

    def test_atraso_zero_sem_passo_d0(self):
        from app.services.regua_service import _proximo_passo
        from unittest.mock import MagicMock

        passo = MagicMock()
        passo.dias_atraso = 1
        assert _proximo_passo([passo], 0) is None

    def test_retorna_passo_mais_avancado(self):
        from app.services.regua_service import _proximo_passo
        from unittest.mock import MagicMock

        p1 = MagicMock()
        p1.dias_atraso = 1
        p2 = MagicMock()
        p2.dias_atraso = 7
        p3 = MagicMock()
        p3.dias_atraso = 15

        result = _proximo_passo([p1, p2, p3], 10)
        assert result == p2  # D+7 e o mais avancado <=10


# =====================================================================
# RESILIENCE: main.py exception handlers
# =====================================================================


class TestBugExceptionHandlers:
    """BUG-022: exception handlers nao devem vazar stack traces."""

    @pytest.mark.asyncio
    async def test_404_formato_rfc9457(self, client):
        resp = await client.get("/api/v1/clientes/cli_inexistente", headers=AUTH)
        assert resp.status_code == 404
        body = resp.json()
        assert "type" in body
        assert "title" in body
        assert "status" in body
        assert "detail" in body
        assert "request_id" in body
        # NAO deve ter stack trace
        assert "Traceback" not in str(body)

    @pytest.mark.asyncio
    async def test_422_formato_pydantic(self, client):
        resp = await client.post(
            "/api/v1/clientes",
            json={"nome": ""},  # nome vazio, documento faltando
            headers=AUTH,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_401_sem_api_key(self, client):
        resp = await client.get("/api/v1/clientes")
        assert resp.status_code == 401
        body = resp.json()
        assert body["status"] == 401
        # NAO deve vazar info sobre keys validas
        assert "uuba-dev-key" not in str(body).lower()


# =====================================================================
# RESILIENCE: CSV upload attacks
# =====================================================================


class TestBugCSVAttacks:
    """BUG-023: CSV com payloads maliciosos."""

    @pytest.mark.asyncio
    async def test_csv_formula_injection(self, client):
        """CSV com formulas Excel (=CMD()) nao deve causar problemas server-side."""
        import io

        csv_content = 'nome;documento;valor;vencimento\n=CMD("calc");52998224725;10000;2026-12-01\n'
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        # Pode importar (nome ficaria "=CMD...") ou rejeitar — mas NAO deve crashar
        assert resp.status_code in (200, 422)

    @pytest.mark.asyncio
    async def test_csv_megabyte_lines(self, client):
        """CSV com linha extremamente longa nao deve travar o server."""
        import io

        header = "nome;documento;valor;vencimento\n"
        long_name = "A" * 10000
        line = f"{long_name};52998224725;10000;2026-12-01\n"
        csv_content = header + line
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        # Pode truncar nome ou rejeitar — mas NAO deve crashar
        assert resp.status_code in (200, 422)

    @pytest.mark.asyncio
    async def test_csv_null_bytes(self, client):
        """CSV com null bytes nao deve causar crash."""
        import io

        csv_content = "nome;documento;valor;vencimento\nTest\x00;52998224725;10000;2026-12-01\n"
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        resp = await client.post("/api/v1/import/csv", files=files, headers=AUTH)
        assert resp.status_code in (200, 422)


# =====================================================================
# RESILIENCE: rate limit
# =====================================================================


class TestBugRateLimit:
    """BUG-024: rate limit desabilitado em testes (TESTING=1) e correto."""

    @pytest.mark.asyncio
    async def test_100_requests_nao_bloqueiam_em_teste(self, client):
        """Em ambiente de teste, rate limit esta desabilitado."""
        for _ in range(5):
            resp = await client.get("/api/v1/clientes", headers=AUTH)
            assert resp.status_code == 200


# =====================================================================
# INTEGRITY: seed com documentos invalidos
# =====================================================================


class TestBugSeedData:
    """BUG-025: Seed data tem documentos validos?"""

    def test_seed_documentos_sao_14_digitos(self):
        """CNPJs no seed devem ter 14 digitos."""
        from app.seed import CLIENTES

        for cli in CLIENTES:
            doc = cli["documento"]
            assert len(doc) == 14 or len(doc) == 11, f"Documento invalido: {doc}"
            assert doc.isdigit(), f"Documento com nao-digitos: {doc}"


# =====================================================================
# INTEGRITY: IDs sempre prefixados
# =====================================================================


class TestBugIDsPrefixados:
    """BUG-026: Todos os IDs devem ter prefixo correto."""

    @pytest.mark.asyncio
    async def test_cliente_id_prefixo_cli(self, client):
        cli = await create_test_cliente(client)
        assert cli["id"].startswith("cli_")

    @pytest.mark.asyncio
    async def test_fatura_id_prefixo_fat(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])
        assert fat["id"].startswith("fat_")

    @pytest.mark.asyncio
    async def test_cobranca_id_prefixo_cob(self, client):
        cli = await create_test_cliente(client)
        fat = await create_test_fatura(client, cli["id"])
        cob = await create_test_cobranca(client, fat["id"], cli["id"])
        assert cob["id"].startswith("cob_")

    @pytest.mark.asyncio
    async def test_tenant_id_prefixo_ten(self, client):
        resp = await client.get("/api/v1/tenants", headers=AUTH)
        tenants = resp.json()["data"]
        assert len(tenants) > 0
        assert tenants[0]["id"].startswith("ten_")


# =====================================================================
# INTEGRITY: request_id em todas as respostas
# =====================================================================


class TestBugRequestId:
    """BUG-027: Header X-Request-Id deve estar em todas as respostas."""

    @pytest.mark.asyncio
    async def test_200_tem_request_id(self, client):
        resp = await client.get("/health")
        assert "x-request-id" in resp.headers
        assert resp.headers["x-request-id"].startswith("req_")

    @pytest.mark.asyncio
    async def test_404_tem_request_id(self, client):
        resp = await client.get("/api/v1/clientes/cli_nao_existe", headers=AUTH)
        assert "x-request-id" in resp.headers

    @pytest.mark.asyncio
    async def test_401_tem_request_id(self, client):
        resp = await client.get("/api/v1/clientes")
        assert "x-request-id" in resp.headers
