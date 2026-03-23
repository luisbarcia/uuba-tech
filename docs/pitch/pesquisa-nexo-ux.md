# Pesquisa UX + Devil's Advocate: UUBA Nexo

> **Produto:** UUBA Nexo -- conecta ERPs, CRMs, bancos, normaliza dados para PMEs brasileiras
> **Data:** 2026-03-22
> **Metodologia:** Desk research (Reclame Aqui, HubSpot State of Data 2025, SEBRAE, portais especializados, Reclame Aqui)

---

## PARTE 1 -- UX RESEARCH

---

### 1. Cenario: como PMEs brasileiras lidam com dados financeiros em multiplos sistemas

**Dados quantitativos coletados:**

| Dado | Fonte |
|------|-------|
| 27,6% das organizacoes brasileiras operam com sistemas completamente desconectados | HubSpot, Panorama de Dados 2025 |
| Empresas brasileiras operam com ate 5 sistemas isolados simultaneamente | HubSpot / Portal Information Management (fev/2026) |
| 87% das empresas tem sistemas integrados, mas 63,5% sofrem com dados conflitantes | Inforchannel (out/2025) |
| 78% das empresas transferem leads manualmente entre sistemas | HubSpot State of Data 2025 |
| 70-80% do tempo operacional e consumido por tarefas repetitivas e manuais | HubSpot State of Data 2025 |
| 68% dos times gastam 5h/semana apenas limpando dados | HubSpot State of Data 2025 |
| PMEs perdem ~60 horas/mes em tarefas manuais | Blog TagguiRH / pesquisa mercado |
| 45% das empresas ja perderam oportunidades por dados desconectados | HubSpot State of Data 2025 |
| 72% nao conseguem consolidar dados para medir ROI com precisao | HubSpot State of Data 2025 |
| Profissionais de dados gastam 27-30% do tempo limpando/corrigindo informacoes | Portal Deducao / ABES |
| Empresas com maturidade em dados sao 23x mais propensas a conquistar clientes | McKinsey |
| 45% das PMEs brasileiras desconhecem beneficios de ERP cloud | Ken Research |
| Conciliacao automatizada pode poupar ate 20h/mes | Conta Azul (pagina de produto) |
| Digitalizacao de documentos reduz tempo de processamento em 50-70% | CNDL / Varejo S.A. |
| IA elimina 87% da necessidade de digitacao manual | CNDL / Varejo S.A. |

**Sintese do cenario:**
O empresario PME brasileiro tipicamente opera com 3-5 ferramentas desconectadas: um ERP (Conta Azul, Omie, Bling), uma planilha do Excel/Google Sheets como "ponte", o internet banking, o sistema do contador, e eventualmente um CRM ou sistema de vendas. Cada sistema tem sua propria verdade. O financeiro fecha de um jeito no ERP, de outro no banco, e de um terceiro na planilha. O resultado: horas de conferencia manual todo mes, e decisoes tomadas com dados que ninguem confia totalmente.

---

### 2. Problemas de conciliacao entre ERP e banco

**Reclamacoes reais documentadas no Reclame Aqui:**

**Conta Azul:**
- O sistema duplicou TODOS os lancamentos de contas a pagar e receber na aba de conciliacao
- Ao eliminar lancamentos duplicados, o sistema eliminou os lancamentos CORRETAMENTE CONCILIADOS em vez dos ignorados, invertendo saldos
- Importacao de notas fiscais com valores diferentes do original (frete nao importado)
- O saldo nao bate entre banco e Conta Azul no fim do mes
- Titulo da reclamacao: "Erros em frequencia assustadora, retrabalhos e decepcao!"
- "Mudei na mao todos os registros, centros de custos e categorias, perdendo a tarde inteira com retrabalho"

