# Plano de Migracao: Evolution API → WhatsApp Business API (Meta Cloud API)

> Objetivo: suportar a API oficial do WhatsApp Business para atender requisitos de compliance
> de empresas medias e grandes, mantendo a Evolution como opcao para PMEs pequenas.
>
> Status: Planejado | Prioridade: Alta (bloqueio comercial para clientes enterprise)
> Data: 2026-03-19

---

## Indice

1. [Contexto e motivacao](#1-contexto)
2. [Arquitetura atual vs futura](#2-arquitetura)
3. [Pre-requisitos Meta Cloud API](#3-pre-requisitos)
4. [Fases de implementacao](#4-fases)
5. [Mapeamento de endpoints](#5-mapeamento)
6. [Mudancas no n8n](#6-n8n)
7. [Mudancas na API](#7-api)
8. [Chatwoot](#8-chatwoot)
9. [Custos](#9-custos)
10. [Riscos e mitigacoes](#10-riscos)
11. [Cronograma estimado](#11-cronograma)
12. [Checklist de go-live](#12-checklist)

---

## 1. Contexto

### Problema
A Evolution API emula o WhatsApp Web (nao oficial). Empresas medias e grandes nao aceitam:
- Sem contrato com Meta
- Risco de ban a qualquer momento
- Sem SLA
- Nao passa por compliance/juridico

### Solucao
Adicionar suporte a **WhatsApp Business API (Meta Cloud API)** como canal oficial.
Manter Evolution como opcao para operacoes menores ou desenvolvimento.

### Estrategia: Gateway Abstraction Layer
Criar uma camada de abstracao que permita trocar o gateway sem alterar a logica de negocio.

```
                    ┌─────────────────────┐
                    │     n8n Workflow     │
                    │  (logica de negocio) │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Gateway Adapter    │
                    │  (sub-workflow n8n)  │
                    └───┬─────────────┬───┘
                        │             │
              ┌─────────▼───┐   ┌─────▼─────────┐
              │  Evolution  │   │ Meta Cloud API │
              │  (dev/PME)  │   │  (enterprise)  │
              └─────────────┘   └────────────────┘
```

---

## 2. Arquitetura

### Hoje (Evolution API)

```
Cliente WhatsApp
    │
    ▼
Evolution API (wa.uuba.tech)
    │ webhook POST (formato Evolution)
    ▼
n8n — Workflow "WhatsApp Receber" (O2Qu40lBWFLBqedq)
    │ identifica cliente, chama IA
    ▼
n8n — Workflow "WhatsApp Enviar" (x7YyAt9NgQ1w9UpM)
    │ POST evolution-api:8080/message/sendText/uuba-bot
    ▼
Evolution API → Cliente WhatsApp
```

### Futuro (dual gateway)

```
Cliente WhatsApp
    │
    ├──────────────────────┐
    ▼                      ▼
Evolution API         Meta Cloud API
    │                      │
    │ webhook              │ webhook
    │ (formato Evolution)  │ (formato Meta)
    ▼                      ▼
n8n — Normalizer (novo sub-workflow)
    │ converte ambos formatos → formato interno padrao
    ▼
n8n — Workflow "WhatsApp Receber" (sem mudanca na logica)
    │
    ▼
n8n — Gateway Router (novo sub-workflow)
    │ decide qual gateway usar baseado em config
    ├──────────────────────┐
    ▼                      ▼
Evolution API         Meta Cloud API
    │                      │
    ▼                      ▼
Cliente WhatsApp      Cliente WhatsApp
```

---

## 3. Pre-requisitos Meta Cloud API

### Conta e aprovacao

| Requisito | Detalhes |
|-----------|----------|
| Meta Business Account | Criar em business.facebook.com (gratis) |
| Meta Developer Account | Criar em developers.facebook.com (gratis) |
| App no Meta for Developers | Criar app tipo "Business" e adicionar produto "WhatsApp" |
| Numero de telefone | Numero novo exclusivo (nao pode estar vinculado a WhatsApp pessoal/business) |
| Verificacao do negocio | CNPJ, site da empresa, documentos — pode levar 3-7 dias uteis |
| Aceitar termos | WhatsApp Business Terms of Service e Meta Business Messaging |

### Credenciais necessarias

| Credencial | Onde obter | Uso |
|------------|-----------|-----|
| Phone Number ID | Dashboard do app → WhatsApp → Getting Started | Identificar o numero de envio |
| WhatsApp Business Account ID | Dashboard → WhatsApp → Configuration | Gerenciar templates e config |
| Access Token (permanente) | System User no Business Manager → gerar token | Autenticacao em todas as chamadas |
| App Secret | Dashboard → Settings → Basic | Validar assinatura dos webhooks |
| Verify Token | Definido por voce ao configurar webhook | Handshake inicial do webhook |

### Templates de mensagem (HSM)

Para iniciar conversa com o cliente (cobranca proativa), e obrigatorio usar **message templates** pre-aprovados pela Meta:

1. Criar template no Business Manager → WhatsApp Manager → Message Templates
2. Categoria: **Utility** (cobranca/lembretes)
3. Aguardar aprovacao (1-24h)
4. Templates aceitam variaveis: `{{1}}`, `{{2}}`, etc.

Exemplo de template para cobranca:
```
Nome: cobranca_lembrete
Categoria: Utility
Idioma: pt_BR
Corpo: Olá {{1}}, identificamos uma pendência no valor de R$ {{2}} com vencimento em {{3}}. Podemos ajudar a resolver?
```

> **Nota:** Respostas a mensagens do cliente (janela de 24h) NAO precisam de template. O bot pode responder livremente.

---

## 4. Fases de implementacao

### Fase 1 — Setup Meta (1-2 dias)

- [ ] Criar Meta Business Account com CNPJ da Uuba
- [ ] Criar app no Meta for Developers
- [ ] Adicionar produto WhatsApp ao app
- [ ] Verificar o negocio (pode levar 3-7 dias)
- [ ] Obter numero de telefone novo para canal oficial
- [ ] Gerar System User + Access Token permanente
- [ ] Configurar webhook apontando para URL do n8n

### Fase 2 — Normalizer de entrada (1 dia)

Criar sub-workflow no n8n que recebe webhooks de ambos os formatos e normaliza para formato interno.

**Formato interno padrao:**

```json
{
  "source": "meta" | "evolution",
  "phone": "5521999999999",
  "name": "Nome do contato",
  "message": "Texto da mensagem",
  "messageId": "wamid.xxx",
  "timestamp": 1679000000,
  "type": "text" | "image" | "audio" | "document",
  "mediaUrl": null,
  "isGroup": false
}
```

### Fase 3 — Gateway Router de saida (1 dia)

Criar sub-workflow que substitui o "WhatsApp Enviar" atual:

1. Recebe mensagem no formato interno
2. Verifica config: qual gateway usar? (env var ou campo no cliente)
3. Formata e envia pelo gateway correto

### Fase 4 — Templates de cobranca (1 dia)

- [ ] Criar 3-5 templates de cobranca na Meta
- [ ] Aguardar aprovacao
- [ ] Implementar envio de template no Gateway Router (para iniciar conversas)
- [ ] Manter envio livre para respostas dentro da janela de 24h

### Fase 5 — Chatwoot (0.5 dia)

- [ ] Configurar inbox oficial WhatsApp Business no Chatwoot
- [ ] Testar escalacao bot → humano no canal oficial
- [ ] Manter inbox Evolution separado (dois canais)

### Fase 6 — Testes e validacao (1-2 dias)

- [ ] Testar recebimento de mensagem via Meta Cloud API
- [ ] Testar resposta do bot via Meta Cloud API
- [ ] Testar cobranca proativa com template
- [ ] Testar escalacao para Chatwoot
- [ ] Testar fallback (Meta fora → Evolution assume, ou vice-versa)
- [ ] Testar com numero real de cliente

### Fase 7 — Documentacao e go-live (0.5 dia)

- [ ] Atualizar pagina de infra no portal
- [ ] Documentar config do Meta no guia de replicacao
- [ ] Atualizar prompts se necessario
- [ ] Go-live gradual (1 cliente → 10 → todos)

---

## 5. Mapeamento de endpoints

### Receber mensagem (webhook)

| | Evolution API | Meta Cloud API |
|--|--------------|----------------|
| **URL** | POST para n8n (configurado na Evolution) | POST para n8n (configurado no app Meta) |
| **Verificacao** | Nenhuma | GET com hub.verify_token (handshake inicial) + assinatura HMAC-SHA256 |
| **Payload msg** | `body.data.message` | `body.entry[0].changes[0].value.messages[0]` |
| **Telefone** | `body.data.key.remoteJid` (formato: 5521999999999@s.whatsapp.net) | `body.entry[0].changes[0].value.messages[0].from` (formato: 5521999999999) |
| **Texto** | `body.data.message.conversation` ou `body.data.message.extendedTextMessage.text` | `body.entry[0].changes[0].value.messages[0].text.body` |
| **Nome** | `body.data.pushName` | `body.entry[0].changes[0].value.contacts[0].profile.name` |
| **Tipo** | Inferido do campo presente | `messages[0].type` (text, image, audio, etc.) |

### Enviar mensagem

| | Evolution API | Meta Cloud API |
|--|--------------|----------------|
| **Endpoint** | `POST /message/sendText/{instance}` | `POST https://graph.facebook.com/v21.0/{phone-number-id}/messages` |
| **Auth** | Header `apikey: {key}` | Header `Authorization: Bearer {token}` |
| **Body texto** | `{"number": "5521999999999", "text": "Mensagem"}` | `{"messaging_product": "whatsapp", "to": "5521999999999", "type": "text", "text": {"body": "Mensagem"}}` |
| **Body template** | N/A | `{"messaging_product": "whatsapp", "to": "5521999999999", "type": "template", "template": {"name": "cobranca_lembrete", "language": {"code": "pt_BR"}, "components": [{"type": "body", "parameters": [{"type": "text", "text": "João"}, {"type": "text", "text": "1.500,00"}, {"type": "text", "text": "20/03/2026"}]}]}}` |
| **Resposta** | `{"key": {"id": "xxx"}}` | `{"messages": [{"id": "wamid.xxx"}]}` |

### Marcar como lida

| | Evolution API | Meta Cloud API |
|--|--------------|----------------|
| **Endpoint** | `PUT /chat/markMessageAsRead/{instance}` | `POST https://graph.facebook.com/v21.0/{phone-number-id}/messages` |
| **Body** | `{"readMessages": [{"id": "xxx", "remoteJid": "xxx"}]}` | `{"messaging_product": "whatsapp", "status": "read", "message_id": "wamid.xxx"}` |

---

## 6. Mudancas no n8n

### Workflows afetados

| Workflow | ID | Mudanca |
|----------|-----|---------|
| WhatsApp Receber | O2Qu40lBWFLBqedq | Adicionar Normalizer no inicio (antes do debounce) |
| WhatsApp Enviar | x7YyAt9NgQ1w9UpM | Substituir por Gateway Router |
| Regua de Cobranca | PLmFT4LDMHCJO543 | Usar Gateway Router + templates para inicio proativo |

### Novo: Webhook Meta (verificacao)

A Meta exige um GET de verificacao no setup do webhook:

```
GET /webhook?hub.mode=subscribe&hub.verify_token=MEU_TOKEN&hub.challenge=CHALLENGE
→ Retornar: CHALLENGE (plain text)
```

No n8n: criar workflow separado ou node de Respond to Webhook que verifica o token e retorna o challenge.

### Novo: Validacao de assinatura

Toda requisicao POST da Meta vem com header `X-Hub-Signature-256`. Validar com HMAC-SHA256 usando o App Secret.

No n8n: Code Node no inicio do workflow que valida a assinatura.

### Node nativo do n8n

O n8n tem node nativo **"WhatsApp Business Cloud"** que suporta:
- Enviar texto, template, midia e mensagens interativas (botoes, listas)
- Credential tipo "WhatsApp Business Cloud API" com Access Token + WABA ID + Phone Number ID

Pode ser usado no lugar do HTTP Request node para simplificar o Gateway Router.

### BSP alternativo: 360dialog

Se a verificacao direta com a Meta for complicada, o **360dialog** e um BSP que:
- Repassa precos da Meta sem markup significativo ($0/mes no free tier)
- Simplifica o onboarding (nao precisa de Business Verification completa pra comecar)
- Ideal para devs que querem API direta sem overhead

### Variaveis de ambiente novas

```
META_PHONE_NUMBER_ID=
META_ACCESS_TOKEN=
META_APP_SECRET=
META_VERIFY_TOKEN=
META_WABA_ID=
WHATSAPP_GATEWAY=evolution|meta  # qual gateway usar por padrao
```

---

## 7. Mudancas na API (uuba-tech-api)

### Minimas

A API nao fala diretamente com WhatsApp — o n8n e o intermediario. Mudancas na API sao opcionais:

| Mudanca | Necessidade | Descricao |
|---------|-------------|-----------|
| Campo `canal_gateway` em cobrancas | Desejavel | Registrar se cobranca foi via Evolution ou Meta |
| Endpoint de config por cliente | Futuro | Permitir que cada cliente tenha gateway diferente |

---

## 8. Chatwoot

### Opcoes de integracao

**Opcao A — API Inbox (recomendada):**
Chatwoot recebe mensagens via API (mesmo modelo atual com Evolution). O n8n encaminha para Chatwoot quando escala.

**Opcao B — WhatsApp Cloud nativo do Chatwoot:**
Chatwoot tem integracao nativa com WhatsApp Cloud API desde v3.x. Configurar direto no painel.

Recomendacao: **Opcao B** — menos trabalho, mais confiavel para o canal oficial. Manter Opcao A para Evolution.

---

## 9. Custos

### Meta Cloud API — Precos por conversa (Brasil, 2026)

| Categoria | Custo por conversa | Quem inicia | Uso na UUBA |
|-----------|-------------------|-------------|-------------|
| **Service** | Gratis (1000/mes), depois ~R$ 0,16 | Cliente | Cliente responde cobranca |
| **Utility** | ~R$ 0,19 | Empresa (com template) | Cobranca proativa, lembretes |
| **Marketing** | ~R$ 0,35 | Empresa (com template) | Campanhas (nao usamos) |
| **Authentication** | ~R$ 0,17 | Empresa (com template) | 2FA (nao usamos) |

> **Importante (desde nov/2024):** Templates de Utility enviados **dentro** de uma janela de Service
> existente sao **gratuitos**. Ou seja, se o cliente mandou mensagem primeiro e voce responde com
> template de cobranca dentro de 24h, nao paga nada.

### Estimativa mensal

| Volume | Custo Evolution | Custo Meta Cloud API |
|--------|----------------|---------------------|
| 100 cobrancas/mes | R$ 0 | ~R$ 19 (utility) + gratis (service) |
| 500 cobrancas/mes | R$ 0 | ~R$ 95 |
| 1.000 cobrancas/mes | R$ 0 | ~R$ 190 |
| 5.000 cobrancas/mes | R$ 0 | ~R$ 950 |

> **Nota:** Conversas de service (cliente inicia) sao gratis ate 1000/mes. Apos isso, ~R$ 0,15 cada.

### Modelo de repasse

O custo da Meta pode ser repassado ao cliente como parte da assinatura ou cobrado por mensagem. O modelo de Parceiros (white-label) ja preve custos variaveis.

---

## 10. Riscos e mitigacoes

| Risco | Impacto | Mitigacao |
|-------|---------|-----------|
| Verificacao do negocio demora >7 dias | Atrasa go-live | Iniciar processo imediatamente, antes de comecar dev |
| Template rejeitado pela Meta | Nao consegue iniciar cobranca proativa | Criar templates simples e neutros. Ter 3-5 variantes |
| Janela de 24h expira | Bot nao pode mais responder | Implementar re-engagement com template automatico |
| Custo Meta sobe | Margem reduz | Monitorar custo/conversa. Manter Evolution como opcao barata |
| Webhook Meta instavel | Mensagens perdidas | Implementar retry + dead letter queue no n8n |
| Mudanca na API da Meta (versioning) | Quebra integracao | Usar versao fixa (v21.0), monitorar deprecation notices |

---

## 11. Cronograma estimado

| Fase | Duracao | Dependencia |
|------|---------|-------------|
| 1. Setup Meta | 1-2 dias dev + 3-7 dias verificacao | Nenhuma — **iniciar primeiro** |
| 2. Normalizer entrada | 1 dia | Fase 1 concluida |
| 3. Gateway Router saida | 1 dia | Fase 1 concluida |
| 4. Templates de cobranca | 1 dia | Fase 1 concluida |
| 5. Chatwoot | 0.5 dia | Fase 2-3 concluidas |
| 6. Testes | 1-2 dias | Fases 2-5 concluidas |
| 7. Documentacao + go-live | 0.5 dia | Fase 6 concluida |
| **Total** | **~6-8 dias uteis** (incluindo espera da verificacao) |

> **Caminho critico:** a verificacao do negocio pela Meta (3-7 dias). Iniciar fase 1 imediatamente — o dev pode comecar em paralelo usando o numero de teste do Meta sandbox.

---

## 12. Checklist de go-live

### Antes de ativar

- [ ] Meta Business Account verificada
- [ ] Numero de telefone aprovado e ativo
- [ ] Access Token permanente gerado (System User)
- [ ] Webhook configurado e respondendo (GET + POST)
- [ ] Assinatura HMAC validada em todos os webhooks
- [ ] Templates de cobranca aprovados (minimo 3)
- [ ] Normalizer testado com payloads reais Meta
- [ ] Gateway Router testado para envio
- [ ] Chatwoot recebendo conversas do canal oficial
- [ ] Escalacao bot → humano funcionando
- [ ] Monitoramento de custos configurado (Meta Business Manager)

### Primeiro dia

- [ ] Enviar 5-10 cobrancas pelo canal oficial (clientes selecionados)
- [ ] Monitorar taxa de entrega e leitura
- [ ] Verificar se bot responde dentro da janela de 24h
- [ ] Confirmar que Evolution continua funcionando em paralelo

### Primeira semana

- [ ] Expandir para todos os clientes enterprise
- [ ] Monitorar custos reais vs estimativa
- [ ] Ajustar templates se taxa de resposta for baixa
- [ ] Documentar issues encontrados

---

## Resumo para apresentar a holdings/clientes

> *"A UUBA suporta dois canais de WhatsApp: a API oficial da Meta (WhatsApp Business Platform)
> para clientes que exigem compliance e SLA, e um canal alternativo para operacoes menores.
> A arquitetura e agnóstica ao gateway — toda a logica de cobranca, IA e integracao funciona
> independentemente do canal. A migracao entre canais e transparente para o cliente final."*
