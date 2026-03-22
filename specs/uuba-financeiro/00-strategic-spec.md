# UUBA Financeiro -- Spec Estrategica

**Tagline:** "Depto financeiro completo. Sem montar equipe."

**Status:** Rascunho estrategico
**Ultima atualizacao:** 2026-03-22
**Autor:** Equipe UUBA Tech

---

## 1. Overview

O UUBA Financeiro entrega um departamento financeiro operacional completo para empresas que nao possuem estrutura interna. Nao se trata de mais uma ferramenta de BI financeiro ou dashboard bonito -- o produto EXECUTA operacoes financeiras de verdade.

Enquanto ferramentas como FinDrive focam em mostrar dados (DRE, indicadores, integracao com Conta Azul), o UUBA Financeiro vai alem: ele categoriza lancamentos, concilia extratos, projeta cenarios, dispara alertas e, no modelo BPO, coloca uma equipe da UUBA operando como extensao do time do cliente.

**Diferencial central:** FinDrive mostra. UUBA faz.

**Modelo de operacao:**
- **SaaS puro:** o cliente usa a plataforma com autonomia, apoiado por IA
- **BPO (Business Process Outsourcing):** a equipe UUBA opera o financeiro pelo cliente, usando a mesma plataforma como ferramenta de trabalho

Essa dualidade (ferramenta + servico) cria uma barreira competitiva dificil de replicar: concorrentes de software nao tem operacao, e BPOs tradicionais nao tem tecnologia proprietaria.

---

## 2. Proposta de Valor

- **Departamento financeiro pronto para uso:** DRE, fluxo de caixa, conciliacao, contas a pagar/receber -- tudo funcional desde o dia 1, sem precisar contratar controller, analista ou assistente financeiro
- **Inteligencia, nao apenas dados:** categorizacao automatica por IA, alertas proativos de risco financeiro e projecoes preditivas que antecipam problemas antes que virem crise
- **Modo BPO como diferencial competitivo:** para empresas que preferem delegar, a equipe UUBA opera o financeiro como extensao do time -- com SLA, processos padronizados e a mesma plataforma
- **Integrado nativamente ao ecossistema UUBA:** dados de cobranca (Recebe), inteligencia de dados (Nexo) e dashboards (360) alimentam o Financeiro automaticamente, eliminando retrabalho e planilhas paralelas

---

## 3. Usuarios-alvo

### 3.1 PMEs sem departamento financeiro (faixa principal)
Empresas de 10 a 100 funcionarios que hoje resolvem o financeiro com planilhas, o contador, e o dono acumulando funcoes. Faturamento tipico: R$ 500k a R$ 10M/ano. Precisam de estrutura mas nao tem volume para justificar uma equipe dedicada.

### 3.2 Empresas com controller solo
Medias empresas (100-500 funcionarios) que tem um controller ou gerente financeiro sobrecarregado. A plataforma amplifica a capacidade dessa pessoa, automatizando tarefas operacionais e liberando tempo para analise estrategica.

### 3.3 Holdings e grupos empresariais
Estruturas com multiplas empresas (CNPJs) que precisam de visao consolidada. Cada empresa opera como tenant separado, mas a holding tem visao agregada. O modelo BPO se encaixa bem aqui: a UUBA opera o financeiro das subsidiarias menores.

### 3.4 Startups em crescimento
Empresas pos-seed/Series A que precisam profissionalizar o financeiro para reportar a investidores. Relatórios executivos automatizados para board meetings sao um diferencial forte nesse segmento.

---

## 4. Features Agrupadas

### 4.1 DRE Automatizado
Demonstrativo de Resultados do Exercicio gerado automaticamente a partir dos dados importados. A IA classifica lancamentos em categorias contabeis (receita operacional, custos fixos/variaveis, despesas administrativas) com acuracia progressiva -- quanto mais o cliente valida, melhor fica a categorizacao.

- Categorizacao inteligente por IA (Claude) com aprendizado por tenant
- Plano de contas configuravel por segmento (servicos, comercio, industria)
- DRE mensal, trimestral e anual com comparativos
- Drill-down: do indicador ate o lancamento individual
- Exportacao para formatos contabeis padrao

