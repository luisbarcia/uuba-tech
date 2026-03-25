# ADR-0007: Criptografia de Dados Pessoais em Repouso

## Status

Aceito

## Contexto

A LGPD (Art. 46) exige medidas técnicas de segurança para proteger dados pessoais. Dados PII (documento, email, telefone) são armazenados em texto plano no PostgreSQL. Precisamos decidir a abordagem de criptografia.

## Opções Avaliadas

### Opção A — Application-level encryption (Fernet/AES)

Criptografar no Python antes de persistir, descriptografar na leitura.

- **Pros:** Independente do DB, controle total, funciona com qualquer provider
- **Cons:** Busca por campo criptografado requer hash index separado; complexidade no ORM
- **Impacto:** Alto (mudança em models, repos, migrations)

### Opção B — PostgreSQL pgcrypto (column-level)

Usar `pgp_sym_encrypt()` / `pgp_sym_decrypt()` nas queries.

- **Pros:** Nativo do PostgreSQL, granular por coluna
- **Cons:** Chave em query SQL (risco se log ativado); WHERE em campo criptografado é lento
- **Impacto:** Médio (mudanças em queries raw, não funciona bem com ORM)

### Opção C — Volume/disk encryption (LUKS/dm-crypt)

Criptografar o volume Docker ou disco do VPS.

- **Pros:** Zero mudança no código; protege contra acesso físico
- **Cons:** Não protege contra acesso lógico (SQL injection, backup leak)
- **Impacto:** Baixo (configuração de infra apenas)

## Decisão

**Opção C (volume encryption) agora + Opção A (application-level) quando necessário.**

### Justificativa

1. **Fase atual (MVP/Piloto):** Volume encryption é suficiente e não atrasa o produto. O risco principal é acesso físico ao servidor, que volume encryption mitiga.

2. **Fase de produção:** Application-level encryption será implementada para `documento` (CPF/CNPJ) quando:
   - Houver mais de 1 operador com acesso ao banco
   - Dados forem replicados para backup externo
   - Auditoria ANPD exigir

3. **Implementação futura (Opção A):**
   ```python
   # Campo criptografado + hash index para busca
   documento_encrypted: Mapped[bytes]     # Fernet.encrypt(cpf)
   documento_hash: Mapped[str]            # SHA256(cpf)[:14] — para busca/dedup
   ```

4. **pgcrypto descartado:** Incompatível com SQLAlchemy ORM async e expõe chave em queries.

## Ação Imediata

- [ ] Configurar LUKS/dm-crypt no volume `uuba_pgdata` do VPS
- [ ] Documentar procedimento em runbook de operações
- [ ] Adicionar `ENCRYPTION_KEY` como env var placeholder para uso futuro

## Consequências

- Código permanece simples na fase MVP
- Volume encryption protege contra acesso físico
- Caminho claro para application-level encryption quando necessário
- Decisão revisável a cada trimestre ou por demanda de auditoria
