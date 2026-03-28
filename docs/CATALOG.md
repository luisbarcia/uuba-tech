# Catalogo de Produtos — UUBA Tech

> Atualizado: 2026-03-28

## Visao Geral

A UUBA Tech e uma plataforma SaaS B2B de gestao financeira para empresas brasileiras. Opera em dois modelos: self-service (o cliente usa) e BPO (a UUBA opera pelo cliente).

## Arquitetura de Produtos

```
┌──────────────────────────────────────────────────────────────┐
│                     UUBA Parceiros                           │
│              White-label B2B2B para todos                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────┐   ┌──────────────┐   ┌─────────────────────┐ │
│  │  Recebe    │   │  Financeiro  │   │        360          │ │
│  │  Cobranca  │   │  DRE / FC    │   │    Dashboards       │ │
│  │  IA + Bot  │   │  SaaS + BPO  │   │    por perfil       │ │
│  └─────┬──────┘   └──────┬───────┘   └──────────┬──────────┘ │
│        │                 │                      │             │
│        └─────────────────┼──────────────────────┘             │
│                          │                                    │
│                  ┌───────▼────────┐                           │
│                  │      Nexo      │                           │
│                  │  Hub de dados  │                           │
│                  │  Conectores    │                           │
│                  └───────┬────────┘                           │
│                          │                                    │
│               ERPs, Bancos, CRMs, Planilhas                  │
└──────────────────────────────────────────────────────────────┘

Tooling interno: uuba-ctl (CLI de operacao + observabilidade)
```

## Produtos

### 1. UUBA Recebe

> "Setup em minutos. Recuperacao de 50%+."

**O que faz**: Plataforma de gestao de recebiveis e cobranca automatizada. IA conversacional + reguas configuraveis + acionamento multicanal.

**Diferenciais**:
- Bot IA com protocolo comportamental (nudge) — negocia de verdade
- Setup em minutos (importou titulos, ja cobra)
- Resultado mensuravel com dashboard de ROI
- Multicanal inteligente (canal certo, hora certa, tom certo)

**Stack**: FastAPI + PostgreSQL + SQLAlchemy async + Evolution API (WhatsApp) + Claude Sonnet

**Status**: Fase 0 em andamento (~20% da spec implementada)

**Spec**: [specs/uuba-recebe/](../specs/uuba-recebe/) (98 FRs, 90 ACs, 11 modulos)

**Repo**: `uuba-tech-api/` (API) + `uuba-ctl` (CLI)

| Fase | Objetivo | Clientes | Criterio |
|------|----------|----------|----------|
| 0 Piloto | Primeiro pagamento recuperado | 1 (BPO) | Regua + bot + pagamento e2e |
| 1 Monetizar | Multi-tenancy + self-service | 3+ | Import + dashboard minimo |
| 2 Escalar | Portal + scoring + A/B | 10-50 | >=40% recuperacao, <=5% churn |
| 3 Diferenciar | Audio + ML + multicanal | 50+ | Lideranca de mercado BR |

---

### 2. UUBA Nexo

> "Os dados da sua empresa vivem em 10 lugares diferentes. O Nexo conecta todos."

**O que faz**: Hub de dados. Conecta ERPs, CRMs, bancos e planilhas. Normaliza em schema unico e distribui via API para os outros produtos.

**Diferenciais**:
- Setup assistido (sem precisar de dev)
- Conectores focados no ecossistema BR (Conta Azul, Omie, Bling)
- Normalizacao automatica + deduplicacao
- Painel de saude das integracoes

**Dependencia critica**: Todos os outros produtos (exceto Recebe) dependem do Nexo.

**Status**: Spec estrategica pronta. Nenhum codigo.

**Spec**: [specs/uuba-nexo/00-strategic-spec.md](../specs/uuba-nexo/00-strategic-spec.md)

| Fase | Escopo |
|------|--------|
| v1 | Conta Azul + planilhas + engine normalizacao + API interna |
| v2 | Omie, Bling, Google Sheets + webhooks + dedup avancada |
| v3 | Open Finance + sync real-time + API publica |

---

### 3. UUBA 360

> "Cada perfil ve o que precisa ver."

**O que faz**: Dashboards e KPIs por perfil de usuario. Consome dados do Nexo e metricas do Recebe. Nao gera dados — apenas visualiza.

