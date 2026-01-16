from __future__ import annotations

import subprocess
import sys

import httpx

from lsp_cli.settings import MANAGER_UDS_PATH
from lsp_cli.utils.http import HttpClient
from lsp_cli.utils.socket import is_socket_alive

from .manager import Manager, get_manager, manager_lifespan
from .models import (
    CreateClientRequest,
    CreateClientResponse,
    DeleteClientRequest,
    DeleteClientResponse,
    ManagedClientInfo,
    ManagedClientInfoList,
)

__all__ = [
    "CreateClientRequest",
    "CreateClientResponse",
    "DeleteClientRequest",
    "DeleteClientResponse",
    "ManagedClientInfo",
    "ManagedClientInfoList",
    "Manager",
    "connect_manager",
    "get_manager",
    "manager_lifespan",
]


def connect_manager() -> HttpClient:
    if not is_socket_alive(MANAGER_UDS_PATH):
        subprocess.Popen(
            (sys.executable, "-m", "lsp_cli.manager"),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    return HttpClient(
        httpx.Client(
            transport=httpx.HTTPTransport(uds=str(MANAGER_UDS_PATH), retries=5),
            base_url="http://localhost",
            timeout=30.0,
        )
    )
