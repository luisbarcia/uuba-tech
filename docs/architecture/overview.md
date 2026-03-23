# UUBA Tech — Arquitetura da Plataforma

> Documento de arquitetura | 2026-03-22
> Padrao: Modular Monolith com evolucao para services

---

## 1. Contexto

A UUBA Tech e uma plataforma de gestao financeira para PMEs com 5 produtos:

| Produto | Funcao | Status |
|---------|--------|--------|
| **Recebe** | Cobranca automatizada com IA | Em desenvolvimento (API + bot funcional) |
| **Nexo** | Infraestrutura de dados (ETL/integracoes) | Planejado |
| **360** | Dashboards por perfil | Planejado |
| **Financeiro** | Depto financeiro automatizado | Planejado |
| **Parceiros** | White-label para revendedores | Planejado |

**Restricoes:**
- Equipe: 1 dev (CTO) + IA
- Infra: VPS Contabo (4 vCPU, 8GB RAM, 200GB SSD) — ~R$60/mes
- Stack atual: FastAPI + PostgreSQL + n8n + Docker
- Precisa suportar multi-tenancy (100 tenants)
- Precisa de bot WhatsApp com IA conversacional

---

## 2. Decisao Arquitetural: Modular Monolith

Ver ADR-001 para detalhes completos.

**Resumo:** Um unico deployable com modulos isolados por fronteiras de dominio. Cada produto e um modulo. Modulos comunicam via eventos internos, nunca importam diretamente uns dos outros.

**Por que nao microservices:** 1 dev nao consegue operar N deploys, service mesh, distributed tracing. O overhead operacional mata a produtividade.

**Por que nao monolito puro:** 5 produtos que evoluem em ritmos diferentes. Sem fronteiras, vira bola de lama em 6 meses.

---

## 3. Estrutura do Projeto

```
uuba-platform/
|
|-- gateway/                     # Ponto de entrada unico
|   |-- main.py                  # FastAPI app, monta todos os routers
|   |-- middleware/
|   |   |-- tenant.py            # Identifica tenant via API key + cache Redis
|   |   |-- auth.py              # Verifica API key, JWT, RBAC
|   |   |-- rate_limit.py        # Rate limiting diferenciado por operacao
|   |   |-- logging.py           # Correlation ID, structured logging
|   |   `-- error_handler.py     # Error handling centralizado
|   `-- health.py                # GET /health com status de cada servico
|
|-- modules/
|   |-- recebe/                  # UUBA Recebe
|   |   |-- routers/             # Endpoints REST
|   |   |-- models/              # SQLAlchemy models (com tenant_id)
|   |   |-- schemas/             # Pydantic schemas
|   |   |-- services/            # Logica de negocio
|   |   |-- workers/             # Background jobs (regua, import, scoring)
|   |   `-- events.py            # Eventos emitidos/consumidos
|   |
|   |-- nexo/                    # UUBA Nexo (futuro)
|   |   |-- connectors/          # Adapters para ERPs (Conta Azul, Omie...)
|   |   |-- sync/                # Engine de sincronizacao
|   |   `-- ...
|   |
|   |-- trezentos_sessenta/      # UUBA 360 (futuro)
|   |-- financeiro/              # UUBA Financeiro (futuro)
|   `-- parceiros/               # UUBA Parceiros (futuro)
|
|-- shared/                      # Infraestrutura compartilhada (NAO logica de negocio)
|   |-- tenancy/
|   |   |-- context.py           # TenantContext — injetado em cada request
|   |   |-- filters.py           # Auto-apply WHERE tenant_id = :id
|   |   `-- provisioning.py      # Criar tenant (DB setup, API key, config)
|   |
|   |-- events/
|   |   |-- bus.py               # EventBus (PostgreSQL LISTEN/NOTIFY)
|   |   |-- types.py             # Enum de eventos (fatura_paga, acordo_fechado...)
|   |   `-- handlers.py          # Registry de handlers por evento
|   |
|   |-- notifications/
|   |   |-- whatsapp.py          # Enviar via Evolution API / Meta Cloud
|   |   |-- email.py             # Enviar via SMTP
|   |   `-- sms.py               # Futuro
|   |
|   |-- payments/
|   |   |-- conta_azul.py        # Gateway Conta Azul
|   |   `-- base.py              # Interface de gateway (futuro: Pix direto, Stripe)
|   |
|   |-- compliance/
|   |   |-- hours.py             # Horarios de contato (seg-sex 8-20, sab 8-14)
|   |   |-- frequency.py         # Rate limiter por devedor
|   |   |-- holidays.py          # Calendario de feriados nacionais
|   |   `-- lgpd.py              # Consentimento, opt-out, anonimizacao
|   |
|   |-- audit/
|   |   `-- trail.py             # Registrar toda interacao com devedor
|   |
|   `-- ai/
|       |-- agent.py             # Interface com Claude API
|       `-- prompt_templates.py  # Templates de prompts versionados
|
|-- workers/                     # Background jobs (Celery ou ARQ)
|   |-- regua_runner.py          # Cron: executa passos da regua
|   |-- vencimento_checker.py    # Cron: transiciona faturas para vencido
|   |-- import_processor.py      # Async: processa CSV/Excel
|   |-- scoring_pipeline.py      # Cron: recalcula scores diariamente
|   |-- webhook_processor.py     # Async: processa webhooks de pagamento
|   `-- promessa_checker.py      # Cron: verifica promessas expiradas
|
|-- tests/
|   |-- unit/
|   |-- integration/
|   `-- e2e/
|
|-- alembic/                     # Migrations
|   `-- versions/
|
|-- infra/
|   |-- docker-compose.yml       # PostgreSQL, Redis, app, workers, n8n
|   |-- docker-compose.prod.yml  # Override para producao
|   |-- Dockerfile               # Multi-stage build
|   |-- nginx/
|   |   `-- default.conf         # Reverse proxy + SSL
|   `-- scripts/
|       |-- deploy.sh            # Deploy na VPS
|       `-- backup.sh            # Backup diario do DB
|
`-- docs/
    |-- architecture/            # Este documento + ADRs
    `-- specs/                   # Specs de produto (ja existem)
