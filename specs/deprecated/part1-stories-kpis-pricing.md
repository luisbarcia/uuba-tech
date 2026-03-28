# UUBA Recebe -- Spec v2 / Parte 1

> Stories, Jornadas, KPIs e Precificacao

---

## 1. USER STORIES

### Empresa (Tenant)

**US-001** -- Como **empresa-cliente**, quero **importar uma planilha CSV/Excel de titulos vencidos e que a cobranca comece automaticamente** para que eu nao precise configurar nada manualmente apos o upload.
[Modulos: Import, Regua, Multi-tenancy]

**US-002** -- Como **empresa-cliente**, quero **ver o ROI da cobranca em tempo real no dashboard** para que eu possa demonstrar o valor do servico ao meu financeiro e justificar o investimento.
[Modulos: Dashboard, Analytics]

**US-003** -- Como **empresa-cliente**, quero **configurar limites do bot (desconto maximo, parcelas maximas, tom)** para que a negociacao automatica respeite minhas politicas comerciais.
[Modulos: Bot IA, Regua]

**US-004** -- Como **empresa-cliente**, quero **receber alertas quando a taxa de recuperacao cai abaixo de um threshold configurado** para que eu possa intervir antes de perder receita.
[Modulos: Dashboard, Alertas]

**US-005** -- Como **empresa-cliente**, quero **comparar a performance de reguas de cobranca diferentes** para que eu identifique qual estrategia funciona melhor para cada perfil de devedor.
[Modulos: Dashboard, Regua, Scoring]

**US-006** -- Como **empresa-cliente**, quero **ver o aging report da minha carteira de recebiveis** para que eu entenda a distribuicao do atraso e tome decisoes sobre provisao e prioridades.
[Modulos: Dashboard, Analytics]

**US-007** -- Como **empresa-cliente**, quero **exportar relatorios de cobranca em PDF e CSV** para que eu possa apresentar resultados a diretoria e auditoria.
[Modulos: Dashboard, Analytics]

**US-008** -- Como **empresa-cliente**, quero **ter garantia de compliance automatico (horarios, frequencia, LGPD, CDC)** para que eu nao corra risco legal ao usar a cobranca automatizada.
[Modulos: Compliance, Regua, Bot IA]

**US-009** -- Como **empresa-cliente**, quero **completar o onboarding em menos de 30 minutos** para que eu consiga comecar a recuperar receita no mesmo dia da contratacao.
[Modulos: Multi-tenancy, Import, Onboarding]

**US-010** -- Como **empresa-cliente**, quero **ser alertada quando a taxa de acordo cumprido cai** para que eu possa ajustar as condicoes de negociacao e reduzir a quebra de acordos.
[Modulos: Dashboard, Alertas, Gestao de Parcelas]

### Devedor

**US-011** -- Como **devedor**, quero **entender exatamente quanto devo, com detalhamento por fatura** para que eu tenha clareza sobre minha situacao financeira antes de decidir pagar.
[Modulos: Bot IA, Portal do Devedor]

**US-012** -- Como **devedor**, quero **pagar via Pix em menos de 2 minutos apos receber a cobranca** para que eu resolva a pendencia sem burocracia.
[Modulos: Portal do Devedor, Pagamento, Bot IA]

**US-013** -- Como **devedor**, quero **negociar parcelamento ou desconto diretamente pelo WhatsApp com o bot** para que eu nao precise ligar ou acessar outro sistema.
[Modulos: Bot IA, Regua, Pagamento]

**US-014** -- Como **devedor**, quero **falar com um humano quando o bot nao resolve meu problema** para que eu tenha uma alternativa quando a situacao e complexa.
[Modulos: Bot IA, Chatwoot, Escalacao]

**US-015** -- Como **devedor**, quero **parar de receber mensagens de cobranca assim que eu pagar** para que eu nao seja incomodado desnecessariamente.
[Modulos: Regua, Pagamento, Bot IA, Compliance]

**US-016** -- Como **devedor**, quero **acessar minhas faturas por um link sem precisar de login ou senha** para que eu possa consultar e pagar a qualquer momento.
[Modulos: Portal do Devedor]

**US-017** -- Como **devedor**, quero **receber confirmacao imediata quando meu pagamento for processado** para que eu tenha tranquilidade de que a pendencia foi resolvida.
[Modulos: Pagamento, Bot IA, Regua]

