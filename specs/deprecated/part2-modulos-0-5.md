# UUBA Recebe — Spec v2 (Parte 2): Modulos 0 a 5

---

## Modulo 0: Multi-tenancy e Infraestrutura

### Descricao

Modulo arquitetural que define isolamento de dados, autenticacao, autorizacao e provisionamento de tenants. Promovido de Modulo 10 para Modulo 0 porque e pre-requisito de todos os demais — implementar depois significaria retrabalho massivo em toda a base de codigo.

### Decisoes Arquiteturais

- **Estrategia de banco:** Shared DB com coluna `tenant_id` em todas as tabelas (v1). DB-per-tenant descartado: 100 tenants = 100 connection pools, exige PgBouncer e aumenta complexidade operacional sem beneficio proporcional para o estagio atual.
- **Cache de roteamento:** Redis armazena mapeamento `api_key -> tenant_id` com TTL de 1h. Overhead de lookup < 10ms p99.
- **Provisionamento:** Setup de banco (migrations, seed) e rapido (< 2min). Configuracao de numero WhatsApp e processo separado, pode levar horas dependendo da aprovacao Meta.

### Open Question

> OQ-001: Evolution API vs Meta Cloud API para escala multi-tenant.
> Evolution API exige uma instancia Docker por numero WhatsApp — 100 tenants = 100 containers, inviavel na VPS atual. Meta Cloud API suporta multiplos numeros sob um unico Business Manager. Decisao deve ser tomada antes do Sprint 3.

### Requisitos Funcionais

**FR-001: Roteamento de tenant por API key**
Where uma requisicao HTTP chega com header `X-API-Key`, the system shall identificar o tenant correspondente via cache Redis e injetar `tenant_id` no contexto da requisicao em menos de 10ms.

**FR-002: Isolamento de dados por tenant**
Where qualquer query ao banco de dados e executada, the system shall aplicar filtro `WHERE tenant_id = :tenant_id` automaticamente via middleware, garantindo que nenhum tenant acesse dados de outro.

**FR-003: Provisionamento de tenant**
When um novo tenant e cadastrado, the system shall executar migrations de banco, gerar API key, criar usuario admin, e configurar parametros padrao (regua default, limites de negociacao, horarios de contato).

**FR-004: RBAC basico**
The system shall suportar tres roles por tenant: `admin` (acesso total, configuracoes, usuarios), `operador` (gestao de faturas, devedores, conversas, sem configuracoes de tenant), e `viewer` (somente leitura em dashboards e relatorios).

**FR-005: Configuracao de numero WhatsApp por tenant**
When um tenant configura seu numero WhatsApp, the system shall registrar o numero, validar conectividade com o provedor (Evolution API ou Meta Cloud API), e ativar o recebimento de mensagens para aquele tenant.

**FR-006: Versionamento de API**
The system shall expor endpoints sob prefixo `/api/v1/` e manter compatibilidade retroativa dentro de uma versao major. Deprecacoes devem ser comunicadas com 90 dias de antecedencia via header `Deprecation`.

### Acceptance Criteria

**AC-001: Isolamento de dados entre tenants**
Given tenant A tem 10 devedores e tenant B tem 5 devedores,
When tenant A consulta `GET /api/v1/debtors`,
Then the system shall retornar apenas os 10 devedores de A,
And nenhum devedor de B deve aparecer no resultado.

**AC-002: API key invalida**
Given uma requisicao com header `X-API-Key: chave_inexistente`,
When a requisicao e recebida,
Then the system shall retornar HTTP 401 com mensagem "API key invalida".

**AC-003: Provisionamento completo em menos de 5 minutos**
Given um novo tenant e cadastrado via admin,
When o provisionamento e executado (excluindo configuracao de WhatsApp),
Then o tenant deve ter banco configurado, API key gerada, usuario admin criado, e regua padrao aplicada em menos de 5 minutos.

**AC-004: RBAC impede acesso indevido**
Given um usuario com role `viewer` no tenant A,
When tenta executar `POST /api/v1/debtors` para criar um devedor,
Then the system shall retornar HTTP 403 com mensagem "Permissao insuficiente".

**AC-005: RBAC operador sem acesso a configuracoes**
Given um usuario com role `operador` no tenant A,
When tenta executar `PUT /api/v1/tenant/settings` para alterar configuracoes,
Then the system shall retornar HTTP 403 com mensagem "Permissao insuficiente".

