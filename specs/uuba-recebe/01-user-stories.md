# UUBA Recebe — User Stories

> 20 stories organizadas por persona. Gerada em 2026-03-22.

---

## 1. USER STORIES

### Empresa (Tenant)

**US-001** -- Como **empresa-cliente**, quero **importar uma planilha CSV/Excel de titulos vencidos e que a cobranca comece automaticamente** para que eu nao precise configurar nada manualmente apos o upload.
[Modulos: Import, Regua, Multi-tenancy]

**US-002** -- Como **empresa-cliente**, quero **ver o ROI da cobranca em tempo real no dashboard** para que eu possa demonstrar o valor do servico ao meu financeiro e justificar o investimento.
[Modulos: Dashboard, Analytics]

**US-003** -- Como **empresa-cliente**, quero **configurar limites do bot (desconto maximo, parcelas maximas, tom)** para que a negociacao automatica respeite minhas politicas comerciais.
[Modulos: Bot IA, Regua]

**US-004** -- Como **empresa-cliente**, quero **receber alertas quando a taxa de recuperacao cai abaixo de um threshold configurado** para que eu possa intervir antes de perder receita.
[Modulos: Dashboard, Alertas]

**US-005** -- Como **empresa-cliente**, quero **comparar a performance de reguas de cobranca diferentes** para que eu identifique qual estrategia funciona melhor para cada perfil de devedor.
[Modulos: Dashboard, Regua, Scoring]

**US-006** -- Como **empresa-cliente**, quero **ver o aging report da minha carteira de recebiveis** para que eu entenda a distribuicao do atraso e tome decisoes sobre provisao e prioridades.
[Modulos: Dashboard, Analytics]

**US-007** -- Como **empresa-cliente**, quero **exportar relatorios de cobranca em PDF e CSV** para que eu possa apresentar resultados a diretoria e auditoria.
[Modulos: Dashboard, Analytics]

**US-008** -- Como **empresa-cliente**, quero **ter garantia de compliance automatico (horarios, frequencia, LGPD, CDC)** para que eu nao corra risco legal ao usar a cobranca automatizada.
[Modulos: Compliance, Regua, Bot IA]

**US-009** -- Como **empresa-cliente**, quero **completar o onboarding em menos de 30 minutos** para que eu consiga comecar a recuperar receita no mesmo dia da contratacao.
[Modulos: Multi-tenancy, Import, Onboarding]

**US-010** -- Como **empresa-cliente**, quero **ser alertada quando a taxa de acordo cumprido cai** para que eu possa ajustar as condicoes de negociacao e reduzir a quebra de acordos.
[Modulos: Dashboard, Alertas, Gestao de Parcelas]

### Devedor

**US-011** -- Como **devedor**, quero **entender exatamente quanto devo, com detalhamento por fatura** para que eu tenha clareza sobre minha situacao financeira antes de decidir pagar.
[Modulos: Bot IA, Portal do Devedor]

**US-012** -- Como **devedor**, quero **pagar via Pix em menos de 2 minutos apos receber a cobranca** para que eu resolva a pendencia sem burocracia.
[Modulos: Portal do Devedor, Pagamento, Bot IA]

**US-013** -- Como **devedor**, quero **negociar parcelamento ou desconto diretamente pelo WhatsApp com o bot** para que eu nao precise ligar ou acessar outro sistema.
[Modulos: Bot IA, Regua, Pagamento]

**US-014** -- Como **devedor**, quero **falar com um humano quando o bot nao resolve meu problema** para que eu tenha uma alternativa quando a situacao e complexa.
[Modulos: Bot IA, Chatwoot, Escalacao]

**US-015** -- Como **devedor**, quero **parar de receber mensagens de cobranca assim que eu pagar** para que eu nao seja incomodado desnecessariamente.
[Modulos: Regua, Pagamento, Bot IA, Compliance]

**US-016** -- Como **devedor**, quero **acessar minhas faturas por um link sem precisar de login ou senha** para que eu possa consultar e pagar a qualquer momento.
[Modulos: Portal do Devedor]

**US-017** -- Como **devedor**, quero **receber confirmacao imediata quando meu pagamento for processado** para que eu tenha tranquilidade de que a pendencia foi resolvida.
[Modulos: Pagamento, Bot IA, Regua]

**US-018** -- Como **devedor**, quero **pedir opt-out de um canal especifico de cobranca** para que eu escolha como prefiro ser contatado (ou nao).
[Modulos: Compliance, Bot IA, Regua]

### Operador/Admin

**US-019** -- Como **operador de atendimento**, quero **ver o historico completo do devedor (mensagens, promessas, pagamentos, score) ao assumir uma escalacao** para que eu tenha contexto total sem precisar perguntar novamente ao devedor.
[Modulos: Bot IA, Chatwoot, Dashboard, Scoring]

**US-020** -- Como **administrador da plataforma**, quero **provisionar um novo cliente (tenant) em minutos com database, API key e numero WhatsApp** para que o onboarding seja rapido e eu nao dependa de devops manual.
[Modulos: Multi-tenancy, Onboarding]
