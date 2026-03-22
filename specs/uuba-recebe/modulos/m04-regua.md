# Modulo 4: Regua de Cobranca

### Descricao

Motor de reguas de cobranca pos-vencimento com compliance embutido, A/B testing, behavioral nudges, e gestao de renegociacao. Compliance (horarios, frequencia, LGPD) e parte integral deste modulo — nao e modulo separado — porque regua sem compliance e risco legal imediato.

### Compliance Embutido

As seguintes restricoes sao aplicadas automaticamente a toda execucao de regua:

- **Horarios de contato:** Segunda a sexta 8h-20h, sabado 8h-14h. Nunca domingo ou feriados nacionais.
- **Limite de frequencia:** Maximo 1 mensagem por dia e 3 mensagens por semana por devedor, independentemente de quantas faturas em aberto.
- **Registro de consentimento (LGPD):** Primeira interacao registra consentimento do devedor para receber comunicacoes. Sem consentimento registrado, apenas 1 tentativa de contato e permitida.
- **Opt-out por canal:** Devedor pode solicitar opt-out de WhatsApp, email, ou SMS individualmente. Opt-out do unico canal disponivel gera alerta para operador.
- **Audit trail:** Cada interacao (mensagem enviada, resposta recebida, pausa, retomada, escalacao) e registrada com timestamp, canal, conteudo, e resultado.

### Requisitos Funcionais

**FR-027: Reguas configuraveis por perfil**
When a empresa configura a cobranca, the system shall permitir criar multiplas reguas com criterios: faixa de atraso (dias), faixa de valor, perfil de risco (baseado em score), e setor do devedor.

**FR-028: Sequencia de passos da regua**
Each regua shall conter uma sequencia ordenada de passos, each com: dia relativo ao vencimento (D+1, D+3, D+7...), canal (WhatsApp, email, SMS), tipo (lembrete, cobranca, follow_up, escalacao), tom (amigavel, neutro, firme, urgente), e template de mensagem com variaveis.

**FR-029: Tom progressivo automatico**
Where o devedor nao responde a cobranca, the system shall escalar o tom automaticamente conforme a regua: amigavel (D+1 a D+3) -> neutro (D+4 a D+7) -> firme (D+8 a D+12) -> urgente (D+13 a D+15).

**FR-030: Execucao automatica da regua**
The system shall executar a regua via cron, verificando faturas vencidas e disparando acoes conforme o passo atual da sequencia, respeitando todas as restricoes de compliance.

**FR-031: Pausa inteligente**
Where o devedor esta em conversa ativa com o bot (ultima mensagem ha menos de 24h) ou ja fez promessa de pagamento valida, the system shall pausar automaticamente a regua para aquela fatura.

**FR-032: Retomada automatica**
Where uma promessa de pagamento expira sem confirmacao, the system shall retomar a regua automaticamente a partir do proximo passo, respeitando horarios e limites de frequencia.

**FR-033: Regua padrao**
Where a empresa nao configurou regua customizada, the system shall aplicar uma regua padrao baseada no protocolo comportamental Uuba (D+1 a D+15, 4 niveis de tom progressivo).

**FR-034: Templates de mensagem com variaveis**
The system shall suportar templates de mensagem com variaveis substituiveis: `{{nome}}`, `{{valor}}`, `{{valor_original}}`, `{{dias_atraso}}`, `{{link_pagamento}}`, `{{data_vencimento}}`, `{{numero_parcela}}`, `{{total_parcelas}}`. Variaveis nao resolvidas devem impedir o envio e gerar alerta.

**FR-035: A/B testing de reguas**
When um tenant configura A/B testing, the system shall permitir criar duas ou mais variantes de regua com distribuicao percentual configuravel (ex: 50/50, 70/30). Devedores sao atribuidos aleatoriamente a uma variante e permanecem nela durante todo o ciclo.

**FR-036: A/B testing de mensagens**
When um passo da regua tem multiplas variantes de copy, the system shall distribuir as variantes conforme configuracao e rastrear metricas por variante: taxa de leitura, taxa de resposta, taxa de pagamento, e tempo ate pagamento.

**FR-037: Promocao automatica da variante vencedora**
Where um teste A/B atinge significancia estatistica (p < 0.05) com amostra minima de 100 devedores por variante, the system shall promover automaticamente a variante vencedora e notificar o operador com relatorio comparativo.

**FR-038: Acao pos-regua**
Where um devedor nao responde e nao paga apos o ultimo passo da regua (D+15), the system shall executar acao configuravel pelo tenant. Opcoes: (a) pausa permanente com revisao mensal, (b) reinicio com intervalo de 15 dias e copy diferente, (c) escalacao para atendimento manual, (d) notificacao ao tenant para decisao. Padrao: opcao (d).

**FR-039: Behavioral nudges configuraveis**
The system shall suportar nudges comportamentais nos templates de mensagem, ativaveis por tenant: social proof ("87% dos clientes na sua situacao ja regularizaram"), loss aversion ("seu credito sera restrito em X dias"), e reciprocidade ("preparamos condicoes especiais para voce").

