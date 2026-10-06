"""Tipos do dominio. Imutaveis por construcao: valor cientifico nao se edita, se recalcula."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class CategoriaFluxo(str, Enum):
    """As seis categorias emergeticas. Um valor fora desta lista nem entra na aplicacao."""

    R = "R"      # renovavel da natureza (sol, chuva, vento)
    N = "N"      # nao renovavel da natureza (solo perdido, agua fossil)
    MR = "MR"    # material comprado, parcela renovavel
    MN = "MN"    # material comprado, parcela nao renovavel
    SR = "SR"    # servico comprado, parcela renovavel
    SN = "SN"    # servico comprado, parcela nao renovavel


@dataclass(frozen=True, slots=True)
class FluxoEmergetico:
    """Um item do inventario, ja convertido para sej.

    A validacao de dominio comeca na construcao, nao na formula: float e valor
    nao positivo sao recusados aqui, antes de chegarem a qualquer divisao.
    """

    recurso: str
    categoria: CategoriaFluxo
    emergia_sej: Decimal

    def __post_init__(self) -> None:
        if isinstance(self.emergia_sej, float):
            raise TypeError("float no caminho do dado cientifico: use Decimal")
        if not isinstance(self.emergia_sej, Decimal):
            raise TypeError("emergia_sej deve ser Decimal")
        if self.emergia_sej <= 0:
            raise ValueError(f"fluxo '{self.recurso}' com emergia nao positiva")


@dataclass(frozen=True, slots=True)
class IndicesEmergeticos:
    """Os seis indices do entregavel, cada um quantizado uma unica vez, no final."""

    y: Decimal
    eyr: Decimal
    elr: Decimal
    esi: Decimal
    eii: Decimal
    percentual_r: Decimal
