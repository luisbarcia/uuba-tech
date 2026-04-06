# ADR 0008: Headers obrigatorios em webhooks para n8n

## Status

Aceito (2026-04-06)

## Contexto

A API faz forward de requests para workflows n8n via webhooks (ex: v0/faturas → n8n para processamento no ERP). Os workflows n8n precisam saber a origem do request para fazer callbacks (atualizar status, buscar dados adicionais) sem hardcode de URLs.

## Decisao

Todo forward da API para webhooks n8n DEVE incluir os seguintes headers:

| Header | Descricao | Exemplo |
|--------|-----------|---------|
| `X-Tenant-Id` | ID do tenant que originou o request | `ten_afe4e3469d60987f` |
| `X-Request-Id` | ID unico do request para rastreamento | `req_abc123` |
| `X-API-Base-URL` | Base URL da API (env var `API_BASE_URL`) | `https://api.uuba.tech` |
| `X-API-Endpoint` | URL completa do endpoint que originou | `https://api.uuba.tech/api/v0/faturas` |

### Configuracao

`API_BASE_URL` eh uma env var do container. Default: `https://api.uuba.tech`.

### Uso no n8n

```
// No workflow n8n, acessar via:
{{ $headers['x-tenant-id'] }}
{{ $headers['x-request-id'] }}
{{ $headers['x-api-base-url'] }}
{{ $headers['x-api-endpoint'] }}

// Callback para a API:
{{ $headers['x-api-base-url'] }}/api/v1/faturas/{{ $json.fatura_id }}
```

## Endpoints que aplicam

- `POST /api/v0/faturas` → n8n receivables webhook
- `POST /api/v1/faturas` → (futuro, quando event bus disparar para n8n)

## Consequencias

- Workflows n8n nao precisam hardcode de URLs da API
- Facilita migrar entre ambientes (staging/prod) sem alterar workflows
- `X-Request-Id` permite correlacionar logs API ↔ n8n
- `X-Tenant-Id` permite workflows multi-tenant
