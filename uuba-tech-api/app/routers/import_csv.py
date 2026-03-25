"""Router para importação de faturas via CSV."""

from fastapi import APIRouter, Depends, UploadFile, File

from app.auth.api_key import verify_api_key
from app.database import get_cliente_repository, get_fatura_repository
from app.exceptions import APIError
from app.schemas.import_csv import ImportResult
from app.services import import_service

router = APIRouter(
    prefix="/api/v1/import",
    tags=["import"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "/csv",
    response_model=ImportResult,
    summary="Importar faturas via CSV",
    description=(
        "Upload de CSV com faturas vencidas para onboarding de carteiras. "
        "Colunas obrigatórias: nome, documento, valor, vencimento. "
        "Colunas opcionais: email, telefone, numero_nf, descricao. "
        "Separador auto-detectado (vírgula ou ponto-e-vírgula)."
    ),
)
async def import_csv(
    file: UploadFile = File(...),
    cliente_repo=Depends(get_cliente_repository),
    fatura_repo=Depends(get_fatura_repository),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise APIError(
            422,
            "formato-invalido",
            "Formato de arquivo inválido",
            "Apenas arquivos .csv são aceitos.",
        )

    content = await file.read()

    if len(content) > 5 * 1024 * 1024:
        raise APIError(
            422,
            "arquivo-grande-demais",
            "Arquivo muito grande",
            "O arquivo CSV deve ter no máximo 5MB.",
        )

    if len(content) == 0:
        raise APIError(
            422,
            "arquivo-vazio",
            "Arquivo vazio",
            "O arquivo CSV está vazio.",
        )

    return await import_service.import_csv(content, cliente_repo, fatura_repo)
