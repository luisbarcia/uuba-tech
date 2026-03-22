# UUBA Recebe -- Spec v2 -- Parte 3: Modulos 6-10, NFRs e Secoes de Suporte

> Continuacao da Parte 2. Numeracao de FRs e ACs segue sequencia da parte anterior.
> Formato: EARS para Functional Requirements, Given/When/Then para Acceptance Criteria.

---

## Modulo 6: Import de Titulos (REESCRITO)

**Status:** Nao implementado

### Functional Requirements

**FR-[CONTINUAR_DE_PARTE_2]+1: Upload assincrono de planilha (CSV/Excel)**
When a empresa faz upload de arquivo CSV ou Excel, the system shall receber o arquivo, retornar HTTP 202 Accepted com `job_id`, e processar o arquivo de forma assincrona em background. O status do processamento deve ser consultado via `GET /api/v1/import/{job_id}`.

**FR-[CONTINUAR_DE_PARTE_2]+2: Mapeamento de colunas**
When o formato da planilha nao corresponde ao layout padrao, the system shall apresentar interface de mapeamento de colunas para o usuario associar campos do arquivo aos campos do sistema (nome, documento, valor, vencimento, numero_nf, descricao).

**FR-[CONTINUAR_DE_PARTE_2]+3: Validacao e relatorio de erros**
Where o arquivo contem linhas invalidas (documento malformado, valor negativo ou zero, data invalida, campos obrigatorios ausentes), the system shall processar as linhas validas e retornar relatorio detalhado das rejeitadas com motivo e numero da linha.

**FR-[CONTINUAR_DE_PARTE_2]+4: Import via API REST (batch)**
The system shall expor endpoint `POST /api/v1/import/batch` que aceita array de faturas em JSON, criando clientes quando necessario (upsert por documento). Para lotes com mais de 1.000 items, o endpoint deve retornar 202 Accepted com `job_id` e processar de forma assincrona.

**FR-[CONTINUAR_DE_PARTE_2]+5: Import via webhook de ERP**
When um ERP envia webhook de fatura vencida, the system shall validar a assinatura HMAC-SHA256 do payload (header `X-Webhook-Signature`), processar automaticamente, e inserir no fluxo de cobranca. O schema generico do webhook deve aceitar campos: `evento` (fatura.criada, fatura.vencida, fatura.cancelada), `dados` (objeto com campos da fatura), `timestamp`, e `hmac_signature`.

**FR-[CONTINUAR_DE_PARTE_2]+6: Deduplicacao**
Where uma fatura com mesmo `numero_nf` + `cliente_id` ja existe no sistema, the system shall ignorar a duplicata e registrar no log de import com motivo "duplicata".

**FR-[CONTINUAR_DE_PARTE_2]+7: Deteccao automatica de encoding e separador**
When o sistema recebe um arquivo CSV, the system shall detectar automaticamente o encoding (UTF-8 ou ISO-8859-1) e o separador (virgula, ponto-e-virgula, ou tab), convertendo para UTF-8 internamente antes do processamento.

**FR-[CONTINUAR_DE_PARTE_2]+8: Limite de arquivo**
Where o arquivo de import contem mais de 100.000 linhas, the system shall rejeitar o upload com HTTP 413 e mensagem "Arquivo excede o limite de 100.000 linhas. Divida o arquivo em partes menores."

**FR-[CONTINUAR_DE_PARTE_2]+9: Preview de import (dry run)**
When a empresa solicita preview antes de confirmar o import, the system shall parsear e exibir as primeiras 10 linhas do arquivo ja mapeadas nos campos do sistema, incluindo indicacao de erros de validacao, sem persistir nenhum dado. O usuario deve confirmar para iniciar o processamento real.

**FR-[CONTINUAR_DE_PARTE_2]+10: Notificacao de conclusao de import**
When um job de import finaliza (sucesso ou falha parcial), the system shall enviar notificacao ao tenant com resumo: quantidade de faturas criadas, quantidade rejeitada com motivos agregados, quantidade de duplicatas ignoradas, e tempo total de processamento.

**FR-[CONTINUAR_DE_PARTE_2]+11: Import recorrente via ERP (futuro)**
Where o tenant configura conexao com ERP, the system shall sincronizar automaticamente novas faturas em intervalos configuraveis (minimo 1h). Este FR esta planejado para versao futura e nao sera implementado no v1.

**FR-[CONTINUAR_DE_PARTE_2]+12: Status do job de import**
The system shall expor endpoint `GET /api/v1/import/{job_id}` que retorna o status atual do job: `pending`, `processing` (com percentual de progresso), `completed` (com resumo), ou `failed` (com motivo do erro). O endpoint deve incluir campos: `status`, `progress_percent`, `total_lines`, `processed_lines`, `created_count`, `rejected_count`, `duplicate_count`, `errors` (array com detalhes), e `completed_at`.

### Acceptance Criteria

**AC-[CONTINUAR_DE_PARTE_2]+1: Upload CSV com 1.000 linhas**
Given um arquivo CSV com 1.000 linhas, 950 validas e 50 invalidas,
When o usuario faz upload,
Then o sistema retorna HTTP 202 com job_id,
And ao consultar o status apos processamento, 950 faturas foram criadas, 50 rejeitadas,
And o relatorio de erros lista linha e motivo para cada rejeicao.

**AC-[CONTINUAR_DE_PARTE_2]+2: Deduplicacao por NF**
Given uma fatura NF-001 para cliente cli_abc ja existe no sistema,
When o usuario importa planilha contendo NF-001 para o mesmo cliente,
Then a linha e ignorada,
And o resumo do job registra 1 duplicata com referencia "NF-001 / cli_abc".

**AC-[CONTINUAR_DE_PARTE_2]+3: Webhook ERP com HMAC valido**
Given um ERP configurado com shared secret "s3cr3t" envia webhook com payload assinado via HMAC-SHA256,
When o webhook e recebido e a assinatura e valida,
Then a fatura e criada com status correspondente ao evento,
And a regua de cobranca e ativada automaticamente se o status for `vencido`.

**AC-[CONTINUAR_DE_PARTE_2]+4: Webhook ERP com HMAC invalido**
Given um request chega no endpoint de webhook sem header `X-Webhook-Signature` ou com assinatura invalida,
When o sistema valida o HMAC,
Then retorna HTTP 401 "Assinatura invalida",
And registra o evento como tentativa de fraude no log de seguranca.

**AC-[CONTINUAR_DE_PARTE_2]+5: Arquivo com 100.000 linhas**
Given um arquivo CSV com exatamente 100.000 linhas validas,
When o usuario faz upload,
Then o sistema aceita e processa de forma assincrona,
And envia notificacao ao tenant com resumo ao finalizar.

**AC-[CONTINUAR_DE_PARTE_2]+6: Arquivo com mais de 100.000 linhas**
Given um arquivo CSV com 100.001 linhas,
When o usuario tenta fazer upload,
Then o sistema retorna HTTP 413 com mensagem "Arquivo excede o limite de 100.000 linhas. Divida o arquivo em partes menores."
And nenhum dado e persistido.

**AC-[CONTINUAR_DE_PARTE_2]+7: Encoding ISO-8859-1 detectado automaticamente**
Given um arquivo CSV encodado em ISO-8859-1 com caracteres acentuados (ex: "Joao", "financas"),
When o sistema processa o arquivo,
Then detecta o encoding automaticamente, converte para UTF-8,
And os nomes e descricoes sao armazenados corretamente sem caracteres corrompidos.

