# Task Plan: Reescrita Spec UÚBA Recebe v2

## Goal
Reescrever a spec completa do UÚBA Recebe incorporando todas as correções das revisões PM e Dev.

## Inputs
- Spec atual: `specs/uuba-recebe.spec.md` (v1 — 66 FRs, 32 ACs)
- Revisão PM: 32 FRs novos, 20 user stories, 22 KPIs, jornadas, pricing
- Revisão Dev: 15 correções técnicas prioritárias
- Benchmarking global: pesquisa completa com 10 plataformas
- Arquitetura: modular monolith (documento separado)

## Phases

### Phase 1: Criar findings.md com todas as correções consolidadas [pending]
- Extrair e organizar todas as correções dos revisores PM e Dev
- Priorizar por severidade

### Phase 2: Reescrever spec — Seções estruturais [pending]
- Overview (atualizar multi-tenancy para shared DB + tenant_id)
- Benchmarking (manter)
- User Stories (NOVO — 20 stories)
- Jornadas (NOVO — empresa + devedor)

### Phase 3: Reescrever spec — Módulos reordenados [pending]
- Módulo 0: Multi-tenancy e Infra (promovido)
- Módulo 1: Clientes (+ edge cases nos ACs)
- Módulo 2: Faturas (+ gestão de parcelas + cancelamento)
- Módulo 3: Pre-delinquency (NOVO)
- Módulo 4: Régua de Cobrança (+ compliance embutido + A/B testing + ação pós-régua)
- Módulo 5: Bot IA (+ áudio + handoff + negociação revisada + Pix corrigido)
- Módulo 6: Import (+ async)
- Módulo 7: Portal do Devedor
- Módulo 8: Dashboard e Analytics
- Módulo 9: Scoring (heurístico v1, ML futuro)
- Módulo 10: Self-healing e Resiliência (NOVO)

### Phase 4: Reescrever spec — Seções de suporte [pending]
- KPIs e métricas de sucesso (NOVO — 22 métricas)
- Modelo de precificação (NOVO — 4 opções)
- NFRs revisados (latência bot 5s, dashboard cache obrigatório, rate limit diferenciado)
- Error handling revisado (+ HMAC webhook + RBAC)
- Mapa de dependências (NOVO)
- Integrações externas (NOVO)
- Implementation TODO (atualizado)
- Open Questions (atualizado)

### Phase 5: Validação e entrega [pending]
- Verificar contagem de FRs (deve ter ~98)
- Verificar consistência entre módulos
- Apresentar resumo ao usuário

## Decisions
- Multi-tenancy: shared DB + tenant_id (v1), schema-per-tenant (v2)
- Scoring: heurístico com regras (v1), ML (v2)
- Compliance: embutido nos módulos de Régua e Bot, não separado
- Arquitetura: documento separado (não na spec)

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| (nenhum ainda) | | |