**FR-040: Renegociacao proativa pos-quebra de acordo**
Where um devedor quebra um acordo (parcela atrasada > 10 dias), the system shall: (1) aguardar cooling period de 24h, (2) enviar proposta de renegociacao com condicoes ajustadas (desconto menor, entrada obrigatoria), (3) limitar a 2 renegociacoes por fatura original.

**FR-041: Deteccao de padrao de quebra recorrente**
Where um devedor quebra acordo pela segunda vez para a mesma fatura, the system shall reclassificar como "negociador serial", escalar para atendimento humano, e ajustar score de risco negativamente.

**FR-042: Simulador de regua (dry run)**
When um operador solicita simulacao de regua, the system shall executar a regua em modo dry run — calcular quantos devedores seriam impactados, em quais dias, com quais mensagens — sem enviar nenhuma mensagem. Resultado apresentado como preview antes da ativacao.

**FR-043: Restricao de horario e enfileiramento**
Where um passo da regua e agendado para horario fora do permitido (domingo, feriado, madrugada), the system shall enfileirar a mensagem para o proximo horario permitido, mantendo a ordem da sequencia.

### Acceptance Criteria

**AC-032: Regua com 5 passos executada corretamente**
Given uma regua configurada com passos em D+1, D+3, D+7, D+10, D+15,
When uma fatura vence e nenhum pagamento ou resposta e recebido,
Then the system shall enviar 5 mensagens nos dias corretos, escalando o tom progressivamente.

**AC-033: Pausa por conversa ativa**
Given o devedor respondeu uma mensagem de cobranca ha menos de 24h,
When o cron tenta executar o proximo passo da regua,
Then a execucao deve ser adiada e o status da regua marcado como `conversa_ativa`.

**AC-034: Retomada apos promessa expirada**
Given o devedor prometeu pagar em 2026-03-25 e nao pagou,
When o sistema verifica em 2026-03-26,
Then a regua retoma do passo seguinte ao que estava quando pausou,
And a retomada respeita horario permitido e limite de frequencia.

**AC-035: Regua em feriado — enfileiramento**
Given o proximo passo da regua esta agendado para 2026-04-21 (Tiradentes),
When o cron executa em 2026-04-21,
Then a mensagem nao deve ser enviada,
And deve ser enfileirada para 2026-04-22 (proximo dia util) no primeiro horario permitido (8h).

**AC-036: Limite de frequencia atingido**
Given um devedor ja recebeu 3 mensagens nesta semana (segunda, quarta, sexta),
When a regua tenta enviar quarta mensagem no sabado,
Then a mensagem deve ser adiada para a proxima semana,
And o log deve registrar "Limite semanal atingido para devedor X".

**AC-037: A/B testing com amostra minima**
Given um teste A/B com variantes A e B, cada uma com 50 devedores (abaixo do minimo de 100),
When a variante A tem taxa de pagamento 40% e B tem 20%,
Then the system nao deve declarar vencedora,
And deve continuar o teste ate atingir amostra minima de 100 por variante.

**AC-038: Promocao automatica de variante vencedora**
Given um teste A/B atingiu 100+ devedores por variante,
And variante A tem taxa de pagamento 35% vs variante B com 20% (p < 0.05),
When o sistema avalia o teste,
Then variante A deve ser promovida como regua principal,
And o operador deve receber notificacao com relatorio comparativo (taxas, p-value, intervalo de confianca).

**AC-039: Renegociacao apos quebra de acordo**
Given um devedor quebrou acordo (parcela atrasada > 10 dias) pela primeira vez,
When o cooling period de 24h expira,
Then the system deve enviar proposta de renegociacao com condicoes ajustadas,
And registrar que esta e a primeira renegociacao.

**AC-040: Segunda quebra de acordo — escalacao para humano**
Given um devedor quebrou acordo pela segunda vez para a mesma fatura original,
When o sistema detecta a segunda quebra,
Then o devedor deve ser reclassificado como "negociador serial",
And a conversa deve ser escalada para atendente humano,
And nenhuma proposta automatica de renegociacao deve ser enviada.

**AC-041: Simulador de regua mostra contagem correta**
Given 500 devedores com faturas vencidas que atendem aos criterios da regua,
When o operador executa simulacao (dry run),
Then o resultado deve mostrar: 500 devedores impactados, cronograma de envio por dia, preview das mensagens,
And nenhuma mensagem real deve ser enviada.

**AC-042: Opt-out do unico canal disponivel**
Given um devedor tem apenas WhatsApp como canal de contato,
When o devedor solicita opt-out de WhatsApp,
Then the system deve registrar o opt-out,
And gerar alerta para o operador informando que nao ha canal alternativo,
And nenhuma mensagem futura deve ser enviada por WhatsApp.

**AC-043: Audit trail completo**
Given uma regua de 5 passos e executada para um devedor,
When o operador consulta o audit trail,
Then cada passo deve ter registro com: timestamp, canal, conteudo da mensagem, status de entrega, resposta do devedor (se houver), e acao tomada.

**Status:** Nao implementado (Sprint 5)