**AC-[CONTINUAR_DE_PARTE_2]+8: CSV com separador ponto-e-virgula**
Given um arquivo CSV usando ponto-e-virgula como separador (padrao comum em planilhas brasileiras),
When o sistema processa o arquivo,
Then detecta o separador automaticamente,
And parseia todas as colunas corretamente.

**AC-[CONTINUAR_DE_PARTE_2]+9: Upload interrompido**
Given o usuario inicia upload de um arquivo e a conexao cai no meio da transferencia,
When o job e criado mas o arquivo esta incompleto ou corrompido,
Then o job falha com status `failed` e motivo "Arquivo incompleto ou corrompido",
And nenhum dado parcial e persistido no banco (transacao atomica).

**AC-[CONTINUAR_DE_PARTE_2]+10: Preview (dry run) antes de confirmar**
Given o usuario faz upload de arquivo CSV com 500 linhas,
When solicita preview,
Then o sistema exibe as primeiras 10 linhas parseadas com campos mapeados e indicacao de erros,
And nenhum dado e persistido ate o usuario confirmar o import.

**AC-[CONTINUAR_DE_PARTE_2]+11: Import ja em andamento**
Given ja existe um job de import ativo (status `processing`) para o tenant,
When o tenant tenta iniciar novo import,
Then o sistema retorna HTTP 409 com mensagem "Ja existe um import em andamento. Aguarde a conclusao."

---

## Modulo 7: Portal do Devedor

**Status:** Nao implementado

### Functional Requirements

**FR-[CONTINUAR_DE_PARTE_2]+13: Acesso via link unico com JWT RS256**
When o devedor recebe uma mensagem de cobranca, the system shall incluir link unico contendo token JWT assinado com RS256 (chave assimetrica). O token deve conter: `devedor_id`, `tenant_id`, `exp` (72h), e `iat`. O sistema deve expor endpoint de revogacao `POST /api/v1/portal/tokens/revoke` que adiciona o token a uma blacklist (Redis com TTL igual ao tempo restante de expiracao).

**FR-[CONTINUAR_DE_PARTE_2]+14: Verificacao secundaria no primeiro acesso**
When o devedor acessa o portal pela primeira vez com um token valido, the system shall solicitar os ultimos 4 digitos do CPF como verificacao secundaria antes de exibir qualquer dado financeiro. Apos verificacao bem-sucedida, o sistema emite cookie de sessao para acessos subsequentes com o mesmo token.

**FR-[CONTINUAR_DE_PARTE_2]+15: Consulta de faturas**
The portal shall exibir lista de faturas do devedor com: valor, vencimento, status, dias de atraso, e opcoes de acao (pagar, negociar).

**FR-[CONTINUAR_DE_PARTE_2]+16: Pagamento online (Pix e boleto)**
Where o devedor clica em "Pagar", the portal shall exibir opcoes de pagamento: Pix (QR code com validade de 30 minutos) e boleto bancario (via Conta Azul).

**FR-[CONTINUAR_DE_PARTE_2]+17: Regeneracao automatica de QR code Pix**
Where o QR code Pix expirou (30 minutos), the portal shall detectar a expiracao e gerar automaticamente um novo QR code sem necessidade de acao do devedor, exibindo mensagem "QR code atualizado".

**FR-[CONTINUAR_DE_PARTE_2]+18: Negociacao de acordo**
Where a empresa habilitou negociacao no portal, the devedor shall poder solicitar parcelamento ou desconto dentro dos limites pre-configurados. Opcoes apresentadas automaticamente (ex: "Pague hoje com 5% de desconto" ou "Parcele em 3x sem juros").

**FR-[CONTINUAR_DE_PARTE_2]+19: Historico de acordos**
The portal shall exibir historico de acordos anteriores, parcelas pagas, e comprovantes de pagamento.

**FR-[CONTINUAR_DE_PARTE_2]+20: Chat com atendente**
Where o devedor precisa de atendimento humano, the portal shall oferecer chat integrado ao Chatwoot para conversar com a equipe de cobranca.

**FR-[CONTINUAR_DE_PARTE_2]+21: Responsividade mobile-first**
The portal shall ser totalmente responsivo (mobile-first) pois a maioria dos acessos vira via link no WhatsApp em dispositivos moveis.

**FR-[CONTINUAR_DE_PARTE_2]+22: Solicitacao de novo link quando expirado**
Where o token JWT expirou, the portal shall exibir mensagem "Link expirado" e opcao de solicitar novo link. Ao solicitar, o sistema envia novo link via WhatsApp para o numero cadastrado do devedor.

**FR-[CONTINUAR_DE_PARTE_2]+23: Rate limit para re-geracao de links**
The system shall limitar a re-geracao de links do portal a no maximo 3 por dia por devedor. Apos atingir o limite, exibir mensagem "Limite de solicitacoes atingido. Tente novamente amanha ou entre em contato pelo WhatsApp."

**FR-[CONTINUAR_DE_PARTE_2]+24: Roteamento multi-tenant no portal**
When o devedor acessa o portal, the system shall identificar o tenant via `tenant_id` embutido no JWT e rotear para os dados corretos, aplicando branding basico do tenant (logo e nome da empresa).

**FR-[CONTINUAR_DE_PARTE_2]+25: Seguranca do portal (CSP, HSTS, anti-phishing)**
The portal shall implementar: Content Security Policy (CSP) restritivo, HTTP Strict Transport Security (HSTS) com max-age de 1 ano, X-Content-Type-Options: nosniff, X-Frame-Options: DENY, e Referrer-Policy: strict-origin-when-cross-origin.

**FR-[CONTINUAR_DE_PARTE_2]+26: Fallback HTML basico**
Where o browser do devedor nao suporta JavaScript moderno (ES2015+), the portal shall renderizar versao HTML basica server-side com funcionalidades essenciais: visualizar faturas, copiar codigo Pix, e acessar link de boleto.

### Acceptance Criteria

**AC-[CONTINUAR_DE_PARTE_2]+12: Acesso via link no WhatsApp**
Given o devedor recebe mensagem com link do portal contendo JWT valido,
When clica no link no celular,
Then o portal solicita os ultimos 4 digitos do CPF,
And apos verificacao correta, exibe suas faturas em aberto.

**AC-[CONTINUAR_DE_PARTE_2]+13: Verificacao CPF bloqueia acesso indevido**
Given um link do portal e compartilhado com terceiro que nao conhece o CPF do devedor,
When o terceiro tenta acessar e insere digitos incorretos do CPF,
Then o portal exibe "Verificacao falhou" e nao exibe dados financeiros,
And apos 5 tentativas incorretas, o token e revogado automaticamente.

**AC-[CONTINUAR_DE_PARTE_2]+14: Pagamento Pix pelo portal**
Given o devedor esta no portal com fatura de R$ 500,00,
When clica em "Pagar com Pix",
Then um QR code e exibido com valor de R$ 500,00 e validade de 30 minutos,
And apos pagamento confirmado via webhook, o status atualiza na tela.

**AC-[CONTINUAR_DE_PARTE_2]+15: QR code Pix expira antes do pagamento**
Given o devedor esta visualizando QR code Pix que expirou (30 minutos),
When o timer de expiracao e atingido,
Then o portal gera automaticamente novo QR code sem acao do devedor,
And exibe mensagem "QR code atualizado — escaneie novamente".

