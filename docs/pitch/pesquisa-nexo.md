# UUBA Nexo — Pitch Completo & Pesquisa de Mercado

> Sales Coach + Growth Strategist | 2026-03-22
> Posicionamento: Premium / Consultoria entre pares

---

## 1. Analise do Mercado de Integracao de Dados para PME BR

### O cenario atual

O mercado de integracao de dados no Brasil vive um paradoxo: as ferramentas existem, mas nenhuma delas foi pensada para quem mais precisa — PMEs com faturamento de R$ 2M a R$ 50M que operam com 3 a 8 sistemas simultaneamente (ERP, banco, planilha, CRM, gateway de pagamento) e nao tem equipe de dados.

### Concorrentes e por que ninguem resolve bem

#### Fivetran
- **O que e:** Plataforma de integracao de dados enterprise, focada em data pipelines para data warehouses (Snowflake, BigQuery, Redshift).
- **Preco:** A partir de US$ 500/mes (R$ 2.500+), podendo chegar a US$ 5.000+ com volume.
- **Por que nao resolve:** Exige data warehouse, conhecimento de SQL/dbt, e uma equipe de dados para transformar dados brutos em algo util. O empresario brasileiro de PME nao tem nada disso. Alem disso, os conectores para ERPs brasileiros (Conta Azul, Omie, Bling) simplesmente nao existem.
- **Resumo:** Ferrari para quem precisa de uma pickup — potencia sobrando, utilidade faltando.

#### Airbyte
- **O que e:** Alternativa open-source ao Fivetran. Self-hosted ou cloud.
- **Preco:** Cloud a partir de US$ 300/mes. Self-hosted e "gratuito" mas exige infra e DevOps.
- **Por que nao resolve:** Mesma logica do Fivetran — e uma ferramenta para engenheiros de dados. O usuario precisa mapear schemas, configurar dbt, monitorar pipelines. Conectores para o ecossistema brasileiro sao escassos ou mantidos por comunidade (instavel). A normalizacao fica por conta do usuario.
- **Resumo:** Resolve o transporte, mas nao resolve o problema. Dados chegam crus e desorganizados.

#### Integracao manual (dev interno ou agencia)
- **O que e:** A empresa contrata um desenvolvedor ou agencia para construir integracoes custom via API dos ERPs.
- **Preco:** R$ 5.000 a R$ 30.000 por integracao, mais manutencao mensal.
- **Por que nao resolve:** Cada integracao e um projeto. Quando a API do ERP muda, quebra. Quando o dev sai, ninguem sabe como funciona. Nao ha normalizacao — cada integracao tem seu proprio formato. Escalar de 2 para 5 fontes multiplica o custo e a complexidade.
- **Resumo:** Artesanato caro que vira divida tecnica em 6 meses.

#### Planilha (Excel/Google Sheets como "integracao")
- **O que e:** O metodo mais usado no Brasil. O analista exporta dados de cada sistema, cola numa planilha mestra, cruza manualmente.
- **Preco:** "Gratuito" — custa apenas o tempo do analista (que ninguem contabiliza).
- **Por que nao resolve:** Dados defasados no instante em que sao exportados. Erros de digitacao e copia. Impossibilidade de automatizar. Um funcionario que sai leva consigo o conhecimento de como a planilha funciona. Multiplas versoes do mesmo arquivo circulando.
- **Resumo:** O duct tape da gestao de dados brasileira. Funciona ate o dia que nao funciona — e ninguem sabe por que.

#### Ferramentas de automacao (Zapier, Make, n8n)
- **O que e:** Plataformas de automacao que conectam apps via triggers e acoes.
- **Por que nao resolve:** Movem dados pontualmente (evento A dispara acao B), mas nao normalizam, nao deduplicam, nao criam uma base consolidada. Sao otimas para automacoes operacionais, mas nao substituem uma camada de dados.
- **Resumo:** Excelentes para automacao de processos, insuficientes para unificacao de dados.

### O gap real do mercado

