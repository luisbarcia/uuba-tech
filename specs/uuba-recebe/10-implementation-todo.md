# UUBA Recebe — Implementation TODO

### Modulo 0: Multi-tenancy e Isolamento [Fase 1]
- [ ] [L] Implementar modelo shared-DB com `tenant_id` em todas as tabelas
- [ ] [M] Criar middleware de roteamento de tenant por API key (cache Redis, TTL 5min)
- [ ] [L] Criar servico de provisionamento automatico de tenant (schema, credenciais, config)
- [ ] [M] Implementar RBAC: roles admin, operador, viewer com permissoes granulares
- [ ] [S] Implementar rotacao de API key com periodo de graca de 7 dias
- [ ] [M] Implementar migration runner por tenant (shared schema)
- [ ] [M] Configurar backup automatico diario
- [ ] [S] Configurar PgBouncer para connection pooling

### Modulo 1: Gestao de Clientes [Fase 2]
- [ ] [S] Adicionar `tenant_id` ao modelo de clientes (ja existe, adaptar)
- [ ] [S] Implementar upsert por documento (CPF/CNPJ) no escopo do tenant
- [ ] [S] Implementar mascaramento de CPF em logs
- [ ] [M] Implementar historico de interacoes (timeline)

### Modulo 2: Gestao de Faturas [Fase 2]
- [ ] [S] Adicionar `tenant_id` ao modelo de faturas (ja existe, adaptar)
- [ ] [M] Implementar maquina de estados completa (pendente -> vencido -> em_negociacao -> acordo -> pago | cancelado)
- [ ] [M] Implementar job cron de transicao automatica para vencido
- [ ] [M] Implementar webhook receiver Conta Azul com validacao HMAC e idempotencia
- [ ] [S] Implementar cancelamento de fatura (FR novo da Parte 2)
- [ ] [M] Implementar geracao de link de pagamento via Conta Azul

### Modulo 3: Pre-delinquency [Fase 3]
- [ ] [L] Implementar regua preventiva (D-30 a D-1)
- [ ] [M] Implementar motor de predicao de inadimplencia (heuristico)
- [ ] [M] Implementar desconto por antecipacao de pagamento
- [ ] [S] Implementar lembretes pre-vencimento configuraveis

### Modulo 4: Regua de Cobranca [Fase 3]
- [ ] [L] Criar modelo `Regua` e `ReguaPasso` com suporte multi-tenant
- [ ] [M] Implementar CRUD de reguas via API
- [ ] [L] Criar worker cron que verifica faturas vencidas e executa regua
- [ ] [M] Implementar tom progressivo automatico
- [ ] [M] Implementar pausa inteligente (conversa ativa, promessa)
- [ ] [M] Implementar retomada automatica apos promessa expirada
- [ ] [S] Criar regua padrao (protocolo comportamental Uuba)
- [ ] [M] Embutir compliance na regua: horarios (8h-20h seg-sex, 8h-14h sab), frequencia (1/dia, 3/sem), feriados
- [ ] [L] Implementar A/B testing de reguas com alocacao aleatoria e metricas
- [ ] [M] Implementar acao pos-regua (D+15 sem resposta)
- [ ] [M] Implementar gestao de parcelas (lembretes, acao em atraso)
- [ ] [M] Implementar renegociacao proativa (cooling period + nova proposta)
- [ ] [M] Implementar simulador de regua (dry run)

### Modulo 5: Bot IA Conversacional [Fase 3]
- [ ] [L] Adaptar agente para multi-tenant (system prompt por tenant, config por tenant)
- [ ] [M] Implementar escalacao para Chatwoot com resumo automatico (handoff)
- [ ] [M] Implementar negociacao semi-automatica (limites configuraveis por tenant)
- [ ] [S] Adicionar tool: gerar link de pagamento
- [ ] [M] Implementar verificacao de pagamento via webhook (nao polling)
- [ ] [M] Implementar deteccao de sentimento e ajuste de tom
- [ ] [S] Adicionar few-shot learning com exemplos aprovados
- [ ] [M] Implementar tabelas agent_decisions e agent_prompts
- [ ] [L] Implementar transcricao de audio via Whisper API
- [ ] [M] Implementar behavioral nudges configuraveis por tenant
- [ ] [M] Implementar confirmacao via comprovante (OCR basico)
- [ ] [S] Implementar webhook de eventos para tenant (cobranca.enviada, pagamento.recebido, etc.)

### Modulo 6: Import de Titulos [Fase 2]
- [ ] [L] Criar endpoint `POST /api/v1/import/csv` com upload assincrono (202 + job_id)
- [ ] [M] Implementar `GET /api/v1/import/{job_id}` para status do job
- [ ] [M] Implementar parser CSV com deteccao de encoding (UTF-8, ISO-8859-1) e separador (virgula, ponto-e-virgula, tab)
- [ ] [M] Implementar mapeamento de colunas (interface + API)
- [ ] [M] Implementar validacao em lote com relatorio de erros
- [ ] [M] Criar endpoint `POST /api/v1/import/batch` (JSON) com suporte assincrono para lotes grandes
- [ ] [M] Implementar webhook receiver para ERPs com validacao HMAC-SHA256
- [ ] [S] Implementar deduplicacao por numero_nf + cliente_id
- [ ] [S] Implementar limite de 100.000 linhas por arquivo
- [ ] [M] Implementar preview/dry run (primeiras 10 linhas)
- [ ] [S] Implementar notificacao de conclusao de import ao tenant

