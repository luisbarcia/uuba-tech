import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.schemas.fatura import FaturaCreate, FaturaUpdate
from app.schemas.cobranca import CobrancaCreate
from app.schemas.common import ProblemDetail, PaginationMeta, ListResponse


# --- ClienteCreate ---


def test_cliente_create_valid():
    c = ClienteCreate(nome="Padaria", documento="12345678000190")
    assert c.nome == "Padaria"
    assert c.email is None
    assert c.telefone is None


def test_cliente_create_with_optionals():
    c = ClienteCreate(
        nome="Padaria",
        documento="12345678000190",
        email="a@b.com",
        telefone="5511999001234",
    )
    assert c.email == "a@b.com"


def test_cliente_create_missing_nome():
    with pytest.raises(ValidationError) as exc_info:
        ClienteCreate(documento="12345678000190")
    assert "nome" in str(exc_info.value)


def test_cliente_create_missing_documento():
    with pytest.raises(ValidationError) as exc_info:
        ClienteCreate(nome="Padaria")
    assert "documento" in str(exc_info.value)


# --- ClienteUpdate ---


def test_cliente_update_partial():
    u = ClienteUpdate(nome="Novo Nome")
    assert u.nome == "Novo Nome"
    assert u.email is None


def test_cliente_update_empty():
    u = ClienteUpdate()
    assert u.model_dump(exclude_unset=True) == {}


# --- FaturaCreate ---


def test_fatura_create_valid():
    f = FaturaCreate(
        cliente_id="cli_abc123",
        valor=250000,
        vencimento=datetime.now(timezone.utc),
    )
    assert f.valor == 250000


def test_fatura_create_valor_zero_rejected():
    with pytest.raises(ValidationError) as exc_info:
        FaturaCreate(
            cliente_id="cli_abc123",
            valor=0,
            vencimento=datetime.now(timezone.utc),
        )
    assert "greater_than" in str(exc_info.value).lower() or "gt" in str(exc_info.value).lower()


def test_fatura_create_valor_negative_rejected():
    with pytest.raises(ValidationError):
        FaturaCreate(
            cliente_id="cli_abc123",
            valor=-100,
            vencimento=datetime.now(timezone.utc),
        )


def test_fatura_create_missing_cliente_id():
    with pytest.raises(ValidationError):
        FaturaCreate(valor=100, vencimento=datetime.now(timezone.utc))


def test_fatura_create_missing_vencimento():
    with pytest.raises(ValidationError):
        FaturaCreate(cliente_id="cli_abc", valor=100)


# --- FaturaUpdate ---


def test_fatura_update_valid_status():
    for status in ("pendente", "pago", "vencido", "cancelado"):
        u = FaturaUpdate(status=status)
        assert u.status == status


def test_fatura_update_invalid_status():
    with pytest.raises(ValidationError):
        FaturaUpdate(status="invalido")


def test_fatura_update_empty():
    u = FaturaUpdate()
    assert u.model_dump(exclude_unset=True) == {}


# --- CobrancaCreate ---


def test_cobranca_create_valid():
    c = CobrancaCreate(
        fatura_id="fat_abc",
        cliente_id="cli_abc",
        tipo="lembrete",
    )
    assert c.canal == "whatsapp"  # default
    assert c.tom is None


def test_cobranca_create_all_tipos():
    for tipo in ("lembrete", "cobranca", "follow_up", "escalacao"):
        c = CobrancaCreate(fatura_id="fat_test", cliente_id="cli_test", tipo=tipo)
        assert c.tipo == tipo


def test_cobranca_create_invalid_tipo():
    with pytest.raises(ValidationError):
        CobrancaCreate(fatura_id="fat_test", cliente_id="cli_test", tipo="invalido")


def test_cobranca_create_all_canais():
    for canal in ("whatsapp", "email", "sms"):
        c = CobrancaCreate(
            fatura_id="fat_test", cliente_id="cli_test", tipo="lembrete", canal=canal
        )
        assert c.canal == canal


def test_cobranca_create_invalid_canal():
    with pytest.raises(ValidationError):
        CobrancaCreate(
            fatura_id="fat_test", cliente_id="cli_test", tipo="lembrete", canal="telegram"
        )


def test_cobranca_create_all_tons():
    for tom in ("amigavel", "neutro", "firme", "urgente"):
        c = CobrancaCreate(fatura_id="fat_test", cliente_id="cli_test", tipo="lembrete", tom=tom)
        assert c.tom == tom


def test_cobranca_create_invalid_tom():
    with pytest.raises(ValidationError):
        CobrancaCreate(
            fatura_id="fat_test", cliente_id="cli_test", tipo="lembrete", tom="agressivo"
        )


# --- Common schemas ---


def test_pagination_meta():
    p = PaginationMeta(total=100, page_size=50, has_more=True, offset=0)
    assert p.total == 100


def test_list_response():
    lr = ListResponse(
        data=[{"id": "1"}],
        pagination=PaginationMeta(total=1, page_size=50, has_more=False),
    )
    assert lr.object == "list"
    assert len(lr.data) == 1


def test_problem_detail():
    pd = ProblemDetail(
        type="https://api.uubatech.com/errors/teste",
        title="Erro de teste",
        status=422,
        detail="Detalhe do erro",
    )
    assert pd.status == 422
    assert pd.errors == []
