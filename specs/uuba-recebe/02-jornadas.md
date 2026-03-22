# UUBA Recebe — Jornadas do Usuario

---

## 2. JORNADAS

### Jornada da Empresa (Tenant)

#### Fase 1: Descoberta

1. Empresa identifica problema de inadimplencia (taxa de recuperacao <25% com metodo atual).
2. Encontra UUBA Recebe via indicacao, site ou conteudo.
3. Acessa pagina do produto, ve ROI prometido (10x+) e benchmarks.
4. Solicita demonstracao ou inicia trial.

[GAPS]
- Nao ha pagina de demonstracao interativa ou simulador de ROI. FR necessario: simulador de ROI na landing page (input: volume de titulos + valor medio + taxa atual; output: projecao de recuperacao e economia).

#### Fase 2: Onboarding (meta: menos de 30 minutos)

1. Admin cria tenant via painel ou API.
2. Sistema provisiona database, schema, tabelas e credenciais automaticamente.
3. Numero WhatsApp e provisionado (Meta Cloud API ou Evolution API).
4. Empresa recebe API key e acesso ao dashboard.
5. Wizard de onboarding guia configuracao inicial: dados da empresa, logo, limites do bot, regua padrao.

[GAPS]
- Wizard de onboarding nao existe. FR necessario: fluxo guiado com 5 passos (dados empresa, upload logo, config bot, preview regua, primeiro import).
- Provisionamento de numero WhatsApp depende de decisao Evolution API vs Meta Cloud API (ver findings). FR necessario: provisioning automatizado para o modelo escolhido.
- Falta preview da regua padrao antes de ativar. FR necessario: simulador de regua (dry run) para tenant visualizar sequencia antes de ir a producao.

#### Fase 3: Primeiro Import

1. Empresa exporta titulos vencidos do ERP/planilha.
2. Faz upload de CSV/Excel no dashboard.
3. Sistema valida, mapeia colunas se necessario, processa em background (async).
4. Relatorio de import mostra: X aceitos, Y rejeitados com motivos.
5. Clientes (devedores) sao criados via upsert por documento.
6. Notificacao: "Import concluido. X titulos prontos para cobranca."

[GAPS]
- Import atualmente e sincrono -- timeout em arquivos grandes. FR necessario: endpoint async (retorna 202 + job_id, status via polling).
- Falta preview do import antes de confirmar. FR necessario: tela de preview mostrando primeiras 10 linhas parseadas para validacao humana.
- Encoding e separadores nao padrao causam falha silenciosa. FR necessario: deteccao automatica de encoding (UTF-8, ISO-8859-1, Windows-1252) e separador (virgula, ponto-e-virgula, tab).

#### Fase 4: Primeiras Cobrancas

1. Regua padrao e ativada automaticamente para faturas importadas.
2. Sistema respeita compliance: horarios, frequencia, feriados.
3. Primeiras mensagens sao enviadas via WhatsApp no proximo horario util.
4. Dashboard mostra em tempo real: enviadas, lidas, respondidas, pagas.
5. Empresa recebe notificacao do primeiro pagamento recuperado.

[GAPS]
- Regua comeca em D-3, deveria comecar D-14 a D-30 (pre-delinquency). FR necessario: regua preventiva com passos pre-vencimento configuravel (D-30 a D-1).
- Nao ha notificacao do primeiro pagamento ao tenant. FR necessario: evento "first_payment_recovered" com notificacao push/email ao admin.
- Falta A/B testing de reguas. FR necessario: motor de A/B para testar variantes de regua com distribuicao configuravel e promocao automatica da vencedora.

#### Fase 5: Otimizacao

1. Empresa analisa dashboard: taxa de recuperacao, DSO, aging, performance por regua.
2. Compara regua padrao com regua customizada.
3. Ajusta limites do bot (desconto, parcelas).
4. Cria segmentos de devedores por perfil de risco.
5. Scoring heuristico comeca a alimentar priorizacao automatica.

[GAPS]
- Scoring ML irreal para v1. FR necessario: scoring heuristico com formula explicita (score = base(50) + historico(-20 a +20) + atraso(-15 a +15) + engajamento(-10 a +10) + valor(-5 a +5)).
- Falta simulador de regua para testar antes de ativar. FR necessario: dry run que mostra quantos devedores seriam impactados e em quais dias.

#### Fase 6: Expansao

1. Empresa aumenta volume de titulos importados.
2. Integra ERP via webhook para import automatico.
3. Contrata plano superior (mais volume, mais canais futuros).
4. Indica outras empresas (referral).

[GAPS]
- Sem programa de referral estruturado. FR necessario: sistema de indicacao com tracking e beneficio (desconto ou credito).
- Webhook de ERP sem validacao HMAC. FR necessario: assinatura HMAC obrigatoria em webhooks recebidos.

---

### Jornada do Devedor

#### Cenario A: Pagamento Rapido (~40% dos devedores)

Perfil: devedor que esqueceu ou atrasou por desorganizacao. Divida pequena a media.

1. [D-3] Recebe lembrete amigavel via WhatsApp: "Oi, {nome}. Lembrete: sua fatura de R$ {valor} vence em 3 dias. Pague agora com desconto de 5%: {link}".
2. [D-3] Abre o link no celular. Portal carrega sem login (token JWT).
3. [D-3] Ve fatura detalhada: valor, vencimento, descricao, NF.
4. [D-3] Clica "Pagar com Pix". QR code aparece. Paga em 30 segundos.
5. [D-3] Webhook do gateway confirma pagamento. Status atualiza para "pago".
6. [D-3] Bot envia mensagem: "Pagamento confirmado. Obrigado, {nome}!"
7. Regua e desativada para esta fatura. Fim.