**Omie:**
- "Conciliacao bancaria esta toda desorganizada" -- integracao com banco nao bate com importacao no sistema
- Conciliacao completada que "sumiu" depois de importar outro extrato
- Valores aparecem como pendentes no extrato mas registrados como pagos e conciliados no financeiro da Omie
- Relatorios que inflam dados de receita, duplicam valores de notas fiscais
- Calculo de preco errado na integracao -- tabela da Omie calcula um valor, integracao reflete outro
- "Perda de informacoes financeiras -- Conciliacao -- Importacao Via OFX"
- Cadastrar lancamentos antecipados ou paralelos gera duplicidade de registros e lancamentos contabeis indevidos

---

### 3. Verbatins do empresario (reclamacoes reais + depoimentos coletados)

> **V1:** "A plataforma duplicou TODOS os lancamentos de contas a pagar e receber na aba de conciliacao. [...] O sistema elimina os lancamentos duplicados, mas ao inves de eliminar os ignorados, elimina os que foram CORRETAMENTE CONCILIADOS."
> -- Cliente Conta Azul, Reclame Aqui

> **V2:** "Mudei na mao todos os registros, centros de custos e categorias, perdendo a tarde inteira com retrabalho."
> -- Cliente Conta Azul, Reclame Aqui

> **V3:** "Conciliacao bancaria esta toda desorganizada. A integracao com o banco nao bate com a importacao efetuada no sistema. E um caos completo."
> -- Cliente Omie, Reclame Aqui

> **V4:** "O ERP nao entrega informacoes fidedignas em seus relatorios. Infla dados de receita, duplica valores de notas fiscais e passa dados errados de devolucao e bonificacao."
> -- Cliente Omie, Reclame Aqui (titulo: "O pior ERP que ja usei")

> **V5:** "Erros em frequencia assustadora, retrabalhos e decepcao!"
> -- Titulo de reclamacao real, Conta Azul, Reclame Aqui

> **V6:** "Foi um dos melhores investimentos que fizemos. Conseguimos cancelar muitas outras ferramentas e hoje eu levo duas horas para parametrizar o relatorio que antes levava de 10 a 15 dias."
> -- Depoimento de cliente que integrou sistemas (fonte: WebmaisSistemas)

> **V7:** "Diminuimos nosso tempo com trabalhos manuais em 70% e meu time consegue focar em tarefas mais estrategicas."
> -- Depoimento de cliente que automatizou conciliacao (fonte: Kamino)

> **V8:** "O tempo gasto procurando informacoes em papeis ou consertando erros de planilhas e um tempo perdido. O dono de uma pequena empresa precisa focar em estrategias para vender mais, e nao em tarefas burocraticas repetitivas."
> -- Blog Contmatic (artigo sobre ERP para pequenas empresas, 2026)

---

### 4. Tempo perdido com digitacao manual e conferencia

| Metrica | Valor | Fonte |
|---------|-------|-------|
| Horas/semana gastas limpando dados | 5h (68% dos times) | HubSpot State of Data 2025 |
| Horas/mes em tarefas manuais (PME) | ~60h | Pesquisa mercado / TagguiRH |
| Economia com conciliacao automatizada | ate 20h/mes | Conta Azul (produto) |
| Reducao de trabalho manual com automacao | 70% | Depoimento cliente Kamino |
| Tempo de relatorio: manual vs integrado | 10-15 dias vs 2 horas | Depoimento cliente WebmaisSistemas |
| Tempo consumido por tarefas repetitivas | 70-80% do operacional | HubSpot State of Data 2025 |
| Tempo de profissionais de dados em limpeza | 27-30% do tempo | ABES / Portal Deducao |

**Traducao pratica:** Um empresario PME com 1-2 pessoas no financeiro perde entre 1 e 3 dias uteis por mes apenas conferindo, corrigindo e re-digitando informacoes que ja existem em outro sistema. Isso equivale a 5-15% do mes de trabalho jogado fora em retrabalho puro.

---

### 5. Jobs to Be Done (JTBD)

#### JTBD 1: "Quando fecho o mes, quero bater o financeiro do ERP com o extrato do banco sem ficar 2 dias conferindo linha por linha"
- **Situacao:** Fechamento mensal, pressao do contador
- **Motivacao:** Evitar erro fiscal, ter confianca nos numeros
- **Resultado desejado:** Conciliacao automatica, alertas de divergencia
- **Emocao:** Ansiedade ("sera que ta certo?"), frustacao ("de novo isso")

