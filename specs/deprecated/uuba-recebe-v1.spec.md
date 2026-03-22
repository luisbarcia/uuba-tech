# Feature: UUBA Recebe

## Overview

Plataforma de gestao de recebiveis e cobranca automatizada que combina IA conversacional, reguas de cobranca configuraveis e acionamento multicanal para recuperar credito com taxa de 50%+ — superando a media do mercado brasileiro (20-25%). O sistema opera em modo self-service, onde o cliente importa titulos vencidos e o UUBA Recebe executa todo o ciclo de cobranca ate a liquidacao.

**Inspiracoes globais:** TrueAccord (96% pagamentos sem humano), InDebted (7x engajamento vs tradicional), Symend (ciencia comportamental), AISphere/CollectiveAI (multi-agente IA generativa no Brasil).

**Usuarios-alvo:** PMEs (ate 50 func.), medias empresas (50-500), operacoes de cobranca dedicadas, e clientes Uuba atendidos via BPO. O produto atende todos os perfis com camadas de profundidade — do basico (importa e cobra) ao avancado (reguas complexas, analytics, scoring).

**Modelo:** Self-service (cliente configura e opera via dashboard).

**Multi-tenancy:** Database isolado por cliente (tenant).

---

## Benchmarking Global

| Plataforma | Pais | Metrica de destaque |
|------------|------|---------------------|
| TrueAccord | EUA | 96% pagamentos sem interacao humana; HeartBeat AI com 20M+ jornadas |
| InDebted | Australia | 7x mais engajamento que metodos tradicionais; 1.8B insights ML |
| Symend | Canada | 10x ROI; ciencia comportamental; 250M+ inadimplencias tratadas |
| Quadient AR | EUA/Franca | Previsao de pagamento 94% precisao; clientes pagam 34% mais rapido |
| Collectly | EUA | 75-300% aumento taxa coleta; 12.6 dias tempo medio |
| Prodigal | EUA | 500M+ interacoes para treino; QA automatizado 100% chamadas |
| Tesorio | EUA | Reducao media 33 dias no DSO; 300% produtividade |
| Peach Finance | EUA | API-first; 200+ variaveis de configuracao; promise-to-pay analytics |
| AISphere | Brasil | Multi-agente IA generativa; +18% acordos, -35% custos |

**Diferenciais UUBA Recebe vs mercado:**
1. IA conversacional com protocolo comportamental (nudge) — nao e chatbot generico
2. Setup em minutos — importou titulos, ja cobra
3. Resultado mensuravel — 50%+ recuperacao com dashboard de ROI
4. Multicanal inteligente — canal certo, hora certa, tom certo

---

## Modulo 1: Gestao de Clientes (Devedores)

### FR-001: Cadastro de clientes
When a empresa importa um novo devedor, the system shall criar um registro com nome, documento (CPF/CNPJ unico), email, e telefone WhatsApp.

### FR-002: Identificacao por telefone
When the bot recebe uma mensagem WhatsApp, the system shall identificar o cliente pelo numero de telefone em menos de 200ms.

### FR-003: Metricas por cliente
When um usuario consulta um cliente, the system shall exibir DSO (dias medios para pagamento), total em aberto, total vencido, e contagem de faturas.

### FR-004: Historico de interacoes
When um usuario abre o perfil de um cliente, the system shall exibir toda a timeline de cobrancas, conversas, promessas, e pagamentos ordenados cronologicamente.

### Acceptance Criteria

**AC-001: Cadastro com documento duplicado**
Given um cliente com CPF 123.456.789-00 ja existe,
When outro cadastro com o mesmo CPF e enviado,
Then the system shall retornar HTTP 409 com mensagem "Documento ja cadastrado".

**AC-002: Busca por telefone WhatsApp**
Given um cliente com telefone 5511999001234 esta cadastrado,
When uma mensagem WhatsApp chega desse numero,
Then the system shall retornar o cliente correto em menos de 200ms.

**AC-003: Metricas calculadas corretamente**
Given um cliente tem 5 faturas (3 pagas, 2 vencidas),
When as metricas sao consultadas,
Then DSO deve refletir a media de dias entre emissao e pagamento das 3 pagas,
And total_em_aberto deve somar as 2 vencidas,
And total_vencido deve somar apenas faturas com vencimento < hoje.

**Status:** Implementado (API v1 — 5 endpoints)

---

