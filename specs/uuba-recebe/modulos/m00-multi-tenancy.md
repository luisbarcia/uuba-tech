# Modulo 0: Multi-tenancy e Infraestrutura

### Descricao

Modulo arquitetural que define isolamento de dados, autenticacao, autorizacao e provisionamento de tenants. Promovido de Modulo 10 para Modulo 0 porque e pre-requisito de todos os demais — implementar depois significaria retrabalho massivo em toda a base de codigo.

### Decisoes Arquiteturais

- **Estrategia de banco:** Shared DB com coluna `tenant_id` em todas as tabelas (v1). DB-per-tenant descartado: 100 tenants = 100 connection pools, exige PgBouncer e aumenta complexidade operacional sem beneficio proporcional para o estagio atual.
- **Cache de roteamento:** Redis armazena mapeamento `api_key -> tenant_id` com TTL de 1h. Overhead de lookup < 10ms p99.
- **Provisionamento:** Setup de banco (migrations, seed) e rapido (< 2min). Configuracao de numero WhatsApp e processo separado, pode levar horas dependendo da aprovacao Meta.

### Open Question

> OQ-001: Evolution API vs Meta Cloud API para escala multi-tenant.
> Evolution API exige uma instancia Docker por numero WhatsApp — 100 tenants = 100 containers, inviavel na VPS atual. Meta Cloud API suporta multiplos numeros sob um unico Business Manager. Decisao deve ser tomada antes do Sprint 3.

### Requisitos Funcionais

**FR-001: Roteamento de tenant por API key**
Where uma requisicao HTTP chega com header `X-API-Key`, the system shall identificar o tenant correspondente via cache Redis e injetar `tenant_id` no contexto da requisicao em menos de 10ms.

**FR-002: Isolamento de dados por tenant**
Where qualquer query ao banco de dados e executada, the system shall aplicar filtro `WHERE tenant_id = :tenant_id` automaticamente via middleware, garantindo que nenhum tenant acesse dados de outro.

**FR-003: Provisionamento de tenant**
When um novo tenant e cadastrado, the system shall executar migrations de banco, gerar API key, criar usuario admin, e configurar parametros padrao (regua default, limites de negociacao, horarios de contato).

**FR-004: RBAC basico**
The system shall suportar tres roles por tenant: `admin` (acesso total, configuracoes, usuarios), `operador` (gestao de faturas, devedores, conversas, sem configuracoes de tenant), e `viewer` (somente leitura em dashboards e relatorios).

**FR-005: Configuracao de numero WhatsApp por tenant**
When um tenant configura seu numero WhatsApp, the system shall registrar o numero, validar conectividade com o provedor (Evolution API ou Meta Cloud API), e ativar o recebimento de mensagens para aquele tenant.

**FR-006: Versionamento de API**
The system shall expor endpoints sob prefixo `/api/v1/` e manter compatibilidade retroativa dentro de uma versao major. Deprecacoes devem ser comunicadas com 90 dias de antecedencia via header `Deprecation`.

### Acceptance Criteria

**AC-001: Isolamento de dados entre tenants**
Given tenant A tem 10 devedores e tenant B tem 5 devedores,
When tenant A consulta `GET /api/v1/debtors`,
Then the system shall retornar apenas os 10 devedores de A,
And nenhum devedor de B deve aparecer no resultado.

**AC-002: API key invalida**
Given uma requisicao com header `X-API-Key: chave_inexistente`,
When a requisicao e recebida,
Then the system shall retornar HTTP 401 com mensagem "API key invalida".

**AC-003: Provisionamento completo em menos de 5 minutos**
Given um novo tenant e cadastrado via admin,
When o provisionamento e executado (excluindo configuracao de WhatsApp),
Then o tenant deve ter banco configurado, API key gerada, usuario admin criado, e regua padrao aplicada em menos de 5 minutos.

**AC-004: RBAC impede acesso indevido**
Given um usuario com role `viewer` no tenant A,
When tenta executar `POST /api/v1/debtors` para criar um devedor,
Then the system shall retornar HTTP 403 com mensagem "Permissao insuficiente".

**AC-005: RBAC operador sem acesso a configuracoes**
Given um usuario com role `operador` no tenant A,
When tenta executar `PUT /api/v1/tenant/settings` para alterar configuracoes,
Then the system shall retornar HTTP 403 com mensagem "Permissao insuficiente".

**AC-006: Cache Redis reduz latencia de roteamento**
Given 100 tenants cadastrados com API keys no Redis,
When 1000 requisicoes consecutivas sao enviadas com API keys validas,
Then o tempo medio de lookup do tenant deve ser inferior a 10ms.

**Status:** Nao implementado
