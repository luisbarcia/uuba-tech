# UUBA 360 -- Spec Estrategica

> Spec estrategica v1 | Gerada em 2026-03-22 | Nivel: estrategico (features agrupadas, sem FRs individuais)

**Tagline:** "Cada perfil ve o que precisa ver."

---

## 1. Overview

O UUBA 360 e o produto de visualizacao e inteligencia da plataforma UUBA. Ele consome dados normalizados do Nexo (e metricas dos outros produtos) para exibir dashboards, KPIs e alertas personalizados por perfil de usuario.

O diferencial do 360 nao e ser "mais um dashboard". E ser um dashboard que JA SABE o que cada perfil precisa ver. O CFO ve DRE e fluxo de caixa. O gerente de operacoes ve aging de clientes e taxa de recuperacao. O analista ve os detalhes granulares. Ninguem precisa configurar queries ou montar graficos -- os paineis vem prontos para o perfil, com a opcao de personalizar.

O 360 NAO gera dados. Ele consome. Toda a inteligencia de dados (normalizacao, dedup, validacao) fica no Nexo. O 360 se preocupa com apresentacao, experiencia e acionabilidade: o usuario viu o numero, entendeu o que significa, e sabe o que fazer a seguir.

### Posicao na plataforma

```
[Nexo]              [360]                [Usuario]

Dados normalizados                      CFO
de clientes,     --> Dashboards por  --> Controller
lancamentos,        perfil, KPIs,       Gerente Ops
faturas, extratos   alertas, relatorios Analista

[Recebe]            [360]
Metricas de      --> Visao de cobranca
cobranca (DSO,      (taxa recuperacao,
aging, taxa rec.)   aging, inadimplencia)

[Financeiro]        [360]
DRE, fluxo de   --> Visao financeira
caixa, indicadores  (margem, liquidez,
                    endividamento)
```

---

## 2. Proposta de Valor

- **Visao por perfil, nao por sistema:** O CFO nao precisa abrir 3 ferramentas para entender a saude financeira da empresa. Tudo esta em um painel adaptado ao seu papel.
- **Dados confiáveis e atualizados:** O 360 consome do Nexo, que ja normalizou e validou os dados. O usuario nao precisa se perguntar "esse numero esta certo?".
- **Alertas que antecipam problemas:** Thresholds configuraveis avisam antes que o fluxo de caixa fique negativo, antes que a inadimplencia passe de 15%, antes que um cliente grande atrase.
- **Consolidacao multi-empresa:** Holdings e grupos veem dados consolidados de todas as filiais em um unico lugar, com drill-down por empresa.

---

## 3. Usuarios-alvo

| Perfil | O que precisa ver | Frequencia de uso |
|--------|-------------------|-------------------|
| **CFO / Diretor Financeiro** | DRE, fluxo de caixa projetado, indicadores de liquidez, endividamento, visao consolidada do grupo | Diario (visao rapida) + semanal (analise profunda) |
| **Controller** | Conciliacao bancaria, variacao orcado vs realizado, compliance fiscal, auditoria | Diario |
| **Gerente de Operacoes** | Aging de clientes, taxa de recuperacao, SLA de atendimento, metricas operacionais | Diario |
| **Analista Financeiro** | Dados granulares, exportacoes, drill-down por cliente/periodo, investigacao de anomalias | Continuo |
| **Dono de PME (acumula funcoes)** | Visao executiva resumida: "como esta minha empresa hoje?" | Diario (mobile) |
| **Parceiro white-label** | Dashboards com sua marca para seus clientes | Configuracao + monitoramento |

---

## 4. Features Agrupadas

### 4.1 Dashboards por Perfil (Role-based Views)

Cada perfil de usuario tem um dashboard pre-configurado com os KPIs e graficos mais relevantes para sua funcao.

