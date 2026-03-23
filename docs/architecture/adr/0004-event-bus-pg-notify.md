# ADR-004: PostgreSQL LISTEN/NOTIFY como event bus interno

**Data:** 2026-03-22
**Status:** Aceito

## Contexto

A arquitetura Modular Monolith (ADR-001) exige que modulos se comuniquem sem dependencias diretas. Exemplos de fluxos entre modulos:

- **fatura_paga** (Recebe) -> parar regua de cobranca (Nexo), atualizar dashboard (360), registrar receita (Financeiro).
- **cliente_cadastrado** (Recebe) -> criar perfil de analise (360), notificar parceiro (Parceiros).
- **scoring_atualizado** (360) -> ajustar condicoes de cobranca (Nexo).

Sem um mecanismo de eventos, essas dependencias seriam resolvidas por imports diretos entre modulos, violando as fronteiras de dominio e criando acoplamento forte.

O volume estimado de eventos para v1 e baixo: dezenas a centenas de eventos por hora, nao milhares por segundo.

A stack ja possui PostgreSQL 16 e Redis 7 disponiveis.

## Decisao

Implementar um **EventBus simples usando PostgreSQL LISTEN/NOTIFY** para comunicacao entre modulos.

Detalhes da implementacao:

- **Canal por tipo de evento:** ex: `NOTIFY fatura_paga, '{"fatura_id": "xxx", "tenant_id": "yyy", "valor": 150.00}'`.
- **Payload serializado como JSON:** limite de 8000 bytes do NOTIFY e suficiente para payloads de referencia (IDs + metadados essenciais).
- **NOTIFY dentro de transaction:** o evento so e disparado se a transaction que o gerou fizer commit, garantindo consistencia.
- **Listeners async:** consumers usam `asyncpg` para escutar canais, integrado ao event loop do FastAPI.
- **Fallback de polling:** a cada 30 segundos, uma tarefa verifica uma tabela `events_log` para eventos que possam ter sido perdidos (reconexao do LISTEN).
- **Tabela `events_log`:** registra todos os eventos emitidos para auditoria e replay manual se necessario.

Interface do EventBus:

```python
# Emitir evento
await event_bus.emit("fatura_paga", {
    "fatura_id": fatura.id,
    "tenant_id": fatura.tenant_id,
    "valor": fatura.valor
})

# Registrar handler
@event_bus.on("fatura_paga")
async def parar_regua(event: dict):
    await regua_service.cancelar(event["fatura_id"])
```

## Consequencias

### Positivas

- **Zero infra adicional:** PostgreSQL ja esta no stack, nao precisa de broker separado.
- **Consistencia transacional:** NOTIFY dentro de transaction garante que eventos so sao emitidos apos commit bem-sucedido.
- **Simplicidade:** implementacao direta, sem configuracao de topicos, particoes ou consumer groups.
- **Auditoria:** tabela `events_log` permite rastrear todos os eventos emitidos.
- **Latencia baixa:** NOTIFY e quase instantaneo para o volume esperado.

### Negativas

- **Limite de escala:** NOTIFY nao e projetado para milhares de eventos por segundo. Suficiente para v1.
- **Sem replay nativo:** NOTIFY e fire-and-forget; se o consumer nao estava escutando, perde o evento. Mitigado pela tabela `events_log` e polling de fallback.
- **Payload limitado a 8000 bytes:** nao suporta payloads grandes. Mitigado usando apenas IDs e metadados essenciais, com consumer buscando dados completos no banco.
- **Sem garantia de ordem:** eventos podem chegar fora de ordem em cenarios de reconexao. Aceitavel para os casos de uso atuais.
- **Reconexao:** se a conexao do LISTEN cair, eventos sao perdidos ate reconectar. Mitigado pelo polling de fallback a cada 30s.

## Alternativas Consideradas

### Redis Pub/Sub

Usar Redis como broker de eventos via Pub/Sub.

**Considerado porque:** rapido, ja no stack, API simples. **Nao adotado porque:** Redis Pub/Sub e fire-and-forget sem persistencia -- se o consumer estiver offline, a mensagem e perdida sem possibilidade de recovery. PostgreSQL NOTIFY tem o mesmo problema, mas a tabela `events_log` no mesmo banco resolve isso com consistencia transacional.

### Apache Kafka

Plataforma de streaming de eventos distribuida.

**Rejeitado porque:** infra pesada (ZooKeeper/KRaft, brokers, consumers), consome memoria e CPU significativos, complexidade de operacao desproporcional para 1 dev e volume de dezenas de eventos por hora. Considerado para v3+ se o volume justificar.

### RabbitMQ

Message broker com suporte a filas, routing e garantia de entrega.

**Rejeitado porque:** componente adicional de infra para gerenciar, exige monitoring separado, e over-engineering para o volume atual. Seria uma boa opcao se houvesse necessidade de garantia de entrega forte e routing complexo.

### Import direto entre modulos

Modulos chamam services de outros modulos diretamente via imports Python.

**Rejeitado porque:** viola as fronteiras de dominio da arquitetura Modular Monolith. Cria acoplamento forte, dificulta testes isolados e torna impossivel extrair modulos para servicos independentes no futuro.