```

---

## 4. Diagrama de Arquitetura

```
                    ┌─────────────────────────────────┐
                    |        Clientes / Devedores       |
                    |   (WhatsApp, Portal, Dashboard)   |
                    └──────────┬──────────┬────────────┘
                               |          |
                    ┌──────────▼──┐  ┌────▼─────────────┐
                    | Evolution   |  |    Nginx           |
                    | API         |  |    (reverse proxy   |
                    | wa.uuba.tech|  |     SSL + cache)    |
                    └──────┬──────┘  └────────┬──────────┘
                           |                  |
                    ┌──────▼──────┐  ┌────────▼──────────┐
                    |    n8n      |  |     FastAPI         |
                    |  - Webhooks |  |     (gateway/)      |
                    |  - Bot IA   |◄►|                     |
                    |  - Regua    |  |  ┌───────────────┐  |
                    |  - Workflows|  |  | modules/      |  |
                    └──────┬──────┘  |  |  recebe/      |  |
                           |         |  |  nexo/        |  |
                    ┌──────▼──────┐  |  |  360/         |  |
                    | Claude API  |  |  |  financeiro/  |  |
                    | (Anthropic) |  |  |  parceiros/   |  |
                    └─────────────┘  |  └───────────────┘  |
                                     |                     |
                                     |  ┌───────────────┐  |
                                     |  | shared/       |  |
                                     |  |  tenancy/     |  |
                                     |  |  events/      |  |
                                     |  |  payments/    |  |
                                     |  |  compliance/  |  |
                                     |  |  audit/       |  |
                                     |  └───────────────┘  |
                                     └──────────┬──────────┘
                                                |
                         ┌──────────────────────┼──────────────────────┐
                         |                      |                      |
                  ┌──────▼──────┐     ┌─────────▼──────┐    ┌─────────▼──────┐
                  | PostgreSQL  |     |     Redis       |    |    Workers      |
                  |             |     |   - Cache       |    |   - regua       |
                  | - uuba_db   |     |   - Rate limit  |    |   - import      |
                  | - tenant_id |     |   - Filas       |    |   - scoring     |
                  | - audit     |     |   - Sessions    |    |   - webhooks    |
                  └─────────────┘     └────────────────┘    |   - promessas   |
                                                            └────────────────┘
                  ┌─────────────┐     ┌────────────────┐
                  | Conta Azul  |     | Chatwoot        |
                  | (pagamento) |     | chat.uuba.tech  |
                  └─────────────┘     └────────────────┘