**AC-006: Cache Redis reduz latencia de roteamento**
Given 100 tenants cadastrados com API keys no Redis,
When 1000 requisicoes consecutivas sao enviadas com API keys validas,
Then o tempo medio de lookup do tenant deve ser inferior a 10ms.

**Status:** Nao implementado

---

## Modulo 1: Gestao de Clientes (Devedores)

### Descricao

Cadastro, identificacao e metricas de devedores. Base para todos os modulos de cobranca.

### Requisitos Funcionais

**FR-007: Cadastro de clientes**
When a empresa importa um novo devedor, the system shall criar um registro com nome, documento (CPF/CNPJ unico por tenant), email, e telefone WhatsApp.

**FR-008: Identificacao por telefone**
When the bot recebe uma mensagem WhatsApp, the system shall identificar o cliente pelo numero de telefone em menos de 200ms.

**FR-009: Metricas por cliente**
When um usuario consulta um cliente, the system shall exibir DSO (dias medios para pagamento), total em aberto, total vencido, e contagem de faturas.

**FR-010: Historico de interacoes**
When um usuario abre o perfil de um cliente, the system shall exibir toda a timeline de cobrancas, conversas, promessas, e pagamentos ordenados cronologicamente.

### Acceptance Criteria

**AC-007: Cadastro com documento duplicado**
Given um cliente com CPF 123.456.789-00 ja existe no tenant A,
When outro cadastro com o mesmo CPF e enviado para o tenant A,
Then the system shall retornar HTTP 409 com mensagem "Documento ja cadastrado".

**AC-008: Busca por telefone WhatsApp**
Given um cliente com telefone 5511999001234 esta cadastrado,
When uma mensagem WhatsApp chega desse numero,
Then the system shall retornar o cliente correto em menos de 200ms.

**AC-009: Metricas calculadas corretamente**
Given um cliente tem 5 faturas (3 pagas, 2 vencidas),
When as metricas sao consultadas,
Then DSO deve refletir a media de dias entre emissao e pagamento das 3 pagas,
And total_em_aberto deve somar as 2 vencidas,
And total_vencido deve somar apenas faturas com vencimento anterior a hoje.

**AC-010: Telefone pertence a mais de um devedor (numero reciclado)**
Given o telefone 5511999001234 esta cadastrado para o devedor A (inativo ha 12 meses),
And uma nova pessoa envia mensagem desse numero e se identifica com CPF diferente,
When o bot processa a identificacao,
Then the system shall criar novo registro de devedor vinculado ao telefone,
And marcar o vinculo anterior como `inativo`,
And registrar a troca no log de auditoria.

**AC-011: Formato de telefone diferente**
Given um devedor cadastrado com telefone 5511999001234,
When uma mensagem chega do numero +55 11 99900-1234 (com formatacao diferente),
Then the system shall normalizar o numero para formato E.164 (5511999001234),
And identificar corretamente o devedor.

**AC-012: Upsert quando CPF existe mas dados diferentes**
Given um devedor com CPF 123.456.789-00 ja existe com nome "Joao Silva",
When um import envia registro com mesmo CPF mas nome "Joao da Silva" e email diferente,
Then the system shall atualizar os campos divergentes (nome, email),
And registrar a alteracao no historico do devedor com valores antigos e novos.

**Status:** Implementado

---

## Modulo 2: Gestao de Faturas (Recebiveis)

### Descricao

Ciclo de vida completo de faturas: criacao, estados, pagamento, cancelamento, parcelamento e acordos. Inclui integracao com gateway de pagamento (Conta Azul) via webhook.

### Requisitos Funcionais

**FR-011: Registro de fatura**
When a empresa registra uma fatura, the system shall armazenar valor (em centavos), moeda, vencimento, descricao, numero da NF, e `tenant_id`.

**FR-012: Maquina de estados da fatura**
The fatura shall transicionar entre os estados: `pendente` -> `vencido` (automatico por data) -> `em_negociacao` -> `acordo` -> `pago` | `cancelado`. Transicoes invalidas devem ser rejeitadas com HTTP 422.

**FR-013: Promessa de pagamento**
When o bot registra uma promessa de pagamento, the system shall armazenar a data prometida, o canal da promessa, e agendar follow-up automatico para o dia seguinte a data prometida.

