from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.dominio.tipos import CategoriaFluxo, FluxoEmergetico
from app.main import app

# Inventario de referencia. Valores didaticos, conferidos a mao em sala:
# R = 100, N = 50, M = 30 (MR 10 + MN 20), S = 20 (SR 5 + SN 15)
# Y = 200 | F = M + S = 50 | renovaveis = 115 | nao renovaveis = 85
GOLDEN = [
    ("chuva", CategoriaFluxo.R, "100"),
    ("solo", CategoriaFluxo.N, "50"),
    ("fertilizante", CategoriaFluxo.MR, "10"),
    ("diesel", CategoriaFluxo.MN, "20"),
    ("mao_de_obra", CategoriaFluxo.SR, "5"),
    ("frete", CategoriaFluxo.SN, "15"),
]

EP_GOLDEN = Decimal("1000")


@pytest.fixture
def fluxos_golden() -> list[FluxoEmergetico]:
    return [FluxoEmergetico(r, c, Decimal(v)) for r, c, v in GOLDEN]


@pytest.fixture
def corpo_golden() -> dict:
    return {
        "fluxos": [{"recurso": r, "categoria": c.value, "emergia_sej": v}
                   for r, c, v in GOLDEN],
        "energia_produto_j": str(EP_GOLDEN),
    }


@pytest.fixture
def cliente() -> TestClient:
    return TestClient(app)
