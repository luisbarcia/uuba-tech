# Modulo 2: Gestao de Faturas (Recebiveis)

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