**FR-014: Link de pagamento**
When uma fatura esta em aberto, the system shall gerar um link de pagamento (Pix/boleto via Conta Azul) e armazenar no campo `pagamento_link`. O link deve ter validade configuravel (padrao: 72h).

**FR-015: Transicao automatica para vencido**
Where a data atual ultrapassa o vencimento da fatura, the system shall alterar automaticamente o status para `vencido` via job agendado (cron). O job deve ser idempotente — executar multiplas vezes para a mesma fatura nao deve gerar efeitos colaterais nem entradas duplicadas no log.

**FR-016: Confirmacao de pagamento via webhook**
When o Conta Azul envia um webhook de pagamento confirmado, the system shall validar a assinatura HMAC do payload, atualizar status para `pago`, preencher `pago_em` com timestamp UTC, e disparar notificacao de agradecimento ao devedor. Webhooks com assinatura invalida devem ser rejeitados com HTTP 401.

**FR-017: Cancelamento de fatura**
When um usuario com role `admin` ou `operador` solicita cancelamento de uma fatura, the system shall verificar que a fatura nao esta em status `pago`, transicionar para `cancelado`, registrar motivo e usuario responsavel, e pausar qualquer regua de cobranca ativa para aquela fatura.

**FR-018: Gestao de parcelas (acordo)**
When um acordo de parcelamento e registrado, the system shall gerar N faturas-filhas vinculadas a fatura original via campo `fatura_pai_id`. Cada parcela recebe: numero sequencial (1/N, 2/N...), valor proporcional (incluindo juros/multa se aplicavel), e data de vencimento. A fatura original transiciona para status `acordo`.

**FR-019: Calculo de juros e multa**
Where uma fatura esta vencida e o tenant configurou juros/multa, the system shall calcular: multa fixa (percentual sobre valor original, aplicada uma vez) + juros pro-rata (percentual mensal dividido por 30, aplicado por dia de atraso). Parametros configuraveis por tenant: `multa_percentual` (padrao 2%), `juros_mensal` (padrao 1%).

**FR-020: Acompanhamento de parcelas**
Where parcelas de um acordo estao vigentes, the system shall agendar lembrete automatico 3 dias antes do vencimento de cada parcela via WhatsApp, incluindo numero da parcela, valor, e link de pagamento.

**FR-021: Parcela atrasada — acao automatica**
Where uma parcela de acordo atrasa por mais de 5 dias, the system shall: (1) notificar o devedor sobre o atraso e risco de rescisao, (2) notificar o operador do tenant. Se atrasar por mais de 10 dias, the system shall rescindir o acordo automaticamente, cancelar parcelas futuras, e reativar a regua de cobranca sobre o saldo devedor original menos pagamentos ja efetuados.

### Acceptance Criteria

**AC-013: Fatura com valor zero**
Given um usuario tenta criar uma fatura com valor 0,
When o request e enviado,
Then the system shall retornar HTTP 422 com mensagem "Valor deve ser maior que zero".

**AC-014: Transicao automatica vencido**
Given uma fatura com vencimento 2026-03-20 e status `pendente`,
When o job de verificacao executa em 2026-03-21,
Then o status deve ser atualizado para `vencido`.

**AC-015: Idempotencia do job de transicao**
Given uma fatura ja com status `vencido`,
When o job de transicao executa novamente para a mesma fatura,
Then nenhuma alteracao deve ser feita,
And nenhuma entrada duplicada deve ser criada no log de transicoes.

**AC-016: Pagamento via webhook com HMAC valido**
Given uma fatura fat_abc123 com status `vencido`,
When o Conta Azul envia webhook `payment.confirmed` com referencia fat_abc123 e assinatura HMAC valida,
Then o status muda para `pago`, `pago_em` recebe timestamp UTC,
And o bot envia mensagem de agradecimento via WhatsApp ao devedor.

**AC-017: Webhook com HMAC invalido**
Given um webhook recebido no endpoint de pagamento,
When a assinatura HMAC do payload nao corresponde a chave secreta configurada,
Then the system shall retornar HTTP 401,
And nenhuma alteracao de status deve ser feita,
And o evento deve ser registrado no log de seguranca.

