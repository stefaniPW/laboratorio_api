"""PRONTO -- exemplo 3 de 3.

A fronteira recusa o que o motor nao saberia tratar, e recusa com o status certo.
Este arquivo passa hoje; o TODO do PASSO 3 e o que falta para os outros casos.
"""

from __future__ import annotations


def test_caminho_feliz_devolve_201_com_os_seis_indices(cliente, corpo_golden):
    r = cliente.post("/v1/safras/42/calculos", json=corpo_golden)
    assert r.status_code == 201
    corpo = r.json()
    for campo in ("y", "eyr", "elr", "esi", "eii", "percentual_r"):
        assert isinstance(corpo[campo], str)   # decimal atravessa a rede como string
    assert corpo["versao_fatores"] == "odum-2024.1"


def test_categoria_fora_do_enum_morre_na_fronteira(cliente, corpo_golden):
    corpo_golden["fluxos"][0]["categoria"] = "X"
    r = cliente.post("/v1/safras/42/calculos", json=corpo_golden)
    assert r.status_code == 422
    # um unico formato de erro na API, inclusive para o 422 do framework
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["status"] == 422


def test_recurso_e_normalizado_antes_de_chegar_ao_dominio(cliente, corpo_golden):
    corpo_golden["fluxos"][0]["recurso"] = "  Chuva  "
    assert cliente.post("/v1/safras/42/calculos", json=corpo_golden).status_code == 201


def test_campo_extra_no_fluxo_e_rejeitado(cliente, corpo_golden):
    corpo_golden["fluxos"][0]["quantidadee"] = "3"
    assert cliente.post("/v1/safras/42/calculos", json=corpo_golden).status_code == 422


def test_path_nao_inteiro_morre_sem_nenhum_if(cliente, corpo_golden):
    assert cliente.post("/v1/safras/abc/calculos", json=corpo_golden).status_code == 422


def test_toda_resposta_carrega_o_request_id(cliente, corpo_golden):
    r = cliente.post("/v1/safras/7/calculos", json=corpo_golden)
    assert r.headers.get("x-request-id")


def test_safra_sem_calculo_devolve_404_em_problem_json(cliente):
    r = cliente.get("/v1/safras/999/indices")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
    for campo in ("type", "title", "status", "detail", "instance"):
        assert campo in r.json()