**US-018** -- Como **devedor**, quero **pedir opt-out de um canal especifico de cobranca** para que eu escolha como prefiro ser contatado (ou nao).
[Modulos: Compliance, Bot IA, Regua]

### Operador/Admin

**US-019** -- Como **operador de atendimento**, quero **ver o historico completo do devedor (mensagens, promessas, pagamentos, score) ao assumir uma escalacao** para que eu tenha contexto total sem precisar perguntar novamente ao devedor.
[Modulos: Bot IA, Chatwoot, Dashboard, Scoring]

**US-020** -- Como **administrador da plataforma**, quero **provisionar um novo cliente (tenant) em minutos com database, API key e numero WhatsApp** para que o onboarding seja rapido e eu nao dependa de devops manual.
[Modulos: Multi-tenancy, Onboarding]

---

## 2. JORNADAS

### Jornada da Empresa (Tenant)

#### Fase 1: Descoberta

1. Empresa identifica problema de inadimplencia (taxa de recuperacao <25% com metodo atual).
2. Encontra UUBA Recebe via indicacao, site ou conteudo.
3. Acessa pagina do produto, ve ROI prometido (10x+) e benchmarks.
4. Solicita demonstracao ou inicia trial.

[GAPS]
- Nao ha pagina de demonstracao interativa ou simulador de ROI. FR necessario: simulador de ROI na landing page (input: volume de titulos + valor medio + taxa atual; output: projecao de recuperacao e economia).

#### Fase 2: Onboarding (meta: menos de 30 minutos)

1. Admin cria tenant via painel ou API.
2. Sistema provisiona database, schema, tabelas e credenciais automaticamente.
3. Numero WhatsApp e provisionado (Meta Cloud API ou Evolution API).
4. Empresa recebe API key e acesso ao dashboard.
5. Wizard de onboarding guia configuracao inicial: dados da empresa, logo, limites do bot, regua padrao.

[GAPS]
- Wizard de onboarding nao existe. FR necessario: fluxo guiado com 5 passos (dados empresa, upload logo, config bot, preview regua, primeiro import).
- Provisionamento de numero WhatsApp depende de decisao Evolution API vs Meta Cloud API (ver findings). FR necessario: provisioning automatizado para o modelo escolhido.
- Falta preview da regua padrao antes de ativar. FR necessario: simulador de regua (dry run) para tenant visualizar sequencia antes de ir a producao.

#### Fase 3: Primeiro Import

1. Empresa exporta titulos vencidos do ERP/planilha.
2. Faz upload de CSV/Excel no dashboard.
3. Sistema valida, mapeia colunas se necessario, processa em background (async).
4. Relatorio de import mostra: X aceitos, Y rejeitados com motivos.
5. Clientes (devedores) sao criados via upsert por documento.
6. Notificacao: "Import concluido. X titulos prontos para cobranca."

[GAPS]
- Import atualmente e sincrono -- timeout em arquivos grandes. FR necessario: endpoint async (retorna 202 + job_id, status via polling).
- Falta preview do import antes de confirmar. FR necessario: tela de preview mostrando primeiras 10 linhas parseadas para validacao humana.
- Encoding e separadores nao padrao causam falha silenciosa. FR necessario: deteccao automatica de encoding (UTF-8, ISO-8859-1, Windows-1252) e separador (virgula, ponto-e-virgula, tab).

#### Fase 4: Primeiras Cobrancas

1. Regua padrao e ativada automaticamente para faturas importadas.
2. Sistema respeita compliance: horarios, frequencia, feriados.
3. Primeiras mensagens sao enviadas via WhatsApp no proximo horario util.
4. Dashboard mostra em tempo real: enviadas, lidas, respondidas, pagas.
5. Empresa recebe notificacao do primeiro pagamento recuperado.

[GAPS]
- Regua comeca em D-3, deveria comecar D-14 a D-30 (pre-delinquency). FR necessario: regua preventiva com passos pre-vencimento configuravel (D-30 a D-1).
- Nao ha notificacao do primeiro pagamento ao tenant. FR necessario: evento "first_payment_recovered" com notificacao push/email ao admin.
- Falta A/B testing de reguas. FR necessario: motor de A/B para testar variantes de regua com distribuicao configuravel e promocao automatica da vencedora.

#### Fase 5: Otimizacao

1. Empresa analisa dashboard: taxa de recuperacao, DSO, aging, performance por regua.
2. Compara regua padrao com regua customizada.
3. Ajusta limites do bot (desconto, parcelas).
4. Cria segmentos de devedores por perfil de risco.
5. Scoring heuristico comeca a alimentar priorizacao automatica.

