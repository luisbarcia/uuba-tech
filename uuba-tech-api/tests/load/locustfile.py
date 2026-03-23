"""
Load tests para a UUBA Recebe API.

Simula fluxos realistas de uso da API:
- Smoke test (health check)
- Fluxo completo: criar cliente -> criar fatura -> listar -> atualizar status
- Batch job de transicao de faturas vencidas
- Leitura intensiva (listagens com filtros)

Executar com:
    locust -f tests/load/locustfile.py --host http://localhost:8000

Ou modo headless:
    locust -f tests/load/locustfile.py --host http://localhost:8000 \
        --headless -u 50 -r 5 --run-time 2m \
        --csv results/load_test
"""

from __future__ import annotations

import os
import random
import string
from datetime import datetime, timedelta, timezone

from locust import HttpUser, SequentialTaskSet, TaskSet, between, tag, task

# ---------------------------------------------------------------------------
# Configuracao
# ---------------------------------------------------------------------------
API_KEY = os.getenv("API_KEY", "dev-api-key-change-me")
API_HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}


# ---------------------------------------------------------------------------
# Helpers para gerar dados aleatorios
# ---------------------------------------------------------------------------
def _random_cpf() -> str:
    """Gera um CPF aleatorio (11 digitos). Nao valida digito verificador."""
    return "".join(random.choices(string.digits, k=11))


def _random_cnpj() -> str:
    """Gera um CNPJ aleatorio (14 digitos). Nao valida digito verificador."""
    return "".join(random.choices(string.digits, k=14))


def _random_documento() -> str:
    """Retorna CPF ou CNPJ aleatoriamente."""
    return random.choice([_random_cpf, _random_cnpj])()


def _random_nome() -> str:
    """Gera nome aleatorio para cliente."""
    prefixos = [
        "Maria",
        "Joao",
        "Ana",
        "Pedro",
        "Carlos",
        "Fernanda",
        "Lucas",
        "Julia",
        "Rafael",
        "Beatriz",
        "Empresa",
    ]
    sufixos = [
        "Silva",
        "Santos",
        "Oliveira",
        "Souza",
        "Ferreira",
        "Costa",
        "Almeida",
        "Ltda",
        "SA",
        "ME",
    ]
    return f"{random.choice(prefixos)} {random.choice(sufixos)} {random.randint(1, 9999)}"


def _random_telefone() -> str:
    """Gera telefone BR aleatorio."""
    ddd = random.choice(["11", "21", "31", "41", "51", "61", "71", "81"])
    return f"55{ddd}9{''.join(random.choices(string.digits, k=8))}"


def _random_email(nome: str) -> str:
    slug = nome.lower().replace(" ", ".")[:20]
    return f"{slug}+{random.randint(1, 99999)}@teste.com"


def _random_valor() -> int:
    """Valor em centavos entre R$50 e R$50.000."""
    return random.randint(5000, 5_000_000)


def _random_vencimento() -> str:
    """Data de vencimento entre -5 e +30 dias (para gerar mix de vencidas/pendentes)."""
    delta = random.randint(-5, 30)
    dt = datetime.now(tz=timezone.utc) + timedelta(days=delta)
    return dt.isoformat()


def _random_descricao() -> str:
    servicos = [
        "Consultoria mensal",
        "Licenca de software",
        "Servico de manutencao",
        "Projeto web",
        "Campanha de marketing",
        "Assessoria juridica",
        "Desenvolvimento de app",
    ]
    return random.choice(servicos)


# ---------------------------------------------------------------------------
# Smoke Test — apenas health check
# ---------------------------------------------------------------------------
class HealthCheckUser(HttpUser):
    """
    Usuario leve que so faz health check.
    Util como smoke test e baseline de latencia.
    """

    weight = 1  # Poucos usuarios desse tipo

    wait_time = between(1, 3)

    @tag("smoke", "health")
    @task
    def health(self) -> None:
        self.client.get("/health", name="/health")