### Modulo 7: Portal do Devedor [Fase 4]
- [ ] [L] Criar SPA mobile-first com React/Next.js
- [ ] [M] Implementar geracao de JWT RS256 com tenant_id e devedor_id
- [ ] [M] Implementar endpoint de revogacao de token (blacklist Redis)
- [ ] [S] Implementar verificacao secundaria (ultimos 4 digitos CPF)
- [ ] [M] Tela de faturas em aberto
- [ ] [M] Tela de pagamento (QR code Pix com regeneracao automatica + boleto)
- [ ] [M] Tela de negociacao (opcoes de desconto/parcelamento)
- [ ] [S] Tela de historico de acordos e comprovantes
- [ ] [M] Widget de chat Chatwoot
- [ ] [S] Tela de link expirado com solicitacao de novo link
- [ ] [S] Implementar rate limit de re-geracao de links (3/dia)
- [ ] [M] Implementar headers de seguranca (CSP, HSTS, X-Frame-Options)
- [ ] [M] Implementar fallback HTML basico server-side

### Modulo 8: Dashboard e Analytics [Fase 5]
- [ ] [L] Criar materialized views para metricas de dashboard
- [ ] [M] Implementar refresh programado (15min operacional, 1h estrategico)
- [ ] [M] Implementar endpoint de dashboard operacional com filtros
- [ ] [M] Implementar aging report
- [ ] [M] Implementar calculo de DSO com historico
- [ ] [M] Implementar calculo de ROI
- [ ] [M] Implementar comparativo de performance entre reguas
- [ ] [M] Implementar promise-to-pay analytics
- [ ] [L] Implementar dashboard de KPIs estrategicos
- [ ] [M] Implementar comparativo de A/B tests com intervalo de confianca
- [ ] [M] Criar endpoint de exportacao CSV/PDF
- [ ] [S] Implementar sistema de alertas (threshold configuravel)

### Modulo 9: Scoring e Inteligencia [Fase 5]
- [ ] [M] Implementar formula heuristica de score (0-100)
- [ ] [M] Criar endpoint `GET /api/v1/clientes/{id}/score`
- [ ] [M] Implementar recalculo por evento (pagamento, resposta, promessa)
- [ ] [M] Implementar job batch diario de recalculo
- [ ] [M] Implementar segmentacao por regras (5 segmentos)
- [ ] [S] Implementar integracao score -> regua (tom e frequencia)
- [ ] [M] Implementar recomendacao de horario agregada
- [ ] [S] Implementar explicabilidade (top 3 fatores)

### Modulo 10: Resiliencia e Self-Healing [Continuo]
- [ ] [L] Implementar circuit breaker por servico externo
- [ ] [M] Implementar self-healing para falhas de envio (classificar transiente/permanente)
- [ ] [M] Implementar auto-recuperacao de regua travada
- [ ] [L] Implementar sistema de eventos internos (PostgreSQL LISTEN/NOTIFY)
- [ ] [S] Implementar endpoint /health com status de cada servico
- [ ] [M] Implementar fallback para Claude API (mensagem generica)

### Frontend -- Dashboard Admin [Fase 5]
- [ ] [L] Criar dashboard com graficos (Recharts ou similar)
- [ ] [M] Visao geral: taxa recuperacao, valor recuperado, valor em aberto
- [ ] [M] Aging report visual (barras empilhadas)
- [ ] [M] Grafico DSO tendencia (linha mensal)
- [ ] [M] Comparativo de reguas (tabela + grafico)
- [ ] [S] Performance por canal
- [ ] [S] ROI calculator
- [ ] [S] Exportacao CSV/PDF
- [ ] [S] Configuracao de alertas

### Testing [Todas as fases]
- [ ] [M] Testes unitarios para scoring (formula + segmentacao)
- [ ] [L] Testes de integracao para regua de cobranca (cron + envio + pausa + retomada)
- [ ] [M] Testes de integracao para webhook de pagamento (HMAC + idempotencia)
- [ ] [XL] Testes e2e: fluxo completo cobranca -> conversa -> pagamento -> confirmacao
- [ ] [L] Testes de carga: 50.000 faturas processadas pela regua
- [ ] [L] Testes de seguranca: isolamento multi-tenant (tenant A nao acessa dados de B)
- [ ] [M] Testes LGPD: anonimizacao e exportacao de dados
- [ ] [M] Testes de circuit breaker e self-healing
- [ ] [M] Testes de import assincrono (100k linhas, encoding, separador)