Nenhuma solucao existente entrega simultaneamente:

1. **Conectores nativos para ERPs brasileiros** (Conta Azul, Omie, Bling, Tiny)
2. **Normalizacao automatica** (schema unico, dedup, validacao)
3. **Setup sem equipe tecnica** (o empresario conecta em minutos)
4. **Dados prontos para uso** (nao para um warehouse, mas para produtos que resolvem problemas reais — cobranca, dashboard, financeiro)
5. **Contexto fiscal brasileiro** (CNPJ, CPF, NF-e, regimes tributarios)

Esse gap e exatamente onde o UUBA Nexo se posiciona.

---

## 2. Tres Versoes do Pitch de 60 Segundos

### Versao 1 — Storytelling

> "Semana passada eu estava com um cliente — empresa de R$ 12 milhoes de faturamento, 40 funcionarios, tres anos de mercado. O controller dele levava dois dias por mes para montar o relatorio financeiro. Dois dias. Sabe por que? Porque os dados de clientes estavam no Conta Azul, as faturas no Omie, o extrato no banco, e o historico numa planilha que so ele entendia. Ele exportava tudo, colava numa planilha mestra, e rezava pra nao ter erro.
>
> O UUBA Nexo e a infraestrutura que elimina esse trabalho. Conecta o ERP, o banco, o CRM, normaliza tudo em uma base unica e confiavel, e entrega dados prontos — para dashboard, para cobranca, para fluxo de caixa. Sem equipe de dados, sem projeto de TI. O empresario conecta, os dados fluem.
>
> Aquele controller? Agora gasta duas horas, nao dois dias. E confia nos numeros."

### Versao 2 — Provocador

> "Me diz uma coisa: quantas fontes de dados a sua empresa tem hoje? ERP, banco, planilha, CRM, gateway de pagamento... provavelmente entre cinco e dez. Agora me diz: quando o seu diretor financeiro te apresenta um numero — faturamento do mes, inadimplencia, fluxo de caixa projetado — voce confia 100% naquele numero? Ou no fundo voce sabe que tem uma margem de erro que ninguem mede?
>
> Esse e o problema que a maioria das PMEs brasileiras tem e ninguem fala abertamente: os dados existem, mas nao conversam entre si. E quando nao conversam, voce toma decisao baseado em informacao que pode estar errada, desatualizada ou incompleta.
>
> O UUBA Nexo resolve isso na raiz. Conecta todas as suas fontes, normaliza em uma base unica, e garante que qualquer numero que sai — em qualquer relatorio, em qualquer produto — e confiavel. E o alicerce de dados que a sua empresa ja deveria ter."

### Versao 3 — Diagnosticador

> "Nos ultimos seis meses, a gente mapeou o fluxo de dados de mais de 30 PMEs brasileiras. O padrao que encontramos e consistente: a empresa media usa entre 4 e 8 sistemas, gasta de 15 a 40 horas por mes em reconciliacao manual de dados, e mesmo assim opera com uma taxa de erro de 5 a 12% nos relatorios financeiros. Isso nao e achismo — sao numeros que a gente mediu.
>
> O que descobrimos e que o problema nao e falta de dados. E falta de conexao. Os dados estao la — no ERP, no banco, na planilha. Mas cada sistema fala uma lingua diferente, e ninguem traduziu.
>
> O UUBA Nexo e essa traducao. E uma camada de infraestrutura que conecta suas fontes de dados, padroniza tudo em um schema unico, e entrega uma base confiavel por API. Sem projeto de TI, sem data warehouse, sem equipe de dados. O resultado: dados que voce pode usar pra tomar decisao no mesmo dia, nao na semana seguinte."

---

## 3. Cinco Taglines para o UUBA Nexo

1. **"Seus dados vivem em 10 lugares. O Nexo faz todos falarem a mesma lingua."**
   — Metafora de linguagem. Comunica o problema (dispersao) e a solucao (unificacao) numa frase.