**AC-018: Webhook duplicado (idempotencia)**
Given a fatura fat_abc123 ja esta com status `pago`,
When o Conta Azul envia o mesmo webhook `payment.confirmed` novamente,
Then the system shall retornar HTTP 200 (sucesso idempoente),
And nenhuma alteracao deve ser feita no registro,
And nenhuma mensagem duplicada deve ser enviada ao devedor.

**AC-019: Webhook para fatura cancelada**
Given a fatura fat_abc123 esta com status `cancelado`,
When um webhook `payment.confirmed` e recebido para essa fatura,
Then the system shall rejeitar a transicao com log de alerta,
And notificar o operador sobre pagamento recebido para fatura cancelada,
And retornar HTTP 200 para evitar retentativas do gateway.

**AC-020: Fatura em em_negociacao nao retrocede**
Given uma fatura com status `em_negociacao`,
When o job de transicao tenta alterar para `vencido`,
Then the system shall manter o status `em_negociacao` inalterado.

**AC-021: Cancelamento de fatura com cobranca ativa**
Given uma fatura com regua de cobranca ativa (proximo passo agendado em D+7),
When um admin cancela a fatura,
Then o status transiciona para `cancelado`,
And a regua de cobranca e pausada imediatamente,
And nenhuma mensagem futura e enviada para essa fatura.

**AC-022: Cancelamento de fatura ja paga**
Given uma fatura com status `pago`,
When um admin tenta cancelar,
Then the system shall retornar HTTP 422 com mensagem "Fatura ja paga nao pode ser cancelada".

**AC-023: Parcelamento gera faturas-filhas**
Given uma fatura original de R$ 3.000,00 em status `em_negociacao`,
When um acordo de 3 parcelas e registrado,
Then the system shall criar 3 faturas-filhas (R$ 1.000,00 cada) vinculadas a original,
And a fatura original transiciona para status `acordo`,
And cada parcela recebe data de vencimento com intervalo de 30 dias.

**AC-024: Lembrete de parcela 3 dias antes**
Given uma parcela 2/3 com vencimento em 2026-04-20,
When o sistema executa verificacao em 2026-04-17,
Then o devedor recebe mensagem WhatsApp com numero da parcela, valor, e link de pagamento.

**AC-025: Parcela atrasada com rescisao de acordo**
Given um acordo de 3 parcelas onde parcela 2/3 venceu ha 11 dias sem pagamento,
And parcela 1/3 foi paga (R$ 1.000,00),
When o sistema verifica em D+11 da parcela 2/3,
Then o acordo deve ser rescindido,
And parcela 3/3 cancelada,
And a regua de cobranca reativada sobre saldo de R$ 2.000,00 (original R$ 3.000,00 menos R$ 1.000,00 ja pago).

**Status:** Parcialmente implementado (CRUD ok, webhook e transicao automatica pendentes, parcelamento nao implementado)

---

## Modulo 3: Pre-delinquency

### Descricao

Regua preventiva que atua ANTES do vencimento da fatura, com objetivo de reduzir inadimplencia em 15-25%. Inspirada nas praticas de InDebted e Symend, que demonstram que intervencao pre-vencimento e significativamente mais eficaz e menos custosa que cobranca pos-vencimento.

### Requisitos Funcionais

**FR-022: Regua preventiva configuravel**
When um tenant configura a regua preventiva, the system shall permitir definir passos entre D-30 e D-1 (dias antes do vencimento), com canal (WhatsApp, email, SMS), template de mensagem, e tom (informativo, lembrete gentil). Cada tenant pode ter multiplas reguas preventivas por perfil de devedor.

**FR-023: Desconto por antecipacao escalonado**
Where o tenant configurou desconto por antecipacao, the system shall aplicar desconto escalonado sobre o valor da fatura: quanto mais cedo o pagamento, maior o desconto. Configuracao padrao: D-14 = 5%, D-7 = 3%, D-3 = 1%. Percentuais sao configuraveis por tenant.

**FR-024: Predicao de inadimplencia**
Where o Modulo 9 (Scoring) atribui score ao devedor, the system shall usar o score para ajustar a intensidade da regua preventiva: devedores com score alto (baixo risco) recebem menos mensagens preventivas; devedores com score baixo (alto risco) recebem a regua completa.

**FR-025: Link de pagamento na primeira mensagem preventiva**
When a primeira mensagem preventiva e enviada, the system shall incluir link de pagamento ja funcional, permitindo que o devedor pague imediatamente sem interacao adicional.

