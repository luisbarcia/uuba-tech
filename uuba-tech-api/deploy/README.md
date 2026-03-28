# Deploy — Uúba Tech API na VPS

> Guia completo de deploy, migrations e troubleshooting: [docs/INTERNALS.md#10-deploy](../../docs/INTERNALS.md#10-deploy)

## Arquitetura na VPS

```
/opt/stack/
├── docker-compose.yml          ← adicionar services uuba-api + uuba-db
├── nginx/default.conf          ← adicionar location /api proxy
├── uuba-tech-api/              ← clone do repo (apenas subdiretorio)
│   ├── app/
│   ├── alembic/
│   ├── .env                    ← credenciais reais (NÃO commitado)
│   └── ...
└── ... (n8n, conduit, etc.)
```

## Setup inicial (uma vez)

```bash
# Na VPS como root
cd /opt/stack

# Clonar o repo
git clone https://github.com/luisbarcia/uuba-tech.git
ln -s uuba-tech/uuba-tech-api uuba-tech-api

# Criar .env com credenciais reais
cp uuba-tech-api/.env.example uuba-tech-api/.env
nano uuba-tech-api/.env  # editar DATABASE_URL, API_KEY, etc.

# Adicionar services ao docker-compose.yml existente
# (ver seção abaixo)

# Subir
docker compose up -d uuba-db uuba-api
```

## Sincronizar (após cada push local)

```bash
# Na VPS
cd /opt/stack/uuba-tech && git pull
cd /opt/stack && docker compose up --build -d uuba-api
```

Ou via n8n webhook (automatizado).
