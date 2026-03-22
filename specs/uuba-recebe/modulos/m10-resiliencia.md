# Modulo 10: Resiliencia e Self-Healing

**Status:** Nao implementado

> **Nota de arquitetura:** Este modulo permeia todos os outros. Seus componentes devem ser implementados junto com cada modulo que depende de servicos externos ou processamento em background.

### Functional Requirements

**FR-107: Self-healing para falhas de envio**
When o envio de uma mensagem WhatsApp falha, the system shall classificar o erro como transiente (timeout, 5xx, connection reset) ou permanente (numero invalido, conta bloqueada, 4xx exceto 429), e aplicar estrategia diferenciada:
- **Transiente:** retry com exponential backoff (1s, 2s, 4s) ate 3 tentativas. Apos 3 falhas, enfileirar para reprocessamento manual.
- **Permanente:** nao fazer retry, marcar como falha permanente, notificar tenant.

**FR-108: Circuit breaker por servico externo**
The system shall implementar circuit breaker para cada servico externo (Evolution API, Conta Azul, Claude API, Chatwoot) com os seguintes parametros:
- **Threshold para abrir:** 5 ou mais falhas em janela de 5 minutos.
- **Estado aberto:** todas as chamadas sao enfileiradas (nao descartadas), alerta enviado ao admin.
- **Half-open:** apos 60 segundos, permitir 1 chamada de teste. Se sucesso, fechar. Se falha, reabrir por mais 60 segundos.
- **Estado fechado:** operacao normal.

**FR-109: Auto-recuperacao de regua travada**
Where o health check detecta uma regua sem nenhuma execucao ha mais de 24 horas (quando existem faturas elegiveis para processamento), the system shall:
1. Registrar alerta de "regua travada" no log.
2. Verificar status do worker responsavel.
3. Reiniciar o worker automaticamente.
4. Notificar admin com detalhes (tenant, regua, ultima execucao, faturas pendentes).

**FR-110: Evento interno para sincronizacao cross-module**
The system shall implementar mecanismo de eventos internos usando PostgreSQL LISTEN/NOTIFY (v1) com possibilidade de migracao para Redis Pub/Sub (v2). Eventos obrigatorios:
- `fatura_paga`: propaga para bot (parar cobranca ativa), dashboard (atualizar metricas), scoring (recalcular).
- `fatura_vencida`: propaga para regua (iniciar cobranca).
- `promessa_registrada`: propaga para regua (pausar), scoring (recalcular).
- `promessa_expirada`: propaga para regua (retomar), scoring (recalcular).
- `acordo_criado`: propaga para regua (ajustar), dashboard (atualizar).
- `opt_out`: propaga para regua (parar canal), bot (respeitar preferencia).

**FR-111: Health check endpoint**
The system shall expor endpoint `GET /health` que retorna status agregado e de cada servico:
```json
{
  "status": "healthy | degraded | unhealthy",
  "timestamp": "ISO-8601",
  "services": {
    "database": { "status": "up", "latency_ms": 5 },
    "redis": { "status": "up", "latency_ms": 2 },
    "evolution_api": { "status": "up", "latency_ms": 150 },
    "conta_azul": { "status": "up", "latency_ms": 200 },
    "claude_api": { "status": "degraded", "latency_ms": 4500 },
    "chatwoot": { "status": "up", "latency_ms": 100 }
  },
  "circuit_breakers": {
    "evolution_api": "closed",
    "conta_azul": "closed",
    "claude_api": "half-open",
    "chatwoot": "closed"
  }
}
```
Status geral: `healthy` se todos up, `degraded` se algum servico nao-critico degradado, `unhealthy` se servico critico down (database, redis).

**FR-112: Fallback para Claude API**
Where a Claude API esta indisponivel (circuit breaker aberto ou 3 timeouts consecutivos), the system shall enviar mensagem generica pre-aprovada ao devedor com link de pagamento e telefone para contato humano, em vez de deixar a conversa sem resposta. A mensagem generica deve ser configuravel por tenant.

### Acceptance Criteria

**AC-088: Evolution API cai por 10 minutos**
Given a Evolution API esta respondendo normalmente,
When a API fica indisponivel por 10 minutos,
Then apos 5 falhas em 5 minutos o circuit breaker abre,
And todas as mensagens pendentes sao enfileiradas (nao descartadas),
And quando a API volta, o circuit breaker entra em half-open,
And apos 1 chamada bem-sucedida, o circuit breaker fecha,
And todas as mensagens enfileiradas sao enviadas em ordem.

**AC-089: Claude API timeout**
Given o devedor envia mensagem e a Claude API nao responde em 10 segundos,
When o sistema faz retry 2 vezes (1s, 2s de backoff),
And na 3a falha consecutiva,
Then o sistema envia mensagem generica configurada pelo tenant ao devedor,
And registra o incidente no log com correlation_id.

**AC-090: Worker de regua morre**
Given o worker de regua de um tenant para de executar,
When o health check detecta ausencia de execucao por mais de 24h com faturas elegiveis,
Then o worker e reiniciado automaticamente em menos de 5 minutos,
And o admin recebe notificacao com detalhes do incidente.

**AC-091: Evento fatura_paga propaga corretamente**
Given uma fatura em cobranca ativa (regua em execucao, conversa aberta no bot),
When o webhook de pagamento confirma a fatura como paga,
Then o evento `fatura_paga` e emitido,
And o bot para de cobrar aquela fatura (se conversa ativa, envia agradecimento),
And o dashboard atualiza metricas na proxima janela de refresh,
And o score do devedor e recalculado em menos de 500ms.

**AC-092: Health check com servico degradado**
Given a Claude API esta respondendo com latencia acima de 5 segundos,
When o endpoint /health e consultado,
Then retorna status geral "degraded",
And o servico `claude_api` aparece com status "degraded" e latencia medida,
And os demais servicos aparecem com seus status reais.