**FR-026: Cancelamento automatico da regua preventiva**
Where o devedor paga a fatura antes do vencimento, the system shall cancelar todos os passos futuros da regua preventiva para aquela fatura em menos de 1 minuto apos confirmacao do pagamento.

### Acceptance Criteria

**AC-026: Regua preventiva executada nos dias corretos**
Given uma fatura com vencimento em 2026-04-15,
And regua preventiva configurada com passos em D-14, D-7, D-3, D-1,
When nenhum pagamento e recebido,
Then the system shall enviar mensagens em 01/04, 08/04, 12/04, e 14/04,
And cada mensagem deve conter valor da fatura, vencimento, e link de pagamento.

**AC-027: Desconto por antecipacao calculado corretamente**
Given uma fatura de R$ 1.000,00 com vencimento em 2026-04-15,
And configuracao de desconto: D-14 = 5%, D-7 = 3%, D-3 = 1%,
When a mensagem preventiva e enviada em D-14 (01/04),
Then o desconto exibido deve ser R$ 50,00 (5%),
And o link de pagamento deve refletir o valor com desconto (R$ 950,00).

**AC-028: Desconto expira no dia seguinte**
Given o desconto de 5% foi oferecido em D-14,
When o devedor acessa o link de pagamento em D-13,
Then o desconto de 5% nao deve mais estar disponivel,
And o proximo desconto aplicavel (3% em D-7) deve ser exibido quando disponivel.

**AC-029: Fatura paga antes do vencimento cancela regua preventiva**
Given uma fatura com regua preventiva ativa (proximo passo agendado em D-7),
When o pagamento e confirmado via webhook em D-10,
Then todos os passos futuros da regua preventiva devem ser cancelados,
And nenhuma mensagem preventiva adicional deve ser enviada.

**AC-030: Devedor de score alto recebe menos mensagens preventivas**
Given devedor A tem score 85 (baixo risco) e devedor B tem score 25 (alto risco),
And ambos tem faturas com vencimento em 2026-04-15,
When a regua preventiva e configurada com 4 passos (D-14, D-7, D-3, D-1),
Then devedor A recebe apenas 2 passos (D-3, D-1),
And devedor B recebe todos os 4 passos.

**AC-031: Regua preventiva nao dispara para fatura ja paga**
Given uma fatura com status `pago`,
When o cron de regua preventiva executa,
Then nenhuma mensagem deve ser enviada para essa fatura.

**Status:** Nao implementado

---

## Modulo 4: Regua de Cobranca

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

---

## Modulo 5: Bot IA Conversacional

### Descricao

Agente IA (Claude Sonnet) com protocolo comportamental de cobranca, tools para consulta de dados em tempo real, negociacao semi-automatica, e integracao com WhatsApp. Inclui recepcao de audio, handoff para humano, circuit breaker para servicos externos, e self-healing.

### Requisitos Funcionais

**FR-044: Agente IA com protocolo comportamental**
The bot shall operar com agente Claude (Sonnet) usando protocolo de cobranca comportamental (nudge), system prompt com regras de negocio, e tom adaptativo baseado no perfil e historico do devedor.

**FR-045: Tools do agente**
The agent shall ter acesso a tools para: buscar faturas em aberto, buscar metricas do cliente, registrar promessa de pagamento, registrar cobranca realizada, gerar link de pagamento, consultar score de risco, e consultar historico de acordos.

**FR-046: Memoria de conversa**
The system shall manter historico das ultimas 10 mensagens por telefone (buffer window) para contexto conversacional. Mensagens mais antigas devem ser resumidas automaticamente para manter contexto sem exceder limite de tokens.

**FR-047: Identificacao de intencao**
When o devedor envia uma mensagem, the agent shall classificar a intencao: pagamento, promessa, duvida, negociacao, reclamacao, saudacao, confirmacao_pagamento, ou off-topic.

**FR-048: Respostas baseadas em dados**
The agent shall responder SOMENTE com dados obtidos via tools (API). Nunca deve inventar valores, datas, ou informacoes financeiras. Se a tool falhar, o agent deve informar que nao conseguiu obter os dados no momento.

**FR-049: Escalacao para humano**
Where o devedor solicita parcelamento acima do limite, demonstra sentimento negativo persistente (detectado via prompt do Claude com threshold configuravel), ou a situacao requer julgamento humano, the system shall encaminhar a conversa para atendente via Chatwoot. Taxa aceitavel de falsos positivos na deteccao de sentimento: ate 10%.