**AC-[CONTINUAR_DE_PARTE_2]+16: Negociacao de desconto no portal**
Given a regra permite ate 10% de desconto para pagamento a vista,
When o devedor acessa fatura de R$ 1.000,00,
Then o portal exibe: "Pague hoje por R$ 900,00 (10% de desconto)".

**AC-[CONTINUAR_DE_PARTE_2]+17: Link expirado com solicitacao de novo**
Given o token do link tem validade de 72h e o devedor acessa apos 72h,
When o portal detecta token expirado,
Then exibe mensagem "Link expirado" e botao "Solicitar novo link via WhatsApp",
And ao clicar, novo link e enviado para o numero cadastrado do devedor.

**AC-[CONTINUAR_DE_PARTE_2]+18: Devedor abre em dois dispositivos**
Given o devedor abre o portal em dois dispositivos simultaneamente (celular e computador),
When ambas as sessoes estao ativas,
Then ambas funcionam normalmente pois a sessao e stateless (JWT),
And operacoes de pagamento sao idempotentes (mesmo pagamento nao duplica).

**AC-[CONTINUAR_DE_PARTE_2]+19: Browser antigo sem JavaScript moderno**
Given o devedor acessa o portal com browser que nao suporta ES2015+,
When a pagina carrega,
Then renderiza versao HTML basica server-side,
And o devedor consegue visualizar faturas e copiar codigo Pix copia-e-cola.

**AC-[CONTINUAR_DE_PARTE_2]+20: Rate limit de re-geracao de links**
Given o devedor ja solicitou 3 novos links no mesmo dia,
When tenta solicitar o 4o link,
Then o sistema exibe "Limite de solicitacoes atingido. Tente novamente amanha ou entre em contato pelo WhatsApp."

---

## Modulo 8: Dashboard e Analytics

**Status:** Nao implementado

### Functional Requirements

**FR-[CONTINUAR_DE_PARTE_2]+27: Visao geral de recuperacao**
The dashboard shall exibir: taxa de recuperacao (%), valor recuperado no periodo, valor em aberto, e valor vencido -- com filtros por periodo, segmento, regua, e tenant (para admin global).

**FR-[CONTINUAR_DE_PARTE_2]+28: Aging report**
The dashboard shall exibir aging report com faixas: 1-15 dias, 16-30 dias, 31-60 dias, 61-90 dias, 90+ dias -- mostrando quantidade e valor por faixa.

**FR-[CONTINUAR_DE_PARTE_2]+29: DSO (Days Sales Outstanding)**
The dashboard shall calcular e exibir DSO medio da carteira, com tendencia historica (grafico de linha mensal) e comparativo com benchmark do setor quando disponivel.

**FR-[CONTINUAR_DE_PARTE_2]+30: Performance por regua**
Where multiplas reguas estao configuradas, the dashboard shall comparar taxa de resposta, taxa de acordo, tempo medio de resolucao, e valor recuperado entre elas.

**FR-[CONTINUAR_DE_PARTE_2]+31: Performance por canal**
The dashboard shall exibir metricas por canal: taxa de entrega, taxa de leitura, taxa de resposta, e taxa de conversao (pagamento) para WhatsApp (e futuros canais).

**FR-[CONTINUAR_DE_PARTE_2]+32: ROI da cobranca**
The dashboard shall calcular ROI: (valor recuperado - custo operacional) / custo operacional. Incluir custo por mensagem enviada, custo de gateway, e hora de atendente humano.

**FR-[CONTINUAR_DE_PARTE_2]+33: Exportacao de relatorios**
The dashboard shall permitir exportar dados em CSV e PDF para auditoria e apresentacao a gestao.

**FR-[CONTINUAR_DE_PARTE_2]+34: Alertas e notificacoes**
Where a taxa de recuperacao cai abaixo do threshold configurado (ex: <30%), the system shall enviar alerta ao administrador via email e/ou WhatsApp.

**FR-[CONTINUAR_DE_PARTE_2]+35: Promise-to-pay analytics**
The dashboard shall exibir analiticos de promessas de pagamento: taxa de cumprimento geral, taxa de cumprimento por segmento de devedor, taxa por dia da semana da promessa, valor medio das promessas cumpridas vs nao cumpridas, e tempo medio entre promessa e pagamento efetivo.

**FR-[CONTINUAR_DE_PARTE_2]+36: Dashboard de KPIs estrategicos**
The system shall oferecer dashboard de KPIs estrategicos (separado do operacional) com as seguintes metricas:
- **Lagging (mensal):** taxa de recuperacao, DSO medio, custo por real recuperado, ROI, taxa de acordo cumprido, churn de tenants.
- **Leading (semanal):** taxa de engajamento (respostas), taxa de leitura, taxa de clique em link de pagamento, taxa de promessa, taxa de escalacao humana, taxa de opt-out.
- **Produto (continuo):** time-to-first-collection, onboarding completion, bot accuracy, uptime.

**FR-[CONTINUAR_DE_PARTE_2]+37: Comparativo de A/B tests de reguas**
Where A/B tests de reguas estao ativos, the dashboard shall exibir comparativo de performance entre variantes: taxa de recuperacao, valor medio recuperado, tempo medio de resolucao, e intervalo de confianca estatistico (95%) para cada metrica.

**FR-[CONTINUAR_DE_PARTE_2]+38: Materialized views para performance**
The system shall utilizar materialized views no PostgreSQL (ou cache pre-computado em Redis) para todas as queries de dashboard, com refresh programado a cada 15 minutos para dados operacionais e a cada 1 hora para dados estrategicos.

### Acceptance Criteria

**AC-[CONTINUAR_DE_PARTE_2]+21: Dashboard carrega em menos de 3s com 50k faturas**
Given uma carteira com 50.000 faturas ativas,
When o usuario acessa o dashboard operacional,
Then todos os indicadores carregam em menos de 3 segundos,
And os dados refletem o ultimo refresh da materialized view (defasagem maxima de 15 minutos).

**AC-[CONTINUAR_DE_PARTE_2]+22: Aging report correto**
Given 100 faturas vencidas com distribuicao: 40 (1-15d), 30 (16-30d), 20 (31-60d), 10 (90+d),
When o aging report e renderizado,
Then os valores e quantidades por faixa correspondem exatamente.

**AC-[CONTINUAR_DE_PARTE_2]+23: ROI calculado corretamente**
Given R$ 100.000 recuperados, R$ 5.000 em custos (mensagens + gateway),
When o ROI e calculado,
Then deve exibir 1900% (19x retorno).

**AC-[CONTINUAR_DE_PARTE_2]+24: Promise-to-pay por segmento**
Given 200 promessas registradas no ultimo mes, sendo 120 de "bom pagador atrasado" e 80 de "recorrente",
When o analytics de promessas e consultado,
Then exibe taxa de cumprimento separada por segmento,
And exibe dia da semana com maior taxa de cumprimento.

**AC-[CONTINUAR_DE_PARTE_2]+25: A/B test comparativo**
Given regua A (controle, 500 faturas) e regua B (variante, 500 faturas) em A/B test,
When o comparativo e consultado,
Then exibe taxa de recuperacao de ambas com intervalo de confianca de 95%,
And indica se a diferenca e estatisticamente significativa.

---

## Modulo 9: Scoring e Inteligencia (REESCRITO)

**Status:** Nao implementado

