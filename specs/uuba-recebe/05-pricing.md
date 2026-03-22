# UUBA Recebe — Modelo de Precificacao

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
