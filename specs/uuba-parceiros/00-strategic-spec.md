# UUBA para Parceiros -- Spec Estrategica

**Tagline:** "A tecnologia e da UUBA. O relacionamento e o faturamento sao seus."

**Status:** Rascunho estrategico
**Ultima atualizacao:** 2026-03-22
**Autor:** Equipe UUBA Tech

---

## 1. Overview

O UUBA para Parceiros e o programa white-label da plataforma UUBA. Ele permite que contadores, consultorias financeiras, BPOs e fintechs revendam os produtos UUBA com sua propria marca, dominio e identidade visual.

O modelo e simples: o parceiro mantem o relacionamento comercial com seus clientes e fatura diretamente. A UUBA cuida de toda a infraestrutura tecnologica, atualizacoes, suporte tecnico de retaguarda e evolucao do produto. O parceiro nao precisa desenvolver software -- apenas vender e atender.

Esse modelo transforma cada parceiro em um canal de distribuicao escalavel para a UUBA, enquanto o parceiro ganha um produto tecnologico completo sem investimento em desenvolvimento. A relacao e ganha-ganha: a UUBA escala sem custo de aquisicao por cliente final, e o parceiro monetiza sua base existente com uma solucao superior.

**Modelo de negocio:** B2B2B -- a UUBA vende para o parceiro, que revende para seus clientes.

---

## 2. Proposta de Valor (para o Parceiro)

- **Produto pronto, sem custo de desenvolvimento:** o parceiro recebe uma plataforma completa de gestao financeira (cobranca, DRE, dashboards, BPO) sem precisar investir em engenharia, infraestrutura ou manutencao
- **Marca propria, receita propria:** white-label completo (logo, cores, dominio, comunicacoes) -- os clientes do parceiro nunca veem a marca UUBA; o parceiro define seu proprio pricing e mantem 100% do relacionamento comercial
- **Monetizacao da base existente:** contadores e consultorias ja tem dezenas ou centenas de clientes PME; o UUBA para Parceiros transforma essa base em receita recorrente de tecnologia sem custo de aquisicao
- **Suporte tecnico de retaguarda:** o parceiro nao precisa montar equipe tecnica; a UUBA fornece suporte nivel 2 e 3, resolucao de bugs, e evolucao continua do produto -- o parceiro foca no atendimento e na venda

---

## 3. Perfis de Parceiros

### 3.1 Escritorios de Contabilidade
**Perfil:** Escritorios com 50 a 500 clientes PME. Ja possuem relacionamento de confianca com o empresario e acesso privilegiado a dados financeiros.

**Motivacao:** Diversificar receita alem de honorarios contabeis. Oferecer tecnologia como diferencial competitivo frente a outros escritorios. Reter clientes que estao migrando para contabilidade digital.

**Produto mais relevante:** UUBA Financeiro (DRE, conciliacao) + UUBA Recebe (cobranca).

### 3.2 Consultorias Financeiras
**Perfil:** Empresas de consultoria que atendem medias empresas com projetos de reestruturacao financeira, planejamento estrategico ou captacao de investimento.

**Motivacao:** Entregar uma plataforma permanente ao cliente apos o projeto de consultoria (receita recorrente pos-projeto). Usar a plataforma como ferramenta de trabalho durante a consultoria.

**Produto mais relevante:** UUBA Financeiro (cenarios, relatorios) + UUBA 360 (dashboards).

### 3.3 BPOs Financeiros
**Perfil:** Empresas que ja operam o departamento financeiro de seus clientes como servico terceirizado. Hoje usam planilhas ou ferramentas genericas.

**Motivacao:** Substituir ferramentas frageis (planilhas, sistemas legados) por uma plataforma integrada e escalavel. Padronizar operacoes entre clientes. Aumentar margem operacional via automacao.

**Produto mais relevante:** UUBA Financeiro (modo BPO) + UUBA Recebe + UUBA Nexo.

### 3.4 Fintechs
**Perfil:** Startups e empresas de tecnologia financeira que querem adicionar gestao financeira ao seu portfolio de produtos sem desenvolver do zero.

**Motivacao:** Time-to-market acelerado. Complementar seu produto core (credito, pagamentos, banking) com gestao financeira completa. API-first permite integracao profunda.

**Produto mais relevante:** Plataforma completa via API, com white-label total.

---

## 4. Features Agrupadas

### 4.1 White-label Completo
Personalizacao total da plataforma para que o cliente final nunca veja a marca UUBA.

