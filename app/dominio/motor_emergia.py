"""NUCLEO PURO. Sem I/O, sem relogio, sem estado, sem import de framework.

Uma funcao: entra inventario, sai indice. A mesma entrada devolve a mesma saida
hoje, na maquina do corretor e na banca da AV4 -- e e isso que o torna auditavel.
"""

from __future__ import annotations

from collections.abc import Iterable, Set
from decimal import ROUND_HALF_EVEN, Decimal, localcontext

from .erros import EnergiaProdutoInvalida, FluxosInsuficientes
from .tipos import CategoriaFluxo, FluxoEmergetico, IndicesEmergeticos

_RENOVAVEIS = frozenset({CategoriaFluxo.R, CategoriaFluxo.MR, CategoriaFluxo.SR})
_NAO_RENOVAVEIS = frozenset({CategoriaFluxo.N, CategoriaFluxo.MN, CategoriaFluxo.SN})
_COMPRADOS = frozenset({CategoriaFluxo.MR, CategoriaFluxo.MN,
                        CategoriaFluxo.SR, CategoriaFluxo.SN})  # F = M + S

SEIS_CASAS = Decimal("1E-6")


def _soma(fluxos: Iterable[FluxoEmergetico], categorias: Set[CategoriaFluxo]) -> Decimal:
    total = Decimal(0)
    for fluxo in fluxos:
        if fluxo.categoria in categorias:
            total += fluxo.emergia_sej
    return total


def calcular_indices(
    fluxos: list[FluxoEmergetico],
    energia_produto_j: Decimal,
) -> IndicesEmergeticos:
    if not fluxos:
        raise FluxosInsuficientes("nenhum fluxo informado")
    if energia_produto_j <= 0:
        raise EnergiaProdutoInvalida("Ep deve ser positiva")

    with localcontext() as ctx:      # nao vaza estado global: o resultado nao
        ctx.prec = 28                # depende de quem configurou o processo antes
        ctx.rounding = ROUND_HALF_EVEN   # vies minimo no empate

        renovaveis = _soma(fluxos, _RENOVAVEIS)
        nao_renovaveis = _soma(fluxos, _NAO_RENOVAVEIS)
        comprados = _soma(fluxos, _COMPRADOS)
        y = renovaveis + nao_renovaveis      # Y = R + N + M + S

        if renovaveis == 0:
            raise FluxosInsuficientes("denominador do ELR nulo: nenhum fluxo renovavel")
        if comprados == 0:
            raise FluxosInsuficientes("F = 0: nada comprado da economia, EYR indefinido")

        eyr = y / comprados
        elr = nao_renovaveis / renovaveis
        if elr == 0:
            raise FluxosInsuficientes("ELR = 0: ESI indefinido")
        esi = eyr / elr
        eii = elr / eyr
        percentual_r = renovaveis / y * Decimal(100)

        # Quantizacao unica, no fim: arredondar no meio produz erro duplo.
        return IndicesEmergeticos(
            y=y.quantize(SEIS_CASAS),
            eyr=eyr.quantize(SEIS_CASAS),
            elr=elr.quantize(SEIS_CASAS),
            esi=esi.quantize(SEIS_CASAS),
            eii=eii.quantize(SEIS_CASAS),
            percentual_r=percentual_r.quantize(SEIS_CASAS),
        )
