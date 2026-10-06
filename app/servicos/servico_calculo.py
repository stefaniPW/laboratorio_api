"""Camada de servico: orquestra e nao contem formula alguma.

Se aparecer uma divisao aqui, ela esta na camada errada.
"""

from __future__ import annotations

from app.dominio import motor_emergia
from app.dominio.tipos import FluxoEmergetico, IndicesEmergeticos
from app.infra.log import log
from app.repositorios.interfaces import RepositorioFatores, RepositorioIndices


class ServicoCalculo:
    def __init__(self, fatores: RepositorioFatores, indices: RepositorioIndices) -> None:
        self._fatores = fatores
        self._indices = indices

    def calcular_para_safra(self, safra_id: int, req) -> tuple[IndicesEmergeticos, str]:
        versao = self._fatores.versao_vigente()
        fluxos = [
            FluxoEmergetico(f.recurso, f.categoria, f.emergia_sej) for f in req.fluxos
        ]

        log("calculo.iniciado", safra_id=safra_id, n_fluxos=len(fluxos),
            versao_fatores=versao)

        resultado = motor_emergia.calcular_indices(fluxos, req.energia_produto_j)
        self._indices.salvar(safra_id, resultado, versao)

        log("calculo.concluido", safra_id=safra_id, esi=str(resultado.esi),
            versao_fatores=versao)
        return resultado, versao

    def obter_indices(self, safra_id: int) -> tuple[IndicesEmergeticos, str] | None:
        return self._indices.obter(safra_id)
