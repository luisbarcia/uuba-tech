# UUBA Recebe — Faseamento

> Estrategia: Uuba opera como BPO para cliente piloto, depois escala para self-service.

## Fase 0: Piloto Interno

**Objetivo:** Cobrar o primeiro devedor real via WhatsApp com regua automatica.
**Modelo:** Uuba opera o Recebe para 1 cliente piloto (BPO).
**Criterio de conclusao:** Primeiro pagamento recuperado via plataforma.

### Ja temos

- [x] API REST (clientes, faturas, cobrancas) — 14 endpoints, 174 testes
- [x] Bot WhatsApp com Claude Sonnet (4 tools, memoria por telefone)
- [x] Protocolo comportamental (nudge) com tom adaptativo
- [x] Evolution API v2.3.7 + Redis (wa.uuba.tech)
- [x] WhatsApp bidirecional (receber + enviar via n8n)
- [x] Infra VPS + Docker + Nginx + SSL

### Falta construir

| # | Item | Modulo | FRs | Complexidade |
|---|------|--------|-----|-------------|
| 1 | Regua automatica (cron verifica vencidas, dispara cobranca) | M04 | FR-027 a FR-033 | L |
| 2 | Compliance basico (horarios seg-sex 8-20h, sab 8-14h, frequencia max 1/dia 3/sem) | M04 | FR-034, FR-035 | M |
| 3 | Escalacao para Chatwoot (bot detecta sentimento, encaminha com contexto) | M05 | FR-049, FR-053 | M |
| 4 | Import CSV basico (upload sincrono, validacao, criacao de clientes+faturas) | M06 | FR-062, FR-064 | M |
| 5 | Integracao Conta Azul — link de pagamento (Pix/boleto) | M02 | FR-014 | L |
| 6 | Integracao Conta Azul — webhook pagamento confirmado | M02 | FR-016 | M |
| 7 | Transicao automatica para vencido (cron diario) | M02 | FR-015 | S |
| 8 | Promessa de pagamento + follow-up agendado | M02 | FR-013 | S |

### Nao precisa na Fase 0

- Multi-tenancy (1 cliente so, single-tenant)
- Portal do devedor (link de pagamento no WhatsApp basta)
- Dashboard (olhar DB direto ou Metabase)
- Scoring (regua padrao funciona)
- Pre-delinquency (cobrar vencido ja e valor)
- RBAC (so a equipe Uuba opera)
- A/B testing (uma regua boa basta)
- Import assincrono (volume pequeno no piloto)
- Gestao de parcelas (escalar pra humano se pedir parcelamento)

### Ordem de implementacao (Fase 0)

```
1. Transicao automatica vencido (S) — base pra regua funcionar
2. Regua automatica + compliance (L+M) — core do produto
3. Import CSV basico (M) — cliente precisa colocar titulos
4. Promessa de pagamento (S) — bot ja precisa disso
5. Escalacao Chatwoot (M) — seguranca pra casos dificeis
6. Integracao Conta Azul - link pagamento (L) — devedor precisa pagar
7. Integracao Conta Azul - webhook (M) — fechar o loop
```

---

## Fase 1: Primeiro Cliente Pagante

**Objetivo:** Receber segundo+ cliente operando self-service (ou semi-assisted).
**Modelo:** Self-service com suporte da equipe Uuba.
**Criterio de conclusao:** 3 clientes ativos com dados isolados.
**Pre-requisito:** Fase 0 validada com piloto.

| # | Item | Modulo | FRs |
|---|------|--------|-----|
| 1 | Multi-tenancy (tenant_id em todas as tabelas, cache Redis) | M00 | FR-001 a FR-003 |
| 2 | Import CSV completo (async, validacao, relatorio, dedup) | M06 | FR-062 a FR-073 |
| 3 | Dashboard minimo (taxa recuperacao, valor recuperado, aging) | M08 | FR-088, FR-089, FR-090 |
| 4 | Gestao de parcelas (acordo gera faturas-filhas, acompanhamento) | M02 | FR-018 a FR-021 |
| 5 | Negociacao semi-automatica no bot (limites por tenant) | M05 | FR-050 |
| 6 | Acao pos-regua (D+15 sem resposta — config por tenant) | M04 | FR-041 |
| 7 | Audit trail completo | M04 | FR-037 |
| 8 | Configuracao de numero WhatsApp por tenant | M00 | FR-005 |

---

## Fase 2: Escala

**Objetivo:** Produto robusto para 10-50 clientes.
**Modelo:** Self-service completo.
**Criterio de conclusao:** 10 clientes ativos, taxa recuperacao >=40%, churn <=5%/mes.

| # | Item | Modulo | FRs |
|---|------|--------|-----|
| 1 | Portal do devedor (JWT, pagamento, negociacao, historico) | M07 | FR-074 a FR-087 |
| 2 | Scoring heuristico (formula explicita, segmentacao, alimenta regua) | M09 | FR-100 a FR-106 |
| 3 | Pre-delinquency (regua preventiva D-30 a D-1, desconto antecipacao) | M03 | FR-022 a FR-026 |
| 4 | A/B testing de reguas e mensagens | M04 | FR-038 a FR-040 |
| 5 | Self-healing e circuit breaker | M10 | FR-107 a FR-112 |
| 6 | RBAC (admin, operador, viewer) | M00 | FR-004 |
| 7 | Templates com variaveis + behavioral nudges | M04 | FR-043 |
| 8 | Simulador de regua (dry run) | M04 | FR-043 |
| 9 | Dashboard completo (performance por regua, ROI, exportacao) | M08 | FR-091 a FR-099 |

---

## Fase 3: Diferenciacao

**Objetivo:** Lideranca de mercado. Features que ninguem no Brasil tem.
**Modelo:** Plataforma completa.
**Criterio de conclusao:** 50+ clientes, taxa recuperacao >=55%, referencia no mercado.

| # | Item | Modulo | FRs |
|---|------|--------|-----|
| 1 | Audio WhatsApp (transcricao Whisper + resposta TTS) | M05 | FR-054, FR-055 |
| 2 | Renegociacao proativa pos-quebra de acordo | M04 | FR-042 |
| 3 | Scoring ML (retreino semanal, SHAP) | M09 | Evolucao de FR-100+ |
| 4 | Handoff bot-humano com resumo automatico | M05 | FR-056 |
| 5 | Confirmacao via comprovante (OCR) | M05 | FR-057 |
| 6 | Integracoes nativas com ERPs (Omie, Bling, SAP) | M06 | FR-073 |
| 7 | Multicanal (email, SMS, voz) | M04/M05 | Novos FRs |
| 8 | Few-shot learning do agente | M05 | FR-061 |
| 9 | Promise-to-pay analytics | M08 | FR-095 |
| 10 | Open Finance para reconciliacao automatica | M06 | Novo FR |

---

## Resumo

| Fase | Foco | Clientes | Entrega principal |
|------|------|----------|-------------------|
| **0** | Piloto | 1 (BPO) | Regua + bot + pagamento funcionando end-to-end |
| **1** | Monetizar | 3+ | Multi-tenancy + import + dashboard minimo |
| **2** | Escalar | 10-50 | Portal + scoring + pre-delinquency + A/B |
| **3** | Dominar | 50+ | Audio + ML + multicanal + integracoes |

---

*Faseamento definido em 2026-03-22*
*Criterio: Uuba como primeiro operador (BPO), escala gradual para self-service*
