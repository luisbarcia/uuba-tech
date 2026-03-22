# Modulo 8: Dashboard e Analytics

**Status:** Nao implementado

### Functional Requirements

**FR-088: Visao geral de recuperacao**
The dashboard shall exibir: taxa de recuperacao (%), valor recuperado no periodo, valor em aberto, e valor vencido -- com filtros por periodo, segmento, regua, e tenant (para admin global).

**FR-089: Aging report**
The dashboard shall exibir aging report com faixas: 1-15 dias, 16-30 dias, 31-60 dias, 61-90 dias, 90+ dias -- mostrando quantidade e valor por faixa.

**FR-090: DSO (Days Sales Outstanding)**
The dashboard shall calcular e exibir DSO medio da carteira, com tendencia historica (grafico de linha mensal) e comparativo com benchmark do setor quando disponivel.

**FR-091: Performance por regua**
Where multiplas reguas estao configuradas, the dashboard shall comparar taxa de resposta, taxa de acordo, tempo medio de resolucao, e valor recuperado entre elas.

**FR-092: Performance por canal**
The dashboard shall exibir metricas por canal: taxa de entrega, taxa de leitura, taxa de resposta, e taxa de conversao (pagamento) para WhatsApp (e futuros canais).

**FR-093: ROI da cobranca**
The dashboard shall calcular ROI: (valor recuperado - custo operacional) / custo operacional. Incluir custo por mensagem enviada, custo de gateway, e hora de atendente humano.

**FR-094: Exportacao de relatorios**
The dashboard shall permitir exportar dados em CSV e PDF para auditoria e apresentacao a gestao.

**FR-095: Alertas e notificacoes**
Where a taxa de recuperacao cai abaixo do threshold configurado (ex: <30%), the system shall enviar alerta ao administrador via email e/ou WhatsApp.

**FR-096: Promise-to-pay analytics**
The dashboard shall exibir analiticos de promessas de pagamento: taxa de cumprimento geral, taxa de cumprimento por segmento de devedor, taxa por dia da semana da promessa, valor medio das promessas cumpridas vs nao cumpridas, e tempo medio entre promessa e pagamento efetivo.

**FR-097: Dashboard de KPIs estrategicos**
The system shall oferecer dashboard de KPIs estrategicos (separado do operacional) com as seguintes metricas:
- **Lagging (mensal):** taxa de recuperacao, DSO medio, custo por real recuperado, ROI, taxa de acordo cumprido, churn de tenants.
- **Leading (semanal):** taxa de engajamento (respostas), taxa de leitura, taxa de clique em link de pagamento, taxa de promessa, taxa de escalacao humana, taxa de opt-out.
- **Produto (continuo):** time-to-first-collection, onboarding completion, bot accuracy, uptime.

**FR-098: Comparativo de A/B tests de reguas**
Where A/B tests de reguas estao ativos, the dashboard shall exibir comparativo de performance entre variantes: taxa de recuperacao, valor medio recuperado, tempo medio de resolucao, e intervalo de confianca estatistico (95%) para cada metrica.

**FR-099: Materialized views para performance**
The system shall utilizar materialized views no PostgreSQL (ou cache pre-computado em Redis) para todas as queries de dashboard, com refresh programado a cada 15 minutos para dados operacionais e a cada 1 hora para dados estrategicos.

### Acceptance Criteria

**AC-077: Dashboard carrega em menos de 3s com 50k faturas**
Given uma carteira com 50.000 faturas ativas,
When o usuario acessa o dashboard operacional,
Then todos os indicadores carregam em menos de 3 segundos,
And os dados refletem o ultimo refresh da materialized view (defasagem maxima de 15 minutos).

**AC-078: Aging report correto**
Given 100 faturas vencidas com distribuicao: 40 (1-15d), 30 (16-30d), 20 (31-60d), 10 (90+d),
When o aging report e renderizado,
Then os valores e quantidades por faixa correspondem exatamente.

**AC-079: ROI calculado corretamente**
Given R$ 100.000 recuperados, R$ 5.000 em custos (mensagens + gateway),
When o ROI e calculado,
Then deve exibir 1900% (19x retorno).

**AC-080: Promise-to-pay por segmento**
Given 200 promessas registradas no ultimo mes, sendo 120 de "bom pagador atrasado" e 80 de "recorrente",
When o analytics de promessas e consultado,
Then exibe taxa de cumprimento separada por segmento,
And exibe dia da semana com maior taxa de cumprimento.

**AC-081: A/B test comparativo**
Given regua A (controle, 500 faturas) e regua B (variante, 500 faturas) em A/B test,
When o comparativo e consultado,
Then exibe taxa de recuperacao de ambas com intervalo de confianca de 95%,
And indica se a diferenca e estatisticamente significativa.
