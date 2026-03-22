# UUBA Nexo -- Spec Estrategica

> Spec estrategica v1 | Gerada em 2026-03-22 | Nivel: estrategico (features agrupadas, sem FRs individuais)

**Tagline:** "Os dados da sua empresa vivem em 10 lugares diferentes. O Nexo conecta todos."

---

## 1. Overview

O UUBA Nexo e a camada de dados da plataforma UUBA. Ele conecta ERPs, CRMs, bancos, gateways de pagamento e planilhas, normaliza a informacao em um schema unico e distribui dados confiáveis via API para todos os outros produtos da plataforma.

Nenhum produto da UUBA funciona isolado. O Recebe precisa de dados de clientes e faturas. O 360 precisa de indicadores financeiros consolidados. O Financeiro precisa de extratos bancarios e lancamentos. O Nexo e o elo que conecta tudo isso -- sem ele, cada produto teria que construir suas proprias integracoes, gerando duplicacao, inconsistencia e custo de manutencao insustentavel.

O Nexo NAO e um produto visivel para o usuario final no dia a dia. Ele e infraestrutura. O usuario interage com ele apenas no setup (conectar fontes) e no monitoramento (painel de saude das integracoes). Todo o resto acontece silenciosamente por baixo dos outros produtos.

### Posicao na plataforma

```
[Fontes externas]     [Nexo]           [Produtos UUBA]

Conta Azul  ------+                +----> Recebe (cobranca)
Omie        ------+                |
Bling       ------+--> Normaliza --+----> 360 (dashboards)
Bancos (OF) ------+    Deduplica   |
CRMs        ------+    Valida      +----> Financeiro (DRE, FC)
Planilhas   ------+    Distribui   |
                                   +----> Parceiros (white-label)
```

---

## 2. Proposta de Valor

- **Fonte unica de verdade:** Dados de 10+ sistemas diferentes consolidados em um schema unico, eliminando planilhas paralelas e reconciliacoes manuais.
- **Setup assistido, nao tecnico:** O empresario conecta seu ERP ou sobe uma planilha sem precisar de desenvolvedor. O Nexo cuida do mapeamento.
- **Dados sempre frescos:** Sync automatico (batch programado + webhooks em tempo real) garante que os outros produtos sempre trabalhem com dados atualizados.
- **Confiabilidade visivel:** Painel de saude mostra o status de cada integracao, erros de sync, e alertas -- o usuario sabe que pode confiar nos numeros.

---

## 3. Usuarios-alvo

| Perfil | Interacao com o Nexo | Motivacao |
|--------|---------------------|-----------|
| **Dono/gestor de PME** | Setup inicial: conecta ERP e/ou sobe planilhas | Quer usar Recebe/360 sem ter que exportar dados manualmente |
| **Analista financeiro** | Monitora painel de saude, resolve erros de sync | Precisa garantir que os dados nos dashboards estao corretos |
| **Equipe UUBA (interno)** | Configura novos conectores, debug de integracoes | Opera a plataforma para clientes BPO |
| **Desenvolvedor (API)** | Consome API do Nexo para construir integracoes customizadas | Parceiros ou clientes maiores que querem consumir dados programaticamente |

---

## 4. Features Agrupadas

### 4.1 Conectores

Modulos de integracao com sistemas externos. Cada conector sabe como autenticar, extrair e mapear dados da fonte para o schema do Nexo.

**ERPs:**
- Conta Azul (prioridade v1 -- ja usado pela Uuba como plataforma de pagamentos)
- Omie
- Bling
- Tiny ERP

**Bancos:**
- Open Finance (fase v3 -- depende de regulamentacao e certificacao)
- Import de extratos OFX/CSV (v1 -- alternativa offline)

**CRMs:**
- Pipedrive
- HubSpot
- RD Station CRM

**Planilhas:**
- Upload manual (CSV, XLSX) com mapeamento assistido (v1)
- Google Sheets (sync automatico)

**Gateways de pagamento:**
- Asaas, Stripe, PagSeguro (leitura de transacoes)

### 4.2 Engine de Normalizacao

O nucleo do Nexo. Recebe dados brutos de qualquer conector e transforma em entidades padronizadas.