**FR-050: Negociacao semi-automatica**
Where o devedor quer negociar desconto ou parcelamento, the agent shall propor opcoes dentro dos limites configurados por tenant (ex: max 10% desconto, max 3x parcelas). Desconto calculado sobre valor original da fatura. Acordos acima dos limites requerem aprovacao humana. Parcelamento gera faturas-filhas conforme FR-018.

**FR-051: Verificacao de pagamento (fluxo "ja paguei")**
When o devedor diz "ja paguei" referindo-se a Pix, the agent shall: (1) informar que esta verificando o pagamento, (2) aguardar webhook de confirmacao com timeout de 60 segundos, (3) se webhook chegar dentro do timeout, confirmar pagamento, (4) se timeout expirar, informar que o pagamento sera confirmado automaticamente quando processado pelo sistema financeiro e que o devedor sera notificado. Para boleto, informar prazo de 1-2 dias uteis.

**FR-052: Verificacao cruzada de pagamento em multiplos gateways**
Where o devedor alega pagamento e nenhum webhook foi recebido, the system shall consultar todos os gateways configurados (Conta Azul e futuros) para verificar se o pagamento foi registrado em outra fonte.

**FR-053: Confirmacao de pagamento via comprovante**
When o devedor envia foto de comprovante de pagamento, the system shall processar a imagem via OCR, extrair dados (valor, data, identificador), e cruzar com faturas em aberto. Se houver match, registrar como "pagamento em verificacao" e notificar operador. Se nao houver match, informar ao devedor que nao foi possivel confirmar automaticamente e escalar para operador.

**FR-054: Saudacao e identificacao**
When um numero desconhecido envia mensagem, the system shall solicitar CPF/CNPJ para identificacao. When um numero conhecido envia saudacao, the system shall cumprimentar pelo nome e oferecer ajuda contextual baseada nas faturas em aberto.

**FR-055: Deteccao de sentimento**
The agent shall detectar sentimento negativo (raiva, frustracao) via analise do Claude no system prompt e ajustar tom para empatico antes de considerar escalacao. Sentimento negativo persistente (2+ mensagens consecutivas) aciona escalacao automatica.

**FR-056: Recepcao e transcricao de audio WhatsApp**
When o devedor envia mensagem de audio via WhatsApp, the system shall transcrever o audio usando Whisper (ou servico equivalente), processar o texto transcrito como mensagem normal, e armazenar tanto o audio original quanto a transcricao no historico.

**FR-057: Resposta em audio (TTS)**
Where o tenant habilitou resposta por audio, the system shall converter a resposta texto do bot em audio (TTS) e enviar como mensagem de voz no WhatsApp. Funcionalidade opcional, desativada por padrao.

**FR-058: Handoff bot para humano com resumo automatico**
When uma conversa e escalada para atendente humano (via Chatwoot), the system shall gerar resumo automatico contendo: ultimas 5 mensagens, intent detectado, faturas em aberto do devedor, score de risco, historico de acordos, e motivo da escalacao. Resumo enviado como nota interna no Chatwoot.

**FR-059: Self-healing para falhas de envio**
Where o envio de mensagem falha, the system shall classificar o erro como transiente (timeout, rate limit, 5xx) ou permanente (numero invalido, bloqueado, 4xx). Erros transientes acionam retry com exponential backoff (1s, 2s, 4s, 8s, max 5 tentativas). Erros permanentes registram falha e notificam operador.

**FR-060: Circuit breaker por servico externo**
Where um servico externo (Evolution API, Conta Azul API, Claude API) apresenta 5 ou mais falhas em janela de 5 minutos, the system shall ativar circuit breaker: parar chamadas ao servico, enfileirar mensagens pendentes, tentar reconexao gradual (1 chamada teste a cada 30s). Quando servico voltar, processar fila na ordem. Operador deve ser notificado quando circuit breaker ativa e desativa.

**FR-061: Resumo agregado para devedores com muitas faturas**
Where um devedor tem mais de 10 faturas em aberto, the agent shall apresentar resumo agregado (total devido, quantidade de faturas, faixa de datas) ao inves de listar cada fatura individualmente. Detalhes disponveis sob solicitacao.

### Acceptance Criteria

