# ADR-003: ARQ como sistema de background jobs

**Data:** 2026-03-22
**Status:** Aceito

## Contexto

A plataforma UUBA Tech possui diversas necessidades de processamento assincrono:

- **Regua de cobranca:** cron jobs que enviam lembretes de pagamento em intervalos definidos.
- **Import assincrono:** processamento de arquivos CSV/XLSX com milhares de linhas de faturas.
- **Processamento de webhooks:** receber e processar webhooks de gateways de pagamento.
- **Scoring diario:** calculo de metricas e scores de saude financeira para cada tenant.
- **Envio de notificacoes:** disparos de WhatsApp, email e push em batch.

O Celery e a solucao mais madura do ecossistema Python para filas de trabalho, porem exige:

- Broker separado (RabbitMQ ou Redis).
- Processo beat separado para cron.
- Flower ou outro dashboard para monitoring.
- Multiplos processos (worker, beat, flower) rodando simultaneamente.

Para 1 desenvolvedor operando uma VPS de 8GB RAM, a simplicidade e prioridade absoluta.

A stack ja utiliza Redis 7 (para cache) e FastAPI com asyncio, o que favorece solucoes async-nativas.

## Decisao

Adotar **ARQ** (Asynchronous Redis Queue) como sistema de background jobs.

Caracteristicas do ARQ que motivaram a escolha:

- **Async-nativo:** usa `asyncio`, compativel diretamente com o event loop do FastAPI.
- **Redis como backend:** ja presente no stack, sem infra adicional.
- **Cron integrado:** suporte nativo a tarefas periodicas, sem processo beat separado.
- **Retry com backoff:** suporte a retry automatico com backoff exponencial.
- **Leve:** um unico processo worker, footprint minimo de memoria.
- **Tipagem:** suporte a type hints nativamente.

Configuracao planejada:

```python
# Worker settings
class WorkerSettings:
    redis_settings = RedisSettings(host='redis', port=6379)
    functions = [processar_cobranca, importar_arquivo, processar_webhook]
    cron_jobs = [
        cron(regua_cobranca, hour=8, minute=0),    # Diario as 8h
        cron(scoring_diario, hour=6, minute=0),     # Diario as 6h
        cron(limpeza_cache, hour=3, minute=0),      # Diario as 3h
    ]
    max_jobs = 10
    job_timeout = 300  # 5 min
```

## Consequencias

### Positivas

- **Mesmo event loop do FastAPI:** compartilha o runtime async, sem overhead de serialization complexa.
- **Redis ja no stack:** zero infra adicional para o backend de filas.
- **Footprint minimo:** um processo worker adicional, consumo de ~50-100MB RAM.
- **Simplicidade de deploy:** um container adicional no docker-compose (ou mesmo processo).
- **Cron integrado:** nao precisa de processo beat separado.

### Negativas

- **Menos features que Celery:** sem canvas (chains, chords, groups), sem priorities de fila, sem routing avancado.
- **Comunidade menor:** menos plugins, menos respostas no Stack Overflow, menos batalha-testado em producao de alto volume.
- **Sem dashboard nativo:** precisa de solucao custom ou arq-dashboard (projeto terceiro) para monitoring.
- **Limite de escala:** para volumes muito altos (milhares de jobs/minuto), pode ser necessario migrar para Celery.

## Alternativas Consideradas

### Celery

Framework de filas de trabalho mais popular do ecossistema Python.

**Rejeitado porque:** exige multiplos processos (worker, beat, flower), broker separado, configuracao verbosa, e e baseado em threads/processos (nao async-nativo). Overhead desproporcional para o volume atual e tamanho da equipe.

### Dramatiq

Alternativa leve ao Celery, com API mais simples.

**Considerado porque:** mais leve que Celery, boa API. Porem, tambem nao e async-nativo e tem comunidade menor. ARQ foi preferido por ser async-first e usar Redis diretamente.

### APScheduler

Scheduler Python para tarefas periodicas.

**Rejeitado porque:** roda in-process (se o processo morre, os jobs param), sem sistema de filas, sem retry automatico, sem persistencia de estado dos jobs.

### Cron puro (crontab do sistema)

Agendamento via crontab do Linux.

**Rejeitado porque:** sem retry automatico, sem sistema de filas, sem monitoring, sem visibilidade do estado dos jobs, e nao integra com o ecossistema Python/Docker facilmente.
