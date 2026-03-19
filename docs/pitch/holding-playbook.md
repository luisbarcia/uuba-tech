# UUBA Tech — Playbook para Conversas com Holdings

> Material estrategico para negociacoes com holdings interessadas em incorporar a UUBA Tech.
> Versao: 2026-03-19 | Confidencial — apenas para uso interno dos cofundadores.

---

## Indice

1. [Resumo Executivo](#1-resumo-executivo)
2. [Por que uma Holding quer a UUBA](#2-por-que-uma-holding-quer-a-uuba)
3. [O que a Holding oferece (sinergias reais)](#3-o-que-a-holding-oferece)
4. [O que a Holding NAO te conta (riscos reais)](#4-o-que-a-holding-nao-te-conta)
5. [Estruturas de Deal possiveis](#5-estruturas-de-deal-possiveis)
6. [Framework de Valuation](#6-framework-de-valuation)
7. [O que proteger na negociacao](#7-o-que-proteger-na-negociacao)
8. [Red Flags — quando sair da mesa](#8-red-flags)
9. [Roteiro da conversa (15 min)](#9-roteiro-da-conversa)
10. [FAQ — Respostas prontas](#10-faq)
11. [Checklist pre-reuniao](#11-checklist)
12. [Referencias de mercado](#12-referencias)

---

## 1. Resumo Executivo

**O que e a UUBA Tech:**

Plataforma de gestao financeira e operacional para PMEs brasileiras. Cinco produtos integrados (Nexo, Financeiro, Recebe, 360, Parceiros) que combinam automacao, IA e profissionais especializados para entregar a operacao financeira completa.

**Estagio atual:**

- UUBA Recebe em producao (bot WhatsApp com IA cobrando clientes)
- API propria: 14 endpoints, 174 testes, CI/CD completo
- Infra self-hosted: Docker, PostgreSQL, Redis, nginx, SSL
- Consultoria (BPO + CFO de Aluguel) com ~1,5 ano de mercado e clientes ativos
- Time: 3 cofundadores complementares (estrategia + operacao + tecnologia)

**Stack propria = margem propria:**

- Nao paga por mensagem WhatsApp (Evolution API self-hosted)
- Nao paga por transacao (API propria)
- Nao depende de plataforma de terceiro
- Custo de infra: 1 VPS Contabo

---

## 2. Por que uma Holding quer a UUBA

Entender a motivacao do comprador e a arma mais importante da negociacao.

### O que a holding provavelmente viu:

| Ativo | Por que tem valor |
|-------|------------------|
| **Canal WhatsApp + IA** | Cobranca conversacional via WhatsApp e um canal com taxa de abertura >90%. Pouquissimas empresas tem um agente de IA funcional cobrando em producao |
| **Vertical fintech para PMEs** | Brasil tem 20M+ PMEs. Gestao financeira e uma dor universal e recorrente |
| **Stack propria** | Sem dependencia de APIs de terceiros = margens altas e controle total |
| **BPO + SaaS** | Modelo hibrido raro: software + servico. Receita recorrente + relacionamento profundo com cliente |
| **Modelo de Parceiros** | White-label permite escalar via contabilidades (cada uma atende 50-200 empresas) |
| **Time tecnico** | CTO com dedicacao exclusiva, infra pronta, documentacao de 19 secoes |

### O que a holding realmente quer:

Uma holding tipicamente busca:

1. **Cross-sell:** Oferecer cobranca/financeiro pros clientes que ela ja tem
2. **Tecnologia:** Absorver a stack pra usar internamente
3. **Acqui-hire:** Contratar o time tecnico via aquisicao
4. **Tese de mercado:** Montar um ecossistema financeiro para PMEs

**Pergunte diretamente:** *"Qual das suas empresas seria a primeira a usar os nossos produtos?"* — a resposta revela a motivacao real.

---

## 3. O que a Holding oferece

### Sinergias potenciais (avalie criticamente):

| Sinergia prometida | Valor real | Cuidado |
|---------------------|------------|---------|
| Base de clientes | Alto — se houver fit de perfil | Clientes da holding podem nao ser PMEs. Verificar o ICP |
| Capital para crescimento | Alto — se vier sem amarras | Capital com muitas condicoes pode ser pior que bootstrapping |
| Infra compartilhada (juridico, RH, contabil) | Medio | Pode tirar agilidade e criar dependencia |
| Credibilidade/marca | Medio | Pode ajudar em vendas B2B enterprise, mas pode confundir o mercado PME |
| Rede de vendas | Medio-Alto | Vendedores generalistas raramente vendem bem produto tecnico |
| P&D compartilhado | Baixo-Medio | Prioridades de P&D podem conflitar |

### A pergunta que importa:

> *"Quantos clientes novos vocês projetam que o deal traria nos primeiros 12 meses?"*

Se nao tem numero, nao tem sinergia — tem promessa.

---

## 4. O que a Holding NAO te conta

### Riscos reais de entrar numa holding:

**Perda de velocidade:**
- Decisoes que voce toma em 5 minutos passam a ter 3 niveis de aprovacao
- Sprints de 1 semana viram ciclos de 1 mes
- "Alinhamento com a holding" vira a pauta principal

**Perda de autonomia:**
- A holding define prioridades. Seu roadmap de produto pode ser sequestrado pra atender demandas internas da holding
- Fundadores viram "heads de unidade" — perdem poder de decisao estrategica

**Conflito de interesses:**
- Se a holding tem outra empresa que faz algo parecido, a UUBA pode virar "feature" e nao "produto"
- Orçamento pode ser redirecionado pra unidade mais rentavel da holding

**Brain drain:**
- Se os fundadores saem apos o lock-up, a holding fica com a casca e perde a essencia
- 67% dos fundadores que vendem para holdings saem em ate 2 anos (media do mercado)

**Sinergias superestimadas:**
- Em M&A, sinergias sao consistentemente superestimadas. Custos de integracao (migracao de sistemas, reestruturacao legal) sao consistentemente subestimados

---

## 5. Estruturas de Deal possiveis

### A. Investimento minoritario (holding como investidora)

```
Holding compra 10-25% da UUBA Tech
Fundadores mantem controle (75-90%)
Capital entra no caixa da empresa
```

- **Pros:** Capital sem perda de controle. Sinergia comercial sem subordinacao
- **Contras:** Holding pode querer board seat + veto rights
- **Quando faz sentido:** Holding quer acesso ao produto/canal mas nao quer operar

### B. Aquisicao majoritaria com permanencia dos fundadores

```
Holding compra 51-70% da UUBA Tech
Fundadores ficam com 30-49%
Fundadores tem lock-up de 2-4 anos
Earnout atrelado a metricas
```

- **Pros:** Liquidez parcial para fundadores. Recursos da holding
- **Contras:** Perda de controle. Decisoes estrategicas passam pela holding
- **Quando faz sentido:** Holding tem canal de distribuicao real que multiplica receita 5x+

### C. Aquisicao total (exit)

```
Holding compra 100%
Cash + earnout
Fundadores ficam 2-3 anos (lock-up)
```

- **Pros:** Liquidez total. Risco zerado
- **Contras:** Voce vira funcionario. Pode perder a empresa que construiu
- **Quando faz sentido:** Valor oferecido e >10x o que voce conseguiria sozinho em 5 anos

### D. Joint Venture / Subsidiaria

```
Holding e UUBA criam empresa nova (50/50 ou outra proporcao)
UUBA entra com tecnologia + operacao
Holding entra com clientes + capital
```

- **Pros:** Ambos tem skin in the game. Estrutura limpa
- **Contras:** Governanca complexa. Decisoes empatam
- **Quando faz sentido:** Quando o valor esta na combinacao, nao na absorcao

### E. Acordo comercial (sem equity)

```
Parceria comercial ou licenciamento
Holding distribui/revende os produtos UUBA
Revenue share ou fee fixo
```

- **Pros:** Zero diluicao. Testa a sinergia antes de casar
- **Contras:** Menos comprometimento da holding. Pode ser cancelado
- **Quando faz sentido:** Quando voce nao tem certeza do fit. Comecar por aqui e sempre valido

---

## 6. Framework de Valuation

### Dados de referencia (Brasil, 2024-2026):

| Metrica | Range | Fonte |
|---------|-------|-------|
| Valuation Seed BR (pre-money) | R$ 14M - R$ 67M | LAVCA/Crunchbase |
| Multiplos SaaS privado | 4,7x - 6,1x receita | SaaS Capital |
| Multiplos Fintech privado | 3,7x - 7,4x receita | Finro/Qubit |
| Desconto LATAM vs EUA | 30-50% | Mercado |

### Como pensar no valor da UUBA Tech:

**Metodo 1 — Custo de replicacao:**

| Ativo | Valor estimado |
|-------|---------------|
| API REST (14 endpoints, 174 testes, CI/CD) | R$ 150k - R$ 250k |
| Bot WhatsApp com IA + protocolo comportamental | R$ 100k - R$ 180k |
| Infra completa (Docker, nginx, SSL, 4 dominios) | R$ 80k - R$ 120k |
| Portal de documentacao (19 secoes) | R$ 30k - R$ 50k |
| Automacoes n8n + integracoes | R$ 40k - R$ 70k |
| **Total custo de replicacao** | **R$ 400k - R$ 670k** |

**Metodo 2 — Valor de mercado do time + ativo:**

| Componente | Valor |
|------------|-------|
| 3 cofundadores (valor de mercado anual) | R$ 720k - R$ 1.2M/ano |
| Carteira de clientes consultoria (~1,5 ano) | R$ 200k - R$ 500k |
| Marca + dominios + presenca digital | R$ 50k - R$ 100k |
| Propriedade intelectual (protocolo de cobranca + prompts) | R$ 100k - R$ 200k |

**Metodo 3 — Projecao de receita (se tiver numeros):**

Se a UUBA Tech projetar R$ X/mes de MRR em 12 meses, aplique multiplo de 4-6x ARR.

Exemplo: R$ 50k MRR → R$ 600k ARR → Valuation de R$ 2,4M - R$ 3,6M

### Regra de ouro:

> Nunca aceite uma proposta sem saber o valuation implicito. Se a holding oferece X por Y%, calcule: X / Y% = valuation. Compare com os benchmarks acima.

---

## 7. O que proteger na negociacao

### Clausulas inegociaveis (nao abra mao):

| Protecao | Por que | Como garantir |
|----------|---------|---------------|
| **Autonomia operacional** | Sem isso, voce vira gerente de projeto | Clausula de "reserved matters" — decisoes de produto, contratacao e tech ficam com os fundadores |
| **Vesting acceleration (double-trigger)** | Se a holding te demitir pos-aquisicao, voce nao perde equity | Clausula de aceleracao: change of control + demissao sem justa causa = 100% vesting |
| **Anti-diluicao (weighted average)** | Se a holding fizer rodada futura, voce nao e diluido sem compensacao | Clausula padrao. NUNCA aceitar full ratchet |
| **Board seat** | Ter voz nas decisoes estrategicas | Minimo 1 seat. Ideal: maioria de fundadores ou empate com independent director |
| **Tag-along** | Se a holding vender a parte dela, voce pode vender junto | Clausula padrao em acordos societarios |
| **Piso de investimento** | Garantir que a holding investe de fato, nao so compra e senta | "A holding se compromete a investir R$ X nos primeiros 24 meses em marketing/vendas/produto" |
| **Non-compete razoavel** | 12 meses max, geograficamente limitado | Nunca aceitar non-compete de 3+ anos ou "global" |

### Clausulas para negociar (importante mas flexivel):

- **Earnout metrics**: Se tiver earnout, metricas devem ser claras, mensuráveis e dentro do seu controle (MRR, clientes ativos) — nunca EBITDA (a holding controla os custos)
- **Lock-up period**: 2 anos e razoavel. 4 anos e agressivo. Negociar liberacao gradual
- **Pro-rata rights**: Direito de participar de rodadas futuras para manter %
- **Drag-along threshold**: Nunca abaixo de 75% de aprovacao
- **IP ownership**: Se sair, o que voce pode levar? Negociar licenca de uso da tech que voce criou

---

## 8. Red Flags

### Saia da mesa se:

- **Full ratchet anti-dilution** — pratica predatoria. 95% do mercado usa weighted average
- **Liquidation preference > 1x** — em 2025, 98% dos deals usam 1x. Se pede mais, e ganancia
- **Participating preferred (double-dip)** — investidor recebe preferencia E participa do rateio. Destrue o payout dos fundadores
- **Earnout = maioria do preco** — se >50% do deal e earnout, o risco e todo seu. Media do mercado: apenas 21% do earnout maximo e efetivamente pago
- **Non-compete de 3+ anos** — desproporcional. Pode bloquear sua carreira
- **Sem definicao clara do papel dos fundadores** — ambiguidade = voce vira subordinado sem contrato
- **Pressa para fechar** — pressao para assinar sem due diligence adequada = algo a esconder
- **Historico ruim com aquisicoes** — sempre perguntar: *"Posso conversar com fundadores de empresas que voces ja adquiriram?"*

### Yellow flags (investigue mais):

- Holding quer exclusividade de negociacao por >30 dias
- Nao quer colocar termos no papel antes de due diligence
- Fala muito em "sinergia" mas nao apresenta numeros
- O interlocutor nao e quem decide (voce pode estar falando com um intermediario)

---

## 9. Roteiro da conversa (15 min)

### Fase 1 — Escutar (5 min)

Antes de apresentar qualquer coisa, entenda o que a holding quer. Perguntas-chave:

1. *"O que motivou o interesse na UUBA?"*
2. *"Como voces enxergam a UUBA dentro do portfolio de voces?"*
3. *"Quais empresas do grupo seriam as primeiras a usar nossos produtos?"*
4. *"Como funcionaram aquisicoes anteriores? Os fundadores ainda estao?"*

> **Regra:** Quem fala mais, revela mais. Deixe a holding falar.

### Fase 2 — Apresentar (5 min)

Use o [roteiro de 5 min para investidores](roteiro-investidor.md), adaptando:

- Enfatize o **modelo de Parceiros** (a holding pode ser o primeiro grande parceiro)
- Enfatize a **stack propria** (nao dependem de ninguem — margem alta)
- Enfatize o **time** (3 cofundadores, dedicacao exclusiva do CTO)
- Se possivel, mostre o bot cobrando ao vivo no WhatsApp

### Fase 3 — Explorar (5 min)

Perguntas para guiar a conversa:

1. *"Que tipo de estrutura voces estao pensando? Investimento, aquisicao, parceria?"*
2. *"Qual o horizonte de tempo que voces trabalham?"*
3. *"Como funciona a autonomia das empresas dentro do grupo?"*
4. *"Vocês tem interesse em distribuir nossos produtos para a base de clientes de vocês?"*

> **Nunca fale em numero primeiro.** Quem fala o numero primeiro perde poder de negociacao. Se perguntarem "quanto vale?", responda: *"Depende da estrutura. Uma coisa é investimento minoritário, outra é aquisição. O que faz mais sentido pra vocês?"*

### Encerramento:

> *"Ótima conversa. Vamos marcar uma segunda reunião com mais detalhes? Podemos trazer um overview técnico e financeiro mais completo."*

Nunca feche nada na primeira reuniao. Sempre peça tempo.

---

## 10. FAQ

### Sobre a empresa

**"Qual o faturamento?"**
> A Uuba consultoria tem receita recorrente com BPO financeiro e CFO de Aluguel. A Uuba Tech (produto) esta em fase de lancamento — o primeiro produto (Recebe) ja esta em producao. *(Ter os numeros exatos de receita mensal da consultoria prontos)*

**"Quantos clientes tem?"**
> *(Ter numero exato pronto)* Clientes ativos de consultoria que serao os primeiros usuarios dos produtos Tech.

**"Qual o burn rate?"**
> Baixissimo. Infra custa uma VPS. Time sao os 3 cofundadores com pro-labore minimo. Nao estamos queimando caixa — estamos construindo.

**"Voces tem concorrente direto?"**
> Ferramentas de cobranca existem (Asaas, Vindi, Neofin), mas nenhuma combina IA conversacional + protocolo comportamental + BPO. O diferencial nao e so o software — e a operacao.

### Sobre o deal

**"Quanto voces estao pedindo?"**
> *"Depende da estrutura. Estamos abertos a investimento, parceria ou algo mais estrategico. O que faz mais sentido pra voces?"* — devolva a pergunta.

**"Voces venderiam 100%?"**
> *"Nao estamos buscando venda nesse momento. Estamos buscando parceiros estrategicos que multipliquem o que ja construimos."*

**"Topam exclusividade para negociar?"**
> *"Podemos discutir uma janela de exclusividade razoavel — 15 a 30 dias — apos termos os principais pontos alinhados em um term sheet."*

**"Quanto vale a empresa?"**
> *"O custo de replicar o que construimos esta na faixa de R$ 400k a R$ 670k — mas valor de empresa nao e custo de replicacao. E potencial de mercado + time + traction. Vamos explorar juntos o que faz sentido."*

### Sobre os fundadores

**"Os fundadores ficariam apos o deal?"**
> *"Esse e um ponto fundamental pra nos. A UUBA funciona por causa das pessoas. Qualquer estrutura precisa manter os tres motivados e com autonomia."*

**"Quem decide o que na empresa?"**
> Heitor: estrategia e analise. Thomaz: operacao e atendimento. Luis: tecnologia e produto. Decisoes estrategicas sao consensuais.

**"E se um fundador quiser sair?"**
> Acordo de socios com clausulas de good/bad leaver e vesting. Protege tanto os que ficam quanto quem sai.

### Perguntas que VOCES devem fazer

1. Quantas aquisicoes/investimentos a holding ja fez?
2. Posso conversar com fundadores de empresas que voces ja incorporaram?
3. Qual a tese de investimento do grupo? Onde a UUBA se encaixa?
4. Como funciona a governanca? Quem aprova orcamento, contratacao, roadmap?
5. Qual o horizonte de retorno que voces trabalham? (3 anos? 5? 10?)
6. Se o deal nao andar, voces teriam interesse numa parceria comercial?

---

## 11. Checklist pre-reuniao

### Preparar:

- [ ] Numeros atualizados: receita mensal da consultoria, numero de clientes, custo mensal de infra
- [ ] Bot WhatsApp funcionando e pronto pra demo ao vivo
- [ ] Portal interno no ar (luisbarcia.github.io/uuba-tech) com paginas de produtos funcionando
- [ ] API respondendo (api.uuba.tech/health)
- [ ] Este documento lido e discutido entre os 3 cofundadores
- [ ] Alinhamento interno: qual a estrutura preferida? (investimento? parceria? JV?)
- [ ] Alinhamento interno: qual o minimo aceitavel? (% de equity, autonomia, pro-labore)
- [ ] Pesquisar a holding: quais empresas tem? Quem sao os socios? Historico de M&A?

### Na reuniao:

- [ ] Levar celular com WhatsApp do bot
- [ ] Nao falar numero primeiro
- [ ] Escutar mais do que falar nos primeiros 5 minutos
- [ ] Anotar tudo (ou gravar com permissao)
- [ ] Nao fechar nada na primeira reuniao
- [ ] Pedir follow-up por escrito

### Apos a reuniao:

- [ ] Registrar tudo que foi discutido por escrito (enviar email de recap)
- [ ] Avaliar internamente: os 3 cofundadores alinhados?
- [ ] Se avancar: pedir term sheet por escrito antes de qualquer compromisso
- [ ] Consultar advogado societario antes de assinar qualquer coisa

---

## 12. Referencias de mercado

### Holdings brasileiras que adquirem tech (para comparar):

| Holding | Perfil | Deals notaveis |
|---------|--------|----------------|
| **TOTVS** | Ecossistema ERP | RD Station (R$ 1,86B), Bematech, Datasul. 30+ aquisicoes. Fundo CVC de R$ 300M |
| **Locaweb** | Ecossistema e-commerce | MelhorEnvio, Vindi, Bling. R$ 393M+ em aquisicoes pos-IPO |
| **Magalu** | Super-app | KaBuM (R$ 3,5B), AiQFome, Jovem Nerd. 25 aquisicoes |
| **Movile** | Holding tech | iFood, Sympla. Modelo descentralizado (mais autonomia) |
| **Stone/PagSeguro** | Fintech | Aquisicoes em pagamentos e gestao para PMEs |

### Padroes comuns em deals brasileiros:

- Cash + earnout e o formato mais frequente (R$ 10M - R$ 200M)
- Fundadores reteem 5-15% com vesting de 2-3 anos
- Lock-up de fundadores: 2-4 anos
- Earnout atrelado a MRR/ARR e retencao de clientes
- Apenas 21% do earnout maximo e efetivamente pago (media global)
- Conversao Seed → Series A no Brasil: apenas 1 em cada 10

### Dados de valuation Brasil:

- Valuation medio pre-money Seed BR (2023): R$ 67M
- SaaS privado global: 4,7x - 6,1x receita
- Fintech privado global: 3,7x - 7,4x receita
- Desconto LATAM vs EUA: 30-50%

---

> **Lembrete final:** A melhor negociacao e aquela em que voce pode levantar e ir embora. Ter opcoes (bootstrapping, outro investidor, parceria comercial sem equity) e a maior fonte de poder numa mesa de negociacao. Nunca negocie como se precisasse do deal — mesmo que precise.
