# Pesquisa UX + Devil's Advocate: UUBA 360

**Produto:** UUBA 360 — Dashboards por perfil (CFO, gerente, analista), KPIs em tempo real
**Data:** 2026-03-22
**Metodologia:** Desk research, pesquisa Sebrae, pesquisa Conta Azul, artigos especializados, dados de mercado

---

## PARTE 1 — UX RESEARCH

### 1. Como PMEs brasileiras acompanham indicadores financeiros hoje

**A realidade nua e crua:**

- **74% dos empreendedores ainda dependem de planilhas** para a gestão financeira (Pesquisa Conta Azul, jul/2024, 421 empresas)
- **30% das PMEs não sabem se fecham o mês com lucro ou prejuizo** (Pesquisa "Digitalização dos empreendedores brasileiros", Conta Azul)
- **85% dos pequenos e medios empresarios nao possuem um fechamento mensal detalhado** que discrimine receitas e despesas
- **Mais de 50% dos empresarios afirmam ter dificuldade para interpretar informacoes financeiras** da propria empresa (Sebrae)
- **49% dedicam tempo excessivo a tarefas burocraticas** ligadas a rotina financeira
- **Apenas 31% digitalizaram seus processos administrativos** ate o momento

**O "sistema" mais comum:** extrato bancario + planilha Excel + caderninho + "cabeca do dono"

**Fluxo tipico:**
1. Dono abre app do banco todo dia pra ver saldo
2. Alguem (ou ninguem) lanca no Excel de vez em quando
3. No fim do mes, contador manda balancete que ninguem le
4. Decisoes sao tomadas com base na "sensacao" de como o mes foi

---

### 2. Problemas com relatorios em Excel/planilha

| Problema | Impacto real |
|----------|-------------|
| **Desatualizada** | Lancamentos atrasam, dados ficam velhos. "Quando olho a planilha, ja nao reflete a realidade" |
| **Sem padronizacao** | Cada pessoa lanca de um jeito, registros inconsistentes, erros acumulados |
| **Sem integracao** | Nao conversa com banco, ERP, nota fiscal. Tudo manual |
| **Sem acesso simultaneo** | So uma pessoa edita por vez, setores nao se falam |
| **Quebra de disciplina** | Comecam motivados, mas em 2 meses param de atualizar |
| **Erros humanos** | Formulas quebradas, linhas deletadas, valores errados |
| **Sem visao consolidada** | Tem 5 planilhas separadas, nenhuma conversando |
| **Nao escala** | Funcionou com 10 transacoes/dia, trava com 200 |

**Dado critico:** A dependencia exclusiva de planilhas limita crescimento. Um bom sistema deve oferecer automacao, integracao bancaria e relatorios confiaveis.

---

### 3. Por que PMEs nao usam Power BI / Metabase / Tableau

| Barreira | Detalhe |
|----------|---------|
| **Custo por usuario** | Power BI Pro custa ~R$54/usuario/mes. Para 10 usuarios = R$540/mes. Premium pode passar de R$100k/ano |
| **Precisa de analista de dados** | Ninguem na empresa sabe modelar dados, criar DAX, montar relacionamentos |
| **Precisa de dados limpos** | "Garbage in, garbage out" — se o ERP esta bagunçado, o dashboard tambem fica |
| **Tempo de implementacao** | Projeto de BI leva meses. PME precisa de resultado pra ontem |
| **Manutencao continua** | Dashboard quebra quando muda o ERP, quando entra campo novo, quando alguem muda a planilha-fonte |
| **Metabase e open-source mas...** | Precisa de servidor, Docker, alguem tecnico pra instalar e manter |
| **Complexidade visual** | "O dashboard estava muito complexo e lento para carregar" — usuarios voltam pro Excel |
| **Falta de contexto de negocio** | Ferramentas sao genericas. Nao sabem o que e importante pra uma PME brasileira |

**Resumo brutal:** O dono da PME precisa de alguem que ENTENDA o negocio dele e ENTREGUE a visao pronta. Ele nao quer construir dashboard — quer ABRIR e VER.

---

### 4. Reclamacoes sobre falta de visibilidade (Sebrae, mercado, especialistas)

