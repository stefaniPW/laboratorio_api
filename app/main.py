"""Monta a aplicacao: middleware de request_id, routers e os handlers de erro.

Tres handlers substituem todos os try/except da aplicacao. O dominio lanca, o
handler traduz, a rota nao sabe de erro.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import rotas_calculo
from app.dominio import erros
from app.infra.log import entrar_no_contexto, log, novo_request_id

app = FastAPI(
    title="AGROEMERGIA -- API de calculo emergetico",
    version="0.1.0",
    description="Fatia vertical: rota -> service -> motor puro -> repositorio.",
)
app.include_router(rotas_calculo.router)


@app.middleware("http")
async def contexto_de_requisicao(request: Request, call_next):
    """Um ID por requisicao reconstroi a historia de um calculo."""
    request_id = request.headers.get("x-request-id") or novo_request_id()
    entrar_no_contexto(request_id, request.url.path)
    resposta = await call_next(request)
    resposta.headers["x-request-id"] = request_id
    return resposta


def _problem(status_code: int, tipo: str, titulo: str, detalhe: str, request: Request,
             extras: dict | None = None):
    """Corpo de erro na RFC 9457: type, title, status, detail, instance.

    Campos extras entram no mesmo objeto: a RFC prevê extensoes, e e assim que
    o detalhe por campo do Pydantic chega ao cliente sem sair do padrao.
    """
    corpo = {"type": f"https://agroemergia.sc/erros/{tipo}",
             "title": titulo, "status": status_code,
             "detail": detalhe, "instance": str(request.url.path)}
    if extras:
        corpo.update(extras)
    return JSONResponse(status_code=status_code,
                        media_type="application/problem+json", content=corpo)


@app.exception_handler(StarletteHTTPException)
async def h_http(request: Request, exc: StarletteHTTPException):
    """404 e demais erros do proprio framework, no mesmo formato dos nossos.

    Sem este handler o 404 sairia como {"detail": ...} em application/json --
    dois formatos de erro na mesma API, e o cliente tendo de tratar os dois.
    """
    return _problem(exc.status_code, "recurso-nao-encontrado" if exc.status_code == 404
                    else f"http-{exc.status_code}",
                    "Recurso nao encontrado" if exc.status_code == 404 else "Erro HTTP",
                    str(exc.detail), request)


@app.exception_handler(RequestValidationError)
async def h_validacao(request: Request, exc: RequestValidationError):
    """422 do Pydantic -- e 400 quando o corpo nem chega a ser JSON.

    Corpo malformado e sintaxe: nao ha o que interpretar, e o status e 400.
    Corpo valido com valor fora do dominio e semantica: 422.
    """
    erros = exc.errors()
    sintatico = any(e.get("type") == "json_invalid" for e in erros)
    campos = [{"campo": ".".join(str(p) for p in e.get("loc", ())),
               "erro": e.get("msg", "")} for e in erros]
    if sintatico:
        return _problem(status.HTTP_400_BAD_REQUEST, "corpo-malformado",
                        "Corpo da requisicao nao e JSON valido",
                        "malformacao sintatica: nao ha o que interpretar", request,
                        {"erros": campos})
    return _problem(status.HTTP_422_UNPROCESSABLE_ENTITY, "requisicao-invalida",
                    "Requisicao nao processavel",
                    "sintaxe ok, semantica nao: ver o campo 'erros'", request,
                    {"erros": campos})


@app.exception_handler(erros.EnergiaProdutoInvalida)
async def h_ep(request: Request, exc: erros.EnergiaProdutoInvalida):
    # 422: sintaxe valida, semantica nao
    log("calculo.recusado", level="warning", erro="energia-produto-invalida")
    return _problem(status.HTTP_422_UNPROCESSABLE_ENTITY, "energia-produto-invalida",
                    "Energia do produto invalida", str(exc), request)

@app.exception_handler(erros.FluxosInsuficientes)
async def h_fluxos_insuficientes(request: Request, exc: erros.FluxosInsuficientes):
    log("calculo.recusado", level="warning", erro="fluxos-insuficientes")
    return _problem(status.HTTP_422_UNPROCESSABLE_ENTITY, "fluxos-insuficientes",
                    "Fluxos insuficientes", str(exc), request)

@app.exception_handler(erros.FatorConversaoNaoEncontrado)
async def h_fator_conversao(request: Request, exc: erros.FatorConversaoNaoEncontrado):
    log("calculo.recusado", level="warning", erro="fator-conversao-nao-encontrado")
    return _problem(status.HTTP_422_UNPROCESSABLE_ENTITY, "fator-conversao-nao-encontrado",
                    "Fator de conversao nao encontrado", str(exc), request)