> **Nota de arquitetura:** A v1 utiliza scoring heuristico com regras explicitas, NAO machine learning real. ML sera implementado na v2 quando o volume de dados for suficiente (>10.000 devedores com historico de pagamento).

### Functional Requirements

**FR-[CONTINUAR_DE_PARTE_2]+39: Score heuristico 0-100 com formula explicita**
The system shall calcular score de probabilidade de pagamento de 0 a 100 para cada devedor usando formula heuristica:

```
score = base(50)
      + historico_pagamento  (-20 a +20)
      + tempo_atraso          (-15 a +15)
      + engajamento           (-10 a +10)
      + valor_relativo        (-5 a +5)
```

Onde:
- `historico_pagamento`: razao entre faturas pagas e total de faturas, ponderada por recencia. Pagou tudo = +20, nunca pagou = -20.
- `tempo_atraso`: dias de atraso da fatura mais antiga em aberto. 0 dias = +15, 90+ dias = -15, interpolacao linear.
- `engajamento`: interacao com mensagens (abriu, leu, respondeu, clicou link). Respondeu e clicou = +10, ignorou tudo = -10.
- `valor_relativo`: valor total em aberto relativo a media do tenant. Abaixo da media = +5 (mais provavel pagar), acima = -5.

**FR-[CONTINUAR_DE_PARTE_2]+40: Recalculo por evento e batch diario**
The system shall recalcular o score do devedor em dois modos:
- **Por evento:** imediatamente apos eventos significativos (pagamento confirmado, resposta recebida, promessa registrada, promessa nao cumprida).
- **Batch diario:** job agendado que recalcula scores de todos os devedores ativos para incorporar mudancas passivas (tempo de atraso crescente, falta de engajamento).

**FR-[CONTINUAR_DE_PARTE_2]+41: Segmentacao automatica baseada em regras**
The system shall classificar cada devedor em exatamente um segmento com base em regras explicitas:
- **"bom pagador atrasado"**: score > 60 E tem historico de pelo menos 2 faturas pagas, mesmo que com atraso.
- **"recorrente"**: score entre 30 e 60 E padrao de atraso constante (media de atraso nos ultimos 3 meses > 10 dias).
- **"inadimplente cronico"**: score < 30 E nenhuma fatura paga nos ultimos 6 meses.
- **"novo"**: menos de 3 faturas registradas no sistema (sem historico suficiente).
- **"negociador"**: solicitou desconto ou parcelamento em pelo menos 50% das interacoes de cobranca.

A classificacao e recalculada junto com o score (por evento e batch diario).

**FR-[CONTINUAR_DE_PARTE_2]+42: Score alimenta regua**
Where o score de um devedor muda, the system shall ajustar o comportamento da regua:
- Score > 70: tom amigavel, frequencia menor, lembrete suave.
- Score 40-70: tom neutro a firme, frequencia padrao.
- Score < 40: escalacao rapida, encurtar intervalos entre passos, priorizar canal com maior engajamento.

**FR-[CONTINUAR_DE_PARTE_2]+43: Recomendacao de melhor horario (agregada)**
Based on dados agregados de todos os devedores do tenant (nao individual, pois o volume por devedor e insuficiente no v1), the system shall recomendar faixas de horario com maior taxa de leitura e resposta, agrupadas por dia da semana. A recomendacao deve ser atualizada semanalmente no batch diario.

**FR-[CONTINUAR_DE_PARTE_2]+44: Explicabilidade do score**
When o operador consulta o score de um devedor, the system shall exibir os top 3 fatores que mais contribuiram para aquele score, com nome do fator, valor numerico da contribuicao, e direcao (positivo ou negativo). Exemplo: "Historico de pagamento: +15 (pagou 4 de 5 faturas)".

**FR-[CONTINUAR_DE_PARTE_2]+45: Endpoint de score**
The system shall expor endpoint `GET /api/v1/clientes/{id}/score` que retorna: `score` (0-100), `segmento` (string), `fatores` (array de top 3), `horario_recomendado` (faixa), `updated_at` (timestamp do ultimo calculo).

### Acceptance Criteria

**AC-[CONTINUAR_DE_PARTE_2]+26: Score inicial para devedor novo**
Given um devedor sem historico (primeira fatura cadastrada),
When o score e calculado,
Then deve retornar score 50 (base) com segmento "novo",
And fator explicativo: "Sem historico -- score padrao".

**AC-[CONTINUAR_DE_PARTE_2]+27: Score sobe apos pagamento**
Given um devedor com score 35 e 3 faturas (1 paga, 2 vencidas),
When ele paga uma das faturas vencidas,
Then o score deve aumentar (recalculo imediato),
And o fator "Historico de pagamento" deve refletir a melhora (ex: de -10 para -3),
And o segmento deve ser reavaliado.

**AC-[CONTINUAR_DE_PARTE_2]+28: Score desce apos promessa nao cumprida**
Given um devedor com score 55 que prometeu pagar em 2026-03-25,
When o sistema verifica em 2026-03-26 que o pagamento nao foi realizado,
Then o score deve diminuir (engajamento negativo),
And o fator "Engajamento" deve refletir a queda.

**AC-[CONTINUAR_DE_PARTE_2]+29: Segmentacao correta por regras**
Given 5 devedores com os seguintes perfis:
- Devedor A: score 75, 5 faturas pagas de 6 totais,
- Devedor B: score 45, media de atraso 15 dias nos ultimos 3 meses,
- Devedor C: score 20, nenhuma fatura paga nos ultimos 6 meses,
- Devedor D: 2 faturas totais no sistema,
- Devedor E: score 50, pediu desconto em 3 de 4 interacoes,
When a segmentacao e executada,
Then Devedor A = "bom pagador atrasado", Devedor B = "recorrente", Devedor C = "inadimplente cronico", Devedor D = "novo", Devedor E = "negociador".

**AC-[CONTINUAR_DE_PARTE_2]+30: Recalculo em tempo aceitavel**
Given um evento de pagamento e registrado para um devedor,
When o recalculo por evento e disparado,
Then o novo score deve estar disponivel em menos de 500ms.

**AC-[CONTINUAR_DE_PARTE_2]+31: Explicabilidade com top 3 fatores**
Given um devedor com score 72,
When o operador consulta o endpoint de score,
Then a resposta inclui exatamente 3 fatores ordenados por magnitude absoluta de contribuicao,
And cada fator contem: nome, valor numerico, e direcao.

---

## Modulo 10: Resiliencia e Self-Healing (NOVO)

**Status:** Nao implementado

> **Nota de arquitetura:** Este modulo permeia todos os outros. Seus componentes devem ser implementados junto com cada modulo que depende de servicos externos ou processamento em background.

### Functional Requirements

**FR-[CONTINUAR_DE_PARTE_2]+46: Self-healing para falhas de envio**
When o envio de uma mensagem WhatsApp falha, the system shall classificar o erro como transiente (timeout, 5xx, connection reset) ou permanente (numero invalido, conta bloqueada, 4xx exceto 429), e aplicar estrategia diferenciada:
- **Transiente:** retry com exponential backoff (1s, 2s, 4s) ate 3 tentativas. Apos 3 falhas, enfileirar para reprocessamento manual.
- **Permanente:** nao fazer retry, marcar como falha permanente, notificar tenant.