## Modulo 2: Gestao de Faturas (Recebiveis)

### FR-005: Registro de fatura
When a empresa registra uma fatura, the system shall armazenar valor (em centavos), moeda, vencimento, descricao, e numero da NF.

### FR-006: Maquina de estados da fatura
The fatura shall transicionar entre os estados: `pendente` → `vencido` (automatico por data) → `em_negociacao` → `acordo` → `pago` | `cancelado`.

### FR-007: Promessa de pagamento
When o bot registra uma promessa de pagamento, the system shall armazenar a data prometida e agendar follow-up automatico.

### FR-008: Link de pagamento
When uma fatura esta em aberto, the system shall gerar um link de pagamento (Pix/boleto via Conta Azul) e armazenar no campo `pagamento_link`.

### FR-009: Transicao automatica para vencido
Where a data atual ultrapassa o vencimento da fatura, the system shall alterar automaticamente o status para `vencido` via job agendado (cron).

### FR-010: Confirmacao de pagamento via webhook
When o Conta Azul envia um webhook de pagamento confirmado, the system shall atualizar status para `pago`, preencher `pago_em`, e disparar notificacao de agradecimento ao devedor.

### Acceptance Criteria

**AC-004: Fatura com valor zero**
Given um usuario tenta criar uma fatura com valor 0,
When o request e enviado,
Then the system shall retornar HTTP 422 com mensagem "Valor deve ser maior que zero".

**AC-005: Transicao automatica vencido**
Given uma fatura com vencimento 2026-03-20 e status `pendente`,
When o job de verificacao executa em 2026-03-21,
Then o status deve ser atualizado para `vencido`.

**AC-006: Pagamento via webhook**
Given uma fatura fat_abc123 com status `vencido`,
When o Conta Azul envia webhook `payment.confirmed` com referencia fat_abc123,
Then o status muda para `pago`, `pago_em` recebe timestamp UTC,
And o bot envia mensagem de agradecimento via WhatsApp ao devedor.

**Status:** Parcialmente implementado (CRUD ok, webhook e transicao automatica pendentes)

---

## Modulo 3: Regua de Cobranca

### FR-011: Reguas configuraveis por perfil
When a empresa configura a cobranca, the system shall permitir criar multiplas reguas com criterios: faixa de atraso (dias), faixa de valor, perfil de risco, e setor do devedor.

### FR-012: Sequencia de passos da regua
Each regua shall conter uma sequencia ordenada de passos, each com: dia relativo ao vencimento (D-3, D+1, D+7...), canal, tipo (lembrete/cobranca/follow_up/escalacao), tom (amigavel/neutro/firme/urgente), e template de mensagem.

### FR-013: Tom progressivo automatico
Where o devedor nao responde a cobranca, the system shall escalar o tom automaticamente conforme a regua: amigavel (D-3 a D+3) → neutro (D+4 a D+7) → firme (D+8 a D+12) → urgente (D+13 a D+15).

### FR-014: Execucao automatica da regua
The system shall executar a regua via cron, verificando faturas vencidas e disparando acoes conforme o passo atual da sequencia.

### FR-015: Pausa inteligente
Where o devedor esta em conversa ativa com o bot ou ja fez promessa de pagamento, the system shall pausar automaticamente a regua para aquela fatura.

### FR-016: Retomada automatica
Where uma promessa de pagamento expira sem confirmacao, the system shall retomar a regua automaticamente a partir do proximo passo.

### FR-017: Regua padrao
Where a empresa nao configurou regua customizada, the system shall aplicar uma regua padrao baseada no protocolo comportamental Uuba (D-3 a D+15, 4 niveis de tom).

### Acceptance Criteria

**AC-007: Regua com 5 passos executada corretamente**
Given uma regua configurada com passos em D-3, D+1, D+3, D+7, D+15,
When uma fatura vence e nenhum pagamento ou resposta e recebido,
Then the system shall enviar 5 mensagens nos dias corretos, escalando o tom.

**AC-008: Pausa por conversa ativa**
Given o devedor respondeu uma mensagem de cobranca ha menos de 24h,
When o cron tenta executar o proximo passo da regua,
Then a execucao deve ser pulada e o status da regua marcado como `conversa_ativa`.

**AC-009: Retomada apos promessa expirada**
Given o devedor prometeu pagar em 2026-03-25 e nao pagou,
When o sistema verifica em 2026-03-26,
Then a regua retoma do passo seguinte ao que estava quando pausou.

