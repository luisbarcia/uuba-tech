from fastapi import Request


def get_request_id(request: Request) -> str:
    """Extrai o request_id injetado pelo RequestIdMiddleware."""
    return request.state.request_id
