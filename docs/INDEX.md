# UUBA Tech — Repository Index

> Mapa de navegacao do repositorio. Cada item linka para sua fonte unica.
> Atualizado: 2026-03-28 | 112 commits | 566 testes | 58 arquivos Python | ~8s

---

## Plataforma

| Documento | Escopo |
|-----------|--------|
| [CATALOG.md](CATALOG.md) | Catalogo dos 5 produtos (Recebe, Nexo, 360, Financeiro, Parceiros) |
| [roadmap/q2-2026.md](roadmap/q2-2026.md) | Roadmap Q2 2026 — Solidificar → F0 Piloto → F1 Monetizar |

---

## Documentacao Tecnica

| Documento | Escopo |
|-----------|--------|
| [README.md](../README.md) | Quick start, visao geral, desenvolvimento local |
| [API-REFERENCE.md](api/API-REFERENCE.md) | Endpoints, schemas, auth, erros, env vars |
| [INTERNALS.md](INTERNALS.md) | Models, domain (DDD), services, infra, middleware, deploy |
| [architecture/overview.md](architecture/overview.md) | Arquitetura, ADRs, stack, diagramas, evolucao |

---

## Estrutura do Repositorio

```
uuba-tech/
├── uuba-tech-api/              # Backend (FastAPI)
│   ├── app/                    # 58 arquivos Python, ~5.600 LOC
│   │   ├── auth/               # → API-REFERENCE.md#autenticacao
│   │   ├── domain/             # → INTERNALS.md#3-domain-layer
│   │   ├── infrastructure/     # → INTERNALS.md#4-repository-pattern
│   │   ├── middleware/         # → INTERNALS.md#7-middleware
│   │   ├── models/             # → INTERNALS.md#2-models
│   │   ├── routers/            # → API-REFERENCE.md#endpoints
│   │   ├── schemas/            # → API-REFERENCE.md#schemas-de-referencia
│   │   ├── services/           # → INTERNALS.md#5-services-layer
│   │   └── utils/              # → INTERNALS.md#11-ids-e-utilitarios
│   ├── alembic/                # → INTERNALS.md#9-migrations
│   ├── deploy/                 # → INTERNALS.md#10-deploy
│   └── tests/                  # 40 arquivos, 566 testes, ~7.200 LOC
├── docs/
│   ├── architecture/           # 7 ADRs + overview
│   ├── api/                    # API reference + openapi.json
│   ├── lgpd/                   # Aviso de privacidade + bases legais
│   ├── pitch/                  # Pesquisas + roteiros + pitches
│   ├── planos/                 # Bot cobranca MVP (historico) + migracao WhatsApp
│   ├── prompts/                # System prompts versionados (bot v1/v2)
│   └── relatorios/             # Relatorios semanais
├── specs/
│   ├── uuba-recebe/            # Spec completa (11 modulos, 98 FRs) + TODO
│   ├── uuba-nexo/              # Spec estrategica (hub de dados)
│   ├── uuba-360/               # Spec estrategica (dashboards por perfil)
│   ├── uuba-financeiro/        # Spec estrategica (depto financeiro)
│   ├── uuba-parceiros/         # Spec estrategica (white-label B2B2B)
│   └── deprecated/             # v1 spec + parts (DEPRECATED/REDUNDANTE)
├── .github/workflows/ci.yml    # CI: lint → test (PG 16) → docker build
└── index.html                  # Landing page uuba.tech
```

---

## Routers → Arquivos

| Prefixo | Router | Arquivo |
|---------|--------|---------|
| `/health` | Health | `main.py` |
| `/api/v1/clientes` | Clientes + LGPD | `routers/clientes.py` |
| `/api/v1/faturas` | Faturas | `routers/faturas.py` |
| `/api/v1/cobrancas` | Cobrancas | `routers/cobrancas.py` |
| `/api/v1/tenants` | Tenants | `routers/tenants.py` |
| `/api/v1/metricas` | Metricas | `routers/metricas.py` |
| `/api/v1/admin` | Admin | `routers/admin.py` |
| `/api/v1/import` | CSV Import | `routers/import_csv.py` |
| `/api/v1/jobs` | Jobs batch | `routers/jobs.py` |
| `/api/v1/privacidade` | LGPD status | `routers/privacidade.py` |

