# Modulo 3: Pre-delinquency (Cobranca Preventiva)

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
