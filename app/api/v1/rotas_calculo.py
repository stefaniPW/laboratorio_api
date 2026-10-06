"""A rota traduz HTTP e dominio -- e nada mais. Sem formula, sem SQL, sem try/except."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dto import CalculoRequestDTO, IndicesResponseDTO
from app.infra.providers import obter_servico_calculo
from app.servicos.servico_calculo import ServicoCalculo

router = APIRouter(prefix="/v1", tags=["calculo emergetico"])


def _resposta(safra_id: int, indices, versao: str) -> IndicesResponseDTO:
    return IndicesResponseDTO(
        safra_id=safra_id, versao_fatores=versao,
        y=indices.y, eyr=indices.eyr, elr=indices.elr,
        esi=indices.esi, eii=indices.eii, percentual_r=indices.percentual_r,
    )


@router.post("/safras/{safra_id}/calculos",
             response_model=IndicesResponseDTO,
             status_code=status.HTTP_201_CREATED)
def calcular(safra_id: int,
             req: CalculoRequestDTO,
             servico: ServicoCalculo = Depends(obter_servico_calculo)):
    # def, nao async: o motor e CPU-bound -> thread pool, nao event loop
    indices, versao = servico.calcular_para_safra(safra_id, req)
    return _resposta(safra_id, indices, versao)


@router.get("/safras/{safra_id}/indices", response_model=IndicesResponseDTO)
def indices(safra_id: int,
            servico: ServicoCalculo = Depends(obter_servico_calculo)):
    encontrado = servico.obter_indices(safra_id)
    if encontrado is None:
        raise HTTPException(status_code=404, detail=f"safra {safra_id} sem calculo")
    return _resposta(safra_id, *encontrado)