Alternativa D+1: devedor nao pagou antes do vencimento, recebe cobranca no D+1, paga pelo portal.

[GAPS]
- Desconto por antecipacao nao implementado. FR necessario: configuracao de desconto por antecipacao (ex: 5% se pagar ate D-1, 3% se pagar ate D+3).
- Confirmacao de pagamento Pix nao e tempo real (depende de webhook). FR necessario: polling de fallback caso webhook demore mais de 60 segundos.
- QR code pode expirar antes do devedor pagar. FR necessario: deteccao de QR expirado + geracao automatica de novo QR com notificacao.

#### Cenario B: Negociacao via Bot (~25% dos devedores)

Perfil: devedor que reconhece a divida mas nao tem condicoes de pagar o valor integral.

1. [D+1] Recebe cobranca neutra via WhatsApp com link de pagamento.
2. [D+1] Responde: "nao consigo pagar tudo agora".
3. [D+1] Bot identifica intencao de negociacao. Consulta limites configurados pelo tenant.
4. [D+1] Bot propoe: "Entendo, {nome}. Posso oferecer: (1) Pague R$ {valor_com_desconto} a vista com 10% de desconto; (2) Parcele em 3x de R$ {parcela} sem juros. Qual prefere?"
5. [D+1] Devedor escolhe opcao 2 (parcelamento).
6. [D+1] Bot gera acordo: 3 parcelas com vencimentos D+5, D+35, D+65.
7. [D+1] Bot envia link de pagamento da primeira parcela.
8. [D+5] Devedor paga parcela 1. Bot confirma e agenda lembrete da parcela 2.
9. [D+33] Bot envia lembrete: "Lembrete: parcela 2 de R$ {parcela} vence em 2 dias. {link}".
10. Ciclo repete ate ultima parcela.

[GAPS]
- Gestao de parcelas nao implementada. FR necessario: entidade "Acordo" com parcelas vinculadas, status por parcela, lembretes automaticos, e acao quando parcela atrasa.
- Mecanica de parcelamento vaga: gera novas faturas? Cobra juros? FR necessario: definicao explicita -- acordo cria N faturas filhas com referencia ao acordo-pai.
- Renegociacao proativa ausente. FR necessario: se devedor quebra acordo, cooling period de 7 dias + nova proposta com condicoes ajustadas + limite de 2 renegociacoes por fatura.

#### Cenario C: Escalacao para Humano (~15% dos devedores)

Perfil: devedor irritado, situacao complexa, ou demanda fora dos limites do bot.

1. [D+3] Recebe cobranca neutra. Responde com raiva: "Para de me mandar mensagem! Ja paguei isso!"
2. [D+3] Bot detecta sentimento negativo (raiva). Ajusta tom para empatico: "Entendo sua frustacao, {nome}. Vou verificar seus pagamentos."
3. [D+3] Bot consulta faturas. Nao encontra pagamento registrado.
4. [D+3] Bot responde: "Nao localizei pagamento para a fatura NF-{numero}. Se voce pagou, pode enviar o comprovante? Ou prefere falar com nosso atendimento?"
5. [D+3] Devedor responde: "Quero falar com alguem."
6. [D+3] Bot escala para Chatwoot com resumo automatico: devedor, faturas, historico de conversa, sentimento detectado, motivo da escalacao.
7. [D+3] Atendente ve contexto completo. Resolve sem repetir perguntas.
8. Atendente confirma pagamento (comprovante), atualiza status, envia confirmacao.

[GAPS]
- Handoff bot-para-humano sem resumo estruturado. FR necessario: resumo automatico para o atendente com campos: devedor (nome, documento, score), faturas em aberto (valor, atraso), historico recente (ultimas 5 mensagens), sentimento detectado, motivo da escalacao.
- Confirmacao via comprovante nao implementada. FR necessario: devedor envia imagem de comprovante, sistema faz OCR para extrair valor/data/codigo, operador valida.
- Falta metricas de escalacao (tempo de resolucao, satisfacao). FR necessario: CSAT pos-atendimento + tempo medio de resolucao por atendente.

#### Cenario D: Nao-Responsivo (~20% dos devedores)

Perfil: devedor que ignora todas as tentativas de contato. Pode ser numero errado, devedor cronico, ou telefone reciclado.

1. [D-3] Lembrete amigavel enviado. Sem leitura.
2. [D+1] Cobranca neutra enviada. Entregue mas nao lida.
3. [D+3] Follow-up. Sem resposta.
4. [D+7] Mensagem firme. Sem resposta.
5. [D+15] Mensagem urgente final. Sem resposta.
6. Regua esgota todos os passos. Fatura marcada como "regua_esgotada".
7. [Acao pos-regua] Sistema aplica tratamento definido pelo tenant: (a) pausa permanente; (b) reinicio de regua apos cooling period de 30 dias; (c) escalacao para tratamento manual; (d) encaminhamento para cobranca juridica (out of scope v1, mas flag para futuro).
8. Tenant recebe relatorio de faturas nao recuperadas com sugestao de acao.

[GAPS]
- Acao pos-regua nao definida na spec v1. FR necessario: configuracao por tenant de acao pos-regua com opcoes (pausa, reinicio, escalacao, export para juridico).
- Telefone reciclado nao detectado. FR necessario: se numero nao recebe mensagem (erro de entrega) em 3 tentativas, marcar como "numero_invalido" e pausar.
- Nao ha mecanismo para tentar canal alternativo. FR necessario (v2): fallback para email/SMS quando WhatsApp falha (out of scope v1, mas arquitetura deve prever).
- Falta relatorio especifico de nao-responsivos para o tenant. FR necessario: relatorio "faturas sem resposta" com aging, valor total, e sugestoes de acao.