**FR-[CONTINUAR_DE_PARTE_2]+47: Circuit breaker por servico externo**
The system shall implementar circuit breaker para cada servico externo (Evolution API, Conta Azul, Claude API, Chatwoot) com os seguintes parametros:
- **Threshold para abrir:** 5 ou mais falhas em janela de 5 minutos.
- **Estado aberto:** todas as chamadas sao enfileiradas (nao descartadas), alerta enviado ao admin.
- **Half-open:** apos 60 segundos, permitir 1 chamada de teste. Se sucesso, fechar. Se falha, reabrir por mais 60 segundos.
- **Estado fechado:** operacao normal.

**FR-[CONTINUAR_DE_PARTE_2]+48: Auto-recuperacao de regua travada**
Where o health check detecta uma regua sem nenhuma execucao ha mais de 24 horas (quando existem faturas elegiveis para processamento), the system shall:
1. Registrar alerta de "regua travada" no log.
2. Verificar status do worker responsavel.
3. Reiniciar o worker automaticamente.
4. Notificar admin com detalhes (tenant, regua, ultima execucao, faturas pendentes).

**FR-[CONTINUAR_DE_PARTE_2]+49: Evento interno para sincronizacao cross-module**
The system shall implementar mecanismo de eventos internos usando PostgreSQL LISTEN/NOTIFY (v1) com possibilidade de migracao para Redis Pub/Sub (v2). Eventos obrigatorios:
- `fatura_paga`: propaga para bot (parar cobranca ativa), dashboard (atualizar metricas), scoring (recalcular).
- `fatura_vencida`: propaga para regua (iniciar cobranca).
- `promessa_registrada`: propaga para regua (pausar), scoring (recalcular).
- `promessa_expirada`: propaga para regua (retomar), scoring (recalcular).
- `acordo_criado`: propaga para regua (ajustar), dashboard (atualizar).
- `opt_out`: propaga para regua (parar canal), bot (respeitar preferencia).

**FR-[CONTINUAR_DE_PARTE_2]+50: Health check endpoint**
The system shall expor endpoint `GET /health` que retorna status agregado e de cada servico:
```json
{
  "status": "healthy | degraded | unhealthy",
  "timestamp": "ISO-8601",
  "services": {
    "database": { "status": "up", "latency_ms": 5 },
    "redis": { "status": "up", "latency_ms": 2 },
    "evolution_api": { "status": "up", "latency_ms": 150 },
    "conta_azul": { "status": "up", "latency_ms": 200 },
    "claude_api": { "status": "degraded", "latency_ms": 4500 },
    "chatwoot": { "status": "up", "latency_ms": 100 }
  },
  "circuit_breakers": {
    "evolution_api": "closed",
    "conta_azul": "closed",
    "claude_api": "half-open",
    "chatwoot": "closed"
  }
}
```
Status geral: `healthy` se todos up, `degraded` se algum servico nao-critico degradado, `unhealthy` se servico critico down (database, redis).

**FR-[CONTINUAR_DE_PARTE_2]+51: Fallback para Claude API**
Where a Claude API esta indisponivel (circuit breaker aberto ou 3 timeouts consecutivos), the system shall enviar mensagem generica pre-aprovada ao devedor com link de pagamento e telefone para contato humano, em vez de deixar a conversa sem resposta. A mensagem generica deve ser configuravel por tenant.

### Acceptance Criteria

**AC-[CONTINUAR_DE_PARTE_2]+32: Evolution API cai por 10 minutos**
Given a Evolution API esta respondendo normalmente,
When a API fica indisponivel por 10 minutos,
Then apos 5 falhas em 5 minutos o circuit breaker abre,
And todas as mensagens pendentes sao enfileiradas (nao descartadas),
And quando a API volta, o circuit breaker entra em half-open,
And apos 1 chamada bem-sucedida, o circuit breaker fecha,
And todas as mensagens enfileiradas sao enviadas em ordem.

**AC-[CONTINUAR_DE_PARTE_2]+33: Claude API timeout**
Given o devedor envia mensagem e a Claude API nao responde em 10 segundos,
When o sistema faz retry 2 vezes (1s, 2s de backoff),
And na 3a falha consecutiva,
Then o sistema envia mensagem generica configurada pelo tenant ao devedor,
And registra o incidente no log com correlation_id.

**AC-[CONTINUAR_DE_PARTE_2]+34: Worker de regua morre**
Given o worker de regua de um tenant para de executar,
When o health check detecta ausencia de execucao por mais de 24h com faturas elegiveis,
Then o worker e reiniciado automaticamente em menos de 5 minutos,
And o admin recebe notificacao com detalhes do incidente.

**AC-[CONTINUAR_DE_PARTE_2]+35: Evento fatura_paga propaga corretamente**
Given uma fatura em cobranca ativa (regua em execucao, conversa aberta no bot),
When o webhook de pagamento confirma a fatura como paga,
Then o evento `fatura_paga` e emitido,
And o bot para de cobrar aquela fatura (se conversa ativa, envia agradecimento),
And o dashboard atualiza metricas na proxima janela de refresh,
And o score do devedor e recalculado em menos de 500ms.

**AC-[CONTINUAR_DE_PARTE_2]+36: Health check com servico degradado**
Given a Claude API esta respondendo com latencia acima de 5 segundos,
When o endpoint /health e consultado,
Then retorna status geral "degraded",
And o servico `claude_api` aparece com status "degraded" e latencia medida,
And os demais servicos aparecem com seus status reais.

---

## Non-Functional Requirements (REVISADOS)

### NFR-01: Performance

| Operacao | Meta p95 | Condicao | Observacao |
|----------|----------|----------|------------|
| API leitura | < 200ms | Qualquer endpoint GET | Cache Redis para tenant routing |
| API escrita | < 500ms | Qualquer endpoint POST/PUT/PATCH | Includes validacao e persistencia |
| Overhead tenant routing | < 10ms | Cache Redis obrigatorio, TTL 5min | Sem cache: ~50-100ms (inaceitavel) |
| Bot resposta simples | < 2s | Saudacao, FAQ, off-topic | Sem chamada a Claude necessaria |
| Bot resposta complexa | < 5s | Consulta faturas + Claude + tools | Claude + tools = 2-5s sozinho |
| Dashboard operacional | < 3s | Ate 50.000 faturas por tenant | REQUER materialized views |
| Dashboard estrategico | < 5s | Dados agregados cross-tenant | REQUER cache pre-computado |
| Import sincrono (preview) | < 5s | Primeiras 10 linhas para dry run | Sem persistencia |
| Import assincrono | < 30s para 10.000 linhas | Processamento em background | Notificacao ao finalizar |
| Score calculo individual | < 500ms | Recalculo por evento | Formula heuristica, sem ML |
| Score batch diario | < 10min | Todos devedores ativos do tenant | Job agendado off-peak |

### NFR-02: Security

| Requisito | Especificacao | Prioridade |
|-----------|---------------|------------|
| Auth API | API key por tenant + RBAC (admin, operador, viewer) | P0 |
| Auth portal | JWT RS256 com revogacao via blacklist (Redis) | P0 |
| Verificacao portal | Ultimos 4 digitos CPF no primeiro acesso | P0 |
| Webhook auth | Validacao HMAC-SHA256 obrigatoria antes de processar | P0 |
| Transporte | TLS 1.3 em todas as conexoes | P0 |
| Headers seguranca | HSTS (max-age 1 ano), CSP, X-Content-Type-Options, X-Frame-Options | P0 |
| Rate limiting leitura | 300 req/min por API key | P0 |
| Rate limiting escrita | 60 req/min por API key | P0 |
| Rate limiting import | 5 req/min por API key | P0 |
| Rate limiting delete | 10 req/min por API key | P0 |
| Rotacao API key | 90 dias, com periodo de graca de 7 dias (ambas chaves ativas) | P1 |
| Criptografia at rest (v1) | Full-disk encryption (Contabo VPS) | P0 |
| Criptografia at rest (v2) | Column-level encryption com blind index para CPF/CNPJ | P2 |
| Mascaramento logs | CPF (***.***.789-00), valores (R$ ***), telefone (****1234) | P0 |
| RBAC roles | admin: tudo; operador: operar + visualizar; viewer: somente leitura | P0 |