```

---

## 5. Regras do Modular Monolith

| # | Regra | Consequencia |
|---|-------|-------------|
| 1 | Modulos NUNCA importam diretamente de outros modulos | `from modules.recebe import ...` dentro de `modules.nexo` e proibido |
| 2 | Comunicacao entre modulos via EventBus | `recebe` emite `fatura_paga`, `financeiro` consome e atualiza DRE |
| 3 | Cada modulo tem seus proprios models/schemas | Sem acoplamento de dados entre modulos |
| 4 | `shared/` e para INFRA, nao para negocio | Auth, notifications, audit = shared. Regua, scoring = modulo |
| 5 | Um modulo pode ser DESLIGADO sem quebrar outros | Feature flags por modulo |
| 6 | Tudo com tenant_id | Nenhuma query sem filtro de tenant (enforced pelo middleware) |

### Comunicacao via Eventos

```python
# modules/recebe/services/fatura_service.py
from shared.events.bus import event_bus
from shared.events.types import EventType

async def confirmar_pagamento(fatura_id: str):
    fatura = await update_status(fatura_id, "pago")
    await event_bus.emit(EventType.FATURA_PAGA, {
        "tenant_id": fatura.tenant_id,
        "fatura_id": fatura.id,
        "valor": fatura.valor,
        "pago_em": fatura.pago_em,
    })
```

```python
# modules/financeiro/events.py (futuro)
from shared.events.bus import event_bus
from shared.events.types import EventType

@event_bus.on(EventType.FATURA_PAGA)
async def atualizar_dre(payload: dict):
    # Atualiza DRE com o recebimento
    await dre_service.registrar_receita(
        tenant_id=payload["tenant_id"],
        valor=payload["valor"],
        data=payload["pago_em"],
    )
```

---

## 6. Camada de Dominio (DDD Tactical Patterns)

Ver ADR-006 para detalhes completos.

Cada modulo possui uma camada de dominio (`domain/`) com Value Objects, Aggregates, Repositories e Domain Events. Essa camada encapsula regras de negocio e e independente de framework (nao depende de FastAPI, SQLAlchemy ou Pydantic).

### Estrutura atual (modulo Recebe)

```
app/domain/
  value_objects/
    fatura_status.py       # Enum com maquina de estados embutida
    cobranca_enums.py      # Tipo, Canal, Tom, Status tipados
    documento.py           # CPF/CNPJ imutavel com validacao de digitos
    money.py               # Centavos + moeda, aritmetica segura
  aggregates/              # (planejado) Fatura como aggregate root
  repositories/            # (planejado) Protocol + implementacoes SQLAlchemy
  events/                  # (planejado) Domain Events para EventBus
```

### Exemplo: transicao de status

Antes (dict solto no service):
```python
FATURA_TRANSITIONS = {"pendente": ["pago", "vencido", "cancelado"], ...}
if new_status not in FATURA_TRANSITIONS.get(fatura.status, []):
    raise APIError(409, ...)
```

Depois (Value Object com logica embutida):
```python
from app.domain.value_objects.fatura_status import FaturaStatus

current = FaturaStatus(fatura.status)
novo = FaturaStatus(new_status)
if not current.pode_transicionar_para(novo):
    raise APIError(409, ...)
```

### Exemplo: validacao de documento

```python
from app.domain.value_objects.documento import Documento

doc = Documento("529.982.247-25")  # aceita com pontuacao
doc.valor       # "52998224725" (so digitos)
doc.tipo        # "cpf"
doc.formatado   # "529.982.247-25"
Documento("00000000000")  # ValueError: CPF invalido
```

### Exemplo: operacoes monetarias

```python
from app.domain.value_objects.money import Money

total = Money(250000)                    # R$ 2.500,00
parcela = Money(50000)                   # R$ 500,00
restante = total - parcela               # Money(200000, "BRL")
restante.formatado                       # "R$ 2.000,00"
Money(100, "BRL") + Money(100, "USD")    # ValueError: moedas diferentes
```

---

## 7. Multi-tenancy

Ver ADR-002 para detalhes completos.

### Estrategia: Shared DB + tenant_id

```python
# shared/tenancy/context.py
from contextvars import ContextVar

_tenant_id: ContextVar[str] = ContextVar("tenant_id")

def get_tenant_id() -> str:
    return _tenant_id.get()