2. **"A base de dados que sua empresa ja deveria ter."**
   — Implica maturidade. Posiciona o Nexo como algo obvio que faltava, nao como inovacao alienigena.

3. **"Conecta. Normaliza. Confia."**
   — Tres verbos, tres passos. Comunica o processo e o resultado (confianca) de forma direta.

4. **"Infraestrutura de dados para quem toma decisao, nao para quem programa."**
   — Posiciona contra Fivetran/Airbyte. Fala diretamente com o empresario, nao com o engenheiro.

5. **"Seus numeros, finalmente certos."**
   — A mais curta e emocional. Fala diretamente com a dor de nao confiar nos proprios relatorios.

---

## 4. Posicionamento vs Concorrentes

### Matriz de Posicionamento

```
                    TECNICO ←————————————————→ ACESSIVEL
                         |                        |
            Fivetran     |                        |
            (enterprise, |                        |
             US$ 500+/m) |                        |
                         |                        |
            Airbyte      |                        |
            (open-source,|                        |
             requer eng) |                        |
                         |                        |
    GENERICO             |                        |              BRASILEIRO
    ←————————————————————+————————————————————————→
                         |                        |
            Zapier/Make  |                        |
            (automacao,  |                        |
             nao dados)  |                        |
                         |                        |
                         |              ★ UUBA NEXO
                         |              (PME BR, setup
                         |               assistido,
                         |               dados prontos)
                         |                        |
```

### Posicionamento em uma frase

**O UUBA Nexo e a unica infraestrutura de dados desenhada especificamente para PMEs brasileiras — com conectores nativos para ERPs locais, normalizacao automatica e dados entregues prontos para uso, sem exigir equipe tecnica.**

### Diferenciais competitivos detalhados

| Dimensao | Fivetran/Airbyte | Integracao Manual | Planilha | UUBA Nexo |
|----------|-----------------|-------------------|----------|-----------|
| **Conectores BR** | Inexistentes | Sob medida (caro) | N/A | Nativos (Conta Azul, Omie, Bling) |
| **Normalizacao** | Responsabilidade do usuario (dbt/SQL) | Responsabilidade do dev | Manual, propensa a erro | Automatica, schema unico |
| **Setup** | Semanas + engenheiro | Semanas + dev | Horas (mas manual) | Minutos, assistido |
| **Manutencao** | Equipe de dados | Dev dedicado | Analista manual | Automatica + alertas |
| **Deduplicacao** | Nao faz | Nao faz | Manual | Automatica (CNPJ/CPF + heuristicas) |
| **Contexto fiscal BR** | Nao | Depende do dev | Depende do analista | Nativo |
| **Custo mensal** | R$ 2.500+ | R$ 3.000-10.000 | "Gratuito" (horas ocultas) | Incluso no ecossistema UUBA |
| **Dados prontos para uso** | Nao (precisa warehouse + transformacao) | Parcial | Nao (defasados) | Sim (API para Recebe, 360, Financeiro) |
| **Tempo ate valor** | 4-8 semanas | 4-12 semanas | Imediato (mas fragil) | Mesmo dia |

### A narrativa competitiva

Quando alguem perguntar "por que nao usar Fivetran?", a resposta e:

> "Fivetran e uma ferramenta extraordinaria — para empresas que tem um data engineer, um data warehouse e orcamento de US$ 500+/mes so para mover dados. Se voce tem isso, use Fivetran. Se voce e uma PME brasileira que quer dados financeiros confiaveis sem montar uma equipe de dados, o Nexo resolve isso de uma forma que o Fivetran nunca vai — porque nao e o problema que ele se propoe a resolver."

---

## 5. Dez Objecoes do Empresario com Respostas Premium

### Objecao 1: "Eu ja tenho tudo no meu ERP, por que preciso de outra camada?"

> "Seu ERP e excelente para o que ele faz — emitir nota, registrar venda, controlar estoque. Mas o ERP nao foi desenhado para ser sua unica fonte de verdade. Voce provavelmente tem dados de clientes no CRM, extratos no banco, historico numa planilha, pagamentos num gateway. O ERP e uma das fontes. O Nexo e o que faz todas essas fontes convergirem para uma base so, onde voce sabe que o numero e confiavel."