**Status:** Pendente (Sprint 5)

---

## Modulo 4: Bot IA Conversacional

### FR-018: Agente IA com protocolo comportamental
The bot shall operar com agente Claude (Sonnet) usando protocolo de cobranca comportamental (nudge), system prompt com regras de negocio, e tom adaptativo baseado no perfil e historico do devedor.

### FR-019: Tools do agente
The agent shall ter acesso a tools para: buscar faturas em aberto, buscar metricas do cliente, registrar promessa de pagamento, registrar cobranca realizada, e gerar link de pagamento.

### FR-020: Memoria de conversa
The system shall manter historico das ultimas 10 mensagens por telefone (buffer window) para contexto conversacional.

### FR-021: Identificacao de intencao
When o devedor envia uma mensagem, the agent shall classificar a intencao: pagamento, promessa, duvida, negociacao, reclamacao, saudacao, ou off-topic.

### FR-022: Respostas baseadas em dados
The agent shall responder SOMENTE com dados obtidos via tools (API). Nunca deve inventar valores, datas, ou informacoes financeiras.

### FR-023: Escalacao para humano
Where o devedor solicita parcelamento acima do limite, esta irritado (deteccao de sentimento), ou a situacao requer julgamento humano, the system shall encaminhar a conversa para um atendente via Chatwoot.

### FR-024: Negociacao semi-automatica
Where o devedor quer negociar desconto ou parcelamento, the agent shall propor opcoes dentro dos limites configurados (ex: max 10% desconto, max 3x parcelas). Acordos acima dos limites requerem aprovacao humana.

### FR-025: Verificacao de pagamento em tempo real
When o devedor diz "ja paguei" (Pix), the system shall verificar o pagamento em tempo real via API do gateway. Para boleto, informar prazo de 1-2 dias uteis e agendar follow-up.

### FR-026: Saudacao e identificacao
When um numero desconhecido envia mensagem, the system shall solicitar CNPJ/CPF para identificacao. When um numero conhecido envia saudacao, the system shall cumprimentar pelo nome e oferecer ajuda.

### FR-027: Deteccao de sentimento
The agent shall detectar sentimento negativo (raiva, frustacao) e ajustar tom para empático antes de escalar se necessario.

### Acceptance Criteria

**AC-010: Bot responde com dados reais**
Given o devedor pergunta "quanto devo?",
When o agent processa a mensagem,
Then deve chamar a tool de faturas e responder com valores exatos do banco de dados.

**AC-011: Promessa de pagamento registrada**
Given o devedor diz "vou pagar sexta-feira",
When o agent processa a mensagem,
Then deve registrar promessa com data calculada (proxima sexta-feira),
And agendar follow-up para o dia seguinte a data prometida.

**AC-012: Escalacao por desconto acima do limite**
Given o limite de desconto configurado e 10%,
When o devedor pede 20% de desconto,
Then o agent deve informar que precisa aprovacao e escalar para humano via Chatwoot.

**AC-013: Numero desconhecido**
Given o telefone 5511888887777 nao esta cadastrado,
When envia "oi" para o bot,
Then o bot responde: "Nao encontrei seu cadastro. Qual seu CPF ou CNPJ?"

**Status:** Parcialmente implementado (agente funcional, escalacao e negociacao pendentes)

---

## Modulo 5: Import de Titulos

### FR-028: Upload de planilha (CSV/Excel)
When a empresa faz upload de arquivo CSV ou Excel, the system shall parsear o arquivo, validar campos obrigatorios (nome, documento, valor, vencimento), e criar clientes + faturas em lote.

### FR-029: Mapeamento de colunas
When o formato da planilha nao corresponde ao layout padrao, the system shall apresentar interface de mapeamento de colunas para o usuario associar campos.

### FR-030: Validacao e relatorio de erros
Where o arquivo contem linhas invalidas (documento malformado, valor negativo, data invalida), the system shall processar as linhas validas e retornar relatorio detalhado das rejeitadas com motivo e numero da linha.

### FR-031: Import via API REST
The system shall expor endpoint `POST /api/v1/import/batch` que aceita array de faturas em JSON, criando clientes quando necessario (upsert por documento).

### FR-032: Import via webhook de ERP
When um ERP envia webhook de fatura vencida, the system shall processar automaticamente e inserir no fluxo de cobranca.

