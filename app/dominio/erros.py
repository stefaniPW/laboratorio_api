"""Erros de dominio. Nao conhecem HTTP: quem traduz e o handler em app/main.py."""


class ErroDeDominio(Exception):
    """Base de todo erro que o motor levanta. Nunca vira 500."""


class FluxosInsuficientes(ErroDeDominio):
    """Inventario vazio, ou incompleto de forma que algum indice fica indefinido."""


class EnergiaProdutoInvalida(ErroDeDominio):
    """Ep <= 0. Sem energia no produto nao existe transformidade."""


class FatorConversaoNaoEncontrado(ErroDeDominio):
    """Nao existe transformidade cadastrada para o recurso na versao vigente."""

    def __init__(self, recurso: str, versao: str) -> None:
        self.recurso = recurso
        self.versao = versao
        super().__init__(f"sem fator de conversao para '{recurso}' na versao {versao}")