**AC-044: Bot responde com dados reais**
Given o devedor pergunta "quanto devo?",
When o agent processa a mensagem,
Then deve chamar a tool de faturas e responder com valores exatos do banco de dados,
And nunca inventar ou estimar valores.

**AC-045: Promessa de pagamento registrada**
Given o devedor diz "vou pagar sexta-feira",
When o agent processa a mensagem,
Then deve registrar promessa com data calculada (proxima sexta-feira),
And agendar follow-up para o dia seguinte a data prometida,
And pausar a regua de cobranca para aquela fatura.

**AC-046: Escalacao por desconto acima do limite**
Given o limite de desconto configurado e 10%,
When o devedor pede 20% de desconto,
Then o agent deve informar que precisa aprovacao e escalar para humano via Chatwoot,
And o resumo automatico deve ser enviado ao atendente.

**AC-047: Numero desconhecido**
Given o telefone 5511888887777 nao esta cadastrado,
When envia "oi" para o bot,
Then o bot responde solicitando CPF ou CNPJ para identificacao.

**AC-048: API fora do ar quando bot busca dados**
Given a API de faturas esta indisponivel (circuit breaker ativo),
When o devedor pergunta "quanto devo?",
Then o bot deve responder "Estou com dificuldade para acessar seus dados no momento. Por favor, tente novamente em alguns minutos.",
And registrar o incidente no log.

**AC-049: Devedor com mais de 10 faturas**
Given um devedor tem 50 faturas em aberto totalizando R$ 25.000,00,
When pergunta "quanto devo?",
Then o bot deve responder com resumo agregado: "Voce tem 50 faturas em aberto totalizando R$ 25.000,00. Deseja ver os detalhes?",
And nao deve listar as 50 faturas individualmente.

**AC-050: Audio de longa duracao**
Given um devedor envia audio de 5 minutos via WhatsApp,
When o sistema recebe o audio,
Then deve transcrever o audio completo usando Whisper,
And processar o texto transcrito normalmente,
And armazenar audio original e transcricao no historico.

**AC-051: Timeout na verificacao de pagamento**
Given o devedor diz "ja paguei via Pix",
And nenhum webhook de confirmacao chega em 60 segundos,
When o timeout expira,
Then o bot deve responder "Ainda nao recebi a confirmacao do seu pagamento. Assim que for processado pelo sistema financeiro, voce sera notificado automaticamente.",
And agendar verificacao cruzada em 30 minutos.

**AC-052: Circuit breaker ativado**
Given a Evolution API falhou 5 vezes nos ultimos 5 minutos,
When o circuit breaker e ativado,
Then novas mensagens devem ser enfileiradas (nao descartadas),
And o operador deve receber notificacao "Circuit breaker ativado para Evolution API",
And o sistema deve tentar reconexao a cada 30 segundos.

**AC-053: Circuit breaker desativado apos recuperacao**
Given o circuit breaker para Evolution API esta ativo,
And uma chamada teste bem-sucedida e detectada,
When o sistema confirma recuperacao (3 chamadas consecutivas com sucesso),
Then o circuit breaker deve ser desativado,
And as mensagens enfileiradas devem ser processadas na ordem,
And o operador deve receber notificacao "Evolution API recuperada, processando fila de N mensagens".

**AC-054: Handoff com resumo automatico**
Given o devedor esta irritado (2 mensagens com sentimento negativo consecutivas),
When a conversa e escalada para Chatwoot,
Then uma nota interna deve ser criada contendo: ultimas 5 mensagens, intent "reclamacao", faturas em aberto, score de risco, e motivo "sentimento negativo persistente",
And o atendente deve ver o resumo antes de iniciar a conversa.

**AC-055: Comprovante de pagamento via foto**
Given o devedor envia foto de comprovante Pix de R$ 500,00,
And existe fatura em aberto de R$ 500,00,
When o sistema processa a imagem via OCR,
Then deve identificar o valor e cruzar com a fatura correspondente,
And registrar como "pagamento em verificacao",
And notificar operador para confirmacao manual.

**AC-056: Latencia do bot**
Given o devedor envia uma mensagem,
When o agent processa e responde,
Then o tempo total de resposta (recebimento -> envio) deve ser inferior a 5 segundos no p95.

**Status:** Parcialmente implementado (agente funcional, escalacao, negociacao, audio, circuit breaker e self-healing pendentes)