### FR-033: Deduplicacao
Where uma fatura com mesmo `numero_nf` + `cliente_id` ja existe, the system shall ignorar duplicata e registrar no log de import.

### Acceptance Criteria

**AC-014: Upload CSV com 1000 linhas**
Given um arquivo CSV com 1000 linhas, 950 validas e 50 invalidas,
When o usuario faz upload,
Then 950 faturas sao criadas, 50 rejeitadas,
And um relatorio de erros e retornado listando linha + motivo para cada rejeicao.

**AC-015: Deduplicacao por NF**
Given uma fatura NF-001 para cliente cli_abc ja existe,
When o usuario importa planilha contendo NF-001 para o mesmo cliente,
Then a linha e ignorada e o log registra "Duplicata: NF-001 ja existe para cli_abc".

**AC-016: Webhook ERP cria fatura automaticamente**
Given um ERP envia webhook com dados de fatura vencida,
When o webhook e recebido,
Then uma fatura e criada com status `vencido` e a regua de cobranca e ativada automaticamente.

**Status:** Nao implementado

---

## Modulo 6: Portal do Devedor

### FR-034: Acesso via link unico
When o devedor recebe uma mensagem de cobranca, the system shall incluir link unico (token JWT temporario) que abre o portal sem necessidade de login/senha.

### FR-035: Consulta de faturas
The portal shall exibir lista de faturas do devedor com: valor, vencimento, status, e dias de atraso.

### FR-036: Pagamento online
Where o devedor clica em "Pagar", the portal shall exibir opcoes de pagamento: Pix (QR code instantaneo) e boleto bancario.

### FR-037: Negociacao de acordo
Where a empresa habilitou negociacao no portal, the devedor shall poder solicitar parcelamento ou desconto dentro dos limites pre-configurados. Opcoes apresentadas automaticamente (ex: "Pague hoje com 5% de desconto" ou "Parcele em 3x sem juros").

### FR-038: Historico de acordos
The portal shall exibir historico de acordos anteriores, parcelas pagas, e comprovantes de pagamento.

### FR-039: Chat com atendente
Where o devedor precisa de atendimento humano, the portal shall oferecer chat integrado ao Chatwoot para conversar com a equipe.

### FR-040: Responsividade mobile
The portal shall ser totalmente responsivo (mobile-first) pois a maioria dos acessos vira via link no WhatsApp.

### Acceptance Criteria

**AC-017: Acesso via link no WhatsApp**
Given o devedor recebe mensagem com link do portal,
When clica no link no celular,
Then o portal abre sem pedir login, mostrando suas faturas em aberto.

**AC-018: Pagamento Pix pelo portal**
Given o devedor esta no portal com fatura de R$ 500,00,
When clica em "Pagar com Pix",
Then um QR code e exibido com valor de R$ 500,00,
And apos pagamento confirmado, status atualiza em tempo real na tela.

**AC-019: Negociacao de desconto no portal**
Given a regra permite ate 10% de desconto para pagamento a vista,
When o devedor acessa fatura de R$ 1.000,00,
Then o portal exibe: "Pague hoje por R$ 900,00 (10% de desconto)".

**AC-020: Link expirado**
Given o token do link tem validade de 72h,
When o devedor acessa apos 72h,
Then o portal exibe mensagem "Link expirado" e opcao de solicitar novo link via WhatsApp.

**Status:** Nao implementado

---

## Modulo 7: Dashboard e Analytics

### FR-041: Visao geral de recuperacao
The dashboard shall exibir: taxa de recuperacao (%), valor recuperado no periodo, valor em aberto, e valor vencido — com filtros por periodo, segmento, e regua.

### FR-042: Aging report
The dashboard shall exibir aging report com faixas: 1-15 dias, 16-30 dias, 31-60 dias, 61-90 dias, 90+ dias — mostrando quantidade e valor por faixa.

### FR-043: DSO (Days Sales Outstanding)
The dashboard shall calcular e exibir DSO medio da carteira, com tendencia historica (grafico de linha mensal).

### FR-044: Performance por regua
Where multiplas reguas estao configuradas, the dashboard shall comparar taxa de resposta, taxa de acordo, e tempo medio de resolucao entre elas.

### FR-045: Performance por canal
The dashboard shall exibir metricas por canal: taxa de entrega, taxa de leitura, taxa de resposta, e taxa de conversao (pagamento) para WhatsApp (e futuros canais).