- **Schema unico:** Entidades canonicas (Cliente, Fatura, Lancamento, Conta, Produto, Contrato) com campos padronizados independente da fonte.
- **Deduplicacao:** Identifica e merge registros duplicados (mesmo cliente em ERP e planilha, por exemplo) usando CNPJ/CPF, email e heuristicas de similaridade.
- **Validacao:** Regras de qualidade de dados -- campos obrigatorios, formatos (CPF/CNPJ valido, datas consistentes), ranges (valores negativos, datas futuras).
- **Mapeamento configuravel:** O administrador pode ajustar como campos da fonte mapeiam para o schema do Nexo quando o mapeamento automatico nao funciona.
- **Auditoria:** Todo dado normalizado mantem referencia a fonte original (source_system, source_id, sync_timestamp) para rastreabilidade.

### 4.3 API de Distribuicao

Interface pela qual os outros produtos (e parceiros) consomem dados do Nexo.

- **REST API:** Endpoints padronizados para cada entidade (GET /clientes, GET /lancamentos, etc.) com filtros, paginacao e versionamento.
- **Webhooks de eventos:** Notificacoes push quando dados mudam (novo cliente, fatura atualizada, lancamento criado). Os produtos se inscrevem nos eventos que interessam.
- **Bulk export:** Endpoint para exportacao em massa (CSV, JSON) para cenarios de migracao ou relatorios pesados.
- **Rate limiting e autenticacao:** API key por tenant, rate limits configuraveis, logs de acesso.

### 4.4 Painel de Saude das Integracoes

Interface visual para o usuario (e a equipe UUBA) monitorar o estado das conexoes.

- **Status por conector:** Verde (ok), amarelo (warning), vermelho (erro) para cada integracao ativa.
- **Log de syncs:** Historico de sincronizacoes com timestamp, volume de registros, erros encontrados.
- **Alertas configuráveis:** Notificacoes (email, WhatsApp) quando um sync falha, quando a qualidade dos dados cai, ou quando uma fonte fica offline por mais de X horas.
- **Metricas de qualidade:** Porcentagem de registros validos, duplicatas encontradas/resolvidas, campos faltantes.

### 4.5 Sync Engine

Motor de sincronizacao que orquestra a extracao de dados das fontes.

- **Batch (agendado):** Syncs programados (ex: a cada 6h, diario, semanal) conforme a necessidade e o plano do cliente.
- **Real-time (webhooks):** Para fontes que suportam webhooks (Conta Azul, Pipedrive), o Nexo recebe notificacoes de mudanca e processa incrementalmente.
- **Sync incremental:** Apenas registros novos ou alterados desde o ultimo sync, evitando reprocessamento total.
- **Retry com backoff:** Falhas de sync sao retentadas automaticamente com backoff exponencial. Apos N falhas, alerta o usuario.
- **Resolucao de conflitos:** Quando o mesmo dado existe em multiplas fontes com valores diferentes, regras configuraveis decidem qual prevalece (ultima atualizacao, fonte prioritaria, merge manual).

---

## 5. User Stories

| # | Como... | Eu quero... | Para que... |
|---|---------|-------------|-------------|
| US-01 | dono de PME | conectar meu Conta Azul ao UUBA em menos de 5 minutos | meus dados de clientes e faturas estejam disponiveis no Recebe e no 360 sem exportar nada |
| US-02 | analista financeiro | subir uma planilha de clientes e o sistema mapear automaticamente as colunas | eu nao precise formatar a planilha em um template rigido |
| US-03 | analista financeiro | ver um painel mostrando o status de todas as integracoes ativas | eu saiba se posso confiar nos numeros que estou vendo nos dashboards |
| US-04 | gestor | receber um alerta quando a sincronizacao com o ERP falhar | eu possa agir antes que os dados fiquem defasados |
| US-05 | operador UUBA | configurar a frequencia de sync por cliente (horario, diario, semanal) | cada cliente tenha o frescor de dados adequado ao seu plano |
| US-06 | analista financeiro | ver o historico de duplicatas detectadas e como foram resolvidas | eu tenha confianca de que nao estou contando o mesmo cliente duas vezes |
| US-07 | desenvolvedor parceiro | consumir a API do Nexo com documentacao clara e sandbox | eu possa construir integracoes customizadas sem depender do suporte |
| US-08 | gestor | importar extratos bancarios (OFX/CSV) e ter os lancamentos normalizados | eu consiga visualizar meu fluxo de caixa no 360 mesmo sem Open Finance |
| US-09 | operador UUBA | ver quais dados de um tenant ainda nao foram sincronizados e por que | eu possa resolver problemas de onboarding rapidamente |
| US-10 | dono de PME | desconectar uma fonte de dados e que o sistema me avise quais produtos serao afetados | eu nao quebre meus dashboards sem querer |

