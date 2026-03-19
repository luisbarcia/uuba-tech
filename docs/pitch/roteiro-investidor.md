# Roteiro de Pitch — UUBA Tech (5 min)

> Para apresentacao a potenciais investidores. Versao: 2026-03-19

---

## [0:00–0:30] Abertura — O Problema

> *"Toda empresa media no Brasil tem o mesmo problema: o financeiro nao funciona direito. DRE defasado, cobranca no braco, planilha de Excel como sistema. E quando precisa cobrar um cliente inadimplente? Liga um estagiario que nao sabe o que falar."*

---

## [0:30–1:30] A Solucao — O que e a UUBA Tech

> *"A UUBA Tech entrega a operacao financeira completa pra PMEs. Nao e um software que o cliente tem que aprender a usar — e a operacao pronta, funcionando."*

Os 5 produtos:

| # | Produto | O que faz |
|---|---------|-----------|
| 1 | **UUBA Nexo** | Conecta CRM, ERP e banco em uma base unica |
| 2 | **UUBA Financeiro** | DRE, fluxo de caixa e projecoes automaticas + equipe de BPO |
| 3 | **UUBA Recebe** | Cobranca automatizada via WhatsApp com IA |
| 4 | **UUBA 360** | Dashboards em tempo real pra cada nivel da empresa |
| 5 | **UUBA para Parceiros** | White-label: escritorios de contabilidade revendem sob a marca deles |

> *"Cinco produtos. Uma operacao. O cliente contrata e ja esta funcionando em 48h."*

---

## [1:30–2:30] Como Funciona — Demo rapida do Recebe

> *"Deixa eu mostrar o que ja ta funcionando. O UUBA Recebe cobra clientes via WhatsApp usando IA. O bot identifica o devedor, consulta as faturas na API, e usa tecnicas de cobranca comportamental — reciprocidade, prova social, aversao a perda — pra negociar o pagamento."*

Pontos-chave:

- **Escala pra humano** quando precisa (via Chatwoot)
- **Memoria** por cliente — sabe o historico
- **Seguranca** — prompt hardened contra manipulacao
- **174 testes automatizados**, CI/CD rodando

---

## [2:30–3:30] Diferenciais Tecnicos

> *"Nao estamos usando API pronta de cobranca. A gente construiu a stack inteira."*

- **API propria** — FastAPI, 14 endpoints, PostgreSQL
- **IA propria** — Claude Sonnet 4, orquestrado por n8n
- **WhatsApp proprio** — Evolution API self-hosted
- **Infra propria** — Docker, nginx, VPS, SSL
- **Tudo documentado** — portal interno com 19 secoes de guia de replicacao

> *"Isso significa que a margem e nossa. Nao pagamos por mensagem enviada, nao dependemos de plataforma de terceiro."*

---

## [3:30–4:15] Modelo de Negocio

> *"Duas frentes de receita:"*

1. **SaaS + BPO** — Assinatura mensal por produto + equipe financeira como extensao
2. **White-label (Parceiros)** — Escritorios de contabilidade revendem. Eles faturam, a gente opera

> *"O Parceiros e o canal de escala. Cada escritorio de contabilidade atende 50-200 empresas. A gente entra por um parceiro, alcanca todas."*

---

## [4:15–5:00] Onde Estamos e O que Precisamos

> *"Hoje: produto UUBA Recebe funcionando em producao. API no ar. Bot cobrando. Infra rodando. Time de 3 cofundadores complementares — estrategia, operacao e tecnologia."*

> *"O que precisamos: capital pra acelerar o go-to-market dos outros 4 produtos e fechar os primeiros parceiros white-label."*

---

## Dica

Leva o celular com o WhatsApp do bot aberto. Se o investidor quiser ver ao vivo, manda uma mensagem pro bot e mostra ele cobrando em tempo real. **Demo ao vivo > slide.**

---

# FAQ — Perguntas Provaveis do Investidor

### 1. "Voces tem clientes pagando?"

A Uuba (consultoria) tem ~1,5 ano de mercado com clientes ativos de BPO financeiro e CFO de Aluguel. A Uuba Tech e a vertical de produto que esta nascendo agora. O Recebe ja esta em producao.

### 2. "Qual o mercado?"

PMEs brasileiras — sao mais de 20 milhoes. Qualquer empresa que precisa cobrar, fazer DRE ou organizar o financeiro. O canal de parceiros (contabilidades) multiplica o alcance.

### 3. "Por que nao usar ferramentas prontas? Asaas, Vindi..."

Essas plataformas cobram por transacao e nao fazem a operacao. A UUBA entrega a operacao financeira completa — software + gente. E com infra propria, a margem e totalmente nossa.

### 4. "Qual o diferencial tecnico? O que impede alguem de copiar?"

A combinacao de IA conversacional + protocolo comportamental de cobranca + integracao multicanal + equipe de BPO. Nao e so software — e a operacao que roda em cima dele. O know-how de cobranca comportamental (Heitor) + a tecnologia (Luis) cria um fosso dificil de replicar.

### 5. "Como escala?"

O canal de Parceiros. Cada escritorio de contabilidade traz dezenas/centenas de clientes. Nao precisa vender empresa por empresa. Um parceiro = um contrato, muitos clientes.

### 6. "Qual o tamanho do time?"

Tres cofundadores: Heitor (CEO, estrategia financeira), Thomaz (operacao e atendimento), Luis (CTO, tecnologia). Estrutura enxuta, sem queimar dinheiro.

### 7. "Qual o custo de infra?"

Toda a stack roda em uma VPS Contabo. Custo mensal baixo. Self-hosted = sem custo variavel por mensagem ou transacao. Escala verticalmente antes de precisar de infra maior.

### 8. "Vao buscar investimento ou bootstrapping?"

Abertos a conversa. A consultoria ja gera receita. O investimento acelera o go-to-market da Tech e a aquisicao de parceiros.

### 9. "Qual o ask? Quanto precisam?"

*(Adaptar conforme o valor definido. Sugestao: ter um numero claro e dizer pra que serve — ex: "R$ X para 12 meses de runway, contratar 2 devs e fechar 10 parceiros white-label")*

### 10. "Qual a estrutura societaria?"

Tres cofundadores com equity definida por vesting. Estrutura juridica em formalizacao com acordo de socios, cliff e good/bad leaver.