### FR-046: ROI da cobranca
The dashboard shall calcular ROI: (valor recuperado - custo operacional) / custo operacional. Incluir custo por mensagem enviada, custo de gateway, e hora de atendente humano.

### FR-047: Exportacao de relatorios
The dashboard shall permitir exportar dados em CSV e PDF para auditoria e apresentacao a gestao.

### FR-048: Alertas e notificacoes
Where a taxa de recuperacao cai abaixo do threshold configurado (ex: <30%), the system shall enviar alerta ao administrador via email e/ou WhatsApp.

### Acceptance Criteria

**AC-021: Dashboard carrega em menos de 3s**
Given uma carteira com 10.000 faturas,
When o usuario acessa o dashboard,
Then todos os indicadores carregam em menos de 3 segundos.

**AC-022: Aging report correto**
Given 100 faturas vencidas com distribuicao: 40 (1-15d), 30 (16-30d), 20 (31-60d), 10 (90+d),
When o aging report e renderizado,
Then os valores e quantidades por faixa devem corresponder exatamente.

**AC-023: ROI calculado corretamente**
Given R$ 100.000 recuperados, R$ 5.000 em custos (mensagens + gateway),
When o ROI e calculado,
Then deve exibir 1900% (19x retorno).

**Status:** Nao implementado

---

## Modulo 8: Scoring e Inteligencia Preditiva

### FR-049: Score de probabilidade de pagamento
The system shall calcular score 0-100 para cada devedor baseado em: historico de pagamentos, tempo de atraso, valor da divida, engajamento com mensagens (abriu, leu, respondeu), setor de atuacao, e dados comportamentais.

### FR-050: Recomendacao de melhor canal e horario
Based on historico de interacoes e dados agregados, the system shall sugerir: melhor canal (WhatsApp, email, SMS, voz), melhor dia da semana, e melhor horario para contato de cada devedor.

### FR-051: Segmentacao automatica
The system shall classificar devedores em clusters: "bom pagador atrasado" (paga mas atrasa), "recorrente" (atrasa sempre), "inadimplente cronico" (nunca paga), "novo" (sem historico), "negociador" (sempre pede desconto).

### FR-052: Score alimenta regua
Where o score de um devedor muda significativamente, the system shall ajustar automaticamente a regua: score alto → tom mais amigavel e menos frequencia; score baixo → escalacao mais rapida.

### FR-053: Modelo de ML iterativo
The system shall retreinar o modelo de scoring periodicamente (semanal) com novos dados de pagamentos e interacoes, melhorando precisao ao longo do tempo.

### FR-054: Explicabilidade do score
When o operador consulta o score de um devedor, the system shall exibir os principais fatores que contribuiram para aquele score (top 5 features).

### Acceptance Criteria

**AC-024: Score inicial para devedor novo**
Given um devedor sem historico,
When o score e calculado,
Then deve retornar score 50 (neutro) com explicacao "Sem historico — score padrao".

**AC-025: Score atualizado apos pagamento**
Given um devedor com score 30 (baixo),
When ele paga uma fatura vencida,
Then o score deve aumentar (ex: para 45) e o fator "Pagamento recente" aparecer na explicacao.

**AC-026: Recomendacao de horario**
Given um devedor que abriu 80% das mensagens WhatsApp enviadas entre 9-11h,
When a recomendacao e gerada,
Then deve sugerir "WhatsApp, terca a quinta, 9-11h" como melhor janela.

**Status:** Nao implementado

---

## Modulo 9: Compliance e Regulatorio

### FR-055: Horarios de contato
The system shall respeitar horarios permitidos para cobranca: segunda a sexta 8h-20h, sabados 8h-14h, nunca domingos ou feriados nacionais.

### FR-056: Limite de frequencia
The system shall limitar contatos a no maximo 1 mensagem por dia e 3 por semana por devedor, conforme regulamentacao.

### FR-057: Registro de consentimento (LGPD)
The system shall registrar consentimento do devedor para receber comunicacoes por cada canal, com timestamp e IP/device quando aplicavel.

### FR-058: Direito ao esquecimento
When o devedor solicita exclusao de seus dados (LGPD Art. 18), the system shall anonimizar dados pessoais mantendo apenas registros financeiros minimos necessarios por obrigacao legal.

