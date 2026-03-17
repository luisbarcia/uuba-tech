from pydantic import BaseModel, Field
from typing import Any


class ProblemDetail(BaseModel):
    """RFC 9457 Problem Details for HTTP APIs."""

    type: str = Field(description="URI que identifica o tipo do problema")
    title: str = Field(description="Resumo curto e legível do problema")
    status: int = Field(description="Código HTTP do erro")
    detail: str = Field(description="Explicação detalhada do problema")
    instance: str = Field(default="", description="URI da ocorrência específica")
    request_id: str = Field(default="", description="ID único da requisição para rastreio")
    errors: list[dict[str, Any]] = Field(
        default=[],
        description="Lista de erros de validação por campo",
    )


class PaginationMeta(BaseModel):
    total: int = Field(description="Total de registros encontrados")
    page_size: int = Field(description="Quantidade de itens por página")
    has_more: bool = Field(description="Indica se existem mais páginas")
    offset: int = Field(default=0, description="Posição inicial da página atual")


class ListResponse(BaseModel):
    object: str = Field(default="list", description="Tipo do objeto retornado")
    data: list[Any] = Field(description="Lista de recursos retornados")
    pagination: PaginationMeta = Field(description="Metadados de paginação")
