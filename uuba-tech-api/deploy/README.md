# Deploy — Uúba Tech API na VPS

> Guia completo de deploy, migrations e troubleshooting: [docs/INTERNALS.md#10-deploy](../../docs/INTERNALS.md#10-deploy)

## Arquitetura na VPS

```
/opt/stack/
├── docker-compose.yml          ← services uuba-api + uuba-db
├── nginx/default.conf          ← location /api proxy para 127.0.0.1:8080
├── uuba-tech/                  ← clone do repo uuba-tech
│   └── uuba-tech-api/
│       ├── app/                ← codigo Python
│       ├── alembic/            ← migrations
│       ├── .env                ← credenciais reais (NAO commitado)
│       └── Dockerfile.prod     ← multi-stage build com cache de deps
└── ... (n8n, conduit, etc.)
```

## Deploy (apos cada push local)

```bash
# Na VPS
cd /opt/stack/uuba-tech && git pull
cd /opt/stack && docker compose up --build -d uuba-api
```

### O que acontece

1. `git pull` — baixa as mudancas
2. `docker compose up --build` — rebuilda a imagem e recria o container
3. O Dockerfile.prod usa multi-stage build com cache de deps:
   - Stage `deps`: instala dependencias (cacheado enquanto pyproject.toml nao muda)
   - Stage `builder`: copia codigo app/ (rapido, ~1s)
   - Stage final: monta imagem slim com codigo + deps
4. `alembic upgrade head` roda automaticamente no CMD do container
5. Healthcheck valida que uvicorn responde em /health

### Tempos esperados

| Cenario | Tempo |
|---------|-------|
| Mudanca so em `app/` (codigo) | ~30s (deps cacheadas) |
| Mudanca em `pyproject.toml` (deps) | ~140s (rebuild deps) |
| Sem mudancas | ~5s (tudo cacheado, container recriado) |

### Verificacao pos-deploy

```bash
# Health check
curl -s https://api.uuba.tech/health
# → {"status":"ok","version":"0.1.0"}

# Container status
docker ps --filter name=uuba-api --format '{{.Names}} {{.Status}}'
# → uuba-api Up X seconds (healthy)

# Logs (ultimas 20 linhas)
docker logs uuba-api --tail 20
```

## Rollback

```bash
# Ver commits disponiveis
cd /opt/stack/uuba-tech && git log --oneline -5

# Voltar para commit especifico
git checkout <commit-hash>
cd /opt/stack && docker compose up --build -d uuba-api

# Verificar
curl -s https://api.uuba.tech/health

# Quando resolver, voltar para main
cd /opt/stack/uuba-tech && git checkout main && git pull
```

## Setup inicial (uma vez)

```bash
# Na VPS como root
cd /opt/stack

# Clonar o repo
git clone https://github.com/luisbarcia/uuba-tech.git

# Criar .env com credenciais reais
cp uuba-tech/uuba-tech-api/.env.example uuba-tech/uuba-tech-api/.env
nano uuba-tech/uuba-tech-api/.env  # editar DATABASE_URL, UNKEY_ROOT_KEY, etc.

# Adicionar services ao docker-compose.yml existente
# (ver secao abaixo)

# Subir
docker compose up -d uuba-db uuba-api
```

## Troubleshooting

| Problema | Diagnostico | Solucao |
|----------|-------------|---------|
| 502 Bad Gateway | `docker ps` — container nao existe ou nao healthy | `docker compose up --build -d uuba-api` |
| 502 apos deploy | Container subindo, uvicorn ainda iniciando | Esperar 15s (healthcheck start-period) |
| Container reinicia em loop | `docker logs uuba-api` — ver erro | Corrigir codigo ou .env e rebuildar |
| Migration falhou | `docker logs uuba-api \| grep alembic` | Fix migration e rebuildar |
| Deps nao atualizam | Cache do Docker | `docker compose build --no-cache uuba-api` |
