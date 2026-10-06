"""Implementacoes em memoria: trocar por Postgres nao toca no dominio nem na rota."""

from __future__ import annotations

from decimal import Decimal

from app.dominio.tipos import IndicesEmergeticos

VERSAO_VIGENTE = "odum-2024.1"

_TRANSFORMIDADES: dict[str, Decimal] = {
    "chuva": Decimal("30500"),
    "solo": Decimal("74000"),
    "diesel": Decimal("66000000"),
    "fertilizante": Decimal("38000000"),
    "mao_de_obra": Decimal("120000000"),
}


class FatoresEmMemoria:
    def versao_vigente(self) -> str:
        return VERSAO_VIGENTE

    def transformidade(self, recurso: str, versao: str) -> Decimal | None:
        if versao != VERSAO_VIGENTE:
            return None
        return _TRANSFORMIDADES.get(recurso)


class IndicesEmMemoria:
    def __init__(self) -> None:
        self._dados: dict[int, tuple[IndicesEmergeticos, str]] = {}

    def salvar(self, safra_id: int, indices: IndicesEmergeticos, versao: str) -> None:
        self._dados[safra_id] = (indices, versao)

    def obter(self, safra_id: int) -> tuple[IndicesEmergeticos, str] | None:
        return self._dados.get(safra_id)