- Logotipo e favicon customizaveis
- Paleta de cores e tipografia do parceiro
- Dominio proprio (financeiro.parceiro.com.br)
- Emails transacionais com remetente do parceiro
- PDFs e relatorios com marca do parceiro
- Tela de login personalizada
- Remocao completa de qualquer referencia a UUBA na interface

### 4.2 Portal do Parceiro
Painel administrativo exclusivo para o parceiro gerenciar seus clientes e sua operacao.

- Visao geral de todos os clientes (tenants) do parceiro
- Criacao e configuracao de novos clientes (provisioning)
- Gestao de usuarios e permissoes por cliente
- Ativacao/desativacao de produtos por cliente
- Historico de acoes e auditoria
- Comunicacao com clientes (avisos, novidades)
- Acesso rapido ao ambiente de qualquer cliente (impersonation controlado)

### 4.3 Multi-tenant Hierarquico
Extensao do modelo multi-tenant da UUBA para suportar a hierarquia parceiro > clientes do parceiro.

- Tenant de parceiro (nivel 1) com visao agregada
- Tenants de clientes do parceiro (nivel 2) isolados entre si
- Dados financeiros de cada cliente isolados (tenant_id + partner_id)
- Parceiro nao acessa dados que o cliente nao autorizar
- Administracao centralizada pelo parceiro sem comprometer isolamento

### 4.4 Billing Flexivel
Sistema que permite ao parceiro definir como cobra seus clientes, independente de como a UUBA cobra o parceiro.

- Parceiro define planos e precos para seus clientes
- Suporte a modelos: preco fixo, por uso, por modulos, tiers
- Faturamento automatico dos clientes do parceiro (opcional)
- Dashboard de receita do parceiro (MRR, churn, LTV)
- Controle de inadimplencia dos clientes do parceiro
- Cobranca wholesale da UUBA para o parceiro (uma fatura consolidada)

### 4.5 SLA e Suporte de Retaguarda
Garantias de nivel de servico e suporte tecnico que o parceiro recebe da UUBA.

- SLA de uptime (99.5% ou superior)
- Suporte tecnico nivel 2 e 3 (o parceiro faz nivel 1)
- Canal dedicado para parceiros (nao e o suporte geral)
- Tempo de resposta garantido por severidade
- Comunicacao antecipada de manutencoes e atualizacoes
- Escalacao direta para engenharia em casos criticos

### 4.6 Escolha de Produtos
Parceiro escolhe quais produtos UUBA quer oferecer, montando pacotes customizados.

- Ativacao por produto: Recebe, Financeiro, 360, Nexo
- Possibilidade de oferecer plataforma completa ou modulos isolados
- Configuracao de features por plano (ex: DRE no plano basico, cenarios no premium)
- Precificacao diferenciada por modulo
- Upsell facilitado: parceiro ativa novos modulos para clientes existentes

### 4.7 Onboarding e Certificacao do Parceiro
Processo estruturado para capacitar o parceiro a vender, implementar e dar suporte nivel 1.

- Treinamento sobre cada produto (video + documentacao)
- Materiais de venda (apresentacoes, one-pagers, cases)
- Certificacao por produto (parceiro certificado UUBA Financeiro, etc.)
- Ambiente sandbox para demonstracoes e treinamento
- Playbook de implementacao (passo a passo para ativar um novo cliente)
- Comunidade de parceiros (troca de experiencias, melhores praticas)

### 4.8 Dashboard do Parceiro
Painel de indicadores de negocio do parceiro, focado em receita e saude da sua base de clientes.

- Receita recorrente mensal (MRR) do parceiro
- Numero de clientes ativos, inativos e em churn
- Uso da plataforma por cliente (engajamento)
- Receita por produto/modulo
- Previsao de receita (baseada em contratos e historico)
- Comparativo periodo anterior
- Exportacao de dados para BI externo

---

## 5. User Stories Estrategicas (ponto de vista do Parceiro)

**US-01:** Como dono de escritorio de contabilidade, quero oferecer uma plataforma de gestao financeira com minha marca para meus clientes, para que eu gere receita recorrente de tecnologia alem dos honorarios contabeis.

**US-02:** Como parceiro, quero criar um novo cliente na plataforma em menos de 5 minutos, para que eu possa fazer onboarding rapido e nao perder o timing da venda.

**US-03:** Como parceiro, quero definir meus proprios planos e precos, para que eu tenha flexibilidade para competir no meu mercado sem depender da tabela da UUBA.

