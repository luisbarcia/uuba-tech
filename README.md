# UUBA Tech

Plataforma de cobranca inteligente para PMEs brasileiras. Combina automacao via WhatsApp, inteligencia artificial e atendimento humano para recuperar creditos de forma eficiente e empática.

## Arquitetura

```
Cliente (WhatsApp)
       |
       v
Evolution API (wa.uuba.tech) ──── Chatwoot (chat.uuba.tech)
       |                            Atendimento humano
       v
n8n (orquestrador)
       |
       ├── Claude Sonnet (IA)
       |   Agente conversacional
       |   com protocolo comportamental
       |
       v
Uuba API (api.uuba.tech)
       |
       v
PostgreSQL (pgvector)
```

## Stack

| Componente | Tecnologia | URL |
|-----------|-----------|-----|
| API REST | FastAPI + SQLAlchemy 2.0 async | [api.uuba.tech](https://api.uuba.tech) |
| Docs API | OpenAPI 3.1 + Scalar | [developers.uuba.tech](https://developers.uuba.tech) |
| WhatsApp | Evolution API v2.3.7 | [wa.uuba.tech](https://wa.uuba.tech) |
| Atendimento | Chatwoot | [chat.uuba.tech](https://chat.uuba.tech) |
| Automacao | n8n (self-hosted) | - |
| IA | Claude Sonnet 4 (Anthropic) | - |
| Database | PostgreSQL 16 + pgvector | - |
| Cache | Redis 7 | - |
| Infra | Docker Compose + nginx + Let's Encrypt | VPS Contabo |

## API

14 endpoints REST para gestao de clientes, faturas e cobrancas.

```bash
# Health check
curl https://api.uuba.tech/health

# Listar clientes (requer API key)
curl -H "X-API-Key: SUA_KEY" https://api.uuba.tech/api/v1/clientes
```

Documentacao completa: [developers.uuba.tech](https://developers.uuba.tech)

## Bot WhatsApp

Agente conversacional que cobra clientes automaticamente via WhatsApp usando tecnicas de cobranca comportamental:

- Reciprocidade, prova social, compromisso, aversao a perda
- Escala para humano quando necessario (via Chatwoot)
- Memoria por cliente (ultimas 10 mensagens)
- 4 tools: buscar faturas, metricas, registrar promessa, registrar cobranca

## Qualidade

- 174 testes automatizados (unit + integration + security + data integrity)
- CI/CD com GitHub Actions (lint + test + docker build)
- Cobertura: auth bypass, SQL injection, XSS, mass assignment, encoding
- Prompt v2 hardened contra injection, manipulacao e vazamento de dados

## Estrutura do Repositorio

```
uuba-tech/
├── uuba-tech-api/          # API REST (FastAPI)
│   ├── app/
│   │   ├── routers/        # Endpoints (clientes, faturas, cobrancas, admin)
│   │   ├── services/       # Logica de negocio
│   │   ├── models/         # SQLAlchemy ORM
│   │   ├── schemas/        # Pydantic (validacao + OpenAPI)
│   │   └── auth/           # Autenticacao por API key
│   ├── tests/              # 174 testes
│   └── alembic/            # Migrations
├── docs/                   # Portal interno (GitHub Pages)
│   ├── infra/              # Documentacao de infraestrutura
│   ├── prompts/            # Backup versionado dos prompts do bot
│   ├── relatorios/         # Relatorios semanais
│   ├── propostas/          # Propostas de features
│   └── guia/               # Guia de replicacao da infra
├── css/ js/ img/           # Site institucional (uuba.tech)
├── produtos/               # Paginas de produtos
└── index.html              # Landing page
```

## Desenvolvimento

```bash
# Clonar
git clone git@github.com:luisbarcia/uuba-tech.git
cd uuba-tech/uuba-tech-api

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Rodar testes
pytest tests/ -q

# Rodar API localmente
uvicorn app.main:app --reload
```

## Documentacao Interna

[luisbarcia.github.io/uuba-tech](https://luisbarcia.github.io/uuba-tech/) — portal com infra, relatorios, propostas e guia de replicacao.

## Licenca

Proprietario. Todos os direitos reservados.