### NFR-03: Scalability

| Dimensao | Limite v1 | Estrategia |
|----------|-----------|------------|
| Tenants simultaneos | Ate 100 | Shared DB + tenant_id, PgBouncer |
| Faturas por tenant | Ate 50.000 | Indexes compostos com tenant_id |
| Mensagens WhatsApp/dia por tenant | Ate 10.000 | Fila Redis, workers horizontais |
| Devedores por tenant | Ate 20.000 | Derivado de faturas/devedor |
| Tamanho arquivo import | Ate 100.000 linhas | Processamento assincrono |
| Requisicoes API concorrentes | Ate 500/s agregado | Load balancer + connection pool |

### NFR-04: Reliability

| Requisito | Especificacao |
|-----------|---------------|
| Uptime | 99.5% (API e bot) -- ~3.6h downtime/mes permitido |
| Mensagens | At-least-once delivery com retry (3x exponential backoff) |
| Webhooks recebidos | Processamento idempotente (mesmo webhook 2x sem efeito duplicado) |
| Backup | Diario automatico do banco de dados |
| Circuit breaker | Por servico externo (Evolution, Conta Azul, Claude, Chatwoot) |
| Transacoes de import | Atomicas -- falha no meio nao persiste dados parciais |
| Eventos internos | At-least-once via PostgreSQL LISTEN/NOTIFY com fallback para polling |

### NFR-05: Observability

| Requisito | Especificacao |
|-----------|---------------|
| Logs | JSON estruturado com correlation_id por request |
| Metricas | Prometheus/Grafana (latencia, throughput, erros, tamanho de filas) |
| Alertas | Email + WhatsApp para erros criticos (bot down, webhook falhando, DB inacessivel, circuit breaker aberto) |
| Tracing | OpenTelemetry para rastrear fluxo completo (webhook -> bot -> API -> resposta) |
| Dashboards operacionais (infra) | Grafana com: CPU, memoria, disco, conexoes DB, filas Redis |
| Retencao de logs | 30 dias em disco, 90 dias em storage frio |

---

## Error Handling (ATUALIZADO)

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

---

## Mapa de Dependencias

```
Modulo 0 (Multi-tenancy) ---> BLOQUEIA TUDO
  |
  |---> Modulo 1 (Clientes/Devedores) ---> Modulo 2 (Faturas/Recebiveis)
  |       |                                   |
  |       |                                   |---> Modulo 3 (Pre-delinquency)
  |       |                                   |       [precisa de: faturas com vencimento futuro]
  |       |                                   |
  |       |                                   |---> Modulo 4 (Regua de Cobranca)
  |       |                                   |       [precisa de: faturas vencidas]
  |       |                                   |       [compliance embutido — nao e modulo separado]
  |       |                                   |       |
  |       |                                   |       |---> Modulo 5 (Bot IA Conversacional)
  |       |                                   |               [precisa de: regua + faturas + clientes]
  |       |                                   |
  |       |                                   |---> Modulo 7 (Portal do Devedor)
  |       |                                           [precisa de: faturas + integracao pagamento]
  |       |
  |       |---> Modulo 6 (Import de Titulos)
  |               [precisa de: clientes + faturas para criar/atualizar]
  |
  |---> Integracoes Externas
  |       |---> Conta Azul (pagamentos) ---> usado por Modulos 2, 4, 7
  |       |---> Evolution API (WhatsApp) ---> usado por Modulos 4, 5
  |       |---> Claude API (IA) ---> usado por Modulo 5
  |       |---> Chatwoot (atendimento) ---> usado por Modulos 5, 7
  |
  |---> Modulo 8 (Dashboard e Analytics)
  |       [precisa de: dados de todos os modulos — implementar apos Modulos 1-7]
  |
  |---> Modulo 9 (Scoring e Inteligencia)
  |       [precisa de: dados historicos — implementar apos ter volume de dados]
  |
  |---> Modulo 10 (Resiliencia e Self-Healing)
          [permeia todos — implementar componentes junto com cada modulo]
```

### Ordem recomendada de implementacao

1. **Fase 1 -- Fundacao:** Modulo 0 (Multi-tenancy) + Integracoes Externas (Conta Azul, Evolution API)
2. **Fase 2 -- Core:** Modulos 1 (Clientes) + 2 (Faturas) + 6 (Import)
3. **Fase 3 -- Cobranca:** Modulos 3 (Pre-delinquency) + 4 (Regua) + 5 (Bot IA)
4. **Fase 4 -- Devedor:** Modulo 7 (Portal do Devedor)
5. **Fase 5 -- Inteligencia:** Modulos 8 (Dashboard) + 9 (Scoring)
6. **Continuo:** Modulo 10 (Resiliencia) -- implementado incrementalmente em cada fase

---

## Integracoes Externas

| Servico | URL/Endpoint | Auth | Rate Limits | Fallback | Custo Estimado |
|---------|-------------|------|-------------|----------|----------------|
| Evolution API | wa.uuba.tech -- WebSocket + REST | API key por instancia | Sem rate limit formal (limitado por WhatsApp: ~80 msg/s) | Retry 3x com backoff, enfileirar, alertar admin | Gratuito (self-hosted) + custo VPS |
| Meta Cloud API (futuro) | graph.facebook.com/v21.0 -- REST | Token OAuth (System User) | 1.000 msg/s por WABA, 250 conversas/24h (Business-initiated tier 1) | Fallback para Evolution API | R$ 0,25-0,65 por conversa (template) |
| Conta Azul | api.contaazul.com -- REST | OAuth2 (access_token + refresh_token) | 60 req/min por aplicacao | Fila de compensacao, retry com backoff | Gratuito (API inclusa no plano) |
| Claude API (Anthropic) | api.anthropic.com -- REST | API key (x-api-key header) | TPM-based (varia por tier), ~60 req/min (tier 1) | Mensagem generica pre-aprovada ao devedor | ~US$ 3/1M input tokens, ~US$ 15/1M output tokens (Sonnet) |
| Chatwoot | chat.uuba.tech -- REST + WebSocket | API key (user_api_key ou platform_api_key) | Sem rate limit formal (self-hosted) | Fila de escalacao manual, notificacao via WhatsApp | Gratuito (self-hosted) + custo VPS |
| Whisper API (OpenAI) | api.openai.com/v1/audio/transcriptions -- REST | API key (Authorization: Bearer) | 50 req/min (tier 1) | Informar devedor para enviar texto, log do audio para processamento manual | US$ 0,006/min de audio |

### Notas sobre integracoes

