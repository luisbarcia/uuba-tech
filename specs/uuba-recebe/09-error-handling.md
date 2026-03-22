# UUBA Recebe — Error Handling

| Error Condition | HTTP Code | User Message | Acao do Sistema |
|-----------------|-----------|--------------|-----------------|
| Input invalido | 400 | "Dados invalidos: {campo} {motivo}" | Log + retornar detalhes de validacao |
| API key invalida | 401 | "Chave de API invalida" | Log + rate limit por IP |
| Webhook sem HMAC valido | 401 | "Assinatura invalida" | Log como tentativa de fraude, alerta seguranca |
| Verificacao CPF falhou (portal) | 401 | "Verificacao falhou. Tente novamente." | Log + counter de tentativas, revogar token apos 5 falhas |
| Tenant nao encontrado | 403 | "Acesso negado" | Log + alerta seguranca |
| Tenant nao autorizado (RBAC) | 403 | "Permissao insuficiente para esta operacao" | Log com role atual e operacao tentada |
| Cliente/fatura nao encontrado | 404 | "{recurso} nao encontrado" | Log |
| Documento duplicado | 409 | "Documento ja cadastrado" | Log |
| Import ja em andamento | 409 | "Ja existe um import em andamento. Aguarde a conclusao." | Log + retornar job_id do import ativo |
| Arquivo de import invalido | 422 | "Arquivo invalido: {motivo}" | Log + relatorio de erros |
| Arquivo de import muito grande | 413 | "Arquivo excede o limite de 100.000 linhas" | Log + rejeitar sem processar |
| Rate limit excedido | 429 | "Limite de requisicoes excedido. Tente novamente em {N}s" | Log + header Retry-After |
| Limite de mensagens por devedor | 429 | "Limite de mensagens excedido para este devedor" | Enfileirar para proximo periodo permitido |
| Rate limit de links do portal | 429 | "Limite de solicitacoes atingido. Tente amanha." | Log + bloquear ate 00:00 UTC-3 |
| Erro interno do servidor | 500 | "Servico temporariamente indisponivel" | Log com stack trace, alerta critico |
| Database do tenant indisponivel | 500 | "Servico temporariamente indisponivel" | Alerta critico imediato, circuit breaker |
| Circuit breaker ativo | 503 | "Servico temporariamente indisponivel. Tente novamente em breve." | Header Retry-After: 60, log + fila de compensacao |
| Evolution API indisponivel | 503 | (interno -- nao exposto ao usuario) | Retry 3x com backoff, enfileirar, alerta |
| Conta Azul API timeout | 504 | (interno -- nao exposto ao usuario) | Retry 3x, fila de compensacao, alerta |
| Claude API timeout | 504 | (interno -- fallback para mensagem generica) | Retry 2x, enviar mensagem generica, log |