#### JTBD 2: "Quando preciso tomar uma decisao sobre fluxo de caixa, quero ver TODOS os numeros num lugar so, sem abrir 4 sistemas"
- **Situacao:** Decisao de compra, investimento ou contratacao
- **Motivacao:** Seguranca na decisao, velocidade
- **Resultado desejado:** Dashboard unico com dados consolidados e confiaveis
- **Emocao:** Inseguranca ("sera que posso confiar nesses numeros?")

#### JTBD 3: "Quando contrato um sistema novo, quero que ele converse com os que ja tenho, sem eu precisar digitar tudo de novo"
- **Situacao:** Adocao de nova ferramenta (CRM, gateway de pagamento, marketplace)
- **Motivacao:** Nao duplicar trabalho, nao criar mais uma ilha de dados
- **Resultado desejado:** Plug-and-play, dados fluem automaticamente
- **Emocao:** Cansaco ("mais um sistema pra alimentar na mao")

#### JTBD 4: "Quando meu contador pede os dados, quero mandar tudo certinho de primeira, sem vai-e-volta de email"
- **Situacao:** Obrigacao fiscal mensal, envio ao escritorio contabil
- **Motivacao:** Evitar multas, retrabalho, constrangimento
- **Resultado desejado:** Exportacao padronizada, dados consistentes entre sistemas
- **Emocao:** Medo ("se der merda no imposto, sobra pra mim")

#### JTBD 5: "Quando abro meu relatorio de vendas e comparo com o financeiro, quero que os numeros batam -- sem ter que ficar cruzando planilha"
- **Situacao:** Reuniao de resultados, analise semanal/mensal
- **Motivacao:** Entender a real saude do negocio
- **Resultado desejado:** Fonte unica de verdade, dados normalizados
- **Emocao:** Desconfianca ("esse numero esta certo?"), raiva ("ja perdi a conta de quantas vezes isso nao fechou")

---

### 6. Vocabulario do empresario PME

#### Palavras que ele USA (linguagem natural):

| Palavra/Expressao | Contexto |
|-------------------|----------|
| "Nao bate" | Dados de dois sistemas divergem |
| "Nao fecha" | Conciliacao com divergencia |
| "Ta errado" | Valor importado diferente do original |
| "Retrabalho" | Corrigir algo que ja foi feito |
| "Na mao" / "No braco" | Processo manual |
| "Planilha" | Ferramenta-ponte universal |
| "Conferir" / "Bater" | Processo de conciliacao manual |
| "Sistema" | Qualquer software (ERP, CRM, banco) |
| "Bagunca" / "Caos" | Estado dos dados desconectados |
| "Perder tempo" | Custo percebido do retrabalho |
| "Nao conversa" | Sistemas que nao se integram |
| "Duplicado" | Lancamento que aparece 2x |
| "Sumiu" | Dado perdido em migracao/importacao |
| "Puxar" / "Importar" | Trazer dados de um sistema para outro |
| "Fechar o mes" | Rotina de conciliacao mensal |

#### Palavras que ele EVITA (jargao tecnico):

| Jargao | O que ele diria no lugar |
|--------|--------------------------|
| "Integracao de dados" | "Fazer os sistemas conversarem" |
| "Normalizacao" | "Deixar tudo no mesmo padrao" |
| "API" | "Conexao" / "plugar" |
| "Middleware" | Nao usa -- nao sabe que existe |
| "iPaaS" | Nao usa -- nao sabe que existe |
| "Data pipeline" | "Fluxo de informacao" (se muito) |
| "ETL" | Nao usa |
| "Conciliacao automatizada" | "Bater sozinho" / "fechar automatico" |
| "Fonte unica de verdade" | "Ver tudo num lugar so" |
| "Dados desconectados" | "Cada sistema tem um numero diferente" |
| "Orquestracao" | "Tudo funcionando junto" |
| "Schema" / "Modelo de dados" | "O jeito que as coisas estao organizadas" |

---

## PARTE 2 -- DEVIL'S ADVOCATE

