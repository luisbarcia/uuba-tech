# DP-01: Value Objects — Plano de Implementação

## Goal
Criar Value Objects imutáveis para FaturaStatus, CobrancaStatus, CobrancaTipo, CobrancaCanal, CobrancaTom, Documento (CPF/CNPJ) e Money. Seguindo TDD strict.

## Approach
- TDD: RED → GREEN → REFACTOR para cada VO
- Python dataclass(frozen=True) para imutabilidade
- Enums para tipos finitos
- Testes unitários puros (sem DB)

## Phases

### Phase 1: Setup + FaturaStatus [complete]
- Criar `app/domain/__init__.py` e `app/domain/value_objects/__init__.py`
- Criar `tests/test_value_objects.py`
- RED: Testes para FaturaStatus (criação, transição, terminal, igualdade)
- GREEN: Implementar FaturaStatus enum com `pode_transicionar_para()` e `is_terminal`
- REFACTOR: Limpar

### Phase 2: Enums de Cobrança [complete]
- RED: Testes para CobrancaStatus, CobrancaTipo, CobrancaCanal, CobrancaTom
- GREEN: Implementar cada enum
- REFACTOR

### Phase 3: Documento (CPF/CNPJ) [complete]
- RED: Testes para validação CPF, CNPJ, formatação, igualdade, tipo
- GREEN: Implementar Documento com validação real de dígitos
- REFACTOR

### Phase 4: Money [complete]
- RED: Testes para criação, adição, subtração, formatação, moeda diferente
- GREEN: Implementar Money(centavos, moeda) imutável
- REFACTOR

### Phase 5: Rodar todos os testes [complete]
- 58 VO tests passed (0.04s)
- 241 total tests passed (2.75s) — zero regressão
- ruff check + format: clean
- `pytest tests/test_value_objects.py -v`
- `pytest` completo (garantir que nada quebrou)
- `ruff check` + `ruff format --check`

## Files to Create
- `app/domain/__init__.py`
- `app/domain/value_objects/__init__.py`
- `app/domain/value_objects/fatura_status.py`
- `app/domain/value_objects/cobranca_enums.py`
- `app/domain/value_objects/documento.py`
- `app/domain/value_objects/money.py`
- `tests/test_value_objects.py`

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| (none yet) | | |