- **48% das micro e pequenas empresas fecham por problemas de planejamento financeiro** (Sebrae)
- **6 em cada 10 empresas nao sobrevivem apos 5 anos** (IBGE)
- **90% das PMEs em crise tem ma gestao financeira** como fator contribuinte
- Mais da metade dos empresarios **nao usa indicadores financeiros de forma recorrente** para embasar decisoes
- **60% relatam nao conseguir implementar ferramentas tecnologicas** que desejam (Conta Azul)
- "Quando o empresario nao consegue enxergar margem, impacto no caixa e compromissos futuros, **ele decide no escuro**"

---

### 5. O que o CFO/controller de PME realmente precisa ver

**Indicadores essenciais (do mais urgente ao estrategico):**

1. **Fluxo de caixa em tempo real** — quanto tenho, quanto entra, quanto sai nos proximos 7/15/30 dias
2. **DRE gerencial mensal** — receita, custos, despesas, lucro operacional (nao o contabil, o REAL)
3. **Margem por produto/servico** — o que da dinheiro e o que esta comendo margem
4. **Contas a receber vs contas a pagar** — visao de compromissos futuros
5. **Inadimplencia** — quem deve, quanto, ha quanto tempo
6. **Ponto de equilibrio** — quanto preciso faturar pra pagar as contas
7. **Comparativo mes a mes / ano a ano** — tendencia, sazonalidade
8. **Capital de giro necessario** — se vai faltar dinheiro antes de receber

**O controller quer:** sair do papel de "gerador de relatorio" e virar **parceiro estrategico**. Mas para isso, precisa de dados consolidados automaticamente.

---

### 6. Verbatins do empresario (8 falas reais reconstruidas a partir de pesquisa)

> **V1:** "Eu fecho o mes e nao sei se dei lucro ou prejuizo. So vou descobrir quando o contador manda o balancete, 40 dias depois."

> **V2:** "Minha empresa fatura bem, mas nunca sobra dinheiro. Eu nao sei pra onde vai. Vendo, vendo, vendo, e no fim do mes estou no cheque especial."

> **V3:** "Tenho tres planilhas: uma do financeiro, uma do comercial, uma minha. Nenhuma bate com a outra. Quando preciso de um numero, passo a tarde inteira juntando dados."

> **V4:** "Ja tentei Power BI. Contratei um freelancer, ele montou um dashboard bonito. Dois meses depois quebrou tudo porque mudamos de sistema. Nunca mais mexemos."

> **V5:** "Eu tomo decisao pelo saldo do banco. Se tem dinheiro na conta, esta bom. Se nao tem, corto custo. E assim que funciona aqui."

> **V6:** "Meu contador me manda um PDF todo mes com numeros que eu nao entendo. Pago R$3.000 de contabilidade e nao consigo responder uma pergunta simples: estou ganhando ou perdendo dinheiro?"

> **V7:** "Queria ter uma tela onde eu abrisse e visse: quanto entrou, quanto saiu, quanto vai entrar, quanto vai sair. So isso. Parece simples, mas ninguem me entrega isso de um jeito que eu consiga usar."

> **V8:** "A gente cresce no escuro. Contrato gente, abro filial, faco investimento... tudo na intuicao. Quando da errado, a gente so descobre 3 meses depois, quando o caixa ja secou."

---

### 7. Jobs to Be Done (5 JTBD sobre dashboards/indicadores)

**JTBD 1 — Saber se estou ganhando ou perdendo dinheiro**
> "Quando eu fecho o caixa no fim do dia, quero saber se aquele dia foi positivo ou negativo, **para que** eu possa reagir rapido se algo estiver errado, **sem** esperar o fechamento do mes."

**JTBD 2 — Antecipar problemas de caixa antes que virem crise**
> "Quando eu olho meus compromissos dos proximos 15 dias, quero ver se vai faltar dinheiro, **para que** eu possa negociar prazo, antecipar recebivel ou cortar gasto, **sem** ser pego de surpresa."

**JTBD 3 — Entender onde o dinheiro esta indo**
> "Quando eu percebo que o faturamento subiu mas o lucro nao acompanhou, quero ver uma abertura por categoria de despesa, **para que** eu identifique o que esta comendo minha margem, **sem** ter que montar relatorio manualmente."