### FR-059: Audit trail completo
Every interacao com o devedor (mensagem enviada, mensagem recebida, acordo, pagamento, escalacao) shall ser registrada com timestamp UTC, canal, conteudo, e agente responsavel (bot ou humano).

### FR-060: Exportacao de dados (LGPD)
When o devedor solicita portabilidade de dados, the system shall gerar arquivo JSON com todos os seus dados em ate 15 dias.

### FR-061: Conformidade CDC/BACEN
The system shall garantir: nao expor divida a terceiros, nao usar coacao ou ameaca, identificar claramente que e cobranca automatizada, e oferecer canal para contestacao.

### FR-062: Opt-out
When o devedor solicita nao ser mais contatado por um canal especifico, the system shall respeitar imediatamente e registrar a preferencia.

### Acceptance Criteria

**AC-027: Bloqueio fora de horario**
Given e domingo as 10h,
When a regua tenta enviar cobranca,
Then a mensagem e enfileirada para segunda-feira 8h.

**AC-028: Limite de frequencia**
Given o devedor ja recebeu 3 mensagens essa semana,
When a regua tenta enviar a 4a mensagem,
Then a mensagem e adiada para a proxima semana.

**AC-029: Audit trail completo**
Given uma cobranca foi enviada via WhatsApp,
When o operador consulta o historico,
Then deve ver: timestamp, canal "whatsapp", mensagem completa, tom "amigavel", agente "bot_claude", status "entregue".

**AC-030: Opt-out por canal**
Given o devedor responde "nao quero mais receber whatsapp",
When o bot processa a mensagem,
Then o canal WhatsApp e desativado para esse devedor,
And a regua continua nos demais canais disponiveis (quando implementados).

**Status:** Parcialmente implementado (horarios e frequencia no protocolo do bot, audit trail parcial)

---

## Modulo 10: Multi-tenancy e Isolamento

### FR-063: Database por cliente (tenant)
Each empresa-cliente da Uuba shall ter seu proprio banco de dados PostgreSQL isolado, garantindo separacao total de dados.

### FR-064: Provisionamento automatico
When uma nova empresa e cadastrada na plataforma, the system shall criar automaticamente: database, schema, tabelas, e credenciais de API.

### FR-065: Roteamento de tenant
When uma requisicao chega a API, the system shall identificar o tenant via API key e rotear para o database correto.

### FR-066: Numero WhatsApp por tenant
Each tenant shall ter seu proprio numero WhatsApp dedicado, gerenciado via Evolution API com instancia separada.

### Acceptance Criteria

**AC-031: Isolamento de dados**
Given tenant_a e tenant_b estao na mesma plataforma,
When tenant_a consulta clientes,
Then deve ver apenas seus proprios clientes, sem acesso aos dados de tenant_b.

**AC-032: Provisionamento de novo tenant**
Given um novo cliente contrata o UUBA Recebe,
When o admin cria o tenant,
Then em menos de 5 minutos: database criado, tabelas migradas, API key gerada, numero WhatsApp provisionado.

**Status:** Nao implementado (API atual e single-tenant)

---

## Non-Functional Requirements

### Performance
- API: < 200ms p95 para endpoints de leitura
- API: < 500ms p95 para endpoints de escrita
- Bot: < 3s entre receber mensagem e enviar resposta
- Dashboard: < 3s para carregar com ate 50.000 faturas
- Import: processar 10.000 linhas CSV em < 30s
- Score: calcular score individual em < 1s

### Security
- Autenticacao: API key por tenant (atual) + JWT para portal do devedor
- Dados sensíveis: CPF/CNPJ e dados financeiros criptografados at rest (AES-256)
- Comunicacao: TLS 1.3 em todas as conexoes
- API keys: rotacao obrigatoria a cada 90 dias
- Rate limiting: 100 req/min por API key

### Scalability
- Suportar ate 100 tenants simultaneos
- Ate 50.000 faturas por tenant
- Ate 10.000 mensagens WhatsApp/dia por tenant
- Auto-scaling horizontal para workers de regua e bot

### Reliability
- Uptime: 99.5% (API e bot)
- Mensagens de cobranca: at-least-once delivery com retry (3 tentativas)
- Webhook de pagamento: idempotente (processar mesmo webhook 2x sem efeito duplicado)
- Backup: diario automatico de cada database de tenant