### 4.2 Fluxo de Caixa Preditivo
Projecao de caixa para 30, 60 e 90 dias baseada em dados reais (contas a receber, recorrencias, sazonalidade historica) e nao em estimativas manuais.

- Projecao automatica com base em historico e recorrencias identificadas
- Cenario pessimista, realista e otimista
- Inclusao de contas a receber (integrado com Recebe) e contas a pagar
- Alerta automatico quando a projecao indica caixa negativo
- Visualizacao de timeline com marcos criticos

### 4.3 Conciliacao Bancaria Automatica
Cruzamento automatico entre extratos bancarios (via Nexo/Open Finance) e lancamentos internos. Reducao drastica do trabalho manual de conferencia.

- Matching automatico por valor, data e descricao (fuzzy matching)
- Fila de pendencias para itens nao conciliados (resolucao assistida por IA)
- Suporte a multiplas contas bancarias por tenant
- Historico de conciliacoes com auditoria
- Regras customizaveis por cliente (ex: tolerancia de R$ 0,01 em arredondamento)

### 4.4 Contas a Pagar e a Receber
Gestao completa do ciclo de pagamentos e recebimentos, integrada nativamente com o UUBA Recebe para contas a receber.

- Cadastro de fornecedores e contas a pagar com recorrencia
- Contas a receber alimentadas automaticamente pelo Recebe (boletos, Pix, cartao)
- Agendamento de pagamentos com aprovacao (workflow configuravel)
- Indicadores de aging (inadimplencia por faixa de atraso)
- Integracao com calendario financeiro do tenant

### 4.5 Projecao de Cenarios (What-if Analysis)
Simulacao de cenarios financeiros para apoiar decisoes estrategicas: "e se eu contratar 3 pessoas?", "e se o faturamento cair 20%?", "e se eu antecipar recebiveis?".

- Criacao de cenarios a partir de variaveis ajustaveis
- Comparacao lado a lado entre cenarios
- Impacto automatico no DRE e fluxo de caixa projetados
- Templates de cenarios comuns (crescimento, corte, investimento)
- Salvamento e versionamento de cenarios para revisao futura

### 4.6 Alertas de Risco Financeiro
Sistema proativo de monitoramento que identifica riscos antes que se tornem problemas. Nao espera o usuario perguntar -- notifica automaticamente.

- Alerta de caixa baixo (projecao abaixo de X dias de operacao)
- Alerta de inadimplencia alta (% de recebiveis vencidos acima do limiar)
- Alerta de margem caindo (compressao de margem bruta/liquida)
- Alerta de concentracao de receita (dependencia excessiva de poucos clientes)
- Canais: email, WhatsApp (via n8n), notificacao in-app
- Severidade configuravel por tipo de alerta

### 4.7 Relatorios para Conselho e Investidores
Geracao automatica de relatorios executivos em PDF, formatados para apresentacao a conselhos, investidores ou socios.

- Template executivo com indicadores-chave (receita, margem, burn rate, runway)
- Comparativo periodo anterior com explicacao automatica de variacoes
- Graficos prontos para apresentacao
- Geracao sob demanda ou agendada (ex: todo dia 5 do mes)
- Personalizacao de marca (logo, cores do cliente)

### 4.8 Modo BPO
Modelo operacional em que a equipe UUBA atua como departamento financeiro terceirizado do cliente, usando a propria plataforma como ferramenta.

- Painel de operacao BPO (tarefas, SLAs, filas de trabalho)
- Segregacao de acesso (operador UUBA vs cliente)
- Checklist operacional diario/semanal/mensal
- Relatorio de atividades para o cliente (transparencia)
- Escalonamento automatico de tarefas criticas
- Metricas de qualidade e tempo de resposta da operacao

---

## 5. User Stories Estrategicas

**US-01:** Como dono de PME, quero ver meu DRE atualizado automaticamente todo mes, para que eu entenda minha saude financeira sem depender do contador.