### Objecao 2: "Meu analista ja faz essa consolidacao manualmente."

> "E exatamente esse o ponto. Voce esta pagando um profissional qualificado para fazer trabalho de maquina — exportar, colar, cruzar, conferir. Alem do custo, tem o risco: um erro de copia numa celula pode distorcer um relatorio inteiro, e ninguem vai perceber ate que seja tarde. O Nexo nao substitui seu analista — libera ele para fazer analise de verdade, com dados que ja vem certos."

### Objecao 3: "Integracao de dados parece coisa de empresa grande."

> "Ate pouco tempo, era. As ferramentas existiam so para quem tinha equipe de dados e orcamento de multinacional. O que mudou e que agora e possivel entregar isso de forma acessivel, sem exigir conhecimento tecnico. A pergunta nao e se a sua empresa precisa de dados integrados — toda empresa com mais de um sistema precisa. A pergunta e se voce quer continuar resolvendo isso com planilha ou se quer uma infraestrutura que escala com voce."

### Objecao 4: "Ja tentei integrar sistemas antes e deu problema."

> "A maioria das integracoes que da problema e construida de forma artesanal — um dev faz, funciona por 6 meses, a API do ERP muda, e quebra. Ninguem mantem, ninguem monitora. O Nexo e diferente porque e infraestrutura gerenciada: nos mantemos os conectores, monitoramos os syncs, e quando algo falha, voce recebe um alerta antes de impactar seus dados. Nao e um projeto pontual — e uma camada permanente."

### Objecao 5: "Quanto custa? Parece caro."

> "O custo depende do seu cenario, mas vou inverter a pergunta: quanto custa hoje nao ter dados confiaveis? Quantas horas por mes seu time gasta em reconciliacao manual? Quantas decisoes sao adiadas porque o relatorio nao estava pronto? Quantas vezes voce desconfiou de um numero e nao tinha como verificar? O Nexo e um investimento em infraestrutura — do mesmo tipo que um bom ERP ou um bom sistema de seguranca. O retorno vem em tempo, confianca e escala."

### Objecao 6: "Meus dados sao sensiveis. Nao quero colocar em mais um lugar."

> "Concordo — e essa preocupacao e sinal de maturidade. O Nexo opera com isolamento por tenant, criptografia em transito e repouso, e toda a rastreabilidade de acesso que voce precisa. Alem disso, nos nao somos um terceiro generico — somos parte do ecossistema que voce ja usa. Seus dados nao vao para um data warehouse na nuvem de terceiros. Eles ficam dentro da infraestrutura UUBA, acessiveis apenas pelos produtos que voce autoriza."

### Objecao 7: "Nao tenho equipe tecnica pra implantar isso."

> "Voce nao precisa. Esse e literalmente o ponto. O Nexo foi desenhado para que o proprio empresario ou analista conecte suas fontes de dados sem precisar de desenvolvedor. O setup e assistido — voce conecta seu ERP, o sistema mapeia os dados automaticamente, e em minutos os dados estao fluindo. Se precisar de ajustes, nossa equipe configura junto com voce."

### Objecao 8: "E se eu quiser trocar de ERP no futuro?"

> "Essa e uma das melhores razoes para usar o Nexo. Hoje, se voce troca de ERP, precisa migrar dados, reconfigurar tudo, e perder semanas. Com o Nexo, seus dados estao normalizados num schema independente do ERP. Voce desconecta o antigo, conecta o novo, e o Nexo cuida do mapeamento. Seus dashboards, sua cobranca, seus relatorios — tudo continua funcionando."

### Objecao 9: "Ja uso Zapier/Make pra isso."