---

## 6. Dependencias

### O que o Nexo precisa

| Dependencia | Tipo | Descricao |
|-------------|------|-----------|
| APIs dos ERPs | Externa | Conta Azul, Omie, Bling precisam fornecer APIs estaveis com webhooks |
| Open Finance (fase v3) | Externa/Regulatoria | Depende de certificacao e aprovacao do Bacen |
| Infraestrutura UUBA | Interna | PostgreSQL, Redis, n8n para orquestracao de syncs |
| Multi-tenancy (M00) | Interna | Isolamento por tenant_id ja definido na spec do Recebe |
| Autenticacao/authz | Interna | Sistema de auth da plataforma para API keys e permissoes |

### Quem depende do Nexo

| Produto | Dados consumidos |
|---------|-----------------|
| **Recebe** | Clientes, faturas/titulos (via import inicial ou sync continuo) |
| **360** | Todos os dados normalizados -- clientes, lancamentos, metricas |
| **Financeiro** | Dados bancarios, extratos, lancamentos, contas a pagar/receber |
| **Parceiros** | Mesmos dados, filtrados por tenant do parceiro white-label |

---

## 7. Relacao com Outros Produtos

### Nexo --> Recebe

O Recebe e o produto de cobranca. Ele precisa de dados de clientes e faturas/titulos vencidos. Hoje, o Recebe tem seu proprio modulo de import (M06). Com o Nexo, o fluxo muda:

- **Sem Nexo (v1 do Recebe):** Empresa importa CSV de titulos direto no Recebe.
- **Com Nexo:** Empresa conecta o ERP uma vez. O Nexo sincroniza clientes e faturas. O Recebe consome via API/webhook. Quando um titulo vence e nao e pago, o Recebe ja sabe e inicia a regua automaticamente.

Isso elimina o import manual repetitivo e permite que a cobranca seja verdadeiramente automatica.

### Nexo --> 360

O 360 e o produto de dashboards. Ele nao gera dados -- apenas consome e visualiza. O Nexo e a unica fonte de dados do 360:

- KPIs financeiros (faturamento, inadimplencia, DSO) vem de lancamentos normalizados pelo Nexo.
- Dados de clientes, por segmento/regiao, vem do Nexo.
- Metricas de cobranca do Recebe tambem passam pelo Nexo para consolidacao.

### Nexo --> Financeiro

O Financeiro e o departamento financeiro virtual. Precisa de:

- Extratos bancarios para conciliacao.
- Lancamentos (contas a pagar e receber) para fluxo de caixa.
- Dados de notas fiscais para DRE.

Tudo isso vem do Nexo, que puxa dos ERPs e bancos.

### Nexo --> Parceiros

Parceiros white-label usam a plataforma sob sua propria marca. O Nexo garante que os dados de cada parceiro (e seus sub-tenants) estejam isolados e acessiveis pela API com as devidas permissoes.

---

## 8. Diferenciais vs Concorrencia

| Aspecto | Fivetran / Airbyte | UUBA Nexo |
|---------|-------------------|-----------|
| **Publico** | Empresas de tecnologia com equipe de dados | PMEs brasileiras sem equipe tecnica |
| **Conectores** | 300+ conectores genericos | 10-15 conectores focados no ecossistema brasileiro (Conta Azul, Omie, Bling, bancos BR) |
| **Setup** | Requer conhecimento tecnico (schema mapping, dbt, warehouse) | Setup assistido com mapeamento automatico, sem jargao tecnico |
| **Destino** | Data warehouse (Snowflake, BigQuery) | Direto para os produtos UUBA (Recebe, 360, Financeiro) |
| **Preco** | A partir de US$ 500/mes (Fivetran), gratuito com complexidade (Airbyte) | Incluso no plano UUBA ou como add-on acessivel |
| **Normalizacao** | Usuario precisa construir (dbt, SQL) | Automatica -- schema unico pronto para uso |
| **Contexto fiscal BR** | Nao entende CNPJ, NF-e, regimes tributarios | Nativamente preparado para o contexto brasileiro |
| **Suporte** | Self-service (docs) | Suporte humano + setup assistido pela equipe UUBA |

