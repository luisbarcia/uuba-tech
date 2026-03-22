# Modulo 5: Bot IA Conversacional

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
