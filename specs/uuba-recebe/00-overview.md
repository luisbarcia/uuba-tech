# UUBA Recebe — Overview

> Spec v2 | Gerada em 2026-03-22 | Feature Forge Workshop + Revisao PM + Revisao Dev

## Produto

Plataforma de gestao de recebiveis e cobranca automatizada que combina IA conversacional, reguas de cobranca configuraveis e acionamento multicanal para recuperar credito com taxa de 50%+ — superando a media do mercado brasileiro (20-25%).

O sistema opera em modo self-service: a empresa importa titulos vencidos e o UUBA Recebe executa todo o ciclo de cobranca ate a liquidacao.

## Diferenciais

1. **IA conversacional com protocolo comportamental (nudge)** — nao e chatbot generico, negocia de verdade
2. **Setup em minutos** — importou titulos, ja cobra
3. **Resultado mensuravel** — 50%+ recuperacao com dashboard de ROI
4. **Multicanal inteligente** — canal certo, hora certa, tom certo (WhatsApp no v1)

## Usuarios-alvo

- PMEs (ate 50 funcionarios) — sem depto financeiro estruturado
- Medias empresas (50-500) — com analista financeiro mas sem equipe de cobranca
- Operacoes de cobranca dedicadas — precisam de escala
- Clientes Uuba (BPO) — Uuba opera por eles

## Decisoes Arquiteturais (v1)

- **Multi-tenancy:** Shared DB com `tenant_id` (v1) — schema-per-tenant (v2) — DB-per-tenant (v3)
- **Stack:** FastAPI + PostgreSQL + SQLAlchemy async + Redis
- **Bot:** n8n + Claude Sonnet + Evolution API (WhatsApp)
- **Infra:** VPS Contabo + Docker + Nginx + SSL
- **Scoring:** Heuristico com regras (v1), ML (v2)
- **Canais:** WhatsApp only (v1), multicanal (v2)

## Benchmarking Global

| Plataforma | Pais | Metrica de destaque |
|------------|------|---------------------|
| TrueAccord | EUA | 96% pagamentos sem interacao humana; HeartBeat AI |
| InDebted | Australia | 7x mais engajamento; 1.8B insights ML |
| Symend | Canada | 10x ROI; ciencia comportamental |
| Quadient AR | EUA/Franca | Previsao de pagamento 94% precisao |
| Collectly | EUA | 75-300% aumento taxa coleta |
| Tesorio | EUA | Reducao media 33 dias no DSO |
| AISphere | Brasil | Multi-agente IA generativa; +18% acordos |

## Estrutura da Spec

| Documento | Conteudo |
|-----------|----------|
| [01-user-stories.md](01-user-stories.md) | 20 user stories (empresa, devedor, operador) |
| [02-jornadas.md](02-jornadas.md) | Jornada da empresa (6 fases) + jornada do devedor (4 cenarios) |
| [modulos/](modulos/) | 11 modulos com FRs (EARS) e ACs (Given/When/Then) |
| [04-kpis.md](04-kpis.md) | 22 metricas de sucesso (lagging, leading, produto) |
| [05-pricing.md](05-pricing.md) | 4 modelos de precificacao analisados |
| [06-nfrs.md](06-nfrs.md) | Requisitos nao-funcionais (performance, security, etc) |
| [07-integracoes.md](07-integracoes.md) | Integracoes externas (Evolution API, Conta Azul, etc) |
| [08-dependencias.md](08-dependencias.md) | Mapa de dependencias entre modulos |
| [09-error-handling.md](09-error-handling.md) | Tabela de erros e acoes |
| [10-implementation-todo.md](10-implementation-todo.md) | TODO de implementacao por modulo |
| [11-out-of-scope.md](11-out-of-scope.md) | O que NAO esta no v1 |
| [12-open-questions.md](12-open-questions.md) | Perguntas pendentes |

## Modulos

| # | Modulo | FRs | Status |
|---|--------|-----|--------|
| 0 | [Multi-tenancy](modulos/m00-multi-tenancy.md) | FR-001 a FR-006 | Nao implementado |
| 1 | [Clientes](modulos/m01-clientes.md) | FR-007 a FR-010 | Implementado |
| 2 | [Faturas](modulos/m02-faturas.md) | FR-011 a FR-021 | Parcialmente |
| 3 | [Pre-delinquency](modulos/m03-pre-delinquency.md) | FR-022 a FR-026 | Nao implementado |
| 4 | [Regua](modulos/m04-regua.md) | FR-027 a FR-043 | Nao implementado |
| 5 | [Bot IA](modulos/m05-bot-ia.md) | FR-044 a FR-061 | Parcialmente |
| 6 | [Import](modulos/m06-import.md) | FR-062+ | Nao implementado |
| 7 | [Portal Devedor](modulos/m07-portal-devedor.md) | ... | Nao implementado |
| 8 | [Dashboard](modulos/m08-dashboard.md) | ... | Nao implementado |
| 9 | [Scoring](modulos/m09-scoring.md) | ... | Nao implementado |
| 10 | [Resiliencia](modulos/m10-resiliencia.md) | ... | Nao implementado |

## Numeros

- **~98 Functional Requirements** (formato EARS)
- **~90 Acceptance Criteria** (Given/When/Then)
- **20 User Stories**
- **22 KPIs** em 3 camadas
- **11 Modulos**
- **6 Integracoes externas**

---

*Spec revisada por: PM Critic Agent + Dev/Architect Critic Agent*
*Baseada em: Feature Forge Workshop + Benchmarking Global (10 plataformas)*
