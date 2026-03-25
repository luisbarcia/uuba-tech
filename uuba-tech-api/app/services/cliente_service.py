"""Serviço de clientes.

Persistência delegada ao ClienteRepository (DP-04).
Exportação de dados pessoais conforme LGPD Art. 18.
"""

from datetime import datetime, timezone

from app.domain.repositories.cliente_repository import ClienteRepository
from app.domain.repositories.cobranca_repository import CobrancaRepository
from app.domain.repositories.fatura_repository import FaturaRepository
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteMetricas, ClienteUpdate
from app.utils.ids import generate_id


def _aware(dt: datetime) -> datetime:
    """Garante que datetime tem timezone (defensivo contra DBs que retornam naive)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def create_cliente(repo: ClienteRepository, data: ClienteCreate) -> Cliente:
    """Cria um novo cliente. Levanta APIError 409 se documento já existir."""
    cliente = Cliente(id=generate_id("cli"), **data.model_dump())
    return await repo.create(cliente)


async def list_clientes(
    repo: ClienteRepository,
    telefone: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Cliente], int]:
    """Lista clientes com paginação.

    Returns:
        Tupla (lista de clientes, total de registros).
    """
    return await repo.list_by_filters(telefone=telefone, limit=limit, offset=offset)


async def get_cliente(repo: ClienteRepository, cliente_id: str) -> Cliente | None:
    """Busca cliente por ID. Retorna None se não encontrado."""
    return await repo.get_by_id(cliente_id)


async def update_cliente(
    repo: ClienteRepository, cliente_id: str, data: ClienteUpdate
) -> Cliente | None:
    """Atualiza campos do cliente (patch parcial). Retorna None se não encontrado."""
    cliente = await repo.get_by_id(cliente_id)
    if not cliente:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cliente, key, value)
    return await repo.update(cliente)


async def anonimizar_cliente(repo: ClienteRepository, cliente_id: str) -> bool:
    """Anonimiza dados PII do cliente e mensagens de cobrança (LGPD Art. 18 VI).

    Returns:
        True se anonimizado, False se não encontrado.
    """
    anonimizado = await repo.anonimizar(cliente_id)
    if anonimizado:
        await repo.anonimizar_mensagens(cliente_id)
    return anonimizado


async def get_metricas(fatura_repo: FaturaRepository, cliente_id: str) -> ClienteMetricas:
    """Calcula métricas financeiras do cliente: DSO, total em aberto, faturas vencidas."""
    now = datetime.now(timezone.utc)
    faturas_list, _ = await fatura_repo.list_by_filters(cliente_id=cliente_id, limit=10000)

    em_aberto = [f for f in faturas_list if f.status in ("pendente", "vencido")]
    vencidas = [f for f in em_aberto if _aware(f.vencimento) < now]

    total_em_aberto = sum(f.valor for f in em_aberto)
    total_vencido = sum(f.valor for f in vencidas)

    dso_dias = 0.0
    pagas = [f for f in faturas_list if f.status == "pago" and f.pago_em]
    if pagas:
        total_dias = sum((_aware(f.pago_em) - _aware(f.vencimento)).days for f in pagas)
        dso_dias = total_dias / len(pagas)

    return ClienteMetricas(
        dso_dias=dso_dias,
        total_em_aberto=total_em_aberto,
        total_vencido=total_vencido,
        faturas_em_aberto=len(em_aberto),
        faturas_vencidas=len(vencidas),
    )


async def exportar_dados_pessoais(
    cliente: Cliente,
    fatura_repo: FaturaRepository,
    cobranca_repo: CobrancaRepository,
) -> dict:
    """Exporta todos os dados pessoais do titular (LGPD Art. 18 II/V).

    Reúne dados cadastrais, faturas e cobranças do cliente em um
    dicionário serializável para entrega ao titular.

    Args:
        cliente: Modelo do cliente cujos dados serão exportados.
        fatura_repo: Repository de faturas para busca por cliente.
        cobranca_repo: Repository de cobranças para busca por cliente.

    Returns:
        Dict com chaves ``titular``, ``faturas``, ``cobrancas``,
        ``exportado_em`` e referência LGPD.
    """
    faturas, _ = await fatura_repo.list_by_filters(cliente_id=cliente.id, limit=10000)
    cobrancas, _ = await cobranca_repo.list_by_filters(cliente_id=cliente.id, limit=10000)

    return {
        "titular": {
            "id": cliente.id,
            "nome": cliente.nome,
            "documento": cliente.documento,
            "email": cliente.email,
            "telefone": cliente.telefone,
            "cadastrado_em": cliente.created_at.isoformat() if cliente.created_at else None,
        },
        "faturas": [
            {
                "id": f.id,
                "valor": f.valor,
                "moeda": f.moeda,
                "status": f.status,
                "vencimento": f.vencimento.isoformat() if f.vencimento else None,
                "descricao": f.descricao,
                "numero_nf": f.numero_nf,
                "pago_em": f.pago_em.isoformat() if f.pago_em else None,
            }
            for f in faturas
        ],
        "cobrancas": [
            {
                "id": c.id,
                "fatura_id": c.fatura_id,
                "tipo": c.tipo,
                "canal": c.canal,
                "mensagem": c.mensagem,
                "tom": c.tom,
                "status": c.status,
                "enviado_em": c.enviado_em.isoformat() if c.enviado_em else None,
            }
            for c in cobrancas
        ],
        "exportado_em": datetime.now(timezone.utc).isoformat(),
        "lgpd": "Exportação conforme Art. 18, II e V da Lei 13.709/2018",
    }
