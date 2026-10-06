"""Log estruturado e request_id. Todo o nao-determinismo da aplicacao mora aqui:
relogio, geracao de ID e escrita em stdout.
"""

from __future__ import annotations

import json
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone

_request_id: ContextVar[str] = ContextVar("request_id", default="-")
_path: ContextVar[str] = ContextVar("path", default="-")


def novo_request_id() -> str:
    return uuid.uuid4().hex


def entrar_no_contexto(request_id: str, path: str) -> None:
    _request_id.set(request_id)
    _path.set(path)


def log(event: str, level: str = "info", **campos) -> None:
    """Um evento por linha, JSON, com nome de fato do dominio.

    Timestamp em UTC ISO-8601: "19/10 as 14h" e ambiguidade, nao instante.
    """
    registro = {
        "event": event,
        "request_id": _request_id.get(),
        "path": _path.get(),
        **campos,
        "level": level,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    sys.stdout.write(json.dumps(registro, ensure_ascii=False) + "\n")
    sys.stdout.flush()
