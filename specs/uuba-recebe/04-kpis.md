# UUBA Recebe — Metricas de Sucesso (KPIs)

---

## 3. METRICAS DE SUCESSO (KPIs)

### Lagging Indicators (mensal)

| KPI | Definicao | Meta v1 | Meta v2 | Como medir |
|-----|-----------|---------|---------|------------|
| Taxa de Recuperacao | (Valor recuperado / Valor total vencido) x 100 | >=40% | >=55% | Query: SUM(valor WHERE status='pago' AND pago_em no periodo) / SUM(valor WHERE vencimento < hoje no periodo). Agregar por mes. |
| DSO Medio | Media de dias entre vencimento e pagamento de faturas pagas no periodo | <=25 dias | <=15 dias | Query: AVG(pago_em - vencimento) WHERE status='pago'. Exibir tendencia mensal em grafico de linha. |
| Custo por Real Recuperado | Custo operacional total / Valor total recuperado | <=R$0,05 | <=R$0,03 | Custo = (mensagens_enviadas x custo_por_msg) + (horas_atendente x custo_hora) + infra_mensal. Dividir pelo valor recuperado. |
| ROI | (Valor recuperado - Custo operacional) / Custo operacional | >=10x | >=20x | Usar mesmos valores de custo e recuperacao. Exibir como multiplicador (ex: 19x). |
| Taxa de Acordo Cumprido | (Acordos pagos integralmente / Total de acordos fechados) x 100 | >=70% | >=85% | Requer entidade Acordo com status terminal (cumprido, quebrado, renegociado). Agregar por mes. |
| Net Revenue Retention | Receita recorrente do tenant no mes atual / Receita do mesmo tenant 12 meses atras | >=100% | >=110% | Requer tracking de receita por tenant ao longo do tempo. Formula: MRR(t) / MRR(t-12). |
| Churn de Tenants | (Tenants que cancelaram no mes / Total de tenants ativos no inicio do mes) x 100 | <=5%/mes | <=3%/mes | Requer registro de data de ativacao e cancelamento de cada tenant. |

### Leading Indicators (semanal)

| KPI | Definicao | Meta v1 | Como medir |
|-----|-----------|---------|------------|
| Taxa de Engajamento | (Devedores que responderam / Devedores contatados) x 100 | >=35% | Contar devedores unicos que enviaram pelo menos 1 mensagem apos receber cobranca na semana. |
| Taxa de Leitura | (Mensagens lidas / Mensagens entregues) x 100 | >=80% | Usar status de leitura do WhatsApp (read receipt). Cuidado: nem todos ativam. Medir sobre entregas confirmadas. |
| Taxa de Clique no Link | (Cliques unicos no link de pagamento / Mensagens com link enviadas) x 100 | >=25% | Usar link com tracking (UTM ou shortener com analytics). Contar clique unico por devedor por fatura. |
| Taxa de Promessa | (Promessas de pagamento registradas / Devedores contatados) x 100 | >=20% | Contar eventos "promessa_registrada" via bot. Dividir por devedores unicos contatados na semana. |
| Taxa de Escalacao | (Conversas escaladas para humano / Total de conversas do bot) x 100 | <=15% | Contar eventos "escalacao_chatwoot". Taxa alta indica bot ineficaz ou limites muito restritos. |
| Taxa de Opt-out | (Opt-outs solicitados / Devedores contatados) x 100 | <=3% | Contar eventos "opt_out_registrado". Taxa alta indica abordagem agressiva demais. |
| Score Medio da Carteira | Media do score de probabilidade de pagamento de todos os devedores ativos | Crescente semana a semana | Calcular AVG(score) por semana. Tendencia crescente indica carteira mais saudavel. |
| Tempo de Resposta do Bot | p95 do tempo entre receber mensagem e enviar resposta | <=5s | Medir timestamp_resposta - timestamp_recebimento. p95 para desconsiderar outliers de rede. |

### Metricas de Produto (continuo)

| KPI | Definicao | Meta | Como medir |
|-----|-----------|------|------------|
| Time-to-First-Collection | Horas entre primeiro import do tenant e primeiro pagamento recuperado | <=72h | Medir diferenca entre timestamp do primeiro import concluido e timestamp do primeiro webhook payment.confirmed para aquele tenant. |
| Onboarding Completion | (Tenants que concluiram onboarding / Tenants que iniciaram) x 100 | >=80% | Definir onboarding completo = tenant provisionado + primeiro import realizado + primeira cobranca enviada. Trackear cada etapa. |
| Bot Accuracy | (Respostas corretas do bot / Total de respostas do bot) x 100 | >=90% | Amostragem manual semanal de 50 conversas + flag "resposta_incorreta" quando atendente corrige apos escalacao. |
| Uptime | (Tempo disponivel / Tempo total) x 100 para API e bot | >=99.5% | Health check a cada 30s via monitor externo (UptimeRobot, Pingdom). Calcular SLA mensal. |
| NPS Tenant | Net Promoter Score dos clientes (empresas) | >=40 | Pesquisa trimestral via email/formulario. Promotores (9-10) - Detratores (0-6). |
| CSAT Devedor | Satisfacao do devedor apos interacao com bot ou atendente | >=3.5/5 | Pesquisa pos-atendimento (1 pergunta): "Como foi sua experiencia? 1 a 5". Enviar apos resolucao de escalacao. |

### Instrumentacao Necessaria

Para medir todos os KPIs acima, implementar:

- [ ] **Tabela `events`**: registrar todos os eventos do sistema com schema (event_type, tenant_id, devedor_id, fatura_id, timestamp, metadata_json). Tipos: mensagem_enviada, mensagem_lida, mensagem_respondida, link_clicado, promessa_registrada, pagamento_confirmado, escalacao_chatwoot, opt_out_registrado, acordo_fechado, acordo_cumprido, acordo_quebrado, regua_esgotada, import_concluido, onboarding_etapa_concluida.
- [ ] **Materialized views** para agregacoes mensais e semanais (taxa recuperacao, DSO, engajamento). Refresh via cron a cada 1h.
- [ ] **Tracking de links**: shortener proprio ou UTM params em todos os links de pagamento enviados.
- [ ] **Health check endpoint** `/health` com resposta em <100ms, monitorado externamente.
- [ ] **Custos por mensagem**: tabela `costs` com custo unitario por tipo de mensagem (WhatsApp template, session, etc.) atualizado conforme precificacao Meta/Evolution.
- [ ] **Dashboard de KPIs**: tela dedicada com todos os indicadores acima, filtros por periodo e tenant (para admin da plataforma) ou apenas proprio tenant (para cliente).
- [ ] **Alertas automaticos**: quando qualquer KPI sai do range aceitavel, disparar notificacao ao admin via email e/ou WhatsApp. Configuravel por tenant para KPIs relevantes (taxa de recuperacao, opt-out).
- [ ] **Amostragem de Bot Accuracy**: job semanal que seleciona 50 conversas aleatorias e marca para revisao manual. Interface de revisao no admin.
- [ ] **CSAT pos-atendimento**: mensagem automatica apos resolucao de escalacao no Chatwoot perguntando satisfacao (1-5).