[GAPS]
- Scoring ML irreal para v1. FR necessario: scoring heuristico com formula explicita (score = base(50) + historico(-20 a +20) + atraso(-15 a +15) + engajamento(-10 a +10) + valor(-5 a +5)).
- Falta simulador de regua para testar antes de ativar. FR necessario: dry run que mostra quantos devedores seriam impactados e em quais dias.

#### Fase 6: Expansao

1. Empresa aumenta volume de titulos importados.
2. Integra ERP via webhook para import automatico.
3. Contrata plano superior (mais volume, mais canais futuros).
4. Indica outras empresas (referral).

[GAPS]
- Sem programa de referral estruturado. FR necessario: sistema de indicacao com tracking e beneficio (desconto ou credito).
- Webhook de ERP sem validacao HMAC. FR necessario: assinatura HMAC obrigatoria em webhooks recebidos.

---

### Jornada do Devedor

#### Cenario A: Pagamento Rapido (~40% dos devedores)

Perfil: devedor que esqueceu ou atrasou por desorganizacao. Divida pequena a media.

1. [D-3] Recebe lembrete amigavel via WhatsApp: "Oi, {nome}. Lembrete: sua fatura de R$ {valor} vence em 3 dias. Pague agora com desconto de 5%: {link}".
2. [D-3] Abre o link no celular. Portal carrega sem login (token JWT).
3. [D-3] Ve fatura detalhada: valor, vencimento, descricao, NF.
4. [D-3] Clica "Pagar com Pix". QR code aparece. Paga em 30 segundos.
5. [D-3] Webhook do gateway confirma pagamento. Status atualiza para "pago".
6. [D-3] Bot envia mensagem: "Pagamento confirmado. Obrigado, {nome}!"
7. Regua e desativada para esta fatura. Fim.

Alternativa D+1: devedor nao pagou antes do vencimento, recebe cobranca no D+1, paga pelo portal.

[GAPS]
- Desconto por antecipacao nao implementado. FR necessario: configuracao de desconto por antecipacao (ex: 5% se pagar ate D-1, 3% se pagar ate D+3).
- Confirmacao de pagamento Pix nao e tempo real (depende de webhook). FR necessario: polling de fallback caso webhook demore mais de 60 segundos.
- QR code pode expirar antes do devedor pagar. FR necessario: deteccao de QR expirado + geracao automatica de novo QR com notificacao.

#### Cenario B: Negociacao via Bot (~25% dos devedores)

Perfil: devedor que reconhece a divida mas nao tem condicoes de pagar o valor integral.

1. [D+1] Recebe cobranca neutra via WhatsApp com link de pagamento.
2. [D+1] Responde: "nao consigo pagar tudo agora".
3. [D+1] Bot identifica intencao de negociacao. Consulta limites configurados pelo tenant.
4. [D+1] Bot propoe: "Entendo, {nome}. Posso oferecer: (1) Pague R$ {valor_com_desconto} a vista com 10% de desconto; (2) Parcele em 3x de R$ {parcela} sem juros. Qual prefere?"
5. [D+1] Devedor escolhe opcao 2 (parcelamento).
6. [D+1] Bot gera acordo: 3 parcelas com vencimentos D+5, D+35, D+65.
7. [D+1] Bot envia link de pagamento da primeira parcela.
8. [D+5] Devedor paga parcela 1. Bot confirma e agenda lembrete da parcela 2.
9. [D+33] Bot envia lembrete: "Lembrete: parcela 2 de R$ {parcela} vence em 2 dias. {link}".
10. Ciclo repete ate ultima parcela.

[GAPS]
- Gestao de parcelas nao implementada. FR necessario: entidade "Acordo" com parcelas vinculadas, status por parcela, lembretes automaticos, e acao quando parcela atrasa.
- Mecanica de parcelamento vaga: gera novas faturas? Cobra juros? FR necessario: definicao explicita -- acordo cria N faturas filhas com referencia ao acordo-pai.
- Renegociacao proativa ausente. FR necessario: se devedor quebra acordo, cooling period de 7 dias + nova proposta com condicoes ajustadas + limite de 2 renegociacoes por fatura.

#### Cenario C: Escalacao para Humano (~15% dos devedores)

Perfil: devedor irritado, situacao complexa, ou demanda fora dos limites do bot.