**US-02:** Como controller solo, quero que a conciliacao bancaria seja feita automaticamente, para que eu gaste meu tempo em analise estrategica em vez de conferencia manual de extratos.

**US-03:** Como CEO de startup, quero gerar um relatorio executivo em PDF para meu board meeting, para que eu apresente dados financeiros profissionais sem montar slides manualmente.

**US-04:** Como gestor financeiro, quero receber alertas proativos quando minha projecao de caixa indicar risco nos proximos 30 dias, para que eu tome providencias antes de entrar em crise.

**US-05:** Como dono de holding, quero ver o DRE consolidado de todas as minhas empresas, para que eu tenha visao unica do grupo sem precisar abrir cada CNPJ separadamente.

**US-06:** Como cliente do modo BPO, quero acompanhar o que a equipe UUBA esta fazendo no meu financeiro, para que eu tenha transparencia sobre as operacoes sem precisar operar pessoalmente.

**US-07:** Como gestor financeiro, quero simular o impacto de contratar 5 pessoas novas no meu fluxo de caixa dos proximos 6 meses, para que eu tome a decisao de contratacao com dados concretos.

**US-08:** Como operador BPO da UUBA, quero ter um painel com todas as tarefas pendentes dos meus clientes organizadas por prioridade e SLA, para que eu execute o trabalho com eficiencia e sem perder prazos.

**US-09:** Como dono de PME, quero que os lancamentos do meu extrato bancario sejam categorizados automaticamente no DRE, para que eu nao precise classificar manualmente centenas de transacoes todo mes.

**US-10:** Como CFO de media empresa, quero comparar cenarios de crescimento versus contencao de custos lado a lado, para que eu apresente opcoes fundamentadas para a diretoria.

---

## 6. Dependencias

### 6.1 UUBA Nexo (fornecedor de dados)
O Nexo e a camada de inteligencia de dados da plataforma. O Financeiro depende dele para:
- Importacao de extratos bancarios (Open Finance, OFX, CSV)
- Conexao com ERPs (Conta Azul, Omie, Bling)
- Normalizacao de dados financeiros entre fontes heterogeneas
- Enriquecimento de dados (CNPJ do fornecedor, categoria sugerida)

**Criticidade:** Alta. Sem Nexo, o Financeiro nao tem dados para operar.

### 6.2 UUBA Recebe (contas a receber)
O Recebe e a plataforma de cobranca. O Financeiro depende dele para:
- Dados de contas a receber (boletos emitidos, Pix, cartao)
- Status de pagamento (pago, vencido, em atraso)
- Previsao de receita baseada em titulos emitidos
- Historico de inadimplencia por cliente

**Criticidade:** Alta. Contas a receber e metade do fluxo de caixa.

### 6.3 UUBA 360 (consumidor de indicadores)
O 360 e a camada de dashboards. Ele CONSOME dados do Financeiro (nao fornece):
- Indicadores financeiros (margem, receita, burn rate) sao calculados pelo Financeiro
- O 360 exibe esses indicadores em dashboards visuais
- O Financeiro e o produtor de dados; o 360 e o apresentador

**Criticidade:** Media. O Financeiro funciona sem o 360, mas a experiencia e melhor com ele.

---

## 7. Analise Competitiva vs FinDrive

| Dimensao | FinDrive | UUBA Financeiro |
|----------|----------|-----------------|
| DRE | Sim, com integracao Conta Azul | Sim, com IA para categorizacao automatica |
| Dashboard financeiro | Sim (foco principal) | Sim, via integracao com 360 |
| Integracao ERP | Conta Azul | Conta Azul + Omie + Bling + Open Finance |
| Conciliacao bancaria | Nao | Sim, automatica com fuzzy matching |
| Fluxo de caixa preditivo | Limitado | Sim, 30/60/90 dias com cenarios |
| Projecao de cenarios | Nao | Sim, what-if analysis completo |
| Alertas proativos | Nao | Sim, multi-canal (email, WhatsApp, in-app) |
| Relatorios para investidores | Nao | Sim, PDF executivo automatizado |
| Modo BPO | Nao | Sim, equipe UUBA opera pelo cliente |
| IA integrada | Nao | Sim, Claude AI para categorizacao e insights |
| Modelo de entrega | SaaS (ferramenta) | SaaS + BPO (ferramenta + servico) |

