<p align="center">
  <img src="img/logo.svg" alt="UUBA Tech" width="80" height="80">
</p>

<h1 align="center">UUBA Tech</h1>

<p align="center">
  <strong>Gestao financeira e operacional para empresas brasileiras</strong>
</p>

<p align="center">
  <a href="https://github.com/luisbarcia/uuba-tech/actions/workflows/ci.yml"><img src="https://github.com/luisbarcia/uuba-tech/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/python-3.13-blue" alt="Python 3.13">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688" alt="FastAPI">
  <img src="https://img.shields.io/badge/license-proprietary-red" alt="License">
</p>

<p align="center">
  <a href="https://uuba.tech">Site</a> &bull;
  <a href="https://developers.uuba.tech">API Docs</a> &bull;
  <a href="https://luisbarcia.github.io/uuba-tech/">Portal Interno</a>
</p>

---

## O que e a UUBA Tech

Plataforma que combina automacao, inteligencia artificial e profissionais especializados para entregar a operacao financeira completa que PMEs brasileiras precisam. Da cobranca inteligente via WhatsApp ao painel de gestao executiva.

## Produtos

| Produto | O que faz |
|---------|-----------|
| **UUBA Nexo** | Centraliza dados de CRM, ERP e bancos em uma unica base de dados |
| **UUBA Financeiro** | DRE, fluxo de caixa e projecoes automatizadas + BPO financeiro |
| **UUBA Recebe** | Cobranca multicanal automatizada (WhatsApp, e-mail, SMS) com IA |
| **UUBA 360** | Dashboards e KPIs em tempo real por nivel de acesso |
| **UUBA para Parceiros** | Plataforma white-label para revenda sob marca propria |

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
       ├── Claude Sonnet 4 (IA)
       |   Agente conversacional
       |   com protocolo comportamental
       |
       v
Uuba API (api.uuba.tech)
       |
       v
PostgreSQL 16 (pgvector) + Redis 7
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
| Cache | Redis 7 (debounce + sessoes) | - |
| Infra | Docker Compose + nginx + Let's Encrypt | VPS Contabo |

## API

14 endpoints REST para gestao de clientes, faturas e cobrancas.

```bash
# Health check
curl https://api.uuba.tech/health

# Listar clientes (requer API key)
curl -H "X-API-Key: SUA_KEY" https://api.uuba.tech/api/v1/clientes
```

Documentacao interativa: [developers.uuba.tech](https://developers.uuba.tech)

## Bot WhatsApp (UUBA Recebe)

Agente conversacional que cobra clientes automaticamente via WhatsApp usando tecnicas de cobranca comportamental:

- **Tecnicas**: reciprocidade, prova social, compromisso, aversao a perda
- **Escalacao**: transfere para humano quando necessario (via Chatwoot)
- **Memoria**: ultimas 10 mensagens por cliente
- **Tools**: buscar faturas, metricas do cliente, registrar promessa, registrar cobranca
- **Seguranca**: prompt v2 hardened contra injection, manipulacao e vazamento de dados

## Qualidade

- **174 testes** automatizados (unit + integration + security + data integrity)
- **CI/CD** com GitHub Actions: lint (ruff) → test (pytest + PostgreSQL) → docker build
- **Cobertura de seguranca**: auth bypass, SQL injection, XSS, mass assignment, encoding
- **Python 3.13** + tipagem estrita com Pydantic v2

## Estrutura

```
uuba-tech/
├── uuba-tech-api/              # API REST (FastAPI)
│   ├── app/
│   │   ├── routers/            # Endpoints (clientes, faturas, cobrancas, admin)
│   │   ├── services/           # Logica de negocio
│   │   ├── models/             # SQLAlchemy ORM
│   │   ├── schemas/            # Pydantic v2 (validacao + OpenAPI)
│   │   ├── auth/               # Autenticacao por API key
│   │   └── utils/              # IDs (nanoid), money
│   ├── tests/                  # 174 testes
│   ├── alembic/                # Migrations
│   ├── Dockerfile.prod         # Imagem de producao
│   └── docker-compose.yml      # Stack local
├── docs/                       # Portal interno (GitHub Pages)
│   ├── infra/                  # Documentacao de infraestrutura
│   ├── prompts/                # Backup versionado dos prompts do bot
│   ├── relatorios/             # Relatorios semanais
│   ├── propostas/              # Propostas de features
│   ├── guia/                   # Guia de replicacao da infra (19 secoes)
│   ├── produtos/               # Catalogo de produtos
│   └── equity/                 # Documentos de alinhamento societario
├── produtos/                   # Paginas individuais dos 5 produtos
├── css/ js/ img/               # Assets do site institucional
├── .github/workflows/ci.yml    # Pipeline CI/CD
└── index.html                  # Landing page (uuba.tech)
```

## Desenvolvimento

```bash
# Clonar
git clone git@github.com:luisbarcia/uuba-tech.git
cd uuba-tech/uuba-tech-api

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Rodar testes
pytest tests/ -v

# Lint
ruff check app/ tests/
ruff format app/ tests/

# Rodar API localmente
uvicorn app.main:app --reload
```

## Deploy

A API roda em Docker na VPS Contabo com nginx como reverse proxy e certificados Let's Encrypt.

```bash
# Build da imagem de producao
docker build -f Dockerfile.prod -t uuba-api .

# Deploy via docker-compose
docker compose up -d
```

## Links

| Recurso | URL |
|---------|-----|
| Site institucional | [uuba.tech](https://uuba.tech) |
| API (producao) | [api.uuba.tech](https://api.uuba.tech) |
| Docs da API | [developers.uuba.tech](https://developers.uuba.tech) |
| Portal interno | [luisbarcia.github.io/uuba-tech](https://luisbarcia.github.io/uuba-tech/) |
| WhatsApp Gateway | [wa.uuba.tech](https://wa.uuba.tech) |
| Atendimento | [chat.uuba.tech](https://chat.uuba.tech) |

## Licenca

Proprietario. Todos os direitos reservados. (c) 2026 UUBA Tech.