Para request/response completos: [API-REFERENCE.md](api/API-REFERENCE.md)

---

## Testes

| Categoria | Arquivos | Testes | Descricao |
|-----------|----------|--------|-----------|
| CRUD | test_clientes, faturas, cobrancas, tenants | ~80 | Endpoints REST |
| LGPD | test_anonimizar_post, lgpd_*, exportar | ~25 | Compliance Art. 18 |
| Auth | test_auth, auth_unkey | ~15 | API key + Unkey |
| Security | test_attack_* | ~66 | Injection, mass assignment, auth bypass |
| IDOR | test_idor_cross_tenant | 10 | Acesso cross-tenant por ID direto |
| Multi-tenant | test_multi_tenant_isolation, tenant_filter | ~12 | Isolamento |
| Domain | test_value_objects, aggregate_*, domain_events | ~60 | DDD |
| Bug regression | test_bugs_critical, bug_hunt, bug_hunt_full | 65 | Bugs encontrados e corrigidos |
| Infra | test_health, ids, schemas, data_integrity | ~30 | Utilitarios |
| Compliance | test_compliance* | ~40 | Edge cases de regras |
| Import | test_import_csv | ~20 | CSV parsing |
| Load | tests/load/ | scripts | k6 stress + locust |

Total: **566 testes** em **40 arquivos** (~8s)

---

## Specs por Produto

| Produto | Spec | Status |
|---------|------|--------|
| **Recebe** | [specs/uuba-recebe/](../specs/uuba-recebe/) (10 modulos) | Em desenvolvimento |
| **Nexo** | [specs/uuba-nexo/](../specs/uuba-nexo/) | Planejado |
| **360** | [specs/uuba-360/](../specs/uuba-360/) | Planejado |
| **Financeiro** | [specs/uuba-financeiro/](../specs/uuba-financeiro/) | Planejado |
| **Parceiros** | [specs/uuba-parceiros/](../specs/uuba-parceiros/) | Planejado |

Modulos Recebe: M00-M10 — status detalhado em [implementation-todo](../specs/uuba-recebe/10-implementation-todo.md)

---

## Ferramentas Externas

| Ferramenta | Uso | Status |
|------------|-----|--------|
| **Unkey** | API key management | Integrado |
| **uuba-ctl** | CLI TypeScript (repo separado) | Em dev |
| **n8n** | Workflows, bot WhatsApp | 2 instancias |
| **Conta Azul** | Pagamentos | Planejado |
| **Chatwoot** | Atendimento (chat.uuba.tech) | Configurado |
| **Evolution API** | WhatsApp gateway | Em uso |

---

## Issues Conhecidas

Revisao: 2026-03-27 | Prioridades em [task_plan.md](../task_plan.md)

### Corrigidos nesta sessao

| Sev. | Issue | Fix |
|------|-------|-----|
| ~~CRITICAL~~ | ~~Metricas vazava cross-tenant~~ | Usa request.state.tenant_id |
| ~~HIGH~~ | ~~Slug duplicado → 500~~ | IntegrityError → 409 |
| ~~MEDIUM~~ | ~~DSO negativo (-249 dias)~~ | max(0, dias) em 3 locais |

### Pendentes

| Sev. | Issue | Local |
|------|-------|-------|
| HIGH | Tenants CRUD sem permissao admin (RBAC) | `routers/tenants.py` |
| HIGH | Cache auth sem TTL (key revogada fica valida) | `auth/api_key.py` |
| HIGH | limit=10000 em export/metricas | `services/cliente_service.py` |
| MEDIUM | tenant_id nullable sem data migration | `alembic/versions/002` |
| MEDIUM | audit_service nao seta tenant_id | `services/audit_service.py` |
| LOW | Feriados hardcoded 2026 | `services/compliance.py` |
| LOW | CSV nao suporta milhar "2.500,00" | `services/import_service.py` |
| LOW | cleanup_service atua em todos tenants | `services/cleanup_service.py` |
