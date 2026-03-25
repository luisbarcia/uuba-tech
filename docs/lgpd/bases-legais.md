# Registro de Bases Legais — LGPD (Art. 7)

> Documento obrigatório conforme Art. 37 da LGPD.
> Última atualização: 2026-03-25

## Controlador

- **Razão Social:** UÚBA Tecnologia Ltda.
- **CNPJ:** (a definir)
- **Encarregado (DPO):** (a designar — Art. 41)
- **Contato LGPD:** privacidade@uuba.tech

## Mapeamento de Processamentos

### 1. Cadastro de cliente (importação CSV ou API)

| Campo | Detalhe |
|-------|---------|
| **Dados tratados** | Nome, CPF/CNPJ, email, telefone |
| **Finalidade** | Identificar o devedor para execução do serviço de cobrança |
| **Base legal** | **Execução de contrato** (Art. 7, V) |
| **Justificativa** | O cadastro é necessário para prestar o serviço de cobrança contratado pelo credor |
| **Retenção** | Enquanto houver relação comercial + 5 anos (obrigação fiscal) |

### 2. Registro de faturas

| Campo | Detalhe |
|-------|---------|
| **Dados tratados** | Valor, vencimento, descrição, número NF, vínculo com cliente |
| **Finalidade** | Registrar obrigação financeira para viabilizar cobrança |
| **Base legal** | **Execução de contrato** (Art. 7, V) + **Obrigação legal** (Art. 7, II) |
| **Justificativa** | Dados financeiros necessários para o serviço; retenção fiscal obrigatória |
| **Retenção** | 5 anos (CTN Art. 173 — obrigação tributária) |

### 3. Envio de cobrança (WhatsApp, Email, SMS)

| Campo | Detalhe |
|-------|---------|
| **Dados tratados** | Canal de contato, mensagem, histórico de comunicação |
| **Finalidade** | Notificar devedor sobre obrigação financeira |
| **Base legal** | **Exercício regular de direitos** (Art. 7, VI) |
| **Justificativa** | O credor tem direito de cobrar dívidas; a cobrança é exercício regular de direito previsto no Código Civil |
| **Retenção** | 2 anos após resolução da fatura |

> **Importante:** NÃO usamos consentimento (Art. 7, I) como base legal para cobrança.
> Consentimento pode ser revogado a qualquer momento (Art. 8, §5º), o que inviabilizaria
> a atividade de cobrança. O exercício regular de direitos é a base adequada.

### 4. Métricas de pagamento (DSO, aging)

| Campo | Detalhe |
|-------|---------|
| **Dados tratados** | Agregados financeiros por cliente (não PII direto) |
| **Finalidade** | Análise de risco de crédito e eficiência operacional |
| **Base legal** | **Interesse legítimo** (Art. 7, IX) |
| **Justificativa** | Necessário para operação eficiente do serviço; dados agregados, baixo impacto ao titular |
| **Retenção** | Calculado em tempo real, não persistido |

### 5. Escalação para atendimento humano (Chatwoot)

| Campo | Detalhe |
|-------|---------|
| **Dados tratados** | ID do cliente, motivo da escalação |
| **Finalidade** | Encaminhar casos complexos para atendimento humano |
| **Base legal** | **Execução de contrato** (Art. 7, V) |
| **Justificativa** | Parte do serviço contratado |
| **Retenção** | 2 anos |

### 6. Promessa de pagamento

| Campo | Detalhe |
|-------|---------|
| **Dados tratados** | Data da promessa, vínculo com fatura/cliente |
| **Finalidade** | Registrar compromisso de pagamento para follow-up |
| **Base legal** | **Execução de contrato** (Art. 7, V) |
| **Justificativa** | Funcionalidade essencial do serviço de cobrança |
| **Retenção** | Vinculada à fatura (5 anos) |

## Bases Legais NÃO Utilizadas

| Base | Por quê não |
|------|-------------|
| Consentimento (Art. 7, I) | Revogável a qualquer momento — inviável para cobrança |
| Proteção da vida (Art. 7, VII) | Não aplicável |
| Tutela de saúde (Art. 7, VIII) | Não aplicável |
| Proteção do crédito (Art. 7, X) | Aplicável mas menos específica que Art. 7, VI |

## Referências

- Lei 13.709/2018 (LGPD) — Art. 7, 11, 15, 16, 37
- Código Civil — Art. 394 (mora), Art. 397 (constituição em mora)
- CTN — Art. 173 (decadência tributária — 5 anos)