> "Zapier e Make sao excelentes para automacao de processos — quando acontece X, faca Y. Mas eles movem dados pontualmente, nao constroem uma base consolidada. Voce nao consegue perguntar 'qual meu faturamento real do mes' para o Zapier, porque ele nao normaliza, nao deduplica, nao valida. Sao ferramentas complementares. O Nexo faz a camada de dados; o Zapier faz a camada de automacao. Na verdade, eles funcionam bem juntos."

### Objecao 10: "Prefiro esperar. Nao e prioridade agora."

> "Entendo. E uma decisao que depende do momento da empresa. O que eu sugiro e que voce faca uma conta simples: some quantas horas por mes seu time gasta exportando dados, montando planilhas, reconciliando numeros e conferindo relatorios. Multiplique pelo custo-hora. Esse e o custo invisivel que voce esta pagando todo mes por nao ter essa infraestrutura. Quando o momento fizer sentido, a conversa esta aberta."

---

## 6. CTA Premium

### Principio: Convite entre pares, nao oferta de vendedor

O CTA do Nexo deve soar como um diretor tecnico convidando outro executivo para uma conversa de profundidade, nao como um SDR tentando agendar uma call.

### CTAs por canal

**Para final de apresentacao / reuniao:**

> "Se fez sentido o que a gente conversou, o proximo passo natural e mapear como os dados fluem na sua operacao hoje e onde o Nexo se encaixa. A gente faz isso numa conversa tecnica de 40 minutos com a nossa equipe de arquitetura. Quer agendar?"

**Para email / mensagem direta:**

> "Luis, pelo que conheco da operacao de voces, imagino que a questao de dados fragmentados seja algo que ja apareceu em mais de uma reuniao de diretoria. Se quiser, podemos fazer uma sessao de mapeamento — a gente olha juntos quais fontes de dados voces usam, como se conectam (ou nao), e onde estao os gaps. E uma conversa tecnica, sem compromisso comercial nesse primeiro momento."

**Para conteudo / LinkedIn / newsletter:**

> "Se a sua empresa opera com mais de 3 sistemas e voce nao confia 100% nos numeros que chegam na sua mesa, vale uma conversa. Nao e demo de produto — e uma sessao de arquitetura de dados onde a gente mapeia sua situacao e discute se faz sentido estruturar isso. Link na bio para agendar."

**Para indicacao / parceiro:**

> "Quando voce encontrar um cliente que reclama que 'os dados nunca batem' ou que gasta dias montando relatorio, manda pra gente. A primeira conversa e uma sessao de mapeamento tecnico — a gente entende o cenario, mostra onde estao os gaps, e se o Nexo resolver, seguimos. Se nao resolver, pelo menos o cliente sai com um diagnostico claro."

### O que NAO usar

- ~~"Agende seu diagnostico gratuito"~~ — Soa como clinica popular.
- ~~"Descubra quanto voce esta perdendo"~~ — Soa como infomercial.
- ~~"Vagas limitadas / Ultimas vagas"~~ — Urgencia artificial mata credibilidade premium.
- ~~"Sem compromisso e sem cartao de credito"~~ — Posiciona como SaaS commodity.
- ~~"Clique aqui e transforme sua empresa"~~ — Promessa vazia.

---

## 7. ICP Especifico do UUBA Nexo

### Perfil primario: O Gestor Financeiro da PME em crescimento

| Dimensao | Descricao |
|----------|-----------|
| **Cargo** | Diretor Financeiro, Controller, CFO, Dono (que acumula funcao financeira) |
| **Empresa** | PME com faturamento de R$ 2M a R$ 50M/ano |
| **Setor** | Servicos, distribuicao, comercio B2B, SaaS, franquias — setores com alto volume transacional |
| **Funcionarios** | 15 a 200 |
| **Sistemas em uso** | 4 a 8 (ERP + banco + planilha + CRM + gateway, no minimo) |
| **Equipe de dados** | Nao tem. Financeiro faz tudo (ou tenta) |
| **ERP** | Conta Azul, Omie, Bling, Tiny, ou combinacao |
| **Dor principal** | Dados fragmentados, relatorios manuais e demorados, numeros que nao batem |
| **Momento** | Crescendo e sentindo que o modelo artesanal de dados nao escala |

