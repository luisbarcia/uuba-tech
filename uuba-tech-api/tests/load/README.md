# Load Tests — UUBA Recebe API

Testes de carga usando [Locust](https://locust.io/) para validar performance e estabilidade da API.

## Instalacao

O Locust **nao** faz parte das dependencias do projeto (nao esta no `pyproject.toml`).
Instale separadamente:

```bash
pip install locust
```

> Recomendado: use um virtualenv separado ou instale no .venv do projeto temporariamente.

## Cenarios de teste

O `locustfile.py` define 4 tipos de usuario simulado:

| Classe            | Peso | Descricao                                                        |
|-------------------|------|------------------------------------------------------------------|
| `HealthCheckUser` | 1    | Smoke test — apenas GET /health                                  |
| `FullFlowUser`    | 6    | Fluxo completo: criar cliente -> faturas -> cobrar -> listar     |
| `ReadHeavyUser`   | 3    | Leitura intensiva — simula dashboards com listagens e filtros    |
| `BatchJobUser`    | 1    | Cron job — transiciona faturas vencidas a cada 10-30s            |

Os pesos determinam a proporcao de usuarios de cada tipo.
Com 50 usuarios: ~27 FullFlow, ~14 ReadHeavy, ~5 Health, ~4 BatchJob.

## Como executar

### 1. Modo Web UI (recomendado para exploracao)

```bash
cd uuba-tech-api
locust -f tests/load/locustfile.py --host http://localhost:8000
```

Abra http://localhost:8089 no navegador. Configure:
- **Number of users**: 50
- **Spawn rate**: 5 (usuarios/segundo)
- Clique em **Start swarming**

### 2. Modo headless (CI/CD ou terminal)

```bash
# Teste rapido: 10 usuarios por 1 minuto
locust -f tests/load/locustfile.py \
    --host http://localhost:8000 \
    --headless \
    -u 10 -r 2 \
    --run-time 1m

# Teste completo: 50 usuarios por 5 minutos com CSV
mkdir -p results
locust -f tests/load/locustfile.py \
    --host http://localhost:8000 \
    --headless \
    -u 50 -r 5 \
    --run-time 5m \
    --csv results/load_test \
    --csv-full-history
```

### 3. Executar apenas um cenario (tags)

```bash
# Apenas smoke test (health check)
locust -f tests/load/locustfile.py \
    --host http://localhost:8000 \
    --headless \
    --tags smoke \
    -u 5 -r 1 --run-time 30s

# Apenas operacoes de escrita
locust -f tests/load/locustfile.py \
    --host http://localhost:8000 \
    --headless \
    --tags write \
    -u 20 -r 5 --run-time 2m

# Apenas leitura (simular dashboards)
locust -f tests/load/locustfile.py \
    --host http://localhost:8000 \
    --headless \
    --tags read \
    -u 30 -r 5 --run-time 2m
```

## Configuracao

### API Key

Por padrao usa `dev-api-key-change-me`. Para mudar:

```bash
export API_KEY="sua-chave-aqui"
locust -f tests/load/locustfile.py --host http://localhost:8000
```

### Host

Aponte para o ambiente desejado:

```bash
# Local
--host http://localhost:8000

# Staging (VPS)
--host https://api-staging.uuba.tech

# Producao (CUIDADO)
--host https://api.uuba.tech
```

## Interpretando resultados

### Metricas principais

| Metrica               | Meta (local) | Meta (producao) |
|-----------------------|-------------|-----------------|
| p50 response time     | < 100ms     | < 200ms         |
| p95 response time     | < 500ms     | < 1000ms        |
| p99 response time     | < 1000ms    | < 2000ms        |
| Error rate            | < 1%        | < 0.1%          |
| Requests/sec (50 usr) | > 50 rps    | > 30 rps        |

### Arquivos CSV gerados

Quando usar `--csv results/load_test`, o Locust gera:

- `results/load_test_stats.csv` — Estatisticas por endpoint
- `results/load_test_stats_history.csv` — Historico temporal (com `--csv-full-history`)
- `results/load_test_failures.csv` — Detalhes de falhas
- `results/load_test_exceptions.csv` — Excecoes capturadas

### O que investigar se os resultados forem ruins

1. **p95 alto em POST /api/v1/faturas** — Verificar indices no banco, locks em transacoes
2. **p95 alto em GET com filtros** — Indices faltando nas colunas de filtro (status, cliente_id)
3. **Error rate > 1%** — Verificar logs da API, conexoes com banco esgotadas
4. **Throughput baixo** — Verificar workers do uvicorn, pool de conexoes do SQLAlchemy

## Perfis de teste sugeridos

### Smoke (validar que nada quebrou)
```bash
locust -f tests/load/locustfile.py --host http://localhost:8000 \
    --headless -u 3 -r 1 --run-time 30s --tags smoke
```

### Soak (estabilidade em uso continuo)
```bash
locust -f tests/load/locustfile.py --host http://localhost:8000 \
    --headless -u 20 -r 2 --run-time 30m \
    --csv results/soak_test --csv-full-history
```

### Stress (encontrar o limite)
```bash
locust -f tests/load/locustfile.py --host http://localhost:8000 \
    --headless -u 200 -r 10 --run-time 5m \
    --csv results/stress_test
```

### Spike (pico subito)
```bash
locust -f tests/load/locustfile.py --host http://localhost:8000 \
    --headless -u 100 -r 50 --run-time 2m \
    --csv results/spike_test
```
