# UUBA Recebe — Integracoes Externas

| Servico | URL/Endpoint | Auth | Rate Limits | Fallback | Custo Estimado |
|---------|-------------|------|-------------|----------|----------------|
| Evolution API | wa.uuba.tech -- WebSocket + REST | API key por instancia | Sem rate limit formal (limitado por WhatsApp: ~80 msg/s) | Retry 3x com backoff, enfileirar, alertar admin | Gratuito (self-hosted) + custo VPS |
| Meta Cloud API (futuro) | graph.facebook.com/v21.0 -- REST | Token OAuth (System User) | 1.000 msg/s por WABA, 250 conversas/24h (Business-initiated tier 1) | Fallback para Evolution API | R$ 0,25-0,65 por conversa (template) |
| Conta Azul | api.contaazul.com -- REST | OAuth2 (access_token + refresh_token) | 60 req/min por aplicacao | Fila de compensacao, retry com backoff | Gratuito (API inclusa no plano) |
| Claude API (Anthropic) | api.anthropic.com -- REST | API key (x-api-key header) | TPM-based (varia por tier), ~60 req/min (tier 1) | Mensagem generica pre-aprovada ao devedor | ~US$ 3/1M input tokens, ~US$ 15/1M output tokens (Sonnet) |
| Chatwoot | chat.uuba.tech -- REST + WebSocket | API key (user_api_key ou platform_api_key) | Sem rate limit formal (self-hosted) | Fila de escalacao manual, notificacao via WhatsApp | Gratuito (self-hosted) + custo VPS |
| Whisper API (OpenAI) | api.openai.com/v1/audio/transcriptions -- REST | API key (Authorization: Bearer) | 50 req/min (tier 1) | Informar devedor para enviar texto, log do audio para processamento manual | US$ 0,006/min de audio |

### Notas sobre integracoes

- **Evolution API vs Meta Cloud API:** A v1 usa Evolution API (self-hosted, custo zero de mensagens). Para escala multi-tenant (100+ numeros), Meta Cloud API e mais viavel (unico Business Manager, sem 100 containers Docker). Decisao deve ser tomada antes da Fase 3.
- **Conta Azul:** Nao tem API de consulta de Pix em tempo real. Verificacao de pagamento vem exclusivamente via webhook. FR-025 (verificacao em tempo real) ajustado na Parte 2 para refletir essa limitacao.
- **Claude API:** Custo variavel conforme volume. Estimativa para 1.000 conversas/dia com media de 5 turnos: ~US$ 15-30/dia. Monitorar com metrica `custo_por_conversa`.
