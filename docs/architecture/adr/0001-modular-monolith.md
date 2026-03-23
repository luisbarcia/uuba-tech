# ADR-001: Modular Monolith como padrao arquitetural

**Data:** 2026-03-22
**Status:** Aceito

## Contexto

A UUBA Tech possui 5 produtos (Recebe, Nexo, 360, Financeiro, Parceiros) que evoluem independentemente, mas a equipe e composta por 1 desenvolvedor (CTO) auxiliado por IA. Uma arquitetura de microservices traria overhead operacional inviavel para esse cenario -- operar N deploys, N pipelines de CI/CD, N repositorios ou monorepo com build complexo, observabilidade distribuida, etc. Por outro lado, um monolito puro sem fronteiras claras nao escala para 5 dominios distintos e tende a se tornar uma "bola de lama" com o tempo.

A stack escolhida (FastAPI + PostgreSQL 16 + SQLAlchemy 2.0 async + Redis 7 + Docker) roda em uma unica VPS Contabo (4 vCPU, 8GB RAM, ~R$60/mes), o que reforza a necessidade de simplicidade operacional.

## Decisao

Adotar **Modular Monolith** como padrao arquitetural da plataforma UUBA Tech.

Isso significa:

- **Um unico deploy** (container Docker) contendo todos os modulos.
- **Modulos isolados por fronteiras de dominio** — cada produto (Recebe, Nexo, 360, Financeiro, Parceiros) e um modulo com seus proprios models, services, routes e schemas.
- **Comunicacao entre modulos via eventos internos** (ver ADR-004), nunca por import direto de services/models de outro modulo.
- **Diretorio `shared/`** para infraestrutura comum (database, cache, auth, middleware, event bus).

Estrutura de diretorios:

```
src/
  shared/          # Infra comum (db, cache, auth, events)
  recebe/          # Modulo Recebe
  nexo/            # Modulo Nexo
  trezentos_sessenta/  # Modulo 360
  financeiro/      # Modulo Financeiro
  parceiros/       # Modulo Parceiros
```

## Consequencias

### Positivas

- **Simples de operar:** um container, um deploy, um pipeline de CI/CD.
- **Debug local facilitado:** toda a aplicacao roda em um processo, sem necessidade de orquestrar multiplos servicos.
- **Sem latencia de rede entre modulos:** chamadas internas sao in-process.
- **Facilita refactoring:** mover codigo entre modulos e trivial comparado a mover entre microservices.
- **Custo de infra minimo:** roda na VPS de R$60/mes sem problemas.

### Negativas

- **Disciplina necessaria:** manter fronteiras entre modulos exige convencoes e code review rigoroso.
- **Risco de acoplamento:** se as regras de fronteira nao forem seguidas, modulos podem se acoplar via imports diretos.
- **Escalabilidade limitada por modulo:** nao e possivel escalar um modulo independentemente dos outros (aceitavel para o volume atual).
- **Deploy atomico:** uma mudanca em um modulo exige redeploy de toda a aplicacao (aceitavel para equipe de 1 dev).

## Alternativas Consideradas

### Microservices

Cada produto como um servico independente com seu proprio deploy, banco e API.

**Rejeitado porque:** 1 desenvolvedor nao consegue operar N deploys, N bancos, service mesh, tracing distribuido, circuit breakers, etc. O custo operacional seria desproporcional ao beneficio para o estagio atual da plataforma.

### Monolito Puro (sem fronteiras de modulo)

Todo o codigo em uma estrutura plana, sem separacao por dominio.

**Rejeitado porque:** com 5 produtos distintos, a falta de fronteiras levaria rapidamente a um acoplamento descontrolado. Qualquer mudanca em um produto poderia quebrar outro. A manutencao se tornaria exponencialmente mais dificil.

### Serverless (AWS Lambda / Google Cloud Functions)

Cada funcionalidade como uma function independente.

**Rejeitado porque:** vendor lock-in forte, cold starts impactam latencia, complexidade de orquestracao entre functions, custo imprevisivel com escala, e dificuldade de desenvolvimento local. Alem disso, a decisao de usar VPS propria (Contabo) ja foi tomada por custo e controle.