---

### Critica 1: "Integracao de dados" e abstrato demais pra PME

**O problema:**
Nenhum empresario PME acorda de manha e pensa "preciso de integracao de dados". Ele pensa "preciso parar de perder 2 dias todo mes conferindo planilha". O conceito de "integrar dados" e invisivel -- e infraestrutura, e encanamento. Ninguem paga por encanamento com entusiasmo. Pagam para resolver a goteira.

**Risco real:** O Nexo pode cair na armadilha de se posicionar como "plataforma de integracao" -- linguagem que fala para CTOs de empresas de 500 funcionarios, nao para o dono de uma loja com 15 funcionarios que usa Conta Azul e Excel.

**Recomendacao:** Comunicar pelo EFEITO, nunca pela CAUSA:
- NAO: "Integre seus dados em uma plataforma unificada"
- SIM: "Pare de perder 2 dias por mes conferindo planilha"
- NAO: "Normalizacao de dados multi-sistema"
- SIM: "Seus numeros vao bater -- automaticamente"
- NAO: "Conecte seu ERP ao banco"
- SIM: "Abra UM lugar e veja se tem dinheiro pra pagar as contas"

---

### Critica 2: O empresario sequer sabe que TEM esse problema?

**Hipotese pessimista:** Sim, ele sabe. Mas ele **naturalizou**. E como dor nas costas cronica -- incomoda, mas voce aprende a conviver. Ele nao busca ativamente solucao porque:

1. **Ja tentou e se frustrou.** Os dados do Reclame Aqui mostram que mesmo quem PAGA por ERP com conciliacao automatica (Conta Azul, Omie) ainda sofre com dados que nao batem. Ele conclui: "e assim mesmo".

2. **Nao sabe quantificar a perda.** Ele sabe que "perde tempo", mas nao calcula que sao 60h/mes ou 5-15% da capacidade produtiva. O custo e invisivel porque esta diluido no dia a dia.

3. **Nao sabe que existe alternativa.** 45% das PMEs desconhecem beneficios de ERP cloud (Ken Research). Se nao sabem de ERP cloud, muito menos sabem que existe middleware/iPaaS.

4. **O "jeitinho" funciona (mais ou menos).** A planilha do Excel, apesar de fragil, e familiar. Trocar por algo desconhecido tem custo de troca alto (curva de aprendizado, migracao, medo de perder dados).

**Implicacao para o Nexo:** O go-to-market NAO pode ser demand capture (buscar quem ja procura solucao). Tem que ser demand creation -- educar, mostrar a dor, quantificar a perda. Isso e caro e demorado. Exige content marketing pesado, calculadoras de ROI, cases de "antes/depois".

---

### Critica 3: Se ele usa Conta Azul e planilha, por que pagaria por MAIS UM sistema?

**Este e o maior risco do Nexo.** O empresario PME ja sofre de "fadiga de ferramenta". Ele ja:
- Paga Conta Azul/Omie (R$ 100-300/mes)
- Usa planilha (gratis, mas custosa em tempo)
- Tem sistema do banco (gratis)
- Talvez pague CRM (R$ 50-200/mes)

Propor MAIS UM sistema e contra-intuitivo. A reacao natural e: **"Mais um?! Ja tenho coisa demais!"**

**Objecoes previsiveis:**
- "Se o Conta Azul ja promete conciliacao automatica, por que eu preciso do Nexo?"
- "Vou pagar um sistema pra conectar meus sistemas? Isso deveria ser funcao do ERP!"
- "Se eu pudesse pagar so um sistema que fizesse tudo, eu preferia"
- "Nao tenho equipe de TI pra configurar mais uma ferramenta"

**Contra-argumentos possiveis:**
1. Posicionar o Nexo NAO como "mais um sistema", mas como o "sistema que elimina os outros" ou "a cola invisivel entre os sistemas que voce ja tem"
2. Mostrar economia liquida: "Voce gasta R$ X em retrabalho/mes. O Nexo custa R$ Y. Economia: R$ X-Y"
3. Zero configuracao como promessa central: se exigir setup complexo, o PME desiste na hora

