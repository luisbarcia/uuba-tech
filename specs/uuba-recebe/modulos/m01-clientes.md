# Modulo 1: Gestao de Clientes (Devedores)

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