- **Evolution API vs Meta Cloud API:** A v1 usa Evolution API (self-hosted, custo zero de mensagens). Para escala multi-tenant (100+ numeros), Meta Cloud API e mais viavel (unico Business Manager, sem 100 containers Docker). Decisao deve ser tomada antes da Fase 3.
- **Conta Azul:** Nao tem API de consulta de Pix em tempo real. Verificacao de pagamento vem exclusivamente via webhook. FR-025 (verificacao em tempo real) ajustado na Parte 2 para refletir essa limitacao.
- **Claude API:** Custo variavel conforme volume. Estimativa para 1.000 conversas/dia com media de 5 turnos: ~US$ 15-30/dia. Monitorar com metrica `custo_por_conversa`.

---

## Implementation TODO (ATUALIZADO)

### Modulo 0: Multi-tenancy e Isolamento [Fase 1]
- [ ] [L] Implementar modelo shared-DB com `tenant_id` em todas as tabelas
- [ ] [M] Criar middleware de roteamento de tenant por API key (cache Redis, TTL 5min)
- [ ] [L] Criar servico de provisionamento automatico de tenant (schema, credenciais, config)
- [ ] [M] Implementar RBAC: roles admin, operador, viewer com permissoes granulares
- [ ] [S] Implementar rotacao de API key com periodo de graca de 7 dias
- [ ] [M] Implementar migration runner por tenant (shared schema)
- [ ] [M] Configurar backup automatico diario
- [ ] [S] Configurar PgBouncer para connection pooling

### Modulo 1: Gestao de Clientes [Fase 2]
- [ ] [S] Adicionar `tenant_id` ao modelo de clientes (ja existe, adaptar)
- [ ] [S] Implementar upsert por documento (CPF/CNPJ) no escopo do tenant
- [ ] [S] Implementar mascaramento de CPF em logs
- [ ] [M] Implementar historico de interacoes (timeline)

### Modulo 2: Gestao de Faturas [Fase 2]
- [ ] [S] Adicionar `tenant_id` ao modelo de faturas (ja existe, adaptar)
- [ ] [M] Implementar maquina de estados completa (pendente -> vencido -> em_negociacao -> acordo -> pago | cancelado)
- [ ] [M] Implementar job cron de transicao automatica para vencido
- [ ] [M] Implementar webhook receiver Conta Azul com validacao HMAC e idempotencia
- [ ] [S] Implementar cancelamento de fatura (FR novo da Parte 2)
- [ ] [M] Implementar geracao de link de pagamento via Conta Azul

### Modulo 3: Pre-delinquency [Fase 3]
- [ ] [L] Implementar regua preventiva (D-30 a D-1)
- [ ] [M] Implementar motor de predicao de inadimplencia (heuristico)
- [ ] [M] Implementar desconto por antecipacao de pagamento
- [ ] [S] Implementar lembretes pre-vencimento configuraveis

### Modulo 4: Regua de Cobranca [Fase 3]
- [ ] [L] Criar modelo `Regua` e `ReguaPasso` com suporte multi-tenant
- [ ] [M] Implementar CRUD de reguas via API
- [ ] [L] Criar worker cron que verifica faturas vencidas e executa regua
- [ ] [M] Implementar tom progressivo automatico
- [ ] [M] Implementar pausa inteligente (conversa ativa, promessa)
- [ ] [M] Implementar retomada automatica apos promessa expirada
- [ ] [S] Criar regua padrao (protocolo comportamental Uuba)
- [ ] [M] Embutir compliance na regua: horarios (8h-20h seg-sex, 8h-14h sab), frequencia (1/dia, 3/sem), feriados
- [ ] [L] Implementar A/B testing de reguas com alocacao aleatoria e metricas
- [ ] [M] Implementar acao pos-regua (D+15 sem resposta)
- [ ] [M] Implementar gestao de parcelas (lembretes, acao em atraso)
- [ ] [M] Implementar renegociacao proativa (cooling period + nova proposta)
- [ ] [M] Implementar simulador de regua (dry run)

### Modulo 5: Bot IA Conversacional [Fase 3]
- [ ] [L] Adaptar agente para multi-tenant (system prompt por tenant, config por tenant)
- [ ] [M] Implementar escalacao para Chatwoot com resumo automatico (handoff)
- [ ] [M] Implementar negociacao semi-automatica (limites configuraveis por tenant)
- [ ] [S] Adicionar tool: gerar link de pagamento
- [ ] [M] Implementar verificacao de pagamento via webhook (nao polling)
- [ ] [M] Implementar deteccao de sentimento e ajuste de tom
- [ ] [S] Adicionar few-shot learning com exemplos aprovados
- [ ] [M] Implementar tabelas agent_decisions e agent_prompts
- [ ] [L] Implementar transcricao de audio via Whisper API
- [ ] [M] Implementar behavioral nudges configuraveis por tenant
- [ ] [M] Implementar confirmacao via comprovante (OCR basico)
- [ ] [S] Implementar webhook de eventos para tenant (cobranca.enviada, pagamento.recebido, etc.)

### Modulo 6: Import de Titulos [Fase 2]
- [ ] [L] Criar endpoint `POST /api/v1/import/csv` com upload assincrono (202 + job_id)
- [ ] [M] Implementar `GET /api/v1/import/{job_id}` para status do job
- [ ] [M] Implementar parser CSV com deteccao de encoding (UTF-8, ISO-8859-1) e separador (virgula, ponto-e-virgula, tab)
- [ ] [M] Implementar mapeamento de colunas (interface + API)
- [ ] [M] Implementar validacao em lote com relatorio de erros
- [ ] [M] Criar endpoint `POST /api/v1/import/batch` (JSON) com suporte assincrono para lotes grandes
- [ ] [M] Implementar webhook receiver para ERPs com validacao HMAC-SHA256
- [ ] [S] Implementar deduplicacao por numero_nf + cliente_id
- [ ] [S] Implementar limite de 100.000 linhas por arquivo
- [ ] [M] Implementar preview/dry run (primeiras 10 linhas)
- [ ] [S] Implementar notificacao de conclusao de import ao tenant

### Modulo 7: Portal do Devedor [Fase 4]
- [ ] [L] Criar SPA mobile-first com React/Next.js
- [ ] [M] Implementar geracao de JWT RS256 com tenant_id e devedor_id
- [ ] [M] Implementar endpoint de revogacao de token (blacklist Redis)
- [ ] [S] Implementar verificacao secundaria (ultimos 4 digitos CPF)
- [ ] [M] Tela de faturas em aberto
- [ ] [M] Tela de pagamento (QR code Pix com regeneracao automatica + boleto)
- [ ] [M] Tela de negociacao (opcoes de desconto/parcelamento)
- [ ] [S] Tela de historico de acordos e comprovantes
- [ ] [M] Widget de chat Chatwoot
- [ ] [S] Tela de link expirado com solicitacao de novo link
- [ ] [S] Implementar rate limit de re-geracao de links (3/dia)
- [ ] [M] Implementar headers de seguranca (CSP, HSTS, X-Frame-Options)
- [ ] [M] Implementar fallback HTML basico server-side

### Modulo 8: Dashboard e Analytics [Fase 5]
- [ ] [L] Criar materialized views para metricas de dashboard
- [ ] [M] Implementar refresh programado (15min operacional, 1h estrategico)
- [ ] [M] Implementar endpoint de dashboard operacional com filtros
- [ ] [M] Implementar aging report
- [ ] [M] Implementar calculo de DSO com historico
- [ ] [M] Implementar calculo de ROI
- [ ] [M] Implementar comparativo de performance entre reguas
- [ ] [M] Implementar promise-to-pay analytics
- [ ] [L] Implementar dashboard de KPIs estrategicos
- [ ] [M] Implementar comparativo de A/B tests com intervalo de confianca
- [ ] [M] Criar endpoint de exportacao CSV/PDF
- [ ] [S] Implementar sistema de alertas (threshold configuravel)

