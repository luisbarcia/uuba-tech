"""Schemas para importação de faturas via CSV."""

from pydantic import BaseModel, Field


class ImportRowError(BaseModel):
    """Erro de validação de uma linha do CSV."""

    linha: int = Field(description="Número da linha no CSV (começando em 1)")
    campo: str = Field(description="Nome do campo com erro")
    valor: str = Field(description="Valor recebido")
    motivo: str = Field(description="Descrição do erro")


class ImportResult(BaseModel):
    """Resultado da importação de CSV."""

    status: str = "ok"
    total_linhas: int = Field(description="Total de linhas processadas (excluindo header)")
    importadas: int = Field(description="Faturas criadas com sucesso")
    ignoradas: int = Field(description="Linhas ignoradas (duplicata por numero_nf)")
    rejeitadas: int = Field(description="Linhas com erro de validação")
    erros: list[ImportRowError] = Field(default_factory=list)
    clientes_criados: int = Field(description="Novos clientes criados")
    clientes_existentes: int = Field(description="Clientes já existentes reutilizados")