1. [D+3] Recebe cobranca neutra. Responde com raiva: "Para de me mandar mensagem! Ja paguei isso!"
2. [D+3] Bot detecta sentimento negativo (raiva). Ajusta tom para empatico: "Entendo sua frustacao, {nome}. Vou verificar seus pagamentos."
3. [D+3] Bot consulta faturas. Nao encontra pagamento registrado.
4. [D+3] Bot responde: "Nao localizei pagamento para a fatura NF-{numero}. Se voce pagou, pode enviar o comprovante? Ou prefere falar com nosso atendimento?"
5. [D+3] Devedor responde: "Quero falar com alguem."
6. [D+3] Bot escala para Chatwoot com resumo automatico: devedor, faturas, historico de conversa, sentimento detectado, motivo da escalacao.
7. [D+3] Atendente ve contexto completo. Resolve sem repetir perguntas.
8. Atendente confirma pagamento (comprovante), atualiza status, envia confirmacao.

[GAPS]
- Handoff bot-para-humano sem resumo estruturado. FR necessario: resumo automatico para o atendente com campos: devedor (nome, documento, score), faturas em aberto (valor, atraso), historico recente (ultimas 5 mensagens), sentimento detectado, motivo da escalacao.
- Confirmacao via comprovante nao implementada. FR necessario: devedor envia imagem de comprovante, sistema faz OCR para extrair valor/data/codigo, operador valida.
- Falta metricas de escalacao (tempo de resolucao, satisfacao). FR necessario: CSAT pos-atendimento + tempo medio de resolucao por atendente.

#### Cenario D: Nao-Responsivo (~20% dos devedores)

Perfil: devedor que ignora todas as tentativas de contato. Pode ser numero errado, devedor cronico, ou telefone reciclado.

1. [D-3] Lembrete amigavel enviado. Sem leitura.
2. [D+1] Cobranca neutra enviada. Entregue mas nao lida.
3. [D+3] Follow-up. Sem resposta.
4. [D+7] Mensagem firme. Sem resposta.
5. [D+15] Mensagem urgente final. Sem resposta.
6. Regua esgota todos os passos. Fatura marcada como "regua_esgotada".
7. [Acao pos-regua] Sistema aplica tratamento definido pelo tenant: (a) pausa permanente; (b) reinicio de regua apos cooling period de 30 dias; (c) escalacao para tratamento manual; (d) encaminhamento para cobranca juridica (out of scope v1, mas flag para futuro).
8. Tenant recebe relatorio de faturas nao recuperadas com sugestao de acao.

[GAPS]
- Acao pos-regua nao definida na spec v1. FR necessario: configuracao por tenant de acao pos-regua com opcoes (pausa, reinicio, escalacao, export para juridico).
- Telefone reciclado nao detectado. FR necessario: se numero nao recebe mensagem (erro de entrega) em 3 tentativas, marcar como "numero_invalido" e pausar.
- Nao ha mecanismo para tentar canal alternativo. FR necessario (v2): fallback para email/SMS quando WhatsApp falha (out of scope v1, mas arquitetura deve prever).
- Falta relatorio especifico de nao-responsivos para o tenant. FR necessario: relatorio "faturas sem resposta" com aging, valor total, e sugestoes de acao.

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

---

## 4. MODELO DE PRECIFICACAO

### Opcao A: Porcentagem do Valor Recuperado (Success Fee)

**Modelo**: cobrar de 5% a 15% sobre cada real efetivamente recuperado. Proposta padrao: 10%.

**Pros**:
- Alinhamento total de incentivos: UUBA so ganha quando o cliente ganha.
- Barreira de entrada zero: cliente nao paga nada adiantado.
- Facil de comunicar: "voce so paga quando recuperar".
- Modelo mais comum no mercado de cobranca terceirizada (benchmark: 15-25% em cobranca tradicional; 5-15% em cobranca digital).

**Contras**:
- Receita imprevisivel para UUBA: depende do volume e perfil da carteira do cliente.
- Clientes com carteiras de alto valor e baixa inadimplencia geram muita receita para o cliente mas pouca para UUBA (10% de R$1.000 = R$100, mesmo custando a mesma infra).
- Risco de selecao adversa: clientes com carteiras muito ruins (taxa recuperacao <15%) geram pouca receita e muito custo.
- Dificil escalar sem capital de giro (custo de infra e mensagens e fixo, receita e variavel).