- **Perfis pre-definidos:** CFO, Controller, Gerente de Operacoes, Analista, Executivo (dono de PME).
- **Dashboard default por perfil:** Ao fazer login, o usuario ja ve o painel adequado ao seu papel.
- **Personalizacao:** O usuario pode esconder/reordenar widgets, mas o default ja funciona sem configuracao.
- **Permissoes por perfil:** O analista nao ve dados de remuneracao. O gerente nao ve DRE. Cada perfil tem acesso controlado.

### 4.2 KPIs em Tempo Real

Indicadores-chave atualizados automaticamente a partir dos dados do Nexo.

- **KPIs financeiros:** Faturamento, margem bruta, margem liquida, EBITDA, liquidez corrente, endividamento.
- **KPIs de cobranca (via Recebe):** Taxa de recuperacao, DSO (Days Sales Outstanding), aging buckets, valor inadimplente.
- **KPIs operacionais:** Clientes ativos, churn, ticket medio, concentracao de receita (top 10 clientes).
- **Comparativos:** Mes atual vs anterior, vs mesmo periodo ano anterior, vs meta.
- **Tendencia:** Graficos de serie temporal com projecao simples (media movel, tendencia linear).

### 4.3 Consolidacao Multi-empresa

Para grupos economicos, holdings e redes de franquias que precisam ver dados agregados.

- **Visao consolidada:** Soma/media dos KPIs de todas as empresas do grupo.
- **Drill-down por empresa:** Clica no consolidado e ve o detalhe por filial/empresa.
- **Comparativo entre empresas:** Ranking de filiais por faturamento, inadimplencia, margem.
- **Eliminacoes intercompany:** Transacoes entre empresas do grupo nao duplicam nos consolidados.

### 4.4 Alertas Configuraveis por Threshold

Notificacoes proativas quando indicadores cruzam limites definidos pelo usuario.

- **Thresholds por KPI:** Ex: "Avise quando inadimplencia passar de 15%", "Avise quando fluxo de caixa projetado for negativo em 30 dias".
- **Canais de notificacao:** Email, WhatsApp (via bot UUBA), notificacao in-app.
- **Frequencia:** Imediato, diario (digest), semanal.
- **Alertas inteligentes (v2+):** Deteccao de anomalias baseada em desvio padrao historico, sem necessidade de configuracao manual.

### 4.5 Relatorios Exportaveis

Geracao de relatorios formatados para reunioes, apresentacoes e compliance.

- **Formatos:** PDF (formatado para impressao/apresentacao), CSV (dados brutos para analise), XLSX.
- **Templates:** DRE mensal, fluxo de caixa, aging report, relatorio de cobranca, resumo executivo.
- **Agendamento:** Relatorios automaticos enviados por email (ex: DRE mensal todo dia 5).
- **Marca do cliente:** Logo e cores da empresa no PDF (importante para parceiros white-label).

### 4.6 Compartilhamento com Acesso Controlado

Permitir que usuarios compartilhem visoes especificas com stakeholders sem dar acesso total a plataforma.

- **Link compartilhavel:** Gera URL com token temporario para um dashboard ou relatorio especifico.
- **Permissoes granulares:** Somente leitura, sem export, expira em X dias.
- **Compartilhamento com contador/auditor:** Acesso restrito a dados financeiros para o contador da empresa.
- **Log de acesso:** Registro de quem visualizou o que e quando.

### 4.7 Mobile Responsive

O dono de PME ve os numeros da empresa no celular enquanto esta na rua.

- **Layout adaptativo:** Dashboards reorganizam widgets para telas menores.
- **Visao mobile simplificada:** No celular, mostra apenas os KPIs mais importantes (nao todos os graficos).
- **PWA:** Instalavel na home screen do celular, com notificacoes push para alertas.
- **Offline basico (v3):** Cache dos ultimos dados para consulta sem conexao.

### 4.8 Composicao Livre de Paineis (Widgets Drag-and-Drop)

Para usuarios avancados que querem montar seus proprios dashboards.