**US-04:** Como parceiro, quero ver um dashboard com minha receita recorrente, churn e uso por cliente, para que eu gerencie meu negocio de revenda com dados concretos.

**US-05:** Como parceiro, quero que meus clientes vejam apenas minha marca na plataforma (logo, cores, dominio, emails), para que a experiencia seja 100% white-label e eu mantenha o relacionamento.

**US-06:** Como parceiro BPO, quero ativar o UUBA Financeiro em modo BPO para meus clientes, para que eu use a plataforma como ferramenta de trabalho e ganhe eficiencia operacional.

**US-07:** Como parceiro, quero ter um canal de suporte dedicado com a UUBA para questoes tecnicas, para que eu resolva problemas dos meus clientes rapidamente sem depender do suporte geral.

**US-08:** Como parceiro fintech, quero integrar a plataforma UUBA via API no meu produto existente, para que meus usuarios tenham gestao financeira embutida sem sair do meu app.

**US-09:** Como parceiro, quero acessar o ambiente de qualquer cliente meu de forma controlada, para que eu possa dar suporte nivel 1 e configurar a plataforma sem pedir credenciais ao cliente.

**US-10:** Como parceiro em fase de avaliacao, quero usar um ambiente sandbox para testar a plataforma antes de assinar contrato, para que eu tenha confianca no produto antes de oferece-lo aos meus clientes.

---

## 6. Dependencias

### 6.1 Estabilidade de todos os produtos
O programa de parceiros so funciona se os produtos subjacentes (Recebe, Financeiro, 360, Nexo) estiverem estaveis e maduros. Um parceiro que revende um produto instavel perde credibilidade com seus clientes e churna rapidamente.

**Implicacao:** Parceiros e o ultimo produto a ser lancado. Ele depende da maturidade de todos os outros.

### 6.2 Multi-tenancy hierarquico
O modelo atual de multi-tenancy (shared DB + tenant_id) precisa ser estendido para suportar a hierarquia parceiro > clientes do parceiro. Isso envolve:

- Campo partner_id nas tabelas principais
- Logica de acesso: parceiro ve seus clientes, mas clientes nao veem outros clientes do mesmo parceiro
- Provisioning automatizado (criar tenant + configurar produto + vincular ao parceiro)
- Isolamento de dados mantido entre clientes do mesmo parceiro

**Criticidade:** Alta. Sem multi-tenancy hierarquico, o portal do parceiro nao funciona.

### 6.3 White-label (tema, emails, dominio)
Infraestrutura tecnica para suportar personalizacao por parceiro:

- Sistema de temas (CSS/config) por partner_id
- Templates de email parametrizaveis (remetente, logo, cores)
- Suporte a dominio customizado (CNAME + certificado SSL automatico)
- Assets estaticos por parceiro (logo, favicon, imagens)

**Criticidade:** Alta. White-label e o requisito mais visivel e o primeiro que o parceiro avalia.

### 6.4 Sistema de billing
Infraestrutura para cobranca em duas camadas:
- UUBA cobra o parceiro (wholesale, fatura consolidada)
- Parceiro cobra seus clientes (com autonomia de pricing)

**Criticidade:** Media para v1 (pode ser manual), alta para v2.

---

## 7. Modelo de Receita do Parceiro

### Opcao A: Wholesale (Preco de Custo + Markup)
A UUBA cobra do parceiro um preco wholesale por cliente ativo (ex: 60% do preco de tabela). O parceiro define o preco final para seu cliente e fica com a diferenca.

| Item | Valor exemplo |
|------|---------------|
| Preco de tabela UUBA (cliente direto) | R$ 500/mes |
| Preco wholesale para parceiro | R$ 300/mes (60%) |
| Preco que o parceiro cobra do cliente | R$ 450/mes (definido pelo parceiro) |
| Margem do parceiro | R$ 150/mes (33%) |

**Vantagem:** Previsibilidade para ambos. Parceiro tem incentivo para vender mais caro.
**Risco:** Parceiro pode vender muito barato para ganhar volume, comprimindo sua propria margem.

### Opcao B: Revenue Share
A UUBA e o parceiro dividem a receita do cliente final em percentual pre-acordado.

| Item | Valor exemplo |
|------|---------------|
| Preco cobrado do cliente final | R$ 500/mes |
| Parcela UUBA | R$ 250/mes (50%) |
| Parcela parceiro | R$ 250/mes (50%) |

**Vantagem:** Alinhamento de incentivos -- ambos ganham mais quando o cliente paga mais.
**Risco:** Parceiro pode se sentir limitado por nao controlar o pricing.

