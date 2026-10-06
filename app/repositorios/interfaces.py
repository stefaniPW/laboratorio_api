"""As portas. O dominio conhece ESTAS interfaces, nunca o Postgres."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol

from app.dominio.tipos import IndicesEmergeticos


class RepositorioFatores(Protocol):
    def versao_vigente(self) -> str: ...

    def transformidade(self, recurso: str, versao: str) -> Decimal | None: ...


class RepositorioIndices(Protocol):
    def salvar(self, safra_id: int, indices: IndicesEmergeticos, versao: str) -> None: ...

    def obter(self, safra_id: int) -> tuple[IndicesEmergeticos, str] | None: ...
