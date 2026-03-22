# Findings: Revisões da Spec UÚBA Recebe

## Revisão PM — Gaps Críticos

### Pre-delinquency (P0)
- Régua começa D-3, deveria começar D-14 a D-30
- InDebted e Symend trabalham com pre-delinquency starting D-14+
- Pode reduzir inadimplência 15-25%
- FRs: régua preventiva, desconto por antecipação, predição de inadimplência

### Ação pós-régua (P0)
- 20% dos devedores não respondem — ficam "soltos" após D+15
- Spec não define: pausa permanente? reinicia? escala para jurídico?
- FR necessário para ação pós-régua

### Gestão de parcelas (P0)
- Acordo parcelado sem acompanhamento = quebra
- Falta: lembretes de parcelas futuras, ação quando parcela atrasa
- FRs: gestão de parcelas, lembretes, ação em atraso

### A/B testing (P1)
- TrueAccord roda 20M+ jornadas com A/B contínuo
- FRs: A/B de réguas, A/B de mensagens, promoção automática de vencedora

### Renegociação proativa (P1)
- Devedor que quebrou acordo precisa tratamento diferente
- 91.9% retomam plano quando renegociação proativa é oferecida
- FRs: cooling period + nova proposta + limite de renegociações

### Self-healing (P1)
- Circuit breaker, retry com backoff, auto-recuperação de régua travada
- FRs: self-healing envio, circuit breaker, auto-recuperação

### WhatsApp áudio (P2)
- Maioria dos usuários BR prefere áudio
- FRs: transcrição de áudio recebido (Whisper), resposta em áudio (TTS)

### Onboarding guiado (P2)
- Sem wizard, churn na primeira semana
- FRs: wizard, preview de import, notificação primeiro pagamento

### Outros FRs PM
- Promise-to-pay analytics
- Behavioral nudges configuráveis
- Webhook de eventos para tenant
- Simulador de régua (dry run)
- Handoff bot→humano com resumo automático
- Confirmação via comprovante (OCR)

## Revisão Dev — Correções Técnicas

### Multi-tenancy deve ser Módulo 0 (ALTA)
- Pré-requisito arquitetural — implementar depois = retrabalho massivo
- DB-per-tenant com 100 tenants = 100 connection pools = PgBouncer necessário
- Sugestão: shared DB + tenant_id para v1

### Pix tempo real irreal (ALTA)
- Conta Azul não tem API de consulta de Pix
- Verificação vem via webhook, não polling
- Reescrever FR-025 para refletir realidade

### 100 instâncias Evolution API inviável (ALTA)
- 100 containers Docker na VPS = impossível
- Meta Cloud API suporta múltiplos números com único Business Manager
- Decisão necessária: Evolution API vs Cloud API para escala

### Scoring ML irreal para v1 (MÉDIA-ALTA)
- Sem infra de ML na VPS
- Retreino semanal compete por recursos com API
- Sugestão: scoring heurístico com fórmula explícita
- score = base(50) + historico(-20 a +20) + atraso(-15 a +15) + engajamento(-10 a +10) + valor(-5 a +5)

### Compliance embutido (ALTA)
- Deve ser parte da Régua e Bot, não módulo separado
- Se régua vai a produção sem compliance = risco legal

### Webhook sem HMAC (ALTA)
- Qualquer pessoa pode enviar webhook falso e marcar faturas como pagas
- Adicionar validação de assinatura HMAC

### Falta RBAC (MÉDIA)
- API key é único auth — sem distinção admin/operador/viewer
- Adicionar roles: admin, operador, viewer

### Import deve ser assíncrono (MÉDIA)
- Upload síncrono de 10k linhas = timeout
- Endpoint retorna 202 + job_id, status via polling

### Latência bot 5s p95 (BAIXA)
- Claude + tools = 2-5s só na LLM
- 3s é otimista, 5s é realista para p95

### ACs faltando edge cases
- Telefone reciclado, múltiplos devedores mesmo número
- Webhook duplicado, fatura já paga
- Import com encoding errado, separador diferente
- QR code expirado, pagamento parcial
- Feriado regional, timezone do devedor
- Opt-out do único canal disponível

### Outros gaps Dev
- Versionamento de API não definido
- Mecânica de parcelamento vaga (gera novas faturas? juros?)
- Cancelamento de fatura sem FR
- Sincronização cross-module (event bus)
- Criptografia at rest vs queries (blind index)
- Dados sensíveis em logs (mascaramento)

## Métricas de Sucesso (do PM)

### Lagging (mensal)
- Taxa de recuperação: ≥40% v1, ≥55% v2
- DSO médio: ≤25d v1, ≤15d v2
- Custo por real recuperado: ≤R$0,05 v1
- ROI: ≥10x v1, ≥20x v2
- Taxa acordo cumprido: ≥70% v1, ≥85% v2
- Churn tenants: ≤5%/mês v1

### Leading (semanal)
- Engajamento: ≥35%
- Leitura: ≥80%
- Clique link pagamento: ≥25%
- Promessa: ≥20%
- Escalação humana: ≤15%
- Opt-out: ≤3%

### Produto (contínuo)
- Time-to-first-collection: ≤72h
- Onboarding completion: ≥80%
- Bot accuracy: ≥90%
- Uptime: ≥99.5%

## Precificação (do PM)

### Recomendação: Híbrido (Opção C)
- Base mensal (R$197-497) + success fee (3-7%) sobre valor recuperado
- Lançar com success fee puro (10%) nos primeiros 6 meses para aquisição
- Depois migrar para híbrido quando tiver cases

### Alternativas analisadas
- A: % valor recuperado (5-15%) — alinhado mas imprevisível
- B: Mensalidade fixa por faixa — previsível mas sem alinhamento
- D: Por mensagem — incentivo perverso, não recomendado