### Observability
- Logs estruturados (JSON) com correlation_id por request
- Metricas: Prometheus/Grafana (latencia, throughput, erros, filas)
- Alertas: PagerDuty/email para erros criticos (bot down, webhook falhando, DB inacessivel)
- Tracing: OpenTelemetry para rastrear fluxo completo (webhook → bot → API → resposta)

---

## Error Handling

| Error Condition | HTTP Code | User Message | Acao do Sistema |
|-----------------|-----------|--------------|-----------------|
| Input invalido | 400 | "Dados invalidos: {campo} {motivo}" | Log + retornar detalhes |
| API key invalida | 401 | "Chave de API invalida" | Log + rate limit IP |
| Tenant nao encontrado | 403 | "Acesso negado" | Log + alerta seguranca |
| Cliente/fatura nao encontrado | 404 | "{recurso} nao encontrado" | Log |
| Documento duplicado | 409 | "Documento ja cadastrado" | Log |
| Arquivo de import invalido | 422 | "Arquivo invalido: {motivo}" | Log + relatorio de erros |
| Evolution API indisponivel | 503 | (interno) | Retry 3x com backoff, alerta |
| Conta Azul API timeout | 504 | (interno) | Retry 3x, fila de compensacao |
| Database do tenant indisponivel | 500 | "Servico temporariamente indisponivel" | Alerta critico imediato |
| Limite de mensagens atingido | 429 | "Limite de mensagens excedido" | Enfileirar para proximo periodo |

---

## Implementation TODO

### Backend — Infra & Multi-tenancy
- [ ] Implementar roteamento de tenant por API key
- [ ] Criar servico de provisionamento automatico de databases
- [ ] Migrar modelo atual para multi-tenant (database-per-tenant)
- [ ] Implementar migration runner por tenant
- [ ] Configurar backup automatico diario por tenant

### Backend — Regua de Cobranca
- [ ] Criar modelo `Regua` e `ReguaPasso` no banco
- [ ] Implementar CRUD de reguas via API
- [ ] Criar worker cron que verifica faturas vencidas
- [ ] Implementar logica de tom progressivo
- [ ] Implementar pausa inteligente (conversa ativa / promessa)
- [ ] Implementar retomada automatica apos promessa expirada
- [ ] Criar regua padrao (protocolo comportamental Uuba)

### Backend — Bot IA
- [ ] Implementar escalacao para Chatwoot
- [ ] Implementar negociacao semi-automatica (limites configuraveis)
- [ ] Adicionar tool: gerar link de pagamento
- [ ] Implementar verificacao de pagamento Pix em tempo real
- [ ] Implementar deteccao de sentimento
- [ ] Adicionar few-shot learning com exemplos aprovados
- [ ] Implementar tabelas agent_decisions e agent_prompts

### Backend — Import
- [ ] Criar endpoint `POST /api/v1/import/csv` com upload de arquivo
- [ ] Implementar parser CSV/Excel com mapeamento de colunas
- [ ] Implementar validacao em lote com relatorio de erros
- [ ] Criar endpoint `POST /api/v1/import/batch` (JSON)
- [ ] Implementar webhook receiver para ERPs
- [ ] Implementar deduplicacao por numero_nf + cliente_id

### Backend — Pagamento
- [ ] Integrar Conta Azul API (gerar boleto e Pix)
- [ ] Implementar webhook receiver para confirmacao de pagamento
- [ ] Garantir idempotencia no processamento de webhooks
- [ ] Implementar fila de compensacao para falhas de webhook

### Backend — Portal do Devedor
- [ ] Criar servico de geracao de links unicos (JWT temporario 72h)
- [ ] Implementar API publica do portal (sem API key, com JWT de devedor)
- [ ] Endpoints: listar faturas, detalhes fatura, gerar pagamento, solicitar negociacao
- [ ] Integrar chat com Chatwoot (widget embeddable)

### Backend — Dashboard & Analytics
- [ ] Criar servico de agregacao de metricas (materialized views ou cache)
- [ ] Implementar endpoint de dashboard com filtros
- [ ] Implementar aging report
- [ ] Implementar calculo de DSO com historico
- [ ] Implementar calculo de ROI
- [ ] Implementar comparativo de performance entre reguas
- [ ] Criar endpoint de exportacao CSV/PDF
- [ ] Implementar sistema de alertas (threshold configuravel)