**Benchmark**: TrueAccord cobra success fee variavel (nao publicado, estimado 10-20%). Cobranca juridica BR cobra 15-30%. Cobranca amigavel digital BR cobra 8-15%.

**Projecao para 10 clientes com carteira media de R$100.000/mes em titulos vencidos**:

| Cenario | Taxa recuperacao | Valor recuperado/mes | Receita UUBA (10%) | Custo estimado/mes |
|---------|-----------------|---------------------|---------------------|--------------------|
| Pessimista | 25% | R$250.000 | R$25.000 | R$8.000 |
| Realista | 40% | R$400.000 | R$40.000 | R$8.000 |
| Otimista | 55% | R$550.000 | R$55.000 | R$8.000 |

Custo estimado: infra VPS (R$500) + WhatsApp msgs (R$3.000 para ~30k msgs a R$0,10) + LLM API (R$2.000) + operacao (R$2.500).

---

### Opcao B: Mensalidade Fixa por Faixa

**Modelo**: cobrar mensalidade fixa baseada no volume de faturas/devedores.

| Faixa | Limite | Mensalidade |
|-------|--------|-------------|
| Starter | Ate 200 faturas/mes | R$297/mes |
| Business | Ate 1.000 faturas/mes | R$697/mes |
| Enterprise | Ate 5.000 faturas/mes | R$1.497/mes |
| Custom | Acima de 5.000 | Sob consulta |

**Pros**:
- Receita previsivel e recorrente para UUBA (MRR estavel).
- Facil de planejar custos e investimentos.
- Cliente sabe exatamente quanto vai pagar.
- Modelo SaaS padrao, familiar para PMEs.

**Contras**:
- Desalinhamento de incentivos: UUBA ganha o mesmo independente do resultado.
- Barreira de entrada: cliente paga antes de ver resultado.
- Dificil justificar para clientes com carteiras pequenas ("pago R$697 e recuperei R$500?").
- Clientes podem sentir que estao pagando por algo que "nao funciona" nos primeiros meses.

**Benchmark**: ferramentas SaaS de cobranca (Neofin, Assertiva) cobram R$200-2.000/mes por faixa. Plataformas de CRM/ERP cobram modelos similares.

**Projecao para 10 clientes distribuidos entre faixas**:

| Distribuicao | Clientes | Receita mensal |
|-------------|----------|----------------|
| 5 Starter + 3 Business + 2 Enterprise | 10 | R$5.970/mes |
| 3 Starter + 4 Business + 3 Enterprise | 10 | R$8.170/mes |
| 2 Starter + 3 Business + 5 Enterprise | 10 | R$10.070/mes |

Receita mais baixa que success fee para carteiras grandes, mas mais previsivel.

---

### Opcao C: Hibrido -- Base Mensal + Success Fee

**Modelo**: mensalidade base menor + porcentagem sobre valor recuperado.

| Faixa | Base mensal | Success fee |
|-------|-------------|-------------|
| Starter | R$197/mes | 7% sobre recuperado |
| Business | R$397/mes | 5% sobre recuperado |
| Enterprise | R$497/mes | 3% sobre recuperado |

**Pros**:
- Equilibrio entre previsibilidade (base) e alinhamento (success fee).
- Base cobre custos fixos de infra; success fee gera upside.
- Cliente paga menos fixo que Opcao B, e menos variavel que Opcao A.
- Modelo escala bem: clientes grandes pagam base baixa mas geram volume no success fee.

**Contras**:
- Mais complexo de comunicar: dois componentes.
- Cliente pode questionar a base mensal ("por que pago fixo se tambem pago por resultado?").
- Requer sistema de billing mais sofisticado (fatura = base + variavel calculado sobre recuperacao do periodo).

**Benchmark**: InDebted usa modelo hibrido (nao publicado). Empresas de cobranca premium cobram retainer + success fee. Modelo comum em consultorias de resultado.

**Projecao para 10 clientes Business com carteira de R$100.000/mes**:

| Cenario | Recuperado/mes | Base | Success (5%) | Receita total | Receita/cliente |
|---------|---------------|------|-------------|---------------|-----------------|
| Pessimista | R$250.000 | R$3.970 | R$12.500 | R$16.470 | R$1.647 |
| Realista | R$400.000 | R$3.970 | R$20.000 | R$23.970 | R$2.397 |
| Otimista | R$550.000 | R$3.970 | R$27.500 | R$31.470 | R$3.147 |

