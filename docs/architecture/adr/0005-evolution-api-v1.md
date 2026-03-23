# ADR-005: Evolution API para WhatsApp na v1

**Data:** 2026-03-22
**Status:** Aceito

## Contexto

O bot da UUBA Tech precisa enviar e receber mensagens via WhatsApp para funcionalidades como:

- **Regua de cobranca:** envio automatico de lembretes de pagamento.
- **Notificacoes:** alertas de faturas vencidas, confirmacoes de pagamento.
- **Atendimento:** chatbot de suporte integrado com n8n + Claude Sonnet.
- **Onboarding:** fluxo guiado de cadastro de novos clientes.

Duas opcoes principais foram avaliadas:

1. **Evolution API:** solucao open-source, self-hosted, que conecta ao WhatsApp via protocolo web (similar ao WhatsApp Web). Custo zero de mensagens, mas exige um container Docker por numero conectado.

2. **Meta Cloud API (oficial):** API oficial do WhatsApp Business fornecida pela Meta. Custo por conversa (~R$0,25-0,65 dependendo da categoria), mas suporta multiplos numeros via um unico Business Manager, com alta disponibilidade e sem risco de ban.

A plataforma atualmente opera com 1-2 numeros de WhatsApp para a propria UUBA, antes de oferecer como produto multi-tenant.

## Decisao

Adotar **Evolution API v2.3.7** para WhatsApp na v1 da plataforma.

Configuracao atual:

- **Self-hosted** na VPS Contabo, acessivel em `wa.uuba.tech`.
- **1 container Docker** por numero de WhatsApp conectado.
- **Integracao com n8n** via webhooks para automacao de fluxos.
- **Bot conversacional** usando n8n + Claude Sonnet para processamento de linguagem natural.
- **Sessao via QR Code:** autenticacao do numero via scan de QR code no painel da Evolution API.

## Consequencias

### Positivas

- **Custo zero de mensagens:** nao ha cobranca por mensagem enviada ou recebida, independente do volume.
- **Controle total:** self-hosted, sem dependencia de terceiros para disponibilidade.
- **Ja operacional:** infraestrutura ja configurada e funcionando em producao.
- **Rapido de configurar:** novo numero conectado em minutos (scan QR code).
- **Integracao nativa com n8n:** webhooks simples para receber mensagens e API REST para enviar.

### Negativas

- **1 container por numero:** para multi-tenancy com 100 tenants, seriam necessarios 100 containers Docker -- inviavel na VPS de 8GB RAM.
- **Sessao via QR Code:** a sessao pode expirar e precisar de reconexao manual (scan de QR code novamente). Instabilidade com atualizacoes do WhatsApp.
- **Risco de ban:** numeros que usam API nao-oficial podem ser banidos pela Meta, especialmente com envio em massa ou comportamento suspeito.
- **Sem suporte oficial:** a Meta nao oferece suporte para integracao via protocolo web. Mudancas no protocolo podem quebrar a Evolution API.
- **Sem templates aprovados:** nao usa message templates aprovados pela Meta, o que limita o envio proativo fora da janela de 24h (embora a Evolution API contorne isso via protocolo web).

## Alternativas Consideradas

### Meta Cloud API (WhatsApp Business API oficial)

API oficial da Meta para WhatsApp Business.

**Planejado para v3 porque:** necessario para escala multi-tenant (multiplos numeros via um unico Business Manager), sem risco de ban, com SLA da Meta, suporte a templates aprovados, e webhooks confiaveis. Custo estimado: ~R$0,25 (utilitaria) a ~R$0,65 (marketing) por conversa. O plano de migracao ja esta documentado em `docs/planos/migracao-whatsapp-oficial.md`.

### Twilio

Plataforma de comunicacao que oferece WhatsApp Business API como servico gerenciado.

**Rejeitado porque:** custo significativamente maior (markup do Twilio sobre o custo da Meta), intermediario desnecessario que adiciona latencia e dependencia, e a UUBA pode contratar a Meta Cloud API diretamente quando necessario.

### WhatsApp Business App

Aplicativo oficial do WhatsApp para pequenas empresas.

**Rejeitado porque:** nao possui API programatica. Toda interacao e manual pelo app. Inviavel para automacao.

## Migracao Planejada

Quando a plataforma precisar suportar 10+ numeros simultaneos (multi-tenancy ativo), a migracao para Meta Cloud API sera executada.

**Gatilhos para migracao:**
- 10+ tenants com numero de WhatsApp proprio.
- Ban de numero em producao.
- Instabilidade recorrente da Evolution API apos atualizacoes do WhatsApp.

**Documentacao de referencia:** `docs/planos/migracao-whatsapp-oficial.md`