**JTBD 4 — Mostrar numeros pro socio/investidor/banco sem passar vergonha**
> "Quando o banco pede informacoes financeiras ou meu socio quer saber como esta a empresa, quero apresentar dados organizados e confiaveis, **para que** eu transmita profissionalismo e credibilidade, **sem** improvisar com planilha bagunçada."

**JTBD 5 — Tomar decisao de investimento/corte com base em dados**
> "Quando eu preciso decidir se contrato mais gente, se compro equipamento ou se corto um produto, quero ver o impacto financeiro projetado, **para que** eu decida com seguranca, **sem** depender so da minha intuicao."

---

### 8. Vocabulario do empresario PME

**O que ele fala vs. o que nos chamamos:**

| O empresario diz | Nos chamamos |
|-----------------|-------------|
| "Meus numeros" | KPIs, metricas |
| "Meu controle" | Dashboard, painel |
| "Ver como esta a empresa" | Visibilidade financeira |
| "Quanto entrou e quanto saiu" | Fluxo de caixa |
| "Se estou no azul ou no vermelho" | Resultado operacional, P&L |
| "O que da dinheiro e o que nao da" | Margem por produto/servico |
| "Quanto preciso vender pra pagar as contas" | Ponto de equilibrio, break-even |
| "Quem me deve" | Contas a receber, inadimplencia |
| "Sobra" ou "Lucro" | EBITDA, lucro liquido |
| "Fechamento do mes" | DRE gerencial |
| "Ver o futuro" ou "Saber o que vem pela frente" | Projecao, forecast |
| "Relatorio" | Report, analytics |
| "Numero batendo" | Conciliacao |
| "Tela com tudo junto" | Dashboard consolidado |
| "Meu extrato" | Movimentacao financeira |

**Regra de ouro para comunicacao do 360:** NUNCA use "KPI", "BI", "analytics", "data-driven" no pitch para o dono. Use "seus numeros", "sua visao", "seu controle".

---

## PARTE 2 — DEVIL'S ADVOCATE

### Provocacao 1: Dashboard e "nice to have" pra PME?

**O argumento contra:**
O empresario de PME vive apagando incendio. Ele nao para pra olhar dashboard. Ele quer vender, entregar, cobrar. Dashboard e luxo de empresa grande que tem controller, analista, gerente. Na PME de 20 funcionarios, quem vai parar pra analisar grafico?

**Contra-argumento (por que e essencial):**
- **30% das PMEs nao sabem se dao lucro.** Isso nao e "nice to have", e sobrevivencia.
- **48% fecham por falta de planejamento financeiro.** O dashboard nao e luxo — e o diferencial entre sobreviver e morrer.
- O dono JA olha numero todo dia (saldo do banco). O problema e que ele olha o numero ERRADO. Saldo bancario nao e saude financeira.
- O dashboard nao e pra ele "analisar grafico". E pra ele abrir o celular e em 5 segundos saber: "estou bem ou estou mal?". **E um termometro, nao um laboratorio.**
- **Posicionamento do 360:** nao e ferramenta de analise. E um ALERTA INTELIGENTE que mostra o que precisa de atencao.

**Veredicto:** Dashboard generico e nice to have. Dashboard que traduz a saude da empresa em linguagem simples e MUST HAVE. O 360 precisa ser o segundo, nao o primeiro.

---

### Provocacao 2: Se o dono ja abre o extrato do banco todo dia, por que precisa de dashboard?

**O argumento contra:**
O empresario ja tem seu "dashboard": o app do banco. Ele abre, ve o saldo, sabe se tem dinheiro. Isso ja resolve 80% da necessidade dele. Por que complicar?

**Contra-argumento:**
- **Saldo bancario e fotografia, nao filme.** Mostra o AGORA, nao mostra o que vem.
- Ter R$50k no banco parece otimo. Mas se tem R$80k de folha pra pagar em 5 dias, ele esta no vermelho e nao sabe.
- O extrato nao mostra **margem por cliente/produto**. Ele pode estar vendendo muito um produto que da prejuizo.
- O extrato nao mostra **tendencia**. Ele nao sabe se janeiro foi melhor que dezembro sem montar planilha.
- O extrato mistura **operacional com financeiro**. Emprestimo entrando parece receita. Antecipacao de recebivel parece venda.
- **A ilusao do saldo:** "Minha empresa fatura bem, mas nunca sobra dinheiro." Esse e o sintoma classico de quem gerencia pelo extrato.