- **Biblioteca de widgets:** KPI card, grafico de linha, barra, pizza, tabela, mapa de calor, gauge.
- **Drag-and-drop:** Arrasta widgets para o painel, redimensiona, reordena.
- **Fonte de dados configuravel:** Cada widget aponta para um endpoint do Nexo ou metrica de outro produto.
- **Salvar e compartilhar:** Paineis customizados podem ser salvos e compartilhados com outros usuarios do mesmo tenant.
- **Templates da comunidade (v3):** Paineis criados por outros usuarios podem ser publicados como templates.

---

## 5. User Stories

| # | Como... | Eu quero... | Para que... |
|---|---------|-------------|-------------|
| US-01 | CFO | abrir o 360 e ver imediatamente meu DRE, fluxo de caixa e inadimplencia sem configurar nada | eu tenha uma visao executiva da saude financeira em segundos |
| US-02 | gerente de operacoes | ver o aging de clientes e a taxa de recuperacao do Recebe em um unico painel | eu saiba quais acoes de cobranca priorizar |
| US-03 | dono de PME | receber um alerta no WhatsApp quando meu fluxo de caixa projetado for negativo em 30 dias | eu possa agir antes de ficar sem caixa |
| US-04 | controller | comparar o realizado vs orcado do mes e identificar desvios acima de 10% | eu reporte variancas significativas na reuniao de diretoria |
| US-05 | analista financeiro | exportar o aging report em PDF com a logo da empresa | eu envie para o diretor em um formato profissional |
| US-06 | dono de holding | ver os KPIs consolidados das 5 empresas do grupo e fazer drill-down por filial | eu identifique qual operacao esta performando abaixo |
| US-07 | dono de PME | acessar meus KPIs pelo celular enquanto estou fora do escritorio | eu nao dependa do computador para acompanhar os numeros |
| US-08 | analista financeiro | montar um dashboard customizado com widgets de cobranca + fluxo de caixa | eu tenha uma visao especifica para minha rotina de trabalho |
| US-09 | CFO | compartilhar o dashboard financeiro com meu contador sem dar acesso total ao sistema | meu contador veja apenas o que precisa para fechar o balancete |
| US-10 | parceiro white-label | configurar dashboards com minha marca para meus clientes | meus clientes vejam a plataforma como se fosse minha |

---

## 6. Dependencias

### O que o 360 precisa

| Dependencia | Tipo | Descricao |
|-------------|------|-----------|
| **Nexo (API)** | Interna/Critica | Fonte primaria de todos os dados. Sem Nexo, o 360 nao tem dados para exibir |
| **Recebe (metricas)** | Interna | Metricas de cobranca (DSO, taxa recuperacao, aging) expostas via API ou passadas pelo Nexo |
| **Financeiro (indicadores)** | Interna | DRE, fluxo de caixa, indicadores financeiros -- quando o produto Financeiro existir |
| **Autenticacao/RBAC** | Interna | Sistema de roles e permissoes da plataforma para controlar o que cada perfil ve |
| **Multi-tenancy (M00)** | Interna | Isolamento de dados por tenant, ja definido no Recebe |
| **Infra de frontend** | Interna | Framework de frontend (React/Next.js), biblioteca de graficos (Recharts, D3, etc.) |

### Riscos de dependencia

- Se o Nexo atrasa, o 360 nao tem dados. **Mitigacao:** v1 do 360 pode consumir dados diretamente do Recebe (que ja existe) enquanto o Nexo nao esta pronto.
- Se o Financeiro ainda nao existe, o 360 nao tem DRE/fluxo de caixa. **Mitigacao:** v1 mostra apenas metricas de cobranca (do Recebe).

---

## 7. Relacao com Outros Produtos

### Nexo --> 360

O Nexo e a unica fonte de dados canonica do 360. A relacao e de produtor-consumidor:

- O 360 NUNCA acessa ERPs, bancos ou planilhas diretamente. Tudo passa pelo Nexo.
- O 360 se inscreve em webhooks do Nexo para atualizar KPIs quando dados mudam.
- Se o Nexo esta fora do ar, o 360 mostra os ultimos dados em cache com um indicador de "dados desatualizados desde [timestamp]".

### Recebe --> 360

