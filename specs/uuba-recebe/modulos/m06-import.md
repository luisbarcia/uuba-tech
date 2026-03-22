# Modulo 6: Import de Titulos

**Status:** Nao implementado

### Functional Requirements

**FR-062: Upload assincrono de planilha (CSV/Excel)**
When a empresa faz upload de arquivo CSV ou Excel, the system shall receber o arquivo, retornar HTTP 202 Accepted com `job_id`, e processar o arquivo de forma assincrona em background. O status do processamento deve ser consultado via `GET /api/v1/import/{job_id}`.

**FR-063: Mapeamento de colunas**
When o formato da planilha nao corresponde ao layout padrao, the system shall apresentar interface de mapeamento de colunas para o usuario associar campos do arquivo aos campos do sistema (nome, documento, valor, vencimento, numero_nf, descricao).

**FR-064: Validacao e relatorio de erros**
Where o arquivo contem linhas invalidas (documento malformado, valor negativo ou zero, data invalida, campos obrigatorios ausentes), the system shall processar as linhas validas e retornar relatorio detalhado das rejeitadas com motivo e numero da linha.

**FR-065: Import via API REST (batch)**
The system shall expor endpoint `POST /api/v1/import/batch` que aceita array de faturas em JSON, criando clientes quando necessario (upsert por documento). Para lotes com mais de 1.000 items, o endpoint deve retornar 202 Accepted com `job_id` e processar de forma assincrona.

**FR-066: Import via webhook de ERP**
When um ERP envia webhook de fatura vencida, the system shall validar a assinatura HMAC-SHA256 do payload (header `X-Webhook-Signature`), processar automaticamente, e inserir no fluxo de cobranca. O schema generico do webhook deve aceitar campos: `evento` (fatura.criada, fatura.vencida, fatura.cancelada), `dados` (objeto com campos da fatura), `timestamp`, e `hmac_signature`.

**FR-067: Deduplicacao**
Where uma fatura com mesmo `numero_nf` + `cliente_id` ja existe no sistema, the system shall ignorar a duplicata e registrar no log de import com motivo "duplicata".

**FR-068: Deteccao automatica de encoding e separador**
When o sistema recebe um arquivo CSV, the system shall detectar automaticamente o encoding (UTF-8 ou ISO-8859-1) e o separador (virgula, ponto-e-virgula, ou tab), convertendo para UTF-8 internamente antes do processamento.

**FR-069: Limite de arquivo**
Where o arquivo de import contem mais de 100.000 linhas, the system shall rejeitar o upload com HTTP 413 e mensagem "Arquivo excede o limite de 100.000 linhas. Divida o arquivo em partes menores."

**FR-070: Preview de import (dry run)**
When a empresa solicita preview antes de confirmar o import, the system shall parsear e exibir as primeiras 10 linhas do arquivo ja mapeadas nos campos do sistema, incluindo indicacao de erros de validacao, sem persistir nenhum dado. O usuario deve confirmar para iniciar o processamento real.

**FR-071: Notificacao de conclusao de import**
When um job de import finaliza (sucesso ou falha parcial), the system shall enviar notificacao ao tenant com resumo: quantidade de faturas criadas, quantidade rejeitada com motivos agregados, quantidade de duplicatas ignoradas, e tempo total de processamento.

**FR-072: Import recorrente via ERP (futuro)**
Where o tenant configura conexao com ERP, the system shall sincronizar automaticamente novas faturas em intervalos configuraveis (minimo 1h). Este FR esta planejado para versao futura e nao sera implementado no v1.

**FR-073: Status do job de import**
The system shall expor endpoint `GET /api/v1/import/{job_id}` que retorna o status atual do job: `pending`, `processing` (com percentual de progresso), `completed` (com resumo), ou `failed` (com motivo do erro). O endpoint deve incluir campos: `status`, `progress_percent`, `total_lines`, `processed_lines`, `created_count`, `rejected_count`, `duplicate_count`, `errors` (array com detalhes), e `completed_at`.

### Acceptance Criteria

**AC-057: Upload CSV com 1.000 linhas**
Given um arquivo CSV com 1.000 linhas, 950 validas e 50 invalidas,
When o usuario faz upload,
Then o sistema retorna HTTP 202 com job_id,
And ao consultar o status apos processamento, 950 faturas foram criadas, 50 rejeitadas,
And o relatorio de erros lista linha e motivo para cada rejeicao.

**AC-058: Deduplicacao por NF**
Given uma fatura NF-001 para cliente cli_abc ja existe no sistema,
When o usuario importa planilha contendo NF-001 para o mesmo cliente,
Then a linha e ignorada,
And o resumo do job registra 1 duplicata com referencia "NF-001 / cli_abc".

**AC-059: Webhook ERP com HMAC valido**
Given um ERP configurado com shared secret "s3cr3t" envia webhook com payload assinado via HMAC-SHA256,
When o webhook e recebido e a assinatura e valida,
Then a fatura e criada com status correspondente ao evento,
And a regua de cobranca e ativada automaticamente se o status for `vencido`.

**AC-060: Webhook ERP com HMAC invalido**
Given um request chega no endpoint de webhook sem header `X-Webhook-Signature` ou com assinatura invalida,
When o sistema valida o HMAC,
Then retorna HTTP 401 "Assinatura invalida",
And registra o evento como tentativa de fraude no log de seguranca.

**AC-061: Arquivo com 100.000 linhas**
Given um arquivo CSV com exatamente 100.000 linhas validas,
When o usuario faz upload,
Then o sistema aceita e processa de forma assincrona,
And envia notificacao ao tenant com resumo ao finalizar.

**AC-062: Arquivo com mais de 100.000 linhas**
Given um arquivo CSV com 100.001 linhas,
When o usuario tenta fazer upload,
Then o sistema retorna HTTP 413 com mensagem "Arquivo excede o limite de 100.000 linhas. Divida o arquivo em partes menores."
And nenhum dado e persistido.

**AC-063: Encoding ISO-8859-1 detectado automaticamente**
Given um arquivo CSV encodado em ISO-8859-1 com caracteres acentuados (ex: "Joao", "financas"),
When o sistema processa o arquivo,
Then detecta o encoding automaticamente, converte para UTF-8,
And os nomes e descricoes sao armazenados corretamente sem caracteres corrompidos.

**AC-064: CSV com separador ponto-e-virgula**
Given um arquivo CSV usando ponto-e-virgula como separador (padrao comum em planilhas brasileiras),
When o sistema processa o arquivo,
Then detecta o separador automaticamente,
And parseia todas as colunas corretamente.

**AC-065: Upload interrompido**
Given o usuario inicia upload de um arquivo e a conexao cai no meio da transferencia,
When o job e criado mas o arquivo esta incompleto ou corrompido,
Then o job falha com status `failed` e motivo "Arquivo incompleto ou corrompido",
And nenhum dado parcial e persistido no banco (transacao atomica).

**AC-066: Preview (dry run) antes de confirmar**
Given o usuario faz upload de arquivo CSV com 500 linhas,
When solicita preview,
Then o sistema exibe as primeiras 10 linhas parseadas com campos mapeados e indicacao de erros,
And nenhum dado e persistido ate o usuario confirmar o import.

**AC-067: Import ja em andamento**
Given ja existe um job de import ativo (status `processing`) para o tenant,
When o tenant tenta iniciar novo import,
Then o sistema retorna HTTP 409 com mensagem "Ja existe um import em andamento. Aguarde a conclusao."
