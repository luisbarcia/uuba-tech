"""Testes do endpoint POST /api/v1/import/csv."""

from httpx import AsyncClient

from tests.conftest import AUTH, create_test_cliente

# Documentos VÁLIDOS (dígitos verificadores corretos)
CNPJ_VALIDO = "11222333000181"
CPF_VALIDO = "52998224725"
CPF_INVALIDO = "00000000000"


def _csv_file(content: str, filename: str = "import.csv"):
    """Helper para criar tupla de upload multipart."""
    return {"file": (filename, content.strip().encode("utf-8"), "text/csv")}


CSV_BASICO = f"""nome,documento,valor,vencimento
Padaria Bom Pao,{CNPJ_VALIDO},250000,2026-04-01
Loja do Ze,{CPF_VALIDO},150000,2026-05-15"""

CSV_SEMICOLON = f"""nome;documento;valor;vencimento
Padaria Bom Pao;{CNPJ_VALIDO};250000;2026-04-01
Loja do Ze;{CPF_VALIDO};150000;2026-05-15"""

CSV_COM_OPCIONAIS = f"""nome,documento,valor,vencimento,email,telefone,numero_nf,descricao
Padaria Bom Pao,{CNPJ_VALIDO},250000,2026-04-01,contato@padaria.com,5511999001234,NF-001,Servicos marco"""

CSV_DOC_INVALIDO = f"""nome,documento,valor,vencimento
Padaria Bom Pao,{CPF_INVALIDO},250000,2026-04-01"""

CSV_VALOR_INVALIDO = f"""nome,documento,valor,vencimento
Padaria Bom Pao,{CNPJ_VALIDO},abc,2026-04-01"""

CSV_VALOR_ZERO = f"""nome,documento,valor,vencimento
Padaria Bom Pao,{CNPJ_VALIDO},0,2026-04-01"""

CSV_VENCIMENTO_BR = f"""nome,documento,valor,vencimento
Padaria Bom Pao,{CNPJ_VALIDO},250000,15/03/2026"""

CSV_MISTO = f"""nome,documento,valor,vencimento
Padaria Bom Pao,{CNPJ_VALIDO},250000,2026-04-01
Linha Ruim,{CPF_INVALIDO},abc,nao-data
Loja do Ze,{CPF_VALIDO},50000,2026-05-15"""

CSV_SEM_COLUNA = """nome,valor,vencimento
Padaria Bom Pao,250000,2026-04-01"""

CSV_VALOR_REAIS = f"""nome,documento,valor,vencimento
Padaria Bom Pao,{CNPJ_VALIDO},2500.00,2026-04-01"""

CSV_DEDUP = f"""nome,documento,valor,vencimento,numero_nf
Padaria Bom Pao,{CNPJ_VALIDO},250000,2026-04-01,NF-001
Padaria Bom Pao,{CNPJ_VALIDO},300000,2026-05-01,NF-001"""


class TestImportCSVBasico:
    async def test_import_csv_basico(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_BASICO),
            headers=AUTH,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_linhas"] == 2
        assert data["importadas"] == 2
        assert data["rejeitadas"] == 0
        assert data["clientes_criados"] == 2

    async def test_import_csv_auto_detect_semicolon(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_SEMICOLON),
            headers=AUTH,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["importadas"] == 2

    async def test_import_csv_colunas_opcionais(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_COM_OPCIONAIS),
            headers=AUTH,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["importadas"] == 1


class TestImportCSVValidacao:
    async def test_documento_invalido_rejeitado(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_DOC_INVALIDO),
            headers=AUTH,
        )
        data = resp.json()
        assert data["rejeitadas"] == 1
        assert data["importadas"] == 0
        assert len(data["erros"]) >= 1
        assert data["erros"][0]["campo"] == "documento"

    async def test_valor_invalido_rejeitado(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_VALOR_INVALIDO),
            headers=AUTH,
        )
        data = resp.json()
        assert data["rejeitadas"] == 1
        assert any(e["campo"] == "valor" for e in data["erros"])

    async def test_valor_zero_rejeitado(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_VALOR_ZERO),
            headers=AUTH,
        )
        data = resp.json()
        assert data["rejeitadas"] == 1

    async def test_colunas_faltando_retorna_422(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_SEM_COLUNA),
            headers=AUTH,
        )
        assert resp.status_code == 422

    async def test_formato_invalido_retorna_422(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files={"file": ("import.txt", b"hello", "text/plain")},
            headers=AUTH,
        )
        assert resp.status_code == 422

    async def test_arquivo_vazio_retorna_422(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files={"file": ("import.csv", b"", "text/csv")},
            headers=AUTH,
        )
        assert resp.status_code == 422


class TestImportCSVFormatos:
    async def test_vencimento_formato_br(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_VENCIMENTO_BR),
            headers=AUTH,
        )
        data = resp.json()
        assert data["importadas"] == 1

    async def test_valor_em_reais_convertido(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_VALOR_REAIS),
            headers=AUTH,
        )
        data = resp.json()
        assert data["importadas"] == 1
        # Verificar que a fatura foi criada com 250000 centavos
        faturas_resp = await client.get("/api/v1/faturas", headers=AUTH)
        faturas = faturas_resp.json()["data"]
        assert any(f["valor"] == 250000 for f in faturas)

    async def test_bom_utf8(self, client: AsyncClient):
        content = b"\xef\xbb\xbf" + CSV_BASICO.strip().encode("utf-8")
        resp = await client.post(
            "/api/v1/import/csv",
            files={"file": ("import.csv", content, "text/csv")},
            headers=AUTH,
        )
        data = resp.json()
        assert data["importadas"] == 2


class TestImportCSVLogica:
    async def test_linha_parcial_nao_bloqueia_outras(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_MISTO),
            headers=AUTH,
        )
        data = resp.json()
        assert data["total_linhas"] == 3
        assert data["importadas"] == 2
        assert data["rejeitadas"] == 1

    async def test_upsert_cliente_existente(self, client: AsyncClient):
        # Criar cliente com documento válido
        await create_test_cliente(client, documento=CNPJ_VALIDO)
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_BASICO),
            headers=AUTH,
        )
        data = resp.json()
        assert data["clientes_existentes"] >= 1
        assert data["importadas"] == 2

    async def test_deduplicacao_numero_nf(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_DEDUP),
            headers=AUTH,
        )
        data = resp.json()
        assert data["importadas"] == 1
        assert data["ignoradas"] == 1


class TestImportCSVAuth:
    async def test_requer_autenticacao(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/import/csv",
            files=_csv_file(CSV_BASICO),
        )
        assert resp.status_code == 401