### Backend — Scoring & ML
- [ ] Definir feature set para modelo de scoring
- [ ] Implementar pipeline de feature engineering
- [ ] Treinar modelo baseline (logistic regression ou gradient boosting)
- [ ] Criar endpoint `GET /api/v1/clientes/{id}/score`
- [ ] Implementar recomendacao de canal + horario
- [ ] Implementar segmentacao automatica (clustering)
- [ ] Criar job de retreino semanal
- [ ] Implementar explicabilidade (SHAP ou feature importance)

### Backend — Compliance
- [ ] Implementar verificacao de horarios e feriados nacionais
- [ ] Implementar rate limiter por devedor (1/dia, 3/semana)
- [ ] Criar sistema de consentimento por canal
- [ ] Implementar endpoint de anonimizacao (LGPD)
- [ ] Implementar exportacao de dados do devedor (LGPD portabilidade)
- [ ] Implementar opt-out por canal
- [ ] Garantir audit trail completo em todas as interacoes

### Frontend — Portal do Devedor
- [ ] Criar SPA mobile-first com React/Next.js
- [ ] Tela de faturas em aberto
- [ ] Tela de pagamento (QR code Pix + boleto)
- [ ] Tela de negociacao (opcoes de desconto/parcelamento)
- [ ] Tela de historico de acordos e comprovantes
- [ ] Widget de chat Chatwoot
- [ ] Tela de link expirado com opcao de renovacao

### Frontend — Dashboard (Admin)
- [ ] Criar dashboard com graficos (Recharts ou similar)
- [ ] Visao geral: taxa recuperacao, valor recuperado, valor em aberto
- [ ] Aging report visual (barras empilhadas)
- [ ] Grafico DSO tendencia (linha mensal)
- [ ] Comparativo de reguas (tabela + grafico)
- [ ] Performance por canal
- [ ] ROI calculator
- [ ] Exportacao CSV/PDF
- [ ] Configuracao de alertas

### Testing
- [ ] Testes unitarios para scoring (modelo + features)
- [ ] Testes de integracao para regua de cobranca (cron + envio + pausa)
- [ ] Testes de integracao para webhook de pagamento (idempotencia)
- [ ] Testes e2e: fluxo completo cobranca → conversa → pagamento → confirmacao
- [ ] Testes de carga: 10.000 faturas processadas pela regua
- [ ] Testes de seguranca: isolamento multi-tenant
- [ ] Testes LGPD: anonimizacao e exportacao

---

## Out of Scope (v1)

- **Canais alem do WhatsApp** — Email, SMS, e voz serao adicionados em versoes futuras
- **Integracao nativa com ERPs especificos** — MVP usa import CSV/API; integracoes nativas (Omie, Bling, SAP) vem depois
- **Cobranca juridica** — protestos, negativacao SPC/Serasa, acoes judiciais
- **White-label completo** — branding customizado do portal por tenant (futuro, alinha com UUBA Parceiros)
- **App mobile nativo** — portal web responsivo e suficiente para v1
- **Voicebot** — chamadas automatizadas com IA de voz (referencia: Collectly Billie)
- **Integracao bancaria direta** — Open Banking/Open Finance para reconciliacao automatica

---

## Open Questions

- [ ] **[Produto]** Conta Azul suporta geracao de Pix QR code via API ou precisa de gateway adicional?
- [ ] **[Produto]** Qual o limite de mensagens/dia do Evolution API por instancia WhatsApp? (risco de ban)
- [ ] **[Tecnico]** Qual threshold de score para alterar regua automaticamente? (definir com dados reais)
- [ ] **[Legal]** Precisa de certificacao especifica para operar como empresa de cobranca no Brasil?
- [ ] **[Negocio]** Modelo de precificacao: por fatura cobrada, por mensagem enviada, % do valor recuperado, ou mensalidade fixa?
- [ ] **[Tecnico]** Evolution API vs Meta Cloud API oficial para WhatsApp em escala? (referencia: plano de migracao ja documentado)
- [ ] **[Produto]** Dashboard admin: aplicacao web separada ou integrada ao portal existente (uuba.tech/docs)?
- [ ] **[Infra]** Quantos tenants a VPS Contabo atual suporta antes de precisar escalar?

---

*Spec gerada em 2026-03-22 via Feature Forge Workshop*
*Baseada em: pagina de produto, bot-cobranca-mvp.md, API existente, e benchmarking global*