### Modulo 9: Scoring e Inteligencia [Fase 5]
- [ ] [M] Implementar formula heuristica de score (0-100)
- [ ] [M] Criar endpoint `GET /api/v1/clientes/{id}/score`
- [ ] [M] Implementar recalculo por evento (pagamento, resposta, promessa)
- [ ] [M] Implementar job batch diario de recalculo
- [ ] [M] Implementar segmentacao por regras (5 segmentos)
- [ ] [S] Implementar integracao score -> regua (tom e frequencia)
- [ ] [M] Implementar recomendacao de horario agregada
- [ ] [S] Implementar explicabilidade (top 3 fatores)

### Modulo 10: Resiliencia e Self-Healing [Continuo]
- [ ] [L] Implementar circuit breaker por servico externo
- [ ] [M] Implementar self-healing para falhas de envio (classificar transiente/permanente)
- [ ] [M] Implementar auto-recuperacao de regua travada
- [ ] [L] Implementar sistema de eventos internos (PostgreSQL LISTEN/NOTIFY)
- [ ] [S] Implementar endpoint /health com status de cada servico
- [ ] [M] Implementar fallback para Claude API (mensagem generica)

### Frontend -- Dashboard Admin [Fase 5]
- [ ] [L] Criar dashboard com graficos (Recharts ou similar)
- [ ] [M] Visao geral: taxa recuperacao, valor recuperado, valor em aberto
- [ ] [M] Aging report visual (barras empilhadas)
- [ ] [M] Grafico DSO tendencia (linha mensal)
- [ ] [M] Comparativo de reguas (tabela + grafico)
- [ ] [S] Performance por canal
- [ ] [S] ROI calculator
- [ ] [S] Exportacao CSV/PDF
- [ ] [S] Configuracao de alertas

### Testing [Todas as fases]
- [ ] [M] Testes unitarios para scoring (formula + segmentacao)
- [ ] [L] Testes de integracao para regua de cobranca (cron + envio + pausa + retomada)
- [ ] [M] Testes de integracao para webhook de pagamento (HMAC + idempotencia)
- [ ] [XL] Testes e2e: fluxo completo cobranca -> conversa -> pagamento -> confirmacao
- [ ] [L] Testes de carga: 50.000 faturas processadas pela regua
- [ ] [L] Testes de seguranca: isolamento multi-tenant (tenant A nao acessa dados de B)
- [ ] [M] Testes LGPD: anonimizacao e exportacao de dados
- [ ] [M] Testes de circuit breaker e self-healing
- [ ] [M] Testes de import assincrono (100k linhas, encoding, separador)

---

## Out of Scope (v1)

Os seguintes items estao explicitamente fora do escopo da v1 e planejados para versoes futuras:

| Item | Motivo | Versao planejada |
|------|--------|------------------|
| Canais alem do WhatsApp (email, SMS, voz) | Complexidade de integracao, WhatsApp e canal dominante no BR | v2 |
| Integracoes nativas com ERPs especificos (Omie, Bling, SAP) | MVP usa import CSV/API; integracao nativa requer parceria | v2 |
| Cobranca juridica (protestos, negativacao SPC/Serasa) | Requer parceria com bureaus e processos legais | v2/v3 |
| White-label completo (branding customizado por tenant) | Futuro com UUBA Parceiros; v1 tem branding basico (logo + nome) | v2 |
| App mobile nativo | Portal web responsivo e suficiente para v1 | v3 |
| Voicebot (chamadas com IA de voz) | Complexidade de infra + custo de telefonia | v3 |
| Open Banking/Open Finance | Regulamentacao ainda em evolucao, integracao custosa | v2/v3 |
| ML real para scoring | Requer >10k devedores com historico; v1 usa heuristico | v2 |
| Multi-idioma | 100% dos clientes v1 sao brasileiros | v3 |
| DB-per-tenant | Shared DB com tenant_id e suficiente para 100 tenants; DB-per-tenant escala melhor para 500+ | v2/v3 |
| Import recorrente via ERP (sync automatico) | Depende de integracao nativa com ERPs | v2 |
| Resposta em audio (TTS) | Transcricao (receber) e prioridade; gerar audio e futuro | v2 |

---

## Open Questions (ATUALIZADO)

### Tecnico

- [ ] **[Tecnico]** Evolution API vs Meta Cloud API para escala multi-tenant? Evolution e gratuita mas requer 1 container por numero. Meta Cloud suporta multiplos numeros em unico Business Manager. Decisao impacta arquitetura da Fase 3.
- [ ] **[Tecnico]** VPS Contabo atual suporta quantos tenants antes de precisar escalar? Fazer benchmark com 5, 10, 20 tenants simulados. Metricas: CPU, memoria, latencia, IOPS.
- [ ] **[Tecnico]** Whisper API (OpenAI) vs alternativa on-premise (faster-whisper) para transcricao de audio? Whisper API e mais simples mas tem custo por minuto e latencia de rede. On-premise requer GPU ou CPU potente.
- [ ] **[Tecnico]** Qual threshold de score para alterar regua automaticamente? Definir com dados reais apos ter pelo menos 1.000 devedores com historico.
- [ ] **[Tecnico]** PostgreSQL LISTEN/NOTIFY e suficiente para volume de eventos esperado (100 tenants x 10k msg/dia)? Ou Redis Pub/Sub desde o inicio?
- [ ] **[Tecnico]** Estrategia de versionamento de API (path /v1/ vs header)? Impacta todos os endpoints.

### Produto

- [ ] **[Produto]** Dashboard admin: aplicacao web separada ou integrada ao portal existente (uuba.tech/docs)?
- [ ] **[Produto]** Templates de regua por industria -- quais industrias priorizar? Sugestao: servicos recorrentes (academia, coworking), saude (clinicas), educacao (escolas).
- [ ] **[Produto]** Onboarding wizard: quais passos sao obrigatorios vs opcionais? Impacta time-to-first-collection.
- [ ] **[Produto]** Mecanica de parcelamento: gera novas faturas filhas? Aplica juros? Qual formula?

### Legal

- [ ] **[Legal]** Certificacao para operar como empresa de cobranca no Brasil? Verificar requisitos com advogado trabalhista/empresarial.
- [ ] **[Legal]** Limites de frequencia de contato variam por estado ou sao nacionais? CDC nao especifica quantidade, apenas "boas praticas".
- [ ] **[Legal]** Armazenamento de audio de devedor (LGPD): necessario consentimento explicito antes de transcrever?

### Negocio

- [ ] **[Negocio]** Precificacao hibrida (base + success fee): validar com 5 clientes potenciais antes de definir faixas finais.
- [ ] **[Negocio]** Custo operacional por tenant (VPS, APIs, mensagens): calcular break-even por tenant para definir preco minimo.
- [ ] **[Negocio]** SLA contratual: 99.5% uptime e viavel com infra atual (unica VPS Contabo)?

---

> Documento gerado em 2026-03-22 como Parte 3 da Spec v2 do UUBA Recebe.
> Numeracao de FRs e ACs usa placeholders [CONTINUAR_DE_PARTE_2] para ajuste na consolidacao.
