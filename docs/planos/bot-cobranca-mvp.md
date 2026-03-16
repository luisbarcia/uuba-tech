# Bot de Cobrança — Plano MVP

> **Produto:** Bot inteligente que cobra e conversa com clientes via WhatsApp
> **Objetivo:** Primeira entrega funcional — bot que inicia cobranças E responde clientes
> **Data:** 16 de março de 2026

---

## O que o bot faz

### Fluxo 1: Bot inicia (régua de cobrança)
```
Régua detecta fatura vencida
  → Bot manda mensagem no WhatsApp (tom baseado em dias de atraso)
  → Cliente responde
  → Bot entende e reage (promessa, dúvida, negociação, etc.)
```

### Fluxo 2: Cliente inicia
```
Cliente manda WhatsApp
  → Bot identifica pelo telefone
  → Puxa contexto (faturas, cobranças, histórico)
  → Conversa com o cliente (consultar faturas, pagar, tirar dúvidas)
```

### Capacidades do bot (v1)

| Situação | Ação do bot |
|----------|-------------|
| Fatura vencida | Envia cobrança com tom progressivo (amigável → firme → urgente) |
| "Vou pagar sexta" | Registra promessa de pagamento, agenda follow-up |
| "Já paguei" | Verifica no sistema, confirma ou pede comprovante |
| "Que fatura é essa?" | Puxa NF, valor, descrição, envia detalhes |
| "Quanto devo?" | Lista total em aberto + faturas pendentes |
| "Quero pagar agora" | Envia link de pagamento |
| "Quero parcelar" | Escala para humano |
| Cliente irritado / palavrão | Detecta sentimento, acalma, escala para humano |
| Cliente ignora | Escala tom automaticamente pela régua |
| Número desconhecido | "Não encontrei seu cadastro, qual seu CNPJ?" |
| "Oi" / saudação | Identifica pelo telefone, cumprimenta, oferece ajuda |

---

## O que já temos (pronto)

- [x] API REST — 14 endpoints (clientes, faturas, cobranças) em produção
- [x] Mock data — 8 clientes, 16 faturas, 13 cobranças
- [x] Métricas por cliente (DSO, total em aberto, vencido)
- [x] 174 testes automatizados + CI/CD verde
- [x] n8n rodando na VPS
- [x] Workflow protótipo da régua (funcional)
- [x] Infra: VPS + Docker + Nginx + SSL

---

## Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│                        WhatsApp                               │
│                     (cliente final)                            │
└─────────────────────────┬────────────────────────────────────┘
                          │ mensagens
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    Evolution API v2                            │
│              (self-hosted na VPS, porta 8080)                  │
│         recebe mensagens + envia mensagens                    │
└─────────────────────────┬────────────────────────────────────┘
                          │ webhook
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                        n8n                                    │
│                                                               │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐  │
│  │ Webhook      │   │ Identificar  │   │ Agente Claude    │  │
│  │ recebe msg   │──▶│ cliente pelo │──▶│ (Sonnet)         │  │
│  │              │   │ telefone     │   │                  │  │
│  └─────────────┘   └──────────────┘   │ - contexto API   │  │
│                                        │ - histórico chat │  │
│  ┌─────────────┐                      │ - regras negócio │  │
│  │ Régua       │                      │ - tom adaptativo │  │
│  │ (cron/      │─────────────────────▶│                  │  │
│  │  schedule)  │                      └────────┬─────────┘  │
│  └─────────────┘                               │             │
│                                                 ▼             │
│                                        ┌──────────────────┐  │
│                                        │ Ações:           │  │
│                                        │ - Responder WA   │  │
│                                        │ - Registrar API  │  │
│                                        │ - Escalar humano │  │
│                                        └──────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    Uúba Tech API                              │
│              (FastAPI + PostgreSQL)                            │
│                                                               │
│  GET  /clientes?telefone=5511...   → identificar cliente      │
│  GET  /clientes/{id}/metricas      → contexto financeiro      │
│  GET  /faturas?cliente_id=...      → faturas em aberto        │
│  POST /cobrancas                   → registrar ação           │
│  PATCH /faturas/{id}               → registrar promessa       │
└──────────────────────────────────────────────────────────────┘
```

---

## Sprints Revisados

### Sprint 3 — WhatsApp bidirecional
**Objetivo:** Conectar WhatsApp ao n8n

- [ ] Instalar Evolution API v2 na VPS (docker-compose)
- [ ] Configurar instância WhatsApp (QR code, número)
- [ ] Nginx + SSL para evolution.uuba.tech (ou subpath)
- [ ] Webhook: Evolution API → n8n (mensagem recebida)
- [ ] Workflow n8n: receber mensagem → identificar cliente pelo telefone → responder "Olá {nome}"
- [ ] Workflow n8n: enviar mensagem via Evolution API (HTTP Request)
- [ ] Testar: enviar e receber mensagens manualmente

**Entrega:** WhatsApp funcionando bidirecionalmente via n8n

---

### Sprint 4 — Agente conversacional
**Objetivo:** Bot que entende e responde o cliente

- [ ] Criar prompt do agente com contexto (role, regras, tom)
- [ ] Workflow n8n: cliente manda msg → buscar dados na API → Claude gera resposta → enviar WhatsApp
- [ ] Tools do agente:
  - Buscar faturas em aberto do cliente
  - Buscar métricas do cliente
  - Registrar promessa de pagamento
  - Registrar cobrança realizada
  - Escalar para humano
- [ ] Memória de conversa (últimas N mensagens por cliente — n8n memory node ou Redis)
- [ ] Detecção de intenção: pagar, dúvida, reclamação, saudação
- [ ] Escalonamento para humano quando necessário
- [ ] Testar com cenários reais (mock clients)

**Entrega:** Bot conversacional funcional no WhatsApp

---

### Sprint 5 — Régua automática integrada
**Objetivo:** Bot inicia cobranças + se integra com a conversa

- [ ] Workflow cron: verificar faturas vencidas → enviar cobrança automática
- [ ] Régua de tom progressivo (amigável → neutro → firme → urgente)
- [ ] Integrar com histórico de conversa (não cobrar se já está conversando)
- [ ] Promessa de pagamento: agendar follow-up automático
- [ ] Fatura paga: enviar agradecimento automático
- [ ] Dashboard: métricas das cobranças (enviadas, respondidas, pagas)

**Entrega:** Régua de cobrança automática + bot conversacional integrados

---

### Sprint 6 — Webhook pagamento + polish
**Objetivo:** Fechar o ciclo completo

- [ ] Webhook Asaas: pagamento confirmado → atualizar fatura → notificar cliente
- [ ] Link de pagamento: gerar via Asaas e enviar no WhatsApp
- [ ] Tabelas de agentes (agent_decisions, agent_prompts) para feedback loop
- [ ] Few-shot learning: agente melhora com exemplos aprovados
- [ ] Testes e2e do fluxo completo
- [ ] Documentação do bot (como configurar, como funciona)

**Entrega:** MVP completo — ciclo cobrança → conversa → pagamento → confirmação

---

## Dependências externas

| Item | Responsável | Precisa para |
|------|-------------|-------------|
| Número WhatsApp (chip/linha) | Equipe | Sprint 3 |
| Conta Asaas (sandbox) | Equipe | Sprint 6 |
| Aprovação do tom/mensagens | Equipe | Sprint 4 |

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| WhatsApp bane número por spam | Começar com poucos clientes, tom amigável, opt-in |
| Evolution API instável | Monitorar, fallback para API oficial se necessário |
| Claude alucina respostas financeiras | Prompt rigoroso, validar dados contra API antes de responder |
| Cliente confunde bot com humano | Mensagem inicial "Sou o assistente da Uúba" |

---

*Plano atualizado em 16/03/2026*