### Opcao C: Hibrido
Combina um fee fixo minimo (wholesale) com bonus por desempenho (revenue share acima de X clientes).

**Recomendacao:** Comecar com Opcao A (wholesale) pela simplicidade operacional. Avaliar revenue share para parceiros maiores (50+ clientes) onde o alinhamento de incentivos importa mais.

---

## 8. Riscos e Open Questions

### Riscos

| Risco | Impacto | Probabilidade | Mitigacao |
|-------|---------|---------------|-----------|
| Parceiro dar suporte ruim e queimar a reputacao do produto | Alto | Alta | Certificacao obrigatoria; metricas de NPS por parceiro; rescisao por SLA nao cumprido |
| Custo de suporte de retaguarda nao escalar | Alto | Media | Self-service maximo; base de conhecimento; comunidade de parceiros para suporte peer-to-peer |
| Parceiro grande demais ter poder de barganha excessivo | Medio | Baixa | Diversificar base de parceiros; limitar concentracao; contrato com clausulas de exclusividade balanceadas |
| Complexidade tecnica do multi-tenant hierarquico | Alto | Media | Investir em arquitetura antes de lancar; testes exaustivos de isolamento de dados |
| Conflito de canal: UUBA vendendo direto vs parceiro vendendo na mesma regiao | Alto | Alta | Politica clara de territorio ou segmento; parceiro tem prioridade em seus clientes existentes |
| White-label incompleto (cliente descobre que e UUBA por tras) | Medio | Media | Auditoria completa de interface; remocao de todas as referencias; teste de usuario cego |

### Open Questions

1. **Exclusividade territorial:** parceiros terao exclusividade por regiao/segmento? Ou qualquer parceiro pode vender em qualquer lugar?
2. **Minimo de clientes:** existe um minimo de clientes ativos para manter o status de parceiro? (ex: 10 clientes em 12 meses)
3. **Self-service vs assistido:** o parceiro provisiona clientes sozinho ou a UUBA participa do onboarding do cliente final?
4. **Suporte ao cliente final:** o cliente final sabe que existe a UUBA por tras? Ou e 100% transparente/invisivel?
5. **Customizacao de features:** parceiros podem pedir features exclusivas? Se sim, quem paga pelo desenvolvimento?
6. **Churn de parceiro:** se um parceiro sai, o que acontece com os clientes? Migram para UUBA direto? Perdem acesso?
7. **Integracao com sistemas do parceiro:** o parceiro tem CRM, ERP proprio? Precisa de API de integracao bidirecional?

---

## 9. Faseamento Sugerido

### v1 -- White-label Basico
**Objetivo:** Permitir que um parceiro revenda a plataforma com sua marca visual.

- White-label de interface (logo, cores, favicon)
- Dominio customizado do parceiro
- Emails transacionais com marca do parceiro
- Criacao manual de clientes pelo time UUBA (sem portal ainda)
- Billing manual (UUBA fatura parceiro por planilha/contrato)
- Ate 3 parceiros piloto

**Criterio de sucesso:** 3 parceiros com pelo menos 5 clientes cada, operando com white-label sem incidentes de marca.

### v2 -- Portal do Parceiro e Billing
**Objetivo:** Dar autonomia ao parceiro para gerenciar seus clientes e automatizar cobranca.

- Portal do parceiro (criacao de clientes, gestao de usuarios, visao geral)
- Multi-tenant hierarquico (partner_id + tenant_id)
- Billing automatizado (UUBA cobra parceiro; parceiro define precos)
- Dashboard do parceiro (MRR, clientes, uso)
- Escolha de produtos/modulos por cliente
- Impersonation controlado (parceiro acessa ambiente do cliente)

**Criterio de sucesso:** Parceiro consegue provisionar e gerenciar clientes sem intervencao da equipe UUBA.

### v3 -- Escala e Certificacao
**Objetivo:** Escalar o programa para dezenas de parceiros com qualidade garantida.

- Programa de certificacao (treinamento + avaliacao por produto)
- Ambiente sandbox para demonstracoes
- Comunidade de parceiros (forum, eventos, melhores praticas)
- API de integracao para fintechs (provisioning, billing, dados)
- Materiais de venda padronizados (one-pagers, cases, apresentacoes)
- Metricas de qualidade por parceiro (NPS, tempo de resposta, churn)
- Politicas de territorio e conflito de canal formalizadas

**Criterio de sucesso:** 20+ parceiros ativos com programa de certificacao rodando e NPS medio acima de 8.
