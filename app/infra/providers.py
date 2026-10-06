"""O UNICO ponto de montagem da aplicacao.

Trocar FatoresEmMemoria por FatoresPostgres e uma linha, e nenhuma outra camada
sabe que isso aconteceu.
"""

from __future__ import annotations

from functools import lru_cache

from app.repositorios.memoria import FatoresEmMemoria, IndicesEmMemoria
from app.servicos.servico_calculo import ServicoCalculo


@lru_cache(maxsize=1)
def _servico() -> ServicoCalculo:
    return ServicoCalculo(FatoresEmMemoria(), IndicesEmMemoria())


def obter_servico_calculo() -> ServicoCalculo:
    return _servico()