**Sintese competitiva:**

O FinDrive e uma boa ferramenta de visualizacao financeira, bem integrada com Conta Azul. Seu publico e o controller ou dono de empresa que quer VER seus numeros de forma organizada.

O UUBA Financeiro atende um problema diferente e mais amplo: nao apenas mostrar dados, mas OPERAR o financeiro. A categorizacao por IA, a conciliacao automatica, os alertas proativos e -- principalmente -- o modo BPO criam uma proposta de valor que o FinDrive nao pode replicar apenas com software.

**Posicionamento: "FinDrive mostra. UUBA faz."**

---

## 8. Riscos e Open Questions

### Riscos

| Risco | Impacto | Probabilidade | Mitigacao |
|-------|---------|---------------|-----------|
| Acuracia da categorizacao por IA insuficiente nos primeiros meses | Alto | Media | Periodo de aprendizado assistido; validacao humana obrigatoria nas primeiras 4 semanas |
| Complexidade regulatoria (contabilidade varia por regime tributario) | Medio | Alta | Plano de contas configuravel; consultoria com contador parceiro |
| Operacao BPO nao escalar (custo de pessoal) | Alto | Media | Automacao maxima via n8n; SOP rigoroso; metricas de eficiencia por operador |
| Dependencia critica do Nexo para dados | Alto | Baixa | Nexo e prioridade no roadmap; fallback com importacao manual |
| Cliente esperar que UUBA substitua o contador | Medio | Alta | Comunicacao clara: UUBA e depto financeiro operacional, nao contabilidade fiscal |

### Open Questions

1. **Precificacao do BPO:** cobrar por empresa operada? Por volume de lancamentos? Por SLA (basico vs premium)?
2. **Limites do BPO:** ate onde a equipe UUBA opera? Pagamentos reais (TED/Pix) ficam com o cliente ou com a UUBA?
3. **Compliance:** o DRE gerado pela UUBA tem validade contabil ou e gerencial? Se gerencial, como posicionar para o mercado?
4. **Multimoeda:** clientes com operacoes internacionais precisam de suporte a dolar/euro? Em qual fase?
5. **Integracao com contadores:** criar um portal para o contador do cliente acessar dados? Isso entra no Parceiros?
6. **Retencao de dados:** por quanto tempo manter historico financeiro? Implicacoes de LGPD?

---

## 9. Faseamento Sugerido

### v1 -- Fundacao (MVP)
**Objetivo:** Entregar valor imediato com DRE e fluxo de caixa.

- DRE automatizado com categorizacao por IA
- Fluxo de caixa realizado e projetado (30 dias)
- Integracao com Conta Azul (via Nexo)
- Importacao de extratos (OFX/CSV)
- Contas a receber basico (integrado com Recebe)
- Dashboard financeiro essencial

**Criterio de sucesso:** 10 clientes usando DRE automatizado sem intervencao manual significativa.

### v2 -- Automacao e Inteligencia
**Objetivo:** Reduzir trabalho manual e adicionar proatividade.

- Conciliacao bancaria automatica
- Alertas de risco financeiro (caixa, inadimplencia, margem)
- Contas a pagar com workflow de aprovacao
- Fluxo de caixa estendido (60/90 dias)
- Integracao com Omie e Bling (via Nexo)
- Relatorios PDF basicos

**Criterio de sucesso:** Reducao de 70% no tempo de conciliacao bancaria dos clientes ativos.

### v3 -- Estrategia e BPO
**Objetivo:** Habilitar uso estrategico e modelo BPO.

- Projecao de cenarios (what-if analysis)
- Relatorios executivos para conselho/investidores
- Modo BPO (painel de operacao, SLAs, checklists)
- Visao consolidada multi-empresa (holdings)
- Open Finance (conexao direta com bancos)
- Metricas de qualidade da operacao BPO

**Criterio de sucesso:** 3 clientes operando em modo BPO com SLA cumprido acima de 95%.