**Resumo:** O Nexo nao compete com Fivetran/Airbyte no mercado de data engineering. Ele compete no mercado de "como faco meus dados financeiros funcionarem juntos" para PMEs que nao tem (e nao querem ter) infraestrutura de dados.

---

## 9. Riscos e Open Questions

### Riscos

| Risco | Impacto | Mitigacao |
|-------|---------|-----------|
| **APIs de ERPs instáveis** | Syncs falham, dados ficam defasados | Retry com backoff, alertas proativos, cache local dos dados |
| **Qualidade dos dados na origem** | Dados sujos propagam para todos os produtos | Engine de validacao robusta + painel de qualidade para o usuario |
| **Complexidade do mapeamento** | Cada ERP tem schema diferente, mapeamento automatico falha | Mapeamento manual como fallback, templates por ERP |
| **Escopo creep** | Tentar construir muitos conectores antes de validar o modelo | Comecar com Conta Azul + planilhas (v1), expandir sob demanda |
| **Open Finance** | Regulamentacao e certificacao podem atrasar | Manter import de OFX/CSV como alternativa ate v3 |
| **Performance com volume** | Tenants grandes podem ter milhoes de lancamentos | Sync incremental, paginacao, indices otimizados |

### Open Questions

1. **Frequencia de sync no plano gratuito/basico:** De quanto em quanto tempo? Diario e suficiente ou o usuario espera tempo real?
2. **Resolucao de conflitos:** Quando o mesmo dado vem de duas fontes com valores diferentes, quem decide? Regra automatica ou usuario?
3. **Dados historicos:** No onboarding, o Nexo importa todo o historico do ERP ou apenas dados recentes (ex: ultimos 12 meses)?
4. **Retencao de dados:** Se o cliente desconecta uma fonte, os dados ja importados permanecem? Por quanto tempo?
5. **Limites por plano:** Quantos conectores ativos por tenant? Quantos registros sincronizados por mes?
6. **Open Finance como diferencial:** Vale investir na certificacao ja ou esperar o mercado amadurecer?
7. **Conta Azul como prioridade:** Qual porcentagem dos clientes-alvo usa Conta Azul? Validar antes de investir pesado.

---

## 10. Faseamento Sugerido

### v1 -- Fundacao (MVP)

**Objetivo:** Provar que o Nexo funciona como camada de dados para o Recebe e o 360.

**Escopo:**
- Conector Conta Azul (clientes, faturas, lancamentos)
- Import de planilhas (CSV, XLSX) com mapeamento assistido
- Import de extratos bancarios (OFX, CSV)
- Engine de normalizacao basica (schema unico, validacao, dedup por CNPJ/CPF)
- API REST para consumo interno (Recebe, 360)
- Painel de saude minimo (status dos conectores, log de syncs)
- Sync batch (agendado)

**Resultado esperado:** Empresa conecta Conta Azul, dados fluem para Recebe (titulos para cobrar) e 360 (dashboards financeiros) sem export manual.

### v2 -- Expansao de Conectores

**Objetivo:** Cobrir os ERPs mais usados por PMEs brasileiras.

**Escopo:**
- Conectores Omie e Bling
- Conector Google Sheets (sync automatico)
- Webhooks de eventos (notificacao push para produtos consumidores)
- Deduplicacao avancada (heuristicas de similaridade alem de CNPJ/CPF)
- Painel de qualidade de dados (metricas, historico de duplicatas)
- Resolucao de conflitos configuravel
- API documentada para parceiros externos

**Resultado esperado:** Cobertura de 70%+ dos ERPs usados pelo publico-alvo. Parceiros conseguem consumir dados via API.

### v3 -- Open Finance e Real-time

**Objetivo:** Dados bancarios direto da fonte e sincronizacao em tempo real.

**Escopo:**
- Open Finance (leitura de extratos e transacoes via API regulada)
- Sync real-time via webhooks (para fontes que suportam)
- Conectores CRM (Pipedrive, HubSpot)
- Conectores gateways de pagamento (Asaas, Stripe)
- Bulk export (CSV, JSON) para migracoes
- API publica com sandbox e documentacao completa

**Resultado esperado:** Dados bancarios sem import manual. Plataforma se posiciona como hub de dados financeiros para PMEs.

---

*Spec estrategica -- sera desdobrada em specs detalhadas (FRs, ACs, diagramas) por modulo conforme o faseamento.*