**Veredicto:** O extrato e como medir febre com a mao. Funciona pra saber se esta "quente", mas nao substitui o termometro. O 360 e o termometro + historico + projecao.

---

### Provocacao 3: Power BI e gratis e faz tudo — por que pagar pelo 360?

**O argumento contra:**
Power BI Desktop e gratis. Metabase e open-source. Google Looker Studio e gratis. Por que o empresario pagaria pelo 360 se existem opcoes gratuitas que tecnicamente fazem TUDO que o 360 faz e mais?

**Contra-argumento:**
- **Gratis ≠ custo zero.** Power BI e gratis pra INSTALAR, mas precisa de:
  - Alguem que saiba modelar dados (analista de dados: R$5-8k/mes)
  - Dados limpos e organizados (se o ERP e baguncado, o BI e baguncado)
  - Manutencao quando algo muda (ERP atualiza, dashboard quebra)
  - Tempo de implementacao: 2-6 meses pra algo util
  - Power BI Pro pra compartilhar: R$54/usuario/mes
- **TCO real do "Power BI gratis"** pra PME: R$8-15k/mes quando soma analista + infra + manutencao
- **74% ainda estao no Excel.** Se Power BI fosse tao acessivel assim, ja teriam migrado.
- **60% nao conseguem implementar ferramentas que desejam.** A barreira nao e vontade, e capacidade.
- **O 360 faz pra voce o que o Power BI te obriga a fazer sozinho:**
  - Conecta nos seus dados automaticamente (via Nexo)
  - Ja vem com os dashboards certos pra PME brasileira
  - Nao precisa de analista, nao precisa de TI
  - Atualiza sozinho, avisa quando algo esta errado

**Analogia:** Power BI e como dar uma cozinha industrial pra quem quer jantar. O 360 e o prato pronto, quentinho, do jeito que voce gosta.

**Veredicto:** A concorrencia do 360 NAO e o Power BI. E o Excel + extrato bancario + intuicao. E contra isso que a gente luta.

---

### Provocacao 4: O 360 depende do Nexo pra funcionar — isso e barreira de adocao?

**O argumento contra:**
Se o cliente precisa PRIMEIRO comprar/usar o Nexo (hub de dados) pra DEPOIS ter o 360 (dashboards), voce criou uma barreira dupla de adocao. O cliente precisa:
1. Confiar na Uuba
2. Implementar o Nexo (conectar seus sistemas)
3. Esperar os dados fluirem
4. Ai sim ver valor no 360

Isso e pedir demais pra um empresario que ja tem desconfianca de tecnologia.

**Contra-argumento:**
- **Sim, e uma barreira real.** Nao da pra negar.
- **Mas o valor do 360 e exatamente o incentivo pra adotar o Nexo.** Ninguem quer um "hub de dados" por si so. Quer "ver seus numeros". O 360 e o MOTIVO pelo qual o empresario aceita conectar seus sistemas.
- **Estrategia de mitigacao:**
  - **Time-to-value agressivo:** em 48h apos conectar, o empresario ve o primeiro dashboard funcionando
  - **Comecar simples:** conecta so o banco + ERP no primeiro dia. Ja entrega fluxo de caixa e DRE basico.
  - **Template pronto:** nao e construcao. E ativacao. "Conectou, apareceu."
  - **Trial com dados demo:** mostrar o 360 funcionando com dados simulados ANTES de pedir pra conectar
- **Paralelo com mercado:** Conta Azul tambem exige que voce migre toda a gestao financeira pra dentro. Omie tambem. A barreira existe, mas o valor percebido supera.
- **Vantagem competitiva escondida:** uma vez que o Nexo esta conectado, o custo de troca e alto. **Lock-in suave** que protege receita recorrente.

**Veredicto:** A dependencia do Nexo e risco real, mas e tambem o MOAT do negocio. A estrategia certa e: vender o 360 como promessa, usar o Nexo como meio, e entregar valor rapido o suficiente pra que o empresario nunca questione a decisao.

---

## SINTESE ESTRATEGICA

### O que esta pesquisa revela para o pitch do 360:

1. **A dor e REAL e URGENTE.** 30% nao sabem se dao lucro. Nao e exagero, e dado de pesquisa.

