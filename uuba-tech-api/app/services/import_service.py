"""Serviço de importação de faturas via CSV.

Processa upload CSV com títulos vencidos para o piloto.
Usa Value Objects (Documento) para validação e repositories (DP-04) para persistência.
"""

import csv
import io
import re
from datetime import datetime, timezone

from app.domain.repositories.cliente_repository import ClienteRepository
from app.domain.repositories.fatura_repository import FaturaRepository
from app.domain.value_objects.documento import Documento
from app.exceptions import APIError
from app.models.cliente import Cliente
from app.models.fatura import Fatura
from app.schemas.import_csv import ImportResult, ImportRowError
from app.utils.ids import generate_id

REQUIRED_COLUMNS = {"nome", "documento", "valor", "vencimento"}
OPTIONAL_COLUMNS = {"email", "telefone", "numero_nf", "descricao"}


def _detect_separator(first_line: str) -> str:
    """Auto-detecta separador do CSV pela primeira linha.

    Args:
        first_line: Primeira linha (header) do arquivo CSV.

    Returns:
        ``';'`` se mais frequente que ``','``, caso contrário ``','``.
    """
    return ";" if first_line.count(";") > first_line.count(",") else ","


def _parse_valor(raw: str) -> int:
    """Converte valor monetário em string para centavos inteiros.

    Aceita: ``"2500.00"``, ``"2500,00"`` (reais com decimais) ou
    ``"250000"`` (já em centavos).

    Args:
        raw: Valor bruto como string do CSV.

    Returns:
        Valor em centavos (inteiro positivo).

    Raises:
        ValueError: Se o formato não for reconhecido ou valor vazio.
    """
    raw = raw.strip()
    if not raw:
        raise ValueError("Valor vazio")
    # Se tem separador decimal (. ou ,) com exatamente 2 casas → reais
    match = re.fullmatch(r"(\d+)[.,](\d{2})", raw)
    if match:
        reais = int(match.group(1))
        centavos = int(match.group(2))
        return reais * 100 + centavos
    # Se é número inteiro → centavos
    if raw.isdigit():
        return int(raw)
    raise ValueError(f"Formato inválido: '{raw}'. Use '2500.00' ou '250000'.")


def _parse_date(raw: str) -> datetime:
    """Converte string de data para datetime com timezone UTC.

    Aceita: ISO 8601 (``"2024-01-15"``) ou formato BR (``"15/01/2024"``).

    Args:
        raw: Data bruta como string do CSV.

    Returns:
        Datetime com timezone UTC.

    Raises:
        ValueError: Se o formato não for reconhecido ou data vazia.
    """
    raw = raw.strip()
    if not raw:
        raise ValueError("Data vazia")
    # Formato BR: dd/mm/yyyy
    match = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", raw)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return datetime(year, month, day, tzinfo=timezone.utc)
    # ISO 8601
    try:
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        raise ValueError(f"Formato inválido: '{raw}'. Use 'dd/mm/yyyy' ou ISO 8601.")


async def import_csv(
    content: bytes,
    cliente_repo: ClienteRepository,
    fatura_repo: FaturaRepository,
) -> ImportResult:
    """Processa CSV de faturas.

    Args:
        content: Bytes do arquivo CSV (max 5MB).
        cliente_repo: Repository para upsert de clientes.
        fatura_repo: Repository para criação de faturas.

    Returns:
        ImportResult com contadores e lista de erros por linha.

    Raises:
        APIError 422: Se colunas obrigatórias estiverem faltando.
    """
    try:
        text = content.decode("utf-8-sig")  # BOM-safe
    except UnicodeDecodeError:
        raise APIError(
            422,
            "encoding-invalido",
            "Encoding inválido",
            "O arquivo deve estar em UTF-8.",
        )

    lines = text.strip().split("\n")
    if len(lines) < 2:
        raise APIError(
            422,
            "arquivo-vazio",
            "Arquivo vazio",
            "O CSV deve ter pelo menos um header e uma linha de dados.",
        )

    sep = _detect_separator(lines[0])
    reader = csv.DictReader(io.StringIO(text), delimiter=sep)

    # Normalize headers (strip whitespace, lowercase)
    header_map = {f.strip().lower(): f for f in (reader.fieldnames or [])}
    missing = REQUIRED_COLUMNS - set(header_map.keys())
    if missing:
        raise APIError(
            422,
            "colunas-faltando",
            "Colunas obrigatórias faltando",
            f"Colunas faltando: {', '.join(sorted(missing))}. "
            f"Colunas encontradas: {', '.join(sorted(header_map.keys()))}.",
        )

    result = ImportResult(
        total_linhas=0,
        importadas=0,
        ignoradas=0,
        rejeitadas=0,
        clientes_criados=0,
        clientes_existentes=0,
    )

    for i, row in enumerate(reader, start=1):
        result.total_linhas += 1
        # Normalize row keys
        norm_row = {k.strip().lower(): (v or "").strip() for k, v in row.items()}
        errors: list[ImportRowError] = []

        # Validar nome
        nome = norm_row.get("nome", "").strip()
        if not nome:
            errors.append(
                ImportRowError(linha=i, campo="nome", valor="", motivo="Nome é obrigatório.")
            )

        # Validar documento
        doc_raw = norm_row.get("documento", "")
        doc = None
        try:
            doc = Documento(doc_raw)
        except (ValueError, TypeError) as e:
            errors.append(ImportRowError(linha=i, campo="documento", valor=doc_raw, motivo=str(e)))

        # Validar valor
        valor_raw = norm_row.get("valor", "")
        valor_centavos = 0
        try:
            valor_centavos = _parse_valor(valor_raw)
            if valor_centavos <= 0:
                raise ValueError("Valor deve ser maior que zero.")
        except ValueError as e:
            errors.append(ImportRowError(linha=i, campo="valor", valor=valor_raw, motivo=str(e)))

        # Validar vencimento
        venc_raw = norm_row.get("vencimento", "")
        vencimento = None
        try:
            vencimento = _parse_date(venc_raw)
        except ValueError as e:
            errors.append(
                ImportRowError(linha=i, campo="vencimento", valor=venc_raw, motivo=str(e))
            )

        if errors:
            result.rejeitadas += 1
            result.erros.extend(errors)
            continue

        # Upsert cliente por documento
        cliente = await cliente_repo.get_by_documento(doc.valor)
        if cliente:
            result.clientes_existentes += 1
        else:
            cliente = Cliente(
                id=generate_id("cli"),
                nome=nome,
                documento=doc.valor,
                email=norm_row.get("email") or None,
                telefone=norm_row.get("telefone") or None,
            )
            cliente = await cliente_repo.create(cliente)
            result.clientes_criados += 1

        # Deduplicar por numero_nf + cliente_id
        numero_nf = norm_row.get("numero_nf") or None
        if numero_nf:
            exists = await fatura_repo.exists_by_numero_nf_and_cliente(numero_nf, cliente.id)
            if exists:
                result.ignoradas += 1
                continue

        # Criar fatura
        fatura = Fatura(
            id=generate_id("fat"),
            cliente_id=cliente.id,
            valor=valor_centavos,
            moeda="BRL",
            vencimento=vencimento,
            descricao=norm_row.get("descricao") or None,
            numero_nf=numero_nf,
        )
        await fatura_repo.create(fatura)
        result.importadas += 1

    return result
