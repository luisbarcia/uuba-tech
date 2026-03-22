# UUBA Recebe — Non-Functional Requirements

### NFR-01: Performance

| Operacao | Meta p95 | Condicao | Observacao |
|----------|----------|----------|------------|
| API leitura | < 200ms | Qualquer endpoint GET | Cache Redis para tenant routing |
| API escrita | < 500ms | Qualquer endpoint POST/PUT/PATCH | Includes validacao e persistencia |
| Overhead tenant routing | < 10ms | Cache Redis obrigatorio, TTL 5min | Sem cache: ~50-100ms (inaceitavel) |
| Bot resposta simples | < 2s | Saudacao, FAQ, off-topic | Sem chamada a Claude necessaria |
| Bot resposta complexa | < 5s | Consulta faturas + Claude + tools | Claude + tools = 2-5s sozinho |
| Dashboard operacional | < 3s | Ate 50.000 faturas por tenant | REQUER materialized views |
| Dashboard estrategico | < 5s | Dados agregados cross-tenant | REQUER cache pre-computado |
| Import sincrono (preview) | < 5s | Primeiras 10 linhas para dry run | Sem persistencia |
| Import assincrono | < 30s para 10.000 linhas | Processamento em background | Notificacao ao finalizar |
| Score calculo individual | < 500ms | Recalculo por evento | Formula heuristica, sem ML |
| Score batch diario | < 10min | Todos devedores ativos do tenant | Job agendado off-peak |

### NFR-02: Security

| Requisito | Especificacao | Prioridade |
|-----------|---------------|------------|
| Auth API | API key por tenant + RBAC (admin, operador, viewer) | P0 |
| Auth portal | JWT RS256 com revogacao via blacklist (Redis) | P0 |
| Verificacao portal | Ultimos 4 digitos CPF no primeiro acesso | P0 |
| Webhook auth | Validacao HMAC-SHA256 obrigatoria antes de processar | P0 |
| Transporte | TLS 1.3 em todas as conexoes | P0 |
| Headers seguranca | HSTS (max-age 1 ano), CSP, X-Content-Type-Options, X-Frame-Options | P0 |
| Rate limiting leitura | 300 req/min por API key | P0 |
| Rate limiting escrita | 60 req/min por API key | P0 |
| Rate limiting import | 5 req/min por API key | P0 |
| Rate limiting delete | 10 req/min por API key | P0 |
| Rotacao API key | 90 dias, com periodo de graca de 7 dias (ambas chaves ativas) | P1 |
| Criptografia at rest (v1) | Full-disk encryption (Contabo VPS) | P0 |
| Criptografia at rest (v2) | Column-level encryption com blind index para CPF/CNPJ | P2 |
| Mascaramento logs | CPF (***.***.789-00), valores (R$ ***), telefone (****1234) | P0 |
| RBAC roles | admin: tudo; operador: operar + visualizar; viewer: somente leitura | P0 |

### NFR-03: Scalability

| Dimensao | Limite v1 | Estrategia |
|----------|-----------|------------|
| Tenants simultaneos | Ate 100 | Shared DB + tenant_id, PgBouncer |
| Faturas por tenant | Ate 50.000 | Indexes compostos com tenant_id |
| Mensagens WhatsApp/dia por tenant | Ate 10.000 | Fila Redis, workers horizontais |
| Devedores por tenant | Ate 20.000 | Derivado de faturas/devedor |
| Tamanho arquivo import | Ate 100.000 linhas | Processamento assincrono |
| Requisicoes API concorrentes | Ate 500/s agregado | Load balancer + connection pool |

### NFR-04: Reliability

| Requisito | Especificacao |
|-----------|---------------|
| Uptime | 99.5% (API e bot) -- ~3.6h downtime/mes permitido |
| Mensagens | At-least-once delivery com retry (3x exponential backoff) |
| Webhooks recebidos | Processamento idempotente (mesmo webhook 2x sem efeito duplicado) |
| Backup | Diario automatico do banco de dados |
| Circuit breaker | Por servico externo (Evolution, Conta Azul, Claude, Chatwoot) |
| Transacoes de import | Atomicas -- falha no meio nao persiste dados parciais |
| Eventos internos | At-least-once via PostgreSQL LISTEN/NOTIFY com fallback para polling |

### NFR-05: Observability

| Requisito | Especificacao |
|-----------|---------------|
| Logs | JSON estruturado com correlation_id por request |
| Metricas | Prometheus/Grafana (latencia, throughput, erros, tamanho de filas) |
| Alertas | Email + WhatsApp para erros criticos (bot down, webhook falhando, DB inacessivel, circuit breaker aberto) |
| Tracing | OpenTelemetry para rastrear fluxo completo (webhook -> bot -> API -> resposta) |
| Dashboards operacionais (infra) | Grafana com: CPU, memoria, disco, conexoes DB, filas Redis |
| Retencao de logs | 30 dias em disco, 90 dias em storage frio |