O Recebe gera metricas especificas de cobranca que o 360 exibe:

- **Taxa de recuperacao:** Percentual de titulos cobrados vs total vencido.
- **DSO (Days Sales Outstanding):** Tempo medio de recebimento.
- **Aging buckets:** Distribuicao de titulos por faixa de atraso (1-30, 31-60, 61-90, 90+).
- **Valor inadimplente:** Total em aberto por periodo.
- **Performance da regua:** Qual canal/etapa da regua tem melhor conversao.

Essas metricas podem ser expostas pelo Recebe via API propria ou normalizadas pelo Nexo. A decisao arquitetural sera tomada na spec detalhada.

### Financeiro --> 360

Quando o produto Financeiro existir, ele fornecera:

- **DRE (Demonstracao do Resultado):** Receita, custos, despesas, lucro/prejuizo.
- **Fluxo de caixa:** Realizado e projetado.
- **Indicadores financeiros:** Margem bruta, margem liquida, liquidez corrente, endividamento.
- **Orcado vs realizado:** Variancas por centro de custo.

Ate la, o 360 pode oferecer uma versao simplificada desses indicadores calculados diretamente dos dados do Nexo (lancamentos + extratos).

### 360 --> Parceiros

Parceiros white-label usam o 360 com sua propria marca:

- Logo, cores, dominio customizado.
- Selecionam quais dashboards/KPIs ficam disponiveis para seus clientes.
- Podem ter dashboards proprios (ex: visao da carteira de clientes do parceiro).

---

## 8. Diferenciais vs Concorrencia

| Aspecto | Metabase / Grafana | FinDrive / Nibo | UUBA 360 |
|---------|--------------------|-----------------|----------|
| **Publico** | Times de dados/BI que escrevem SQL | Contadores e financeiro de PME | Gestores de PME por perfil (CFO, gerente, analista) |
| **Setup** | Precisa conectar banco, escrever queries, montar dashboards | Precisa inputar dados manualmente ou integrar ERP | Zero config -- dados vem do Nexo, dashboards ja prontos por perfil |
| **Personalizacao** | Total (e necessaria -- vem em branco) | Limitada (templates fixos) | Dashboards prontos + composicao livre para quem quiser |
| **Contexto financeiro BR** | Generico -- nao sabe o que e DRE, DSO, aging | Sabe, mas limitado a contabilidade | Nativamente financeiro + cobranca + operacional |
| **Multi-empresa** | Precisa configurar multi-schema manualmente | Limitado ou inexistente | Consolidacao multi-empresa nativa com drill-down |
| **Alertas** | Basico (Grafana) ou inexistente (Metabase) | Basico | Por threshold, por perfil, multicanal (email, WhatsApp) |
| **Mobile** | Responsivo mas nao otimizado | App proprio (FinDrive) | PWA otimizado com visao simplificada para celular |
| **Preco** | Gratuito (self-hosted) mas custo de manutencao | R$ 50-200/mes | Incluso no plano UUBA ou add-on |

**Resumo:** O 360 nao compete com Metabase/Grafana no mercado de BI generico. Ele compete no espaco de "dashboard financeiro pronto para PME que nao tem time de BI". O diferencial e que ele ja vem com os dados certos (via Nexo), os paineis certos (por perfil) e os alertas certos (por threshold de negocio).

---

## 9. Riscos e Open Questions

### Riscos

| Risco | Impacto | Mitigacao |
|-------|---------|-----------|
| **Dependencia total do Nexo** | Sem Nexo, 360 nao funciona | v1 consome direto do Recebe; cache local para dados recentes |
| **Definicao de perfis errada** | Dashboards pre-definidos nao servem para ninguem | Pesquisa com usuarios reais antes de definir os defaults; composicao livre como fallback |
| **Performance com muitos dados** | Dashboards lentos com tenants grandes (milhoes de lancamentos) | Aggregacoes pre-calculadas, materialized views, cache de KPIs |
| **Complexidade do drag-and-drop** | Feature cara de construir e manter | Deixar para v3; v1 e v2 com dashboards pre-definidos + personalizacao simples |
| **Multi-empresa** | Eliminacoes intercompany sao complexas | v1 sem eliminacoes; consolidacao simples (soma); eliminacoes em v3 |
| **Mobile** | PWA pode nao ter adocao se a experiencia for ruim | Testar com usuarios reais; manter simples (KPIs, nao dashboards completos) |