**Mas o contra-argumento honesto e:** ERPs como Conta Azul e Omie vao continuar melhorando suas integracoes nativas. Cada atualizacao deles reduz o TAM do Nexo. O Nexo precisa entregar valor que o ERP NUNCA vai entregar: conexao ENTRE ecossistemas (ERP + banco + CRM + marketplace + contador), nao dentro de um ecossistema so.

---

### Critica 4: O Nexo sozinho entrega valor ou precisa dos outros produtos UUBA?

**Risco de dependencia:**
Se o Nexo so faz sentido como "camada de dados" para o UUBA Flow (automacao), UUBA Pulse (BI), ou UUBA Core (gestao), entao ele NAO e um produto -- e uma feature. E features nao se vendem sozinhas.

**Teste acido:** Um empresario que NAO usa nenhum outro produto UUBA compraria o Nexo? Se a resposta for "nao", entao:
- O Nexo nao tem proposta de valor standalone
- Ele precisa ser vendido como parte de um bundle/suite
- O preco percebido fica mais alto (precisa comprar o pacote)
- O concorrente direto passa a ser "suite completa" (Omie, Conta Azul Pro, Bling)

**Se a resposta for "sim", o Nexo precisa entregar valor tangivel isolado:**
- Conciliacao automatica multi-banco + multi-ERP
- Dashboard unico de caixa consolidado
- Alertas de divergencia em tempo real
- Exportacao padronizada para contador

**Recomendacao:** Definir claramente o valor standalone do Nexo ANTES de posiciona-lo. Se ele nao se sustenta sozinho, nao chame de "produto" -- chame de "recurso" dentro da plataforma UUBA.

---

### Critica 5 (bonus): O timing e certo?

**A favor:**
- Estudo HubSpot (fev/2026) mostra que o problema e reconhecido e crescente
- 94% das empresas brasileiras explorando IA -- mas sem dados limpos, IA nao funciona
- Reforma tributaria 2026 vai forcar empresas a ter dados fiscais mais organizados
- Mercado de iPaaS cresce 30,7% ao ano (Gartner)

**Contra:**
- PMEs estao em modo de sobrevivencia economica -- cortar custos, nao adicionar
- ERPs incumbentes estao adicionando integracoes nativas agressivamente
- O empresario PME prioriza vendas sobre infraestrutura de dados
- Low-code/no-code (n8n, Make, Zapier) ja resolve parte do problema para quem e minimamente tecnico

---

## SINTESE FINAL

### O que ficou claro:
1. **A dor existe e e real.** Dados do Reclame Aqui, HubSpot e depoimentos confirmam: PMEs perdem tempo e dinheiro com dados desconectados
2. **A dor e naturalizada.** O empresario convive com ela, nao busca solucao ativamente
3. **A linguagem importa mais que a tecnologia.** "Integracao de dados" nao vende. "Seus numeros vao bater" vende
4. **O maior risco e ser "mais um sistema".** O posicionamento precisa ser de "eliminador de retrabalho", nao de "plataforma de integracao"
5. **O Nexo precisa provar valor standalone.** Se depende dos outros produtos UUBA, e feature, nao produto

### Proximos passos recomendados:
1. Entrevistar 5-10 empresarios PME (cliente Conta Azul/Omie) para validar verbatins e JTBD
2. Construir calculadora de ROI ("quanto voce perde por mes com dados que nao batem?")
3. Definir se o Nexo e produto ou feature -- isso muda tudo no go-to-market
4. Testar 3 posicionamentos diferentes em landing page (A/B test):
   - "Seus numeros vao bater -- automaticamente"
   - "Pare de perder 2 dias por mes conferindo planilha"
   - "Todos os seus sistemas, uma unica verdade"

---

## Fontes