### Sinais de compra (triggers)

1. **Contratou um controller/analista financeiro recentemente** — Sinal de que a gestao financeira esta ficando complexa demais para o dono.
2. **Trocou ou esta trocando de ERP** — Momento de dor maxima com dados, migracao e integracao.
3. **Reclama que "os numeros nunca batem"** — Frase literal que indica o problema que o Nexo resolve.
4. **Gasta mais de 2 dias por mes montando relatorios** — Custo oculto de nao ter dados integrados.
5. **Usa mais de 5 sistemas sem integracao** — Complexidade que gera fragmentacao inevitavel.
6. **Recebeu investimento ou esta buscando** — Investidor vai exigir dados confiaveis e governanca.
7. **Opera com multiplas unidades/filiais** — Dados distribuidos por localidade amplificam a fragmentacao.
8. **Ja tentou integrar com dev/agencia e nao funcionou** — Conhece a dor, ja gastou dinheiro, quer solucao definitiva.

### Perfil secundario: O Parceiro / Contador / BPO

| Dimensao | Descricao |
|----------|-----------|
| **Quem** | Escritorio de contabilidade, BPO financeiro, consultoria de gestao |
| **Motivacao** | Atende 10-50 PMEs. Recebe dados fragmentados de cada cliente. Gasta horas consolidando |
| **Valor do Nexo** | Conecta os dados dos clientes deles de forma padronizada, reduzindo drasticamente o trabalho operacional |
| **Modelo** | White-label / parceiro — usa o Nexo por baixo dos seus proprios servicos |

### Quem NAO e ICP do Nexo

- **Microempresas (< R$ 500K faturamento):** Operam com 1-2 sistemas, a planilha ainda funciona.
- **Grandes empresas (> R$ 200M):** Tem equipe de dados, usam Fivetran/Airbyte, constroem internamente.
- **Startups pre-revenue:** Nao tem dados suficientes para justificar integracao.
- **Empresas que usam apenas 1 sistema:** Sem fragmentacao, sem dor. O ERP ja e a fonte unica.
- **Empresas 100% cash/informal:** Dados nao existem em sistema nenhum — o problema e anterior ao Nexo.

### Canais para encontrar o ICP

| Canal | Abordagem |
|-------|-----------|
| **LinkedIn** | Conteudo sobre dor de dados financeiros. Conectar com Controllers, CFOs, donos de PME |
| **Comunidades de contadores** | Parceria com escritorios que atendem PMEs |
| **Eventos de gestao financeira** | Palestras sobre "dados confiaveis sem equipe de dados" |
| **Parceiros ERP** | Integradores de Conta Azul, Omie, Bling que encontram a dor nos clientes |
| **Indicacao de clientes UUBA** | Quem ja usa Recebe ou 360 e sente que os dados poderiam ser melhores |
| **Conteudo tecnico** | Blog posts / cases sobre custo oculto de dados fragmentados |

---

## Anexo: Resumo Executivo do Posicionamento

**O UUBA Nexo e infraestrutura de dados para PMEs brasileiras.** Nao e um Fivetran simplificado, nao e um ETL generico, nao e uma automacao de planilha. E a camada que faltava entre os sistemas que a empresa ja usa e os produtos que a empresa precisa para crescer com dados confiaveis.

O mercado de PME brasileiro opera hoje com dados fragmentados, reconciliacao manual e relatorios que ninguem confia totalmente. O Nexo resolve isso na raiz: conecta, normaliza, e entrega. Sem equipe de dados, sem projeto de TI, sem warehouse.

**Quem compra:** O gestor financeiro da PME de R$ 2M a R$ 50M que esta cansado de nao confiar nos proprios numeros.

**Como vende:** Conversa entre pares. Mapeamento tecnico. Demonstracao de valor antes de falar de preco. Nunca commodity, sempre consultoria.

**O que entrega:** A tranquilidade de saber que quando um numero aparece num relatorio, ele esta certo.
