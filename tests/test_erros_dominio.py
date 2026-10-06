"""PRONTO -- exemplo 1 de 3.

Os tres erros de dominio, cada um com a sua condicao. Repare que nenhum deles
depende de HTTP, de banco ou de relogio: o motor e testavel em microssegundos.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.dominio.erros import EnergiaProdutoInvalida, FluxosInsuficientes
from app.dominio.motor_emergia import calcular_indices
from app.dominio.tipos import CategoriaFluxo, FluxoEmergetico


def test_inventario_vazio_levanta_fluxos_insuficientes():
    with pytest.raises(FluxosInsuficientes, match="nenhum fluxo"):
        calcular_indices([], Decimal("1000"))


def test_energia_do_produto_nao_positiva_levanta_erro(fluxos_golden):
    with pytest.raises(EnergiaProdutoInvalida):
        calcular_indices(fluxos_golden, Decimal("0"))


def test_sem_fluxo_renovavel_o_elr_fica_indefinido():
    fluxos = [FluxoEmergetico("solo", CategoriaFluxo.N, Decimal("50")),
              FluxoEmergetico("diesel", CategoriaFluxo.MN, Decimal("20"))]
    with pytest.raises(FluxosInsuficientes, match="denominador do ELR"):
        calcular_indices(fluxos, Decimal("1000"))


def test_nada_comprado_da_economia_deixa_o_eyr_indefinido():
    fluxos = [FluxoEmergetico("chuva", CategoriaFluxo.R, Decimal("100")),
              FluxoEmergetico("solo", CategoriaFluxo.N, Decimal("50"))]
    with pytest.raises(FluxosInsuficientes, match="F = 0"):
        calcular_indices(fluxos, Decimal("1000"))


def test_float_recusado_na_construcao_do_fluxo():
    with pytest.raises(TypeError, match="float"):
        FluxoEmergetico("chuva", CategoriaFluxo.R, 100.0)
