# Régua de Cobrança — Protocolo UÚBA

> Documento de referência do motor de cobrança automática.
> Versão 1.0 — 2026-03-25

## O que é

A régua de cobrança é o motor que transforma o UÚBA Recebe de "gestão de faturas" em "plataforma de cobrança inteligente". Ela automatiza o envio de mensagens para devedores com faturas vencidas, escalando o tom progressivamente.

## Como funciona

```
Fatura vence → Job detecta (cron 1h) → Identifica passo na régua → Verifica compliance → Envia → Registra cobrança
```

### Fluxo detalhado

1. **Job `processar-regua`** roda a cada hora (cron externo ou endpoint manual)
2. Busca todas as faturas com `status = vencido`
3. Para cada fatura:
   - Calcula `dias_atraso = hoje - vencimento`
   - Busca última cobrança enviada
   - Determina próximo passo da régua (baseado em dias_atraso)
   - **Guards de compliance:**
     - Horário útil? (seg-sex 8-20h, sáb 8-14h)
     - Já enviou hoje? (max 1/dia)
     - Já enviou 3x esta semana? (max 3/semana)
     - É feriado?
   - Se passou nos guards → cria cobrança + emite Domain Event `CobrancaEnviada`
   - Se não → pula (será reprocessada na próxima execução)

## Régua Padrão (5 passos)

| Passo | Dias de atraso | Tipo | Tom | Objetivo |
|-------|---------------|------|-----|----------|
| 1 | D+1 | Lembrete | Amigável | Lembrar da fatura + oferecer link de pagamento |
| 2 | D+3 | Follow-up | Neutro | Verificar se precisa de ajuda |
| 3 | D+7 | Cobrança | Firme | Comunicar necessidade de regularização |
| 4 | D+12 | Cobrança | Urgente | Alertar sobre medidas adicionais |
| 5 | D+15 | Escalação | Urgente | Última tentativa antes de escalação humana |

### Escala de Tom (CobrancaTom)

| Tom | Intensidade | Uso |
|-----|-------------|-----|
| Amigável | 1 | Primeiros contatos, lembretes |
| Neutro | 2 | Follow-ups, verificações |
| Firme | 3 | Cobranças formais após sem resposta |
| Urgente | 4 | Últimas tentativas antes de escalação |

## Compliance

### Horários permitidos

| Dia | Horário |
|-----|---------|
| Segunda a Sexta | 08:00 — 20:00 |
| Sábado | 08:00 — 14:00 |
| Domingo | Nunca |
| Feriado nacional | Nunca |

### Limites de frequência

| Regra | Limite |
|-------|--------|
| Por dia (por devedor) | Máximo 1 mensagem |
| Por semana (por devedor) | Máximo 3 mensagens |

### Feriados nacionais (2026)

Hardcoded para 2026. Lista inclui feriados fixos e móveis:
- Confraternização Universal (01/01)
- Carnaval (16-17/02)
- Sexta-feira Santa (03/04)
- Tiradentes (21/04)
- Dia do Trabalho (01/05)
- Corpus Christi (04/06)
- Independência (07/09)
- Aparecida (12/10)
- Finados (02/11)
- Proclamação da República (15/11)
- Natal (25/12)

> Para 2027+: atualizar `FERIADOS_NACIONAIS` em `app/services/compliance.py`.

## Templates de mensagem

Cada passo da régua tem um template com variáveis:

| Variável | Fonte | Exemplo |
|----------|-------|---------|
| `{numero_nf}` | `fatura.numero_nf` | "NF-2024-0042" |
| `{valor}` | `fatura.valor` formatado | "2.500,00" |
| `{vencimento}` | `fatura.vencimento` formatado | "20/03/2026" |
| `{dias_atraso}` | calculado | "7" |
| `{link_pagamento}` | `fatura.pagamento_link` | "https://..." |

### Exemplo de mensagem (D+1, amigável)

> Olá! Passando para lembrar da fatura NF-2024-0042 no valor de R$ 2.500,00. Venceu em 20/03/2026. Segue o link para pagamento: https://pag.contaazul.com/xxx. Qualquer dúvida, estamos à disposição!

## Integrações

### Envio (fase atual — MVP)

Na fase MVP, a cobrança é **registrada** na API mas o envio real é delegado ao **n8n**:

```
API registra cobrança → Domain Event CobrancaEnviada → n8n webhook → Evolution API (WhatsApp)
```

O campo `status` da cobrança rastreia o ciclo de vida:
- `enviado` → mensagem entregue ao provedor
- `entregue` → confirmação de entrega
- `lido` → destinatário abriu
- `respondido` → destinatário respondeu
- `pausado` → régua pausada para este devedor

### Pausa inteligente (futuro)

Se o devedor respondeu uma mensagem nas últimas 24h (`status = respondido`), a régua pausa automaticamente para não atrapalhar uma conversa em andamento.

## Banco de dados

### Tabela `reguas`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | String(20) | Ex: `reg_padrao_uuba` |
| `nome` | String(100) | "Régua Padrão UÚBA" |
| `ativa` | Boolean | Se False, régua não é processada |

### Tabela `regua_passos`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | String(20) | Ex: `rps_abc123` |
| `regua_id` | FK → reguas | Régua a que pertence |
| `ordem` | Integer | Posição na sequência (1-5) |
| `dias_atraso` | Integer | Trigger: D+N dias de atraso |
| `tipo` | String | lembrete, cobranca, follow_up, escalacao |
| `canal` | String | whatsapp, email, sms |
| `tom` | String | amigavel, neutro, firme, urgente |
| `template_mensagem` | Text | Template com variáveis |

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/jobs/processar-regua` | Executa um ciclo da régua (chamado por cron) |
| POST | `/api/v1/admin/seed` | Inclui régua padrão no seed de dados mock |

## Arquivos do código

| Arquivo | Responsabilidade |
|---------|-----------------|
| `app/models/regua.py` | Models SQLAlchemy (Regua, ReguaPasso) |
| `app/seed_regua.py` | Seed da régua padrão com 5 passos |
| `app/services/compliance.py` | Engine de compliance (horários, frequência, feriados) |
| `app/services/regua_service.py` | Motor principal da régua |
| `tests/test_compliance.py` | Testes do compliance engine |
| `tests/test_regua.py` | Testes do motor da régua |

## Decisões de design

1. **Régua como dados no banco (não hardcoded):** Permite customização futura por cliente/segmento sem deploy
2. **Compliance como módulo separado:** Reutilizável para outros processos (ex: envio manual via API)
3. **Domain Events (DP-03):** `CobrancaEnviada` permite que n8n reaja ao evento sem acoplamento direto
4. **Envio desacoplado:** A régua *registra* cobranças; o *envio* é responsabilidade do n8n/Evolution API
5. **Feriados hardcoded:** Suficiente para MVP; futuro: API de feriados ou tabela no banco
