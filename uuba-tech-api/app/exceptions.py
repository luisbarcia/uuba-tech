class APIError(Exception):
    """Erro de API seguindo RFC 9457 (Problem Details for HTTP APIs).

    Capturado pelo exception handler em main.py e serializado como JSON
    com campos ``type``, ``title``, ``status``, ``detail``.

    Args:
        status: HTTP status code (ex: 404, 409, 422).
        error_type: Identificador do erro (ex: ``"cliente-nao-encontrado"``).
        title: Título legível do erro.
        detail: Descrição detalhada do problema.

    Example:
        >>> raise APIError(404, "fatura-nao-encontrada", "Fatura não encontrada", "Fatura fat_abc não existe.")
    """

    def __init__(self, status: int, error_type: str, title: str, detail: str):
        self.status = status
        self.error_type = error_type
        self.title = title
        self.detail = detail
