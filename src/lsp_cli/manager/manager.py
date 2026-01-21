from __future__ import annotations

import signal
import subprocess
import sys
from collections.abc import AsyncGenerator, Iterable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Final

import anyio
import asyncer
import httpx
import loguru
from attrs import define, field
from litestar import Litestar, delete, get, post
from litestar.datastructures import State
from litestar.exceptions import NotFoundException
from loguru import logger

from lsp_cli.client import ClientTarget, find_target, match_target
from lsp_cli.settings import (
    MANAGER_LOG_PATH,
    MANAGER_UDS_PATH,
)
from lsp_cli.utils.http import AsyncHttpClient
from lsp_cli.utils.logging import extra_filter
from lsp_cli.utils.socket import is_socket_alive, wait_socket

from .client import ManagedClient, get_client_id
from .models import (
    CreateClientRequest,
    CreateClientResponse,
    DeleteClientRequest,
    ManagedClientInfo,
)


@define
class Manager:
    _clients: dict[str, ManagedClient] = field(factory=dict, init=False)
    _tg: asyncer.TaskGroup = field(init=False)
    _logger: loguru.Logger = field(init=False)
    _sink_id: int = field(init=False)

    def _setup_logger(self) -> None:
        MANAGER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

        self._sink_id = logger.add(
            MANAGER_LOG_PATH,
            filter=extra_filter("client_id", exclude=True),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
        )
        self._logger = logger

    def __attrs_post_init__(self) -> None:
        self._setup_logger()
        self._logger.info("Manager initialized at {}", MANAGER_LOG_PATH)

    def _get_target(
        self, path: Path, project_path: Path | None = None
    ) -> ClientTarget | None:
        return match_target(project_path) if project_path else find_target(path)

    def _get_client(
        self, path: Path, project_path: Path | None = None
    ) -> ManagedClient | None:
        if target := self._get_target(path, project_path):
            client_id = get_client_id(target)
            if client := self._clients.get(client_id):
                return client
        return None

    async def create_client(self, path: Path, project_path: Path | None = None) -> Path:
        if existing_client := self._get_client(path, project_path):
            self._logger.info(
                "Reusing existing client: {client_id}", client_id=existing_client.id
            )
            existing_client._reset_timeout()
            return existing_client.uds_path

        target = self._get_target(path, project_path)
        if not target:
            raise NotFoundException(f"No LSP client found for path: {path}")

        client_id = get_client_id(target)
        self._logger.info("Creating new client: {client_id}", client_id=client_id)
        m_client = ManagedClient(target)
        self._clients[client_id] = m_client
        self._tg.soonify(self._run_client)(m_client)
        return m_client.uds_path

    async def _run_client(self, client: ManagedClient) -> None:
        try:
            self._logger.info("Running client: {client_id}", client_id=client.id)
            await client.run()
        finally:
            self._logger.info("Removing client: {client_id}", client_id=client.id)
            self._clients.pop(client.id, None)

    async def delete_client(
        self,
        path: Path | None = None,
        project_path: Path | None = None,
        all: bool = False,
    ) -> list[ManagedClientInfo]:
        clients: Iterable[ManagedClient] = []
        if all:
            clients = self._clients.values()
        elif path and (client := self._get_client(path, project_path)):
            clients = [client]

        for client in clients:
            self._logger.info("Stopping client: {client_id}", client_id=client.id)
            client.stop()

        return [client.info for client in clients]

    def inspect_client(
        self, path: Path, project_path: Path | None = None
    ) -> ManagedClientInfo | None:
        if client := self._get_client(path, project_path):
            return client.info
        return None

    def list_clients(self) -> list[ManagedClientInfo]:
        return [client.info for client in self._clients.values()]

    @asynccontextmanager
    async def run(self) -> AsyncGenerator[Manager]:
        self._logger.info("Starting manager")
        try:
            async with asyncer.create_task_group() as tg:
                self._tg = tg
                yield self
        finally:
            self._logger.info("Shutting down manager")


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None]:
    async with Manager().run() as manager:
        app.state.manager = manager
        yield


def get_manager(state: State) -> Manager:
    manager = state.manager
    assert isinstance(manager, Manager)
    return manager


@post("/create", status_code=201)
async def create_client_handler(
    data: CreateClientRequest, state: State
) -> CreateClientResponse:
    manager = get_manager(state)
    uds_path = await manager.create_client(data.path, project_path=data.project_path)

    if info := manager.inspect_client(data.path, project_path=data.project_path):
        return CreateClientResponse(uds_path=uds_path, info=info)
    raise RuntimeError("Failed to create client")


@delete("/delete", status_code=200)
async def delete_client_handler(
    data: DeleteClientRequest, state: State
) -> list[ManagedClientInfo]:
    manager = get_manager(state)
    return await manager.delete_client(
        data.path, project_path=data.project_path, all=data.all
    )


@get("/list")
async def list_clients_handler(state: State) -> list[ManagedClientInfo]:
    manager = get_manager(state)
    return manager.list_clients()


@post("/shutdown")
async def shutdown_handler(state: State) -> None:
    manager = get_manager(state)
    manager._logger.info("Shutdown requested")
    await manager.delete_client(all=True)
    # shutdown uvicorn
    signal.raise_signal(signal.SIGINT)


app: Final = Litestar(
    route_handlers=[
        create_client_handler,
        delete_client_handler,
        list_clients_handler,
        shutdown_handler,
    ],
    lifespan=[lifespan],
)


async def start_manager() -> None:
    await anyio.open_process(
        (sys.executable, "-m", "lsp_cli.manager"),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    await wait_socket(MANAGER_UDS_PATH, timeout=10.0)


@asynccontextmanager
async def connect_manager(start: bool = True) -> AsyncGenerator[AsyncHttpClient]:
    if start and not await is_socket_alive(MANAGER_UDS_PATH):
        await start_manager()

    transport = httpx.AsyncHTTPTransport(uds=str(MANAGER_UDS_PATH), retries=5)

    async with AsyncHttpClient(
        httpx.AsyncClient(
            transport=transport,
            base_url="http://localhost",
            timeout=30.0,
        )
    ) as client:
        yield client