- [HubSpot - Panorama de Dados 2025](https://br.hubspot.com/ofertas/state-of-data-2025)
- [Portal Information Management - Empresas brasileiras operam com ate 5 sistemas desconectados](https://docmanagement.com.br/02/16/2026/empresas-brasileiras-operam-com-ate-cinco-sistemas-desconectados-e-perdem-eficiencia-aponta-estudo/)
- [ABES - Como dados desconectados fazem empresas perderem milhoes](https://abes.org.br/en/como-dados-desconectados-fazem-empresas-perderem-milhoes-sem-perceber-especialista-explica-impacto-silencioso/)
- [Portal Deducao - Impacto silencioso dos dados desconectados](https://deducao.com.br/como-dados-desconectados-fazem-empresas-perderem-milhoes-sem-perceber-especialista-explica-impacto-silencioso/)
- [Inforchannel - 87% das empresas tem sistemas integrados mas 63,5% sofrem com dados conflitantes](https://inforchannel.com.br/2025/10/28/pesquisa-conclui-que-87-das-empresas-tem-sistemas-integrados-mas-635-sofrem-com-dados-conflitantes/)
- [Conta Azul - Reclame Aqui (Lancamentos duplicados)](https://www.reclameaqui.com.br/contaazul/conta-azul-e-seus-lancamentos-duplicados_Bfa_tGjezK1bLE03/)
- [Conta Azul - Reclame Aqui (Erros em frequencia assustadora)](https://www.reclameaqui.com.br/contaazul/erros-em-frequencia-assustadora-retrabalhos-e-decepcao_hwdT25j3vhjHw_5b/)
- [Conta Azul - Reclame Aqui (Problemas integracao bancaria)](https://www.reclameaqui.com.br/contaazul/problemas-na-integracao-bancaria_vEjRongZkjEnJVUM/)
- [Omie - Reclame Aqui (Conciliacao desorganizada)](https://www.reclameaqui.com.br/omiexperience/conciliacao-bancaria-esta-toda-desorganizada_t7cJyguvsW3Ss8zn/)
- [Omie - Reclame Aqui (O pior ERP que ja usei)](https://www.reclameaqui.com.br/omiexperience/o-pior-erp-que-ja-usei_vi2rJyB7LLeDpwe7/)
- [Omie - Reclame Aqui (Falhas graves)](https://www.reclameaqui.com.br/omiexperience/sistema-omie-com-falhas-graves-atualizacao-manual-de-precos-e-problemas-co_IsqN6GlVYhbWUB4F/)
- [Omie - Reclame Aqui (Perda de informacoes financeiras)](https://www.reclameaqui.com.br/omiexperience/perda-de-informacoes-financeiras-conciliacao-importacao-via-ofx_s2wztEoTrhjoMIxs/)
- [Conquest Sistemas - ERPs engessados prejudicam gestao](https://conquest.com.br/erps-engessados-prejudicam-gestao-como-evitar/)
- [Flash - Planilhas manuais: problemas e solucoes](https://flashapp.com.br/blog/planilhas-manuais-problemas)
- [Contmatic - Sistema ERP para pequenas empresas 2026](https://blog.contmatic.com.br/sistema-erp-para-pequenas-empresas-como-escolher-em-2026/)
- [CNDL/Varejo S.A. - IA elimina digitacao manual](https://cndl.org.br/varejosa/tendencia-2026-ia-elimina-digitacao-manual-e-redefine-a-eficiencia-no-comex/)
- [Senior - Retrabalho nas empresas](https://www.senior.com.br/blog/retrabalho-nas-empresas)
- [Ken Research - Brazil Cloud ERP for SMEs Market](https://www.kenresearch.com/cloud-erp-for-smes-in-brazil)
- [The Best Solution - Cost of Disconnected Systems](https://www.thebestsolution.com/the-cost-of-disconnected-systems-poor-data-integration-in-erp/)
- [Panorama Consulting - Consequences of Poor System Integration](https://panorama-consulting.com/the-consequences-of-system-integration-issues/)
- [NetSuite - ERP Statistics](https://www.netsuite.com/portal/resource/articles/erp/erp-statistics.shtml)
- [IT Convergence - 5 Reasons Brazil ERP is Most Complex](https://www.itconvergence.com/blog/5-reasons-brazil-is-the-worlds-most-complex-erp-and-fiscal-environment/)