2. **O vocabulario importa.** Fale "seus numeros", nao "KPIs". Fale "seu controle", nao "dashboard". Fale "saber se esta ganhando ou perdendo", nao "P&L em tempo real".

3. **O inimigo nao e o Power BI.** E o combo "Excel + extrato + achismo + intuicao". E contra isso que o 360 compete.

4. **O valor nao e o dashboard.** O valor e CLAREZA. O empresario quer DORMIR TRANQUILO sabendo que a empresa esta saudavel.

5. **Time-to-value e tudo.** Se demorar mais de 48h pra mostrar o primeiro numero util, voce perdeu o cliente.

6. **O 360 vende o Nexo.** Nao o contrario. Ninguem compra infraestrutura por infraestrutura. Compra resultado.

---

## FONTES

- [Tres em cada dez PMEs no Brasil nao sabem se tem lucro ou prejuizo — CartaCapital](https://www.cartacapital.com.br/do-micro-ao-macro/tres-em-cada-dez-pmes-no-brasil-nao-sabem-se-tem-lucro-ou-prejuizo/)
- [Pesquisa Digitalizacao dos Empreendedores Brasileiros — Conta Azul](https://blog.contaazul.com/digitalizacao-dos-empreendedores-brasileiros/)
- [Falta de visibilidade financeira expoe riscos silenciosos — SA Mais Varejo](https://samaisvarejo.com.br/publicacoes/falta-de-visibilidade-financeira-expoe-riscos-silenciosos-em-empresas-em-crescimento)
- [Falta de leitura financeira transforma decisoes em apostas — Luca Moreira](https://lucamoreira.com.br/economia/falta-de-leitura-financeira-transforma-decisoes-estrategicas-em-apostas-nas-empresas-de-servicos/)
- [Falta de estrutura financeira compromete decisoes estrategicas — Revista Ecotour](https://www.revistaecotour.news/2026/03/falta-de-estrutura-financeira.html)
- [Ma gestao financeira leva 90% das PMEs a crise — O Hoje](https://ohoje.com/2025/09/03/ma-gestao-financeira-leva-90-das-pmes-a-crise-e-ameaca-sobrevivencia/)
- [Mortalidade empresarial — Sebrae RS](https://digital.sebraers.com.br/blog/mercado/mortalidade-empresarial-o-que-fazer-para-prevenir/)
- [Planilhas manuais: problemas e solucoes — Flash](https://flashapp.com.br/blog/despesas-corporativas/planilhas-manuais-problemas)
- [Sebrae: pequenos negocios tem maior taxa de mortalidade — Agencia Brasil](https://agenciabrasil.ebc.com.br/economia/noticia/2021-06/sebrae-pequenos-negocios-tem-maior-taxa-de-mortalidade)
- [7 erros mais comuns na gestao financeira — Sebrae](https://sebrae.com.br/sites/PortalSebrae/artigos/conheca-os-7-erros-mais-comuns-na-gestao-financeira-e-como-evita-los,d36ded1b43222810VgnVCM100000d701210aRCRD)
- [Quanto custa implementar Power BI — BMR](https://www.bmr-e.com.br/quanto-custa-implementar-o-power-bi-na-sua-empresa-veja-o-que-considerar-no-orcamento/)
- [Metabase: BI sem custo de licenca — Proactus](https://proactus.com.br/metabase-como-ter-um-bi-de-alto-nivel-sem-gastar-com-licencas-por-usuario/)
- [Voce nao precisa de um dashboard — Medium/Brites](https://medium.com/@brites.jd/voc%C3%AA-n%C3%A3o-precisa-de-um-dashboard-954d4971b7de)
- [Indicadores financeiros para pequenas empresas — GestaoClick](https://gestaoclick.com.br/blog/indicadores-financeiros-para-pequenas-empresas/)
- [Faturamento nem sempre e sinal de saude financeira — Crescento](https://www.crescento.com.br/en/negocios/saude-financeira-da-empresa/)
- [Taxa de sobrevivencia das empresas — Sebrae](https://sebrae.com.br/sites/PortalSebrae/artigos/a-taxa-de-sobrevivencia-das-empresas-no-brasil,d5147a3a415f5810VgnVCM1000001b00320aRCRD)