**Diferenciais**:
- Dashboards pre-configurados por perfil (CFO, controller, gerente, analista)
- Zero config — dados vem do Nexo, paineis ja prontos
- Consolidacao multi-empresa (holdings, franquias)
- Alertas configuraveis por threshold (email, WhatsApp)

**Dependencias**: Nexo (fonte de dados), Recebe (metricas de cobranca), Financeiro (DRE/FC quando existir)

**Status**: Spec estrategica pronta. Nenhum codigo.

**Spec**: [specs/uuba-360/00-strategic-spec.md](../specs/uuba-360/00-strategic-spec.md)

| Fase | Escopo |
|------|--------|
| v1 | Dashboards do Recebe (cobranca) — independe do Nexo |
| v2 | Dados financeiros via Nexo + multi-empresa |
| v3 | Composicao livre (drag-and-drop) + alertas inteligentes |

---

### 4. UUBA Financeiro

> "Depto financeiro completo. Sem montar equipe."

**O que faz**: Departamento financeiro operacional completo. DRE, fluxo de caixa, conciliacao, contas a pagar/receber. Opera em modo SaaS (cliente usa) ou BPO (UUBA opera).

**Diferencial central**: FinDrive mostra. UUBA faz.

**Dependencias**: Nexo (extratos, lancamentos, notas fiscais)

**Status**: Rascunho estrategico. Nenhum codigo.

**Spec**: [specs/uuba-financeiro/00-strategic-spec.md](../specs/uuba-financeiro/00-strategic-spec.md)

---

### 5. UUBA Parceiros

> "A tecnologia e da UUBA. O relacionamento e o faturamento sao seus."

**O que faz**: White-label B2B2B. Contadores, consultorias e BPOs revendem UUBA com sua marca, dominio e identidade visual.

**Modelo**: A UUBA cuida da tecnologia. O parceiro mantem o relacionamento e fatura diretamente.

**Perfis de parceiros**: Escritorios de contabilidade, consultorias financeiras, BPOs financeiros, fintechs.

**Dependencias**: Todos os outros produtos (revende qualquer combinacao)

**Status**: Rascunho estrategico. Nenhum codigo.

**Spec**: [specs/uuba-parceiros/00-strategic-spec.md](../specs/uuba-parceiros/00-strategic-spec.md)

---

## Tooling

### uuba-ctl

**O que e**: CLI de controle interno da plataforma. NAO e produto — e ferramenta de operacao.

**O que faz**: Gerencia tenants, API keys (Unkey), clientes, faturas, metricas. Inclui features LLM-powered (ask, watch, report, chat, insights, churn-risk, suggest).

**Stack**: Node.js + TypeScript + Commander.js + Vercel AI SDK

**Repo**: [luisbarcia/uuba-ctl](https://github.com/luisbarcia/uuba-ctl) (v2.1.0, 895 testes)

---

## Dependencias entre Produtos

```
Recebe ──────── funciona sozinho (import CSV direto)
   │
   ├── Nexo ──── alimenta Recebe com dados de ERPs (elimina import manual)
   │    │
   │    ├── 360 ──── consome Nexo + metricas do Recebe
   │    │
   │    └── Financeiro ── consome Nexo (extratos, lancamentos)
   │
   └── Parceiros ── white-label de TODOS os produtos
```

**Ponto critico**: O Nexo e a dependencia central. Sem ele, 360 e Financeiro nao existem. Mas o Recebe funciona sozinho e e o primeiro produto a ir a mercado.

## Ordem de Lancamento

| Trimestre | Produto | Marco |
|-----------|---------|-------|
| Q2 2026 | Recebe F0 + F1 | Primeiro pagamento + 3 clientes |
| Q3 2026 | Recebe F2 | 10+ clientes, portal, scoring |
| Q4 2026 | Nexo v1 + 360 v1 | Hub de dados + dashboards do Recebe |
| Q1 2027 | Financeiro v1 | DRE, FC, conciliacao |
| Q2 2027 | Parceiros v1 | White-label do Recebe + 360 |

## Tracking

- **GitHub Project**: [UUBA Platform (#3)](https://github.com/users/luisbarcia/projects/3) — board unificado com campos Product e Sprint
- **uuba-ctl Project**: [uuba-ctl (#9)](https://github.com/users/luisbarcia/projects/9) — board da CLI
- **Roadmap ativo**: [docs/roadmap/q2-2026.md](roadmap/q2-2026.md)

---

*Catalogo atualizado em 2026-03-28.*
