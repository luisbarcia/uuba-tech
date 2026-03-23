# ADR-002: Shared DB com tenant_id para multi-tenancy

**Data:** 2026-03-22
**Status:** Aceito

## Contexto

A plataforma UUBA Tech precisa suportar multiplos tenants (clientes/empresas) com isolamento de dados. A projecao inicial e de ate 100 tenants na v1.

A abordagem de database-per-tenant (um banco PostgreSQL por cliente) implicaria em 100 connection pools separados, necessidade de PgBouncer para gerenciar conexoes, migrations replicadas em 100 databases, e complexidade operacional alta para monitoramento e backup. Com 1 desenvolvedor operando uma VPS de 8GB RAM, essa abordagem e inviavel.

A stack usa SQLAlchemy 2.0 async com PostgreSQL 16 e Redis 7 para cache.

## Decisao

Adotar **Shared Database com coluna `tenant_id`** em todas as tabelas que armazenam dados de tenants.

Detalhes da implementacao:

- **Coluna `tenant_id`** (UUID, NOT NULL, indexada) presente em todas as tabelas multi-tenant.
- **Middleware SQLAlchemy** aplica filtro `WHERE tenant_id = :current_tenant` automaticamente em todas as queries, usando event hooks do SQLAlchemy.
- **Cache Redis** para routing de tenant (TTL 1h, overhead <10ms por request).
- **Tabelas globais** (planos, configuracoes da plataforma) nao possuem `tenant_id`.
- **Foreign keys** referenciam sempre dentro do mesmo tenant (constraint composta com `tenant_id`).

## Consequencias

### Positivas

- **Simplicidade operacional:** um unico banco, um pool de conexoes, migrations em um lugar so.
- **Custo minimo de infra:** sem necessidade de PgBouncer ou multiplas instancias de banco.
- **Queries cross-tenant faceis:** relatorios agregados da plataforma (admin) sao triviais.
- **Backup e restore simples:** um pg_dump, um restore.

### Negativas

- **Risco de query sem filtro:** uma query que esqueca o `WHERE tenant_id = ...` expoe dados de todos os tenants. Mitigado pelo middleware automatico do SQLAlchemy que injeta o filtro.
- **Sem isolamento de performance:** um tenant com queries pesadas impacta todos os outros. Aceitavel para v1 com volume baixo.
- **Migrations afetam todos os tenants:** uma migration com `ALTER TABLE` bloqueia a tabela para todos. Mitigado usando migrations online (sem lock) quando possivel.
- **Limite de escala:** com centenas de tenants e milhoes de rows, indices compostos com `tenant_id` podem crescer significativamente.

## Alternativas Consideradas

### Database-per-tenant

Um banco PostgreSQL separado para cada tenant.

**Rejeitado para v1 porque:** 100 databases = 100 connection pools, necessidade de PgBouncer, complexidade de migrations, e custo de memoria na VPS de 8GB. Considerado para v3 (50+ clientes com requisitos de isolamento forte).

### Schema-per-tenant

Um schema PostgreSQL por tenant dentro do mesmo banco.

**Considerado para v2 porque:** oferece bom equilibrio entre isolamento e simplicidade. Cada tenant tem seu schema (`tenant_abc.faturas`), migrations podem ser aplicadas via loop, e `search_path` do PostgreSQL facilita o roteamento. Planejado para quando houver 10+ clientes.

### Row-Level Security (RLS) do PostgreSQL

Usar politicas RLS nativas do PostgreSQL para filtrar rows por tenant automaticamente no nivel do banco.

**Considerado mas adiado porque:** mais seguro (filtro no banco, nao na aplicacao), porem mais complexo de debugar, testar e operar. Queries no psql precisam de `SET app.current_tenant = 'xxx'` para funcionar. Pode ser adotado como camada adicional de seguranca no futuro.

## Caminho Evolutivo

| Fase | Estrategia | Gatilho |
|------|-----------|---------|
| v1 | Shared DB + `tenant_id` | Ate ~10 clientes |
| v2 | Schema-per-tenant | 10+ clientes, necessidade de isolamento maior |
| v3 | Database-per-tenant | 50+ clientes, requisitos regulatorios ou SLA individual |
