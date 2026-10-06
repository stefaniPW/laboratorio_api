"""PRONTO -- exemplo 2 de 3.

A propriedade que o entregavel cobra primeiro: a mesma entrada, em qualquer
ordem, produz o mesmo resultado. Sem isso o numero nao e auditavel.
"""

from __future__ import annotations

import random
from decimal import Decimal

from app.dominio.motor_emergia import calcular_indices


def test_permutacao_do_inventario_nao_altera_o_resultado(fluxos_golden):
    referencia = calcular_indices(fluxos_golden, Decimal("1000"))
    for semente in range(20):
        embaralhado = list(fluxos_golden)
        random.Random(semente).shuffle(embaralhado)
        assert calcular_indices(embaralhado, Decimal("1000")) == referencia


def test_mil_execucoes_zero_variacao(fluxos_golden):
    resultados = {calcular_indices(fluxos_golden, Decimal("1000")) for _ in range(1000)}
    assert len(resultados) == 1


def test_indices_sao_imutaveis(fluxos_golden):
    indices = calcular_indices(fluxos_golden, Decimal("1000"))
    try:
        indices.esi = Decimal("99")
    except (AttributeError, TypeError):
        return
    raise AssertionError("valor cientifico nao deveria aceitar atribuicao")
