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

### Fluxo 3: Pagamento (Pix / Boleto via Conta Azul)
```
Cliente quer pagar → Bot gera link via Conta Azul
  → Conta Azul confirma via webhook → Bot atualiza fatura e agradece
```

### Capacidades do bot (v1)

| Situação | Ação do bot |
|----------|-------------|
| Fatura vencida | Envia cobrança com tom progressivo (amigável → firme → urgente) |
| "Vou pagar sexta" | Registra promessa de pagamento, agenda follow-up |
| "Já paguei" (Pix) | Verifica em tempo real, confirma e atualiza |
| "Já paguei" (Boleto) | Avisa que leva 1-2 dias úteis, agenda follow-up |
| "Que fatura é essa?" | Puxa NF, valor, descrição, envia detalhes |
| "Quanto devo?" | Lista total em aberto + faturas pendentes |
| "Quero pagar agora" | Envia link de pagamento (Pix/boleto via Conta Azul) |
| "Quero parcelar" | Escala para humano |
| Cliente irritado / palavrão | Detecta sentimento, acalma, escala para humano |
| Cliente ignora | Escala tom automaticamente pela régua |
| Número desconhecido | "Não encontrei seu cadastro, qual seu CNPJ?" |
| "Oi" / saudação | Identifica pelo telefone, cumprimenta, oferece ajuda |
| Pagamento confirmado | Webhook Conta Azul → atualiza fatura → agradece |

---

## O que já temos (pronto)

- [x] API REST — 14 endpoints (clientes, faturas, cobranças) em produção
- [x] Mock data — 8 clientes, 16 faturas, 13 cobranças
- [x] Métricas por cliente (DSO, total em aberto, vencido)
- [x] 174 testes automatizados + CI/CD verde
- [x] n8n rodando na VPS
- [x] Workflow protótipo da régua (funcional)
- [x] Infra: VPS + Docker + Nginx + SSL
- [x] Evolution API v2.3.7 + Redis (wa.uuba.tech)
- [x] WhatsApp bidirecional (receber + enviar via n8n)
- [x] Agente IA (Claude Sonnet) com 4 tools + memória por cliente
- [x] Protocolo de cobrança comportamental (nudge)
- [x] Modelo multi-número (Uúba fornece número por cliente)

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
│                Evolution API v2.3.7                            │
│          (wa.uuba.tech — self-hosted na VPS)                  │
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
│  └─────────────┘   └──────────────┘   │ - 4 tools API    │  │
│                                        │ - memória/cliente│  │
│  ┌─────────────┐                      │ - protocolo nudge│  │
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

## Sprints

### Sprint 3 — WhatsApp bidirecional ✅
**Objetivo:** Conectar WhatsApp ao n8n

- [x] Instalar Evolution API v2.3.7 + Redis na VPS (docker-compose)
- [x] Nginx + SSL para wa.uuba.tech
- [x] Criar database evolution no PostgreSQL
- [x] Configurar instância WhatsApp (QR code)
- [x] Webhook: Evolution API → n8n (mensagem recebida)
- [x] Workflow n8n: receber mensagem → identificar cliente → responder
- [x] Workflow n8n: enviar mensagem via Evolution API (sub-workflow)
- [x] Filtro: ignorar mensagens de grupo (só diretas)
- [x] Testar: enviar e receber mensagens

**Entrega:** WhatsApp funcionando bidirecionalmente via n8n

---

### Sprint 4 — Agente conversacional ✅
**Objetivo:** Bot que entende e responde o cliente

- [x] Criar prompt do agente com protocolo de cobrança comportamental
- [x] Workflow n8n: cliente manda msg → buscar dados na API → Claude gera resposta → enviar WhatsApp
- [x] Tools do agente:
  - Buscar faturas em aberto do cliente
  - Buscar métricas do cliente
  - Registrar promessa de pagamento
  - Registrar cobrança realizada
- [x] Memória de conversa (últimas 10 mensagens por cliente — buffer window por telefone)
- [x] System prompt com regras de negócio, tom, escalação
- [ ] Escalonamento para humano (encaminhar para atendente)
- [ ] Testar com cenários reais (mock clients)

**Entrega:** Bot conversacional funcional no WhatsApp

---

### Sprint 5 — Régua automática integrada
**Objetivo:** Bot inicia cobranças + se integra com a conversa

- [ ] Workflow cron: verificar faturas vencidas → enviar cobrança automática
- [ ] Régua de tom progressivo (protocolo comportamental: D-3 a D+15)
- [ ] Integrar com histórico de conversa (não cobrar se já está conversando)
- [ ] Promessa de pagamento: agendar follow-up automático
- [ ] Fatura paga: enviar agradecimento automático
- [ ] Dashboard: métricas das cobranças (enviadas, respondidas, pagas)

**Entrega:** Régua de cobrança automática + bot conversacional integrados

---

### Sprint 6 — Webhook pagamento + polish
**Objetivo:** Fechar o ciclo completo

- [ ] Webhook Conta Azul: pagamento confirmado → atualizar fatura → notificar cliente
- [ ] Link de pagamento: gerar via Conta Azul e enviar no WhatsApp
- [ ] Tabelas de agentes (agent_decisions, agent_prompts) para feedback loop
- [ ] Few-shot learning: agente melhora com exemplos aprovados
- [ ] Testes e2e do fluxo completo
- [ ] Documentação do bot (como configurar, como funciona)

**Entrega:** MVP completo — ciclo cobrança → conversa → pagamento → confirmação

---

## Dependências externas

| Item | Responsável | Precisa para |
|------|-------------|-------------|
| ~~Número WhatsApp (chip/linha)~~ | ~~Equipe~~ | ~~Sprint 3~~ ✅ Uúba fornece |
| Conta Azul (sandbox) | Equipe | Sprint 6 |
| ~~Aprovação do tom/mensagens~~ | ~~Equipe~~ | ~~Sprint 4~~ ✅ Protocolo comportamental aprovado |

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| WhatsApp bane número por spam | Começar com poucos clientes, tom amigável, opt-in, protocolo comportamental |
| Evolution API instável | Monitorar, fallback para API oficial se necessário. Atualizado para v2.3.7 |
| Claude alucina respostas financeiras | Prompt rigoroso, bot só responde com dados das tools (API), nunca inventa |
| Cliente confunde bot com humano | Mensagem inicial "Sou o assistente da Uúba" |
| Desconto abusivo | Máximo 10% pelo bot, acima escala para humano |

---

*Plano atualizado em 16/03/2026*