---

### Opcao D: Por Mensagem Enviada

**Modelo**: cobrar por mensagem de cobranca enviada (R$0,15-0,50 por mensagem).

**Pros**:
- Modelo simples e transparente.
- Escala diretamente com uso.

**Contras**:
- Incentivo perverso: UUBA ganha mais enviando mais mensagens, mesmo que nao resultem em pagamento.
- Contradiz objetivo de eficiencia (menos mensagens, mais resultado).
- Cliente pode sentir que esta pagando por "spam".
- Risco reputacional: modelo incentiva quantidade sobre qualidade.
- Nao alinha com proposta de valor (resultado, nao volume).

**Benchmark**: provedores de WhatsApp cobram por mensagem (R$0,05-0,15), mas sao infraestrutura, nao servico de resultado. Nenhum concorrente relevante de cobranca cobra por mensagem.

**Projecao para 10 clientes com 500 devedores cada, regua de 5 msgs**:

| Volume | Preco/msg | Receita mensal | vs Success fee 10% |
|--------|-----------|----------------|---------------------|
| 25.000 msgs | R$0,25 | R$6.250 | 6x menor que cenario realista |
| 25.000 msgs | R$0,50 | R$12.500 | 3x menor que cenario realista |

Receita significativamente menor e desalinhada. Nao recomendado.

---

### Recomendacao

**Lancamento (primeiros 6 meses): Opcao A -- Success Fee puro de 10%.**

Justificativa:
- Remove barreira de entrada para os primeiros clientes. Argumento de venda imbativel: "voce so paga quando recuperar."
- Permite acumular cases de sucesso com dados reais (taxa de recuperacao, ROI, DSO).
- 10% e competitivo vs cobranca tradicional (15-25%) e suficiente para cobrir custos com 10+ clientes.
- Risco controlado: custo fixo de infra e baixo (~R$8.000/mes total), e se a plataforma nao recupera, o custo de mensagens tambem e baixo.

**Apos 6 meses (com cases): migrar para Opcao C -- Hibrido.**

Justificativa:
- Com cases provando ROI de 10x+, justifica-se cobrar base mensal.
- Base mensal garante receita recorrente previsivel para UUBA.
- Success fee mantem alinhamento de incentivos.
- Clientes existentes podem migrar gradualmente (oferecer desconto no success fee em troca de base).
- Modelo escala melhor: 50 clientes pagando R$397/mes base = R$19.850/mes garantidos antes de qualquer recuperacao.

**Regra de transicao**: clientes que entraram na Opcao A mantem o modelo por 12 meses. Apos 12 meses, migram para Opcao C com success fee reduzido (5% em vez de 7%) como beneficio de early adopter.

---

### TODOs para Decisao Final de Precificacao

- [ ] Validar custo real por mensagem WhatsApp no modelo escolhido (Evolution API vs Meta Cloud API). Meta Cloud API cobra ~R$0,08 por mensagem utility e ~R$0,25 por marketing. Evolution API tem custo de infra mas sem custo por mensagem.
- [ ] Definir se success fee incide sobre valor nominal da fatura ou valor efetivamente pago (com desconto). Recomendacao: sobre valor efetivamente pago para evitar disputa.
- [ ] Modelar cenario de selecao adversa: o que acontece se os 10 primeiros clientes tiverem carteiras com taxa de recuperacao <20%? Qual o breakeven minimo?
- [ ] Calcular custo real da LLM (Claude API) por conversa media. Estimar: 3-5 turnos por devedor, ~2.000 tokens por turno, custo Sonnet por token.
- [ ] Definir politica de cobranca do success fee: cobrar mensalmente sobre valor recuperado no periodo? Ou por evento (cada pagamento confirmado gera fatura)? Recomendacao: mensal, com relatorio detalhado.
- [ ] Decidir se ha minimo mensal no success fee (ex: se recuperou R$0, paga R$0? Ou ha um piso de R$97?). Recomendacao: sem piso nos primeiros 6 meses.
- [ ] Benchmark com 3-5 empresas-alvo: apresentar Opcao A e medir receptividade antes de lancar.
- [ ] Definir mecanismo de billing: fatura manual via Conta Azul ou automatizado via API.

---

*Parte 1 da Spec v2 -- gerada em 2026-03-22*
*Proximas partes: Part 2 (Functional Requirements revisados), Part 3 (Arquitetura e NFRs), Part 4 (Roadmap e Sprints)*
