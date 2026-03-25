"""Geração de identificadores prefixados com nanoid."""

import nanoid


def generate_id(prefix: str, size: int = 12) -> str:
    """Gera ID com prefixo descritivo. Ex: fat_abc123def456"""
    return f"{prefix}_{nanoid.generate(size=size)}"
