# ADR-006: DDD Tactical Patterns como padrao de modelagem de dominio

**Data:** 2026-03-23
**Status:** Aceito

## Contexto

A API do UUBA Recebe (Fase 0) esta funcional com CRUD de Clientes, Faturas e Cobrancas, mas a logica de negocio vive nos services como funcoes procedurais operando sobre models SQLAlchemy. Regras de dominio como transicoes de status ficam em dicts soltos (`FATURA_TRANSITIONS`), valores monetarios sao `int` sem encapsulamento, documentos (CPF/CNPJ) sao strings sem validacao de digitos verificadores.

Com 5 modulos planejados (Recebe, Nexo, 360, Financeiro, Parceiros) que precisam se comunicar via eventos (ADR-004), a ausencia de uma camada de dominio formal cria riscos:

- **Primitive Obsession:** `status`, `documento`, `valor` sao strings/ints — regras espalhadas nos services e schemas.
- **Acoplamento modules→DB:** services fazem queries SQLAlchemy diretamente, impossibilitando testes unitarios sem banco.
- **Sem invariantes:** e possivel criar uma cobranca para uma fatura cancelada — o service precisa lembrar de checar.
- **Sem eventos de dominio:** efeitos colaterais sao chamados inline, sem padrao para comunicacao entre modulos.

O ADR-001 (Modular Monolith) define que modulos comunicam via eventos, mas nao especifica como modelar o dominio interno de cada modulo.

## Decisao

Adotar **DDD Tactical Patterns** como padrao de modelagem de dominio para todos os modulos da UUBA Tech.

Isso significa:

### 1. Value Objects

Tipos imutaveis que encapsulam conceitos de dominio com validacao embutida:

- `FaturaStatus` — enum com maquina de estados (`pode_transicionar_para()`, `is_terminal`, `transicoes_validas`)
- `Documento` — CPF/CNPJ com validacao real de digitos verificadores, formatacao, imutabilidade
- `Money` — centavos + moeda com aritmetica segura (soma, subtracao, comparacao, formatacao BRL)
- `CobrancaTipo`, `CobrancaCanal`, `CobrancaTom`, `CobrancaStatus` — enums tipados substituindo strings magicas

Localizam-se em `app/domain/value_objects/`.

### 2. Aggregates (planejado)

Clusters de entidades com um Aggregate Root que garante invariantes:

- `Fatura` como aggregate root de `Cobranca` — toda operacao sobre cobranca passa pela fatura.
- Invariantes: fatura cancelada/paga nao aceita novas cobrancas; transicoes de status so pelo aggregate.

### 3. Repositories (planejado)

Interface (Protocol) para acesso a aggregates, implementacao com SQLAlchemy:

- `FaturaRepository(Protocol)` — `get_by_id()`, `save()`, `list_vencidas()`
- `SQLAlchemyFaturaRepository` — implementacao concreta
- `InMemoryFaturaRepository` — para testes unitarios sem DB

### 4. Domain Events (planejado)

Objetos imutaveis representando fatos do dominio:

- `FaturaVenceu`, `PagamentoConfirmado`, `CobrancaEnviada`, `PromessaRegistrada`
- Emitidos pelos aggregates, publicados via EventBus (ADR-004)
- Fundacao para comunicacao entre modulos sem import direto

### Estrutura de diretorios

```
app/domain/
  value_objects/
    fatura_status.py       # Enum com maquina de estados
    cobranca_enums.py      # Tipo, Canal, Tom, Status
    documento.py           # CPF/CNPJ imutavel com validacao
    money.py               # Centavos + moeda, aritmetica segura
  aggregates/              # (planejado) Fatura como aggregate root
  repositories/            # (planejado) Protocol + implementacoes
  events/                  # (planejado) Domain Events
```

## Consequencias

### Positivas

- **Regras no dominio, nao nos services:** `FaturaStatus.pode_transicionar_para()` substitui dict solto e ifs espalhados.
- **Validacao real:** `Documento("00000000000")` levanta erro — antes passava como string valida.
- **Seguranca monetaria:** `Money(100, "BRL") + Money(100, "USD")` levanta erro — antes era soma de ints sem checagem.
- **Testavel sem DB:** Value Objects sao puros, testados em 0.04s (58 testes). Repositories permitirao testes de service sem banco.
- **Preparacao para multi-modulo:** Domain Events + Aggregates sao o fundamento para comunicacao via ADR-004.
- **Extensivel:** adicionar estado `em_negociacao` a fatura = adicionar 1 membro ao enum + regras de transicao.

### Negativas

- **Camada adicional:** models SQLAlchemy continuam existindo, agora com uma camada de dominio acima. Mais indirection.
- **Curva de aprendizado:** devs novos precisam entender a diferenca entre model (persistencia) e aggregate (dominio).
- **Conversao necessaria:** dados entram como string via API, precisam ser convertidos para VOs, e de volta para string no banco.
- **Over-engineering para 1 dev?** Mitigado pela abordagem incremental — so implementamos o que usamos. Nao ha abstractions sem consumidores.

## Abordagem de Integracao

Os Value Objects NAO mudam o schema do banco de dados. A integracao e feita na camada de services:

- **DB → str** → `FaturaStatus("pendente")` → logica de dominio → `status.value` → **str → DB**
- Models SQLAlchemy continuam com `String`, `Integer` — nenhuma migration necessaria.
- Schemas Pydantic continuam aceitando strings — validacao adicional via VOs acontece nos services.

Isso permite adocao incremental sem big-bang.

## Alternativas Consideradas

### Manter logica nos services (status quo)

Continuar com funcoes procedurais e dicts de transicao.

**Rejeitado porque:** com 5 modulos e features crescendo (regua, scoring, portal do devedor), a logica de dominio ficaria cada vez mais espalhada. Cada service precisaria reimplementar validacoes que deveriam ser do dominio.

### DDD completo desde o inicio (Aggregates + Repositories + Events + CQRS)

Implementar tudo de uma vez.

**Rejeitado porque:** over-engineering para o estagio atual. Adotamos incrementalmente — Value Objects primeiro (impacto imediato), depois Aggregates e Repositories conforme a complexidade justifica.

### Pydantic como camada de dominio (sem camada separada)

Usar validadores Pydantic nos schemas como unica camada de validacao.

**Rejeitado porque:** Pydantic e para serializacao/deserializacao de API, nao para logica de dominio. Um `FaturaStatus` com `pode_transicionar_para()` e `is_terminal` nao pertence a um schema de API — pertence ao dominio. Misturar os dois acopla a logica de negocio ao formato de transporte.

## Rastreabilidade

| Issue | Titulo | Status |
|-------|--------|--------|
| #19 | DP-01: Value Objects | Implementado |
| #23 | DP-05: Eliminar Primitive Obsession | Implementado (fatura_service) |
| #20 | DP-02: Aggregate Root | Planejado |
| #24 | DP-06: Extract Method | Planejado |
| #22 | DP-04: Repository Pattern | Planejado |
| #21 | DP-03: Domain Events | Planejado |
