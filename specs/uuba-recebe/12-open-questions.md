# UUBA Recebe — Open Questions

### Tecnico

- [ ] **[Tecnico]** Evolution API vs Meta Cloud API para escala multi-tenant? Evolution e gratuita mas requer 1 container por numero. Meta Cloud suporta multiplos numeros em unico Business Manager. Decisao impacta arquitetura da Fase 3.
- [ ] **[Tecnico]** VPS Contabo atual suporta quantos tenants antes de precisar escalar? Fazer benchmark com 5, 10, 20 tenants simulados. Metricas: CPU, memoria, latencia, IOPS.
- [ ] **[Tecnico]** Whisper API (OpenAI) vs alternativa on-premise (faster-whisper) para transcricao de audio? Whisper API e mais simples mas tem custo por minuto e latencia de rede. On-premise requer GPU ou CPU potente.
- [ ] **[Tecnico]** Qual threshold de score para alterar regua automaticamente? Definir com dados reais apos ter pelo menos 1.000 devedores com historico.
- [ ] **[Tecnico]** PostgreSQL LISTEN/NOTIFY e suficiente para volume de eventos esperado (100 tenants x 10k msg/dia)? Ou Redis Pub/Sub desde o inicio?
- [ ] **[Tecnico]** Estrategia de versionamento de API (path /v1/ vs header)? Impacta todos os endpoints.

### Produto

- [ ] **[Produto]** Dashboard admin: aplicacao web separada ou integrada ao portal existente (uuba.tech/docs)?
- [ ] **[Produto]** Templates de regua por industria -- quais industrias priorizar? Sugestao: servicos recorrentes (academia, coworking), saude (clinicas), educacao (escolas).
- [ ] **[Produto]** Onboarding wizard: quais passos sao obrigatorios vs opcionais? Impacta time-to-first-collection.
- [ ] **[Produto]** Mecanica de parcelamento: gera novas faturas filhas? Aplica juros? Qual formula?

### Legal

- [ ] **[Legal]** Certificacao para operar como empresa de cobranca no Brasil? Verificar requisitos com advogado trabalhista/empresarial.
- [ ] **[Legal]** Limites de frequencia de contato variam por estado ou sao nacionais? CDC nao especifica quantidade, apenas "boas praticas".
- [ ] **[Legal]** Armazenamento de audio de devedor (LGPD): necessario consentimento explicito antes de transcrever?

### Negocio

- [ ] **[Negocio]** Precificacao hibrida (base + success fee): validar com 5 clientes potenciais antes de definir faixas finais.
- [ ] **[Negocio]** Custo operacional por tenant (VPS, APIs, mensagens): calcular break-even por tenant para definir preco minimo.
- [ ] **[Negocio]** SLA contratual: 99.5% uptime e viavel com infra atual (unica VPS Contabo)?