def set_tenant_id(tenant_id: str):
    _tenant_id.set(tenant_id)
```

```python
# shared/tenancy/filters.py
from sqlalchemy import event
from shared.tenancy.context import get_tenant_id

@event.listens_for(Session, "do_orm_execute")
def apply_tenant_filter(orm_execute_state):
    """Aplica WHERE tenant_id = :id em TODA query automaticamente."""
    if orm_execute_state.is_select:
        orm_execute_state.statement = orm_execute_state.statement.filter_by(
            tenant_id=get_tenant_id()
        )
```

```python
# gateway/middleware/tenant.py
import redis.asyncio as redis

async def tenant_middleware(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    tenant_id = await redis_client.get(f"apikey:{api_key}")
    if not tenant_id:
        tenant_id = await db_lookup_tenant(api_key)
        await redis_client.set(f"apikey:{api_key}", tenant_id, ex=3600)
    set_tenant_id(tenant_id)
    return await call_next(request)
```

### Caminho Evolutivo

| Estagio | Quando | Estrategia | Complexidade |
|---------|--------|------------|-------------|
| v1 | Agora (0-10 tenants) | Shared DB + tenant_id | Baixa |
| v2 | 10-50 tenants | Schema-per-tenant | Media |
| v3 | 50+ tenants | DB-per-tenant + PgBouncer | Alta |

A mudanca de v1 para v2/v3 afeta apenas `shared/tenancy/` — os modulos nao sabem e nao se importam com a estrategia de isolamento.

---

## 8. Workers e Background Jobs

| Worker | Trigger | Frequencia | Modulo |
|--------|---------|------------|--------|
| `regua_runner` | Cron | A cada 1h (dentro de horario comercial) | Recebe |
| `vencimento_checker` | Cron | Diario 00:05 UTC | Recebe |
| `promessa_checker` | Cron | Diario 08:00 BRT | Recebe |
| `scoring_pipeline` | Cron | Diario 03:00 BRT (off-peak) | Recebe |
| `import_processor` | Fila Redis | On-demand (quando upload chega) | Recebe |
| `webhook_processor` | Fila Redis | On-demand (quando webhook chega) | Recebe |

**Framework:** ARQ (async Redis queue) — leve, nativo async, compativel com FastAPI.

---

## 9. Stack Tecnologico

| Camada | Tecnologia | Justificativa |
|--------|------------|--------------|
| API | FastAPI 0.115+ | Async nativo, tipagem, OpenAPI auto, performance |
| ORM | SQLAlchemy 2.0 async | Maturidade, async support, migration (Alembic) |
| DB | PostgreSQL 16 | ACID, JSONB, LISTEN/NOTIFY, full-text search |
| Cache/Fila | Redis 7 | Cache de tenant, rate limiting, filas de workers |
| Workers | ARQ | Async, Redis-backed, leve |
| Bot/Workflows | n8n (self-hosted) | Visual, webhook handling, Claude AI nodes |
| IA | Claude Sonnet (Anthropic API) | Melhor custo-beneficio para conversacao |
| WhatsApp | Evolution API v2.3.7 | Self-hosted, custo zero de mensagens (v1) |
| Atendimento | Chatwoot (self-hosted) | Escalacao humana, chat integrado |
| Pagamento | Conta Azul API | Gateway do cliente (Pix + boleto) |
| Proxy | Nginx | Reverse proxy, SSL, rate limiting, cache |
| Container | Docker + Docker Compose | Deploy reprodutivel, isolamento |
| CI/CD | GitHub Actions | Integrado ao repo, automacao de testes e deploy |

---

## 10. Fluxo de Dados Principal (Cobranca)

```
1. Empresa importa CSV
   └─► Import processor cria clientes + faturas (tenant_id aplicado)

2. Cron vencimento_checker
   └─► Faturas pendente → vencido (diario)

3. Cron regua_runner (a cada 1h)
   └─► Verifica faturas vencidas sem cobranca recente
   └─► Verifica compliance (horario, frequencia, feriados)
   └─► Envia mensagem via Evolution API / n8n
   └─► Registra cobranca no DB

4. Devedor responde WhatsApp
   └─► Evolution API → webhook → n8n
   └─► n8n identifica tenant + devedor
   └─► Claude Sonnet processa (tools: faturas, metricas, promessa, cobranca)
   └─► Bot responde via Evolution API
   └─► Se escalacao: encaminha para Chatwoot com resumo

5. Devedor paga
   └─► Conta Azul envia webhook payment.confirmed
   └─► webhook_processor valida HMAC, atualiza fatura
   └─► EventBus emite FATURA_PAGA
   └─► Regua pausada para essa fatura
   └─► Bot envia agradecimento via WhatsApp
```

---

## 11. Seguranca

| Camada | Mecanismo |
|--------|-----------|
| Transporte | TLS 1.3 (Nginx + Let's Encrypt) |
| Autenticacao API | API key por tenant (header X-API-Key) |
| Autenticacao Portal | JWT RS256 (72h, com revogacao) |
| Autorizacao | RBAC (admin, operador, viewer) |
| Webhook | HMAC-SHA256 (Conta Azul, ERPs) |
| Rate Limiting | Redis-backed (300/min leitura, 60/min escrita) |
| Dados em repouso | Full-disk encryption (v1), column-level (v2) |
| Logs | Mascaramento de CPF, valores, telefone |
| Headers | HSTS, CSP, X-Content-Type-Options, X-Frame-Options |

---

## 12. Deploy

### Pipeline (GitHub Actions)

```
push to main → lint + type check → tests → build image → deploy to VPS
```

### Deploy na VPS

```bash
# Via SSH
ssh deploy@vps.uuba.tech
cd /opt/stack
docker compose pull uuba-api
docker compose up -d uuba-api
docker compose logs -f uuba-api --tail=50
```

### Docker Compose (simplificado)

```yaml
services:
  uuba-api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [postgres, redis]

  uuba-workers:
    build: .
    command: arq workers.main.WorkerSettings
    env_file: .env
    depends_on: [postgres, redis]

  postgres:
    image: postgres:16-alpine
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes: [./nginx:/etc/nginx/conf.d, certs:/etc/letsencrypt]

  n8n:
    image: n8nio/n8n
    ports: ["5678:5678"]

  chatwoot:
    # Ja rodando em chat.uuba.tech

volumes:
  pgdata:
  certs:
```

---

## 13. Monitoramento

| O que | Como | Alerta |
|-------|------|--------|
| API up | Health check externo (UptimeRobot) | Downtime > 1min |
| Latencia | Prometheus + Grafana | p95 > 500ms |
| Erros | Logs JSON + Grafana Loki | Taxa de erro > 1% |
| Workers | Metricas ARQ no Redis | Job falhando 3x consecutivas |
| DB | pg_stat_statements | Query > 1s |
| Redis | redis-cli info | Memoria > 80% |
| Disco VPS | df -h via cron | Uso > 85% |
| WhatsApp | Status Evolution API | Desconexao > 5min |
| Circuit breakers | Metricas internas | Qualquer breaker aberto |

---

## 14. Caminho Evolutivo

```
AGORA (1 dev, 1 VPS)           6 MESES (2-3 devs)          12+ MESES (time)
────────────────────           ─────────────────            ────────────────
Modular Monolith               + Schema-per-tenant          + DB-per-tenant
Shared DB + tenant_id          + Workers separados          + Extrair Nexo
Docker Compose                 + Redis gerenciado           + Kubernetes/Nomad
1 VPS Contabo                  + 2a VPS ou cloud            + Cloud auto-scale
n8n para orquestracao          + Dashboard React             + Voicebot
ARQ workers                    + Scoring baseline           + ML pipeline
Evolution API                  + Portal do devedor          + Meta Cloud API
                               + Monitoring completo        + A/B testing
```

---

## ADRs

| ADR | Decisao | Status |
|-----|---------|--------|
| [ADR-001](adr/0001-modular-monolith.md) | Adotar Modular Monolith | Accepted |
| [ADR-002](adr/0002-multi-tenancy-shared-db.md) | Multi-tenancy com shared DB + tenant_id | Accepted |
| [ADR-003](adr/0003-arq-workers.md) | ARQ para background jobs | Accepted |
| [ADR-004](adr/0004-event-bus-pg-notify.md) | EventBus via PostgreSQL LISTEN/NOTIFY | Accepted |
| [ADR-005](adr/0005-evolution-api-v1.md) | Evolution API para WhatsApp (v1) | Accepted |

---

*Documento de arquitetura gerado em 2026-03-22*
*Padrao: Modular Monolith — pragmatico para 1 dev, preparado para escala*