### Open Questions

1. **Quais KPIs por perfil?** Precisamos definir exatamente quais metricas cada perfil ve no default. Pesquisa com CFOs e gerentes reais.
2. **Tempo real vs near-real-time:** O usuario espera que o KPI atualize instantaneamente ou um delay de 5-15 minutos e aceitavel?
3. **Calculo de DRE sem o produto Financeiro:** E possivel calcular DRE a partir dos dados do Nexo (lancamentos do ERP) ou precisa de input adicional?
4. **Graficos: biblioteca propria ou terceira?** Recharts, Chart.js, D3, ou biblioteca comercial (Highcharts)?
5. **Limites de compartilhamento:** Quantos links compartilhaveis por tenant? Expiracao padrao?
6. **White-label no 360:** O parceiro pode esconder KPIs que nao fazem sentido para seus clientes? Pode adicionar KPIs customizados?
7. **Composicao livre (drag-and-drop):** Construir do zero ou usar framework existente (ex: React Grid Layout)?

---

## 10. Faseamento Sugerido

### v1 -- Dashboards do Recebe

**Objetivo:** Entregar valor imediato para quem ja usa o Recebe, sem depender do Nexo completo.

**Escopo:**
- Dashboards pre-definidos consumindo metricas do Recebe (cobranca)
- KPIs: taxa de recuperacao, DSO, aging buckets, valor inadimplente, performance por canal
- 2 perfis: Gestor (visao executiva) e Analista (visao detalhada)
- Alertas basicos por email (threshold de inadimplencia, DSO)
- Exportacao PDF e CSV
- Mobile responsive (layout adaptativo, sem PWA ainda)

**Resultado esperado:** Quem usa o Recebe ganha dashboards de cobranca automaticamente. O 360 valida o modelo de dashboards por perfil com usuarios reais.

### v2 -- Dados Financeiros + Multi-empresa

**Objetivo:** Expandir para dados financeiros (via Nexo) e atender grupos/holdings.

**Escopo:**
- Consumo de dados do Nexo (lancamentos, extratos, clientes)
- KPIs financeiros basicos: faturamento, margem, fluxo de caixa (simplificado)
- Perfis adicionais: CFO, Controller
- Consolidacao multi-empresa (soma simples, sem eliminacoes)
- Drill-down por empresa/filial
- Alertas multicanal (email + WhatsApp)
- Relatorios agendados
- Compartilhamento com link (acesso controlado)
- PWA (instalavel no celular)

**Resultado esperado:** O 360 se torna a visao unificada da empresa -- cobranca + financeiro. Holdings conseguem ver tudo consolidado.

### v3 -- Composicao Livre + Avancado

**Objetivo:** Empoderar usuarios avancados e parceiros com personalizacao total.

**Escopo:**
- Composicao livre de paineis (drag-and-drop de widgets)
- Biblioteca de widgets (KPI card, graficos diversos, tabelas, gauges)
- Alertas inteligentes (deteccao de anomalias sem configuracao manual)
- Eliminacoes intercompany na consolidacao
- Templates de dashboard compartilhaveis
- Offline basico (cache de KPIs no PWA)
- Dashboards white-label completo (marca, cores, selecao de KPIs)
- Orcado vs realizado (quando produto Financeiro existir)

**Resultado esperado:** Plataforma madura de BI financeiro para PMEs. Diferenciacao clara vs Metabase/Grafana (pronto para usar) e vs FinDrive (mais flexivel e integrado).

---

*Spec estrategica -- sera desdobrada em specs detalhadas (FRs, ACs, wireframes) por modulo conforme o faseamento.*
