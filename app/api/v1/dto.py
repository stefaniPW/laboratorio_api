"""A fronteira. Validar checa e esquece; parsear produz um tipo confiavel.

Convencao da disciplina: extra="forbid" por padrao em todo DTO de entrada.
Abrir excecao e decisao consciente, registrada -- nunca omissao.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.dominio.tipos import CategoriaFluxo


class FluxoEntradaDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")   # campo extra = 422

    recurso: str = Field(min_length=1, max_length=120)
    categoria: CategoriaFluxo                   # Enum: "X" nem entra
    emergia_sej: Decimal = Field(gt=0)

    @field_validator("recurso")
    @classmethod
    def normalizar_recurso(cls, v: str) -> str:
        return v.strip().lower()                # "  Diesel " == "diesel"


class CalculoRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fluxos: list[FluxoEntradaDTO] = Field(min_length=1)
    energia_produto_j: Decimal = Field(gt=0)


class IndicesResponseDTO(BaseModel):
    """Contrato de saida: filtra, converte e documenta. So o que o dashboard precisa."""

    safra_id: int
    y: Decimal
    eyr: Decimal
    elr: Decimal
    esi: Decimal
    eii: Decimal
    percentual_r: Decimal
    versao_fatores: str          # com QUAL tabela se calculou

    @field_serializer("y", "eyr", "elr", "esi", "eii", "percentual_r")
    def serializar_decimal(self, v: Decimal) -> str:
        """JSON nao tem tipo decimal. Float na borda desfaz o motor inteiro."""
        return str(v)