# ---------------------------------------------------------------------------
# Fluxo completo: criar cliente -> criar fatura -> listar -> atualizar
# ---------------------------------------------------------------------------
class FullFlowTasks(SequentialTaskSet):
    """
    Simula o fluxo real de um operador:
    1. Cria um cliente
    2. Cria 1-3 faturas para esse cliente
    3. Lista faturas (com e sem filtro)
    4. Atualiza status de uma fatura
    5. Cria uma cobranca para a fatura
    6. Lista cobrancas
    """

    cliente_id: str | None = None
    fatura_ids: list[str] = []

    def on_start(self) -> None:
        self.cliente_id = None
        self.fatura_ids = []

    # --- Passo 1: Criar cliente ---
    @tag("write", "clientes")
    @task
    def create_cliente(self) -> None:
        nome = _random_nome()
        payload = {
            "nome": nome,
            "documento": _random_documento(),
            "email": _random_email(nome),
            "telefone": _random_telefone(),
        }
        with self.client.post(
            "/api/v1/clientes",
            json=payload,
            headers=API_HEADERS,
            name="POST /api/v1/clientes",
            catch_response=True,
        ) as resp:
            if resp.status_code == 201:
                data = resp.json()
                self.cliente_id = data["id"]
                resp.success()
            elif resp.status_code == 409:
                # Documento duplicado — ok, tentar de novo na proxima iteracao
                resp.success()
            else:
                resp.failure(f"Status {resp.status_code}: {resp.text[:200]}")

    # --- Passo 2: Criar faturas ---
    @tag("write", "faturas")
    @task
    def create_faturas(self) -> None:
        if not self.cliente_id:
            return

        num_faturas = random.randint(1, 3)
        for _ in range(num_faturas):
            payload = {
                "cliente_id": self.cliente_id,
                "valor": _random_valor(),
                "vencimento": _random_vencimento(),
                "descricao": _random_descricao(),
            }
            with self.client.post(
                "/api/v1/faturas",
                json=payload,
                headers=API_HEADERS,
                name="POST /api/v1/faturas",
                catch_response=True,
            ) as resp:
                if resp.status_code == 201:
                    data = resp.json()
                    self.fatura_ids.append(data["id"])
                    resp.success()
                else:
                    resp.failure(f"Status {resp.status_code}: {resp.text[:200]}")

    # --- Passo 3: Listar faturas (sem filtro) ---
    @tag("read", "faturas")
    @task
    def list_faturas(self) -> None:
        self.client.get(
            "/api/v1/faturas?limit=20",
            headers=API_HEADERS,
            name="GET /api/v1/faturas",
        )

    # --- Passo 4: Listar faturas com filtro de status ---
    @tag("read", "faturas")
    @task
    def list_faturas_filtered(self) -> None:
        status = random.choice(["pendente", "vencido", "pendente,vencido"])
        self.client.get(
            f"/api/v1/faturas?status={status}&limit=20",
            headers=API_HEADERS,
            name="GET /api/v1/faturas?status=<filter>",
        )

    # --- Passo 5: Listar clientes ---
    @tag("read", "clientes")
    @task
    def list_clientes(self) -> None:
        self.client.get(
            "/api/v1/clientes?limit=20",
            headers=API_HEADERS,
            name="GET /api/v1/clientes",
        )

    # --- Passo 6: Atualizar status da fatura ---
    @tag("write", "faturas")
    @task
    def update_fatura_status(self) -> None:
        if not self.fatura_ids:
            return

        fatura_id = random.choice(self.fatura_ids)
        new_status = random.choice(["pago", "cancelado"])
        payload = {"status": new_status}

        with self.client.patch(
            f"/api/v1/faturas/{fatura_id}",
            json=payload,
            headers=API_HEADERS,
            name="PATCH /api/v1/faturas/{id}",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Status {resp.status_code}: {resp.text[:200]}")

    # --- Passo 7: Criar cobranca ---
    @tag("write", "cobrancas")
    @task
    def create_cobranca(self) -> None:
        if not self.fatura_ids or not self.cliente_id:
            return

        fatura_id = random.choice(self.fatura_ids)
        payload = {
            "fatura_id": fatura_id,
            "cliente_id": self.cliente_id,
            "tipo": random.choice(["lembrete", "cobranca", "follow_up", "escalacao"]),
            "canal": random.choice(["whatsapp", "email", "sms"]),
            "tom": random.choice(["amigavel", "neutro", "firme", "urgente"]),
            "mensagem": f"Teste de carga - cobranca {random.randint(1, 99999)}",
        }
        with self.client.post(
            "/api/v1/cobrancas",
            json=payload,
            headers=API_HEADERS,
            name="POST /api/v1/cobrancas",
            catch_response=True,
        ) as resp:
            if resp.status_code == 201:
                resp.success()
            else:
                resp.failure(f"Status {resp.status_code}: {resp.text[:200]}")

    # --- Passo 8: Listar cobrancas ---
    @tag("read", "cobrancas")
    @task
    def list_cobrancas(self) -> None:
        self.client.get(
            "/api/v1/cobrancas?limit=20",
            headers=API_HEADERS,
            name="GET /api/v1/cobrancas",
        )

    # --- Fim do fluxo: reinicia ---
    @task
    def stop(self) -> None:
        """Encerra o TaskSet para que o user possa recomecar outro fluxo."""
        self.interrupt()


class FullFlowUser(HttpUser):
    """
    Usuario que executa o fluxo completo de operacao:
    criar cliente -> faturas -> cobrar -> listar.
    """

    weight = 6  # Maioria dos usuarios simulados

    wait_time = between(1, 5)
    tasks = [FullFlowTasks]


# ---------------------------------------------------------------------------
# Leitura intensiva — simula dashboards e consultas
# ---------------------------------------------------------------------------
class ReadHeavyTasks(TaskSet):
    """
    Simula usuario consultando dashboards e listagens.
    Predominantemente leitura (GET).
    """

    @tag("read", "clientes")
    @task(3)
    def list_clientes(self) -> None:
        limit = random.choice([10, 20, 50])
        offset = random.randint(0, 100)
        self.client.get(
            f"/api/v1/clientes?limit={limit}&offset={offset}",
            headers=API_HEADERS,
            name="GET /api/v1/clientes (paginado)",
        )

    @tag("read", "faturas")
    @task(5)
    def list_faturas(self) -> None:
        params: list[str] = [f"limit={random.choice([10, 20, 50])}"]
        if random.random() < 0.6:
            status = random.choice(["pendente", "vencido", "pago", "pendente,vencido"])
            params.append(f"status={status}")
        qs = "&".join(params)
        self.client.get(
            f"/api/v1/faturas?{qs}",
            headers=API_HEADERS,
            name="GET /api/v1/faturas (dashboard)",
        )

    @tag("read", "cobrancas")
    @task(2)
    def list_cobrancas(self) -> None:
        periodo = random.choice(["7d", "30d", "90d"])
        self.client.get(
            f"/api/v1/cobrancas?periodo={periodo}&limit=20",
            headers=API_HEADERS,
            name="GET /api/v1/cobrancas (periodo)",
        )

    @tag("smoke", "health")
    @task(1)
    def health(self) -> None:
        self.client.get("/health", name="/health")

    @task
    def stop(self) -> None:
        """Permite o Locust intercalar com outros tasksets se houver."""
        if random.random() < 0.1:
            self.interrupt()


class ReadHeavyUser(HttpUser):
    """
    Usuario de dashboard — predominantemente leitura.
    """

    weight = 3

    wait_time = between(0.5, 2)
    tasks = [ReadHeavyTasks]


# ---------------------------------------------------------------------------
# Batch Job — transicionar faturas vencidas
# ---------------------------------------------------------------------------
class BatchJobUser(HttpUser):
    """
    Simula o cron job que roda periodicamente para transicionar faturas vencidas.
    Executa a cada 10-30s (bem menos frequente que usuarios normais).
    """

    weight = 1  # Poucos — simula cron

    wait_time = between(10, 30)

    @tag("job", "batch")
    @task
    def transicionar_vencidas(self) -> None:
        with self.client.post(
            "/api/v1/jobs/transicionar-vencidas",
            headers=API_HEADERS,
            name="POST /api/v1/jobs/transicionar-vencidas",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    resp.success()
                else:
                    resp.failure(f"Job retornou status inesperado: {data}")
            else:
                resp.failure(f"Status {resp.status_code}: {resp.text[:200]}")
