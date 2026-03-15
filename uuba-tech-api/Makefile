.PHONY: dev test db migrate lint clean

dev: db migrate  ## Sobe tudo e roda a API
	uvicorn app.main:app --reload

db:  ## Sobe PostgreSQL e cria DB de teste
	docker compose up -d db
	sleep 2
	docker compose exec db psql -U uuba -c "CREATE DATABASE uuba_test;" 2>/dev/null || true

migrate:  ## Roda migrations
	alembic upgrade head

test: db  ## Roda testes (sobe DB se necessario)
	pytest -v --tb=short

lint:  ## Roda linter
	ruff check . --fix

clean:  ## Reseta tudo (DESTRUTIVO)
	docker compose down -v
	$(MAKE) db migrate
