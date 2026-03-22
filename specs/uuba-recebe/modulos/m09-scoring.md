# Modulo 9: Scoring e Inteligencia Preditiva

**Status:** Nao implementado

> **Nota de arquitetura:** A v1 utiliza scoring heuristico com regras explicitas, NAO machine learning real. ML sera implementado na v2 quando o volume de dados for suficiente (>10.000 devedores com historico de pagamento).

### Functional Requirements

**FR-100: Score heuristico 0-100 com formula explicita**
The system shall calcular score de probabilidade de pagamento de 0 a 100 para cada devedor usando formula heuristica:

```
score = base(50)
      + historico_pagamento  (-20 a +20)
      + tempo_atraso          (-15 a +15)
      + engajamento           (-10 a +10)
      + valor_relativo        (-5 a +5)
```

Onde:
- `historico_pagamento`: razao entre faturas pagas e total de faturas, ponderada por recencia. Pagou tudo = +20, nunca pagou = -20.
- `tempo_atraso`: dias de atraso da fatura mais antiga em aberto. 0 dias = +15, 90+ dias = -15, interpolacao linear.
- `engajamento`: interacao com mensagens (abriu, leu, respondeu, clicou link). Respondeu e clicou = +10, ignorou tudo = -10.
- `valor_relativo`: valor total em aberto relativo a media do tenant. Abaixo da media = +5 (mais provavel pagar), acima = -5.

**FR-101: Recalculo por evento e batch diario**
The system shall recalcular o score do devedor em dois modos:
- **Por evento:** imediatamente apos eventos significativos (pagamento confirmado, resposta recebida, promessa registrada, promessa nao cumprida).
- **Batch diario:** job agendado que recalcula scores de todos os devedores ativos para incorporar mudancas passivas (tempo de atraso crescente, falta de engajamento).

**FR-102: Segmentacao automatica baseada em regras**
The system shall classificar cada devedor em exatamente um segmento com base em regras explicitas:
- **"bom pagador atrasado"**: score > 60 E tem historico de pelo menos 2 faturas pagas, mesmo que com atraso.
- **"recorrente"**: score entre 30 e 60 E padrao de atraso constante (media de atraso nos ultimos 3 meses > 10 dias).
- **"inadimplente cronico"**: score < 30 E nenhuma fatura paga nos ultimos 6 meses.
- **"novo"**: menos de 3 faturas registradas no sistema (sem historico suficiente).
- **"negociador"**: solicitou desconto ou parcelamento em pelo menos 50% das interacoes de cobranca.

A classificacao e recalculada junto com o score (por evento e batch diario).

**FR-103: Score alimenta regua**
Where o score de um devedor muda, the system shall ajustar o comportamento da regua:
- Score > 70: tom amigavel, frequencia menor, lembrete suave.
- Score 40-70: tom neutro a firme, frequencia padrao.
- Score < 40: escalacao rapida, encurtar intervalos entre passos, priorizar canal com maior engajamento.

**FR-104: Recomendacao de melhor horario (agregada)**
Based on dados agregados de todos os devedores do tenant (nao individual, pois o volume por devedor e insuficiente no v1), the system shall recomendar faixas de horario com maior taxa de leitura e resposta, agrupadas por dia da semana. A recomendacao deve ser atualizada semanalmente no batch diario.

**FR-105: Explicabilidade do score**
When o operador consulta o score de um devedor, the system shall exibir os top 3 fatores que mais contribuiram para aquele score, com nome do fator, valor numerico da contribuicao, e direcao (positivo ou negativo). Exemplo: "Historico de pagamento: +15 (pagou 4 de 5 faturas)".

**FR-106: Endpoint de score**
The system shall expor endpoint `GET /api/v1/clientes/{id}/score` que retorna: `score` (0-100), `segmento` (string), `fatores` (array de top 3), `horario_recomendado` (faixa), `updated_at` (timestamp do ultimo calculo).

### Acceptance Criteria

**AC-082: Score inicial para devedor novo**
Given um devedor sem historico (primeira fatura cadastrada),
When o score e calculado,
Then deve retornar score 50 (base) com segmento "novo",
And fator explicativo: "Sem historico -- score padrao".

**AC-083: Score sobe apos pagamento**
Given um devedor com score 35 e 3 faturas (1 paga, 2 vencidas),
When ele paga uma das faturas vencidas,
Then o score deve aumentar (recalculo imediato),
And o fator "Historico de pagamento" deve refletir a melhora (ex: de -10 para -3),
And o segmento deve ser reavaliado.

**AC-084: Score desce apos promessa nao cumprida**
Given um devedor com score 55 que prometeu pagar em 2026-03-25,
When o sistema verifica em 2026-03-26 que o pagamento nao foi realizado,
Then o score deve diminuir (engajamento negativo),
And o fator "Engajamento" deve refletir a queda.

**AC-085: Segmentacao correta por regras**
Given 5 devedores com os seguintes perfis:
- Devedor A: score 75, 5 faturas pagas de 6 totais,
- Devedor B: score 45, media de atraso 15 dias nos ultimos 3 meses,
- Devedor C: score 20, nenhuma fatura paga nos ultimos 6 meses,
- Devedor D: 2 faturas totais no sistema,
- Devedor E: score 50, pediu desconto em 3 de 4 interacoes,
When a segmentacao e executada,
Then Devedor A = "bom pagador atrasado", Devedor B = "recorrente", Devedor C = "inadimplente cronico", Devedor D = "novo", Devedor E = "negociador".

**AC-086: Recalculo em tempo aceitavel**
Given um evento de pagamento e registrado para um devedor,
When o recalculo por evento e disparado,
Then o novo score deve estar disponivel em menos de 500ms.

**AC-087: Explicabilidade com top 3 fatores**
Given um devedor com score 72,
When o operador consulta o endpoint de score,
Then a resposta inclui exatamente 3 fatores ordenados por magnitude absoluta de contribuicao,
And cada fator contem: nome, valor numerico, e direcao.
