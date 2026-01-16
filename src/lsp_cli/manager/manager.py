from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Final, cast

import anyio
import asyncer
from attrs import Factory, define, field
from litestar import Litestar, delete, get, post
from litestar.datastructures import State
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from loguru import logger

from lsp_cli.client import ClientTarget, find_target, match_target
from lsp_cli.settings import LOG_DIR, settings

from .client import ManagedClient, get_client_id
from .models import (
    CreateClientRequest,
    CreateClientResponse,
    DeleteClientRequest,
    DeleteClientResponse,
    ManagedClientInfo,
)


@define
class Manager:
    _clients: dict[str, ManagedClient] = Factory(dict)
    _tg: asyncer.TaskGroup = field(init=False)
    _logger_sink_id: int = field(init=False)

    def __attrs_post_init__(self) -> None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_path = LOG_DIR / "manager.log"
        log_level = settings.effective_log_level
        self._logger_sink_id = logger.add(
            log_path,
            rotation="10 MB",
            retention="1 day",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            enqueue=True,
        )
        logger.info(
            f"[Manager] Manager log initialized at {log_path} (level: {log_level})"
        )

    def _get_target(
        self, path: Path, project_path: Path | None = None
    ) -> ClientTarget | None:
        if project_path:
            return match_target(project_path)
        return find_target(path)

    async def create_client(self, path: Path, project_path: Path | None = None) -> Path:
        target = self._get_target(path, project_path)
        if not target:
            raise NotFoundException(f"No LSP client found for path: {path}")

        logger.debug(f"[Manager] Found client target: {target}")

        client_id = get_client_id(target)
        if client_id not in self._clients:
            logger.info(f"[Manager] Creating new client: {client_id}")
            m_client = ManagedClient(target)
            self._clients[client_id] = m_client
            self._tg.soonify(self._run_client)(m_client)
        else:
            logger.info(f"[Manager] Reusing existing client: {client_id}")
            self._clients[client_id]._reset_timeout()

        return self._clients[client_id].uds_path

    @logger.catch(level="ERROR")
    async def _run_client(self, client: ManagedClient) -> None:
        try:
            logger.info(f"[Manager] Running client: {client.id}")
            await client.run()
        finally:
            logger.info(f"[Manager] Removing client: {client.id}")
            self._clients.pop(client.id, None)

    async def delete_client(self, path: Path, project_path: Path | None = None) -> None:
        if target := self._get_target(path, project_path):
            client_id = get_client_id(target)
            if client := self._clients.get(client_id):
                logger.info(f"[Manager] Stopping client: {client_id}")
                client.stop()

    def inspect_client(
        self, path: Path, project_path: Path | None = None
    ) -> ManagedClientInfo | None:
        if target := self._get_target(path, project_path):
            client_id = get_client_id(target)
            if client := self._clients.get(client_id):
                return client.info
        return None

    def list_clients(self) -> list[ManagedClientInfo]:
        return [client.info for client in self._clients.values()]

    @asynccontextmanager
    async def run(self) -> AsyncGenerator[Manager]:
        logger.info("[Manager] Starting manager")
        try:
            async with asyncer.create_task_group() as tg:
                self._tg = tg
                yield self
        finally:
            logger.info("[Manager] Shutting down manager")
            logger.remove(self._logger_sink_id)


def get_manager(state: State) -> Manager:
    return cast(Manager, state.manager)


@asynccontextmanager
async def manager_lifespan(app: Litestar) -> AsyncGenerator[None]:
    await anyio.Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    async with Manager().run() as manager:
        app.state.manager = manager
        yield


logger.add(
    LOG_DIR / "manager.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
)


@post("/create", status_code=201)
async def create_client_handler(
    data: CreateClientRequest, state: State
) -> CreateClientResponse:
    manager = get_manager(state)
    uds_path = await manager.create_client(data.path, project_path=data.project_path)
    info = manager.inspect_client(data.path, project_path=data.project_path)
    if not info:
        raise RuntimeError("Failed to create client")

    return CreateClientResponse(uds_path=uds_path, info=info)


@delete("/delete", status_code=200)
async def delete_client_handler(
    data: DeleteClientRequest, state: State
) -> DeleteClientResponse:
    manager = get_manager(state)
    info = manager.inspect_client(data.path, project_path=data.project_path)
    await manager.delete_client(data.path, project_path=data.project_path)

    return DeleteClientResponse(info=info)


@get("/list")
async def list_clients_handler(state: State) -> list[ManagedClientInfo]:
    manager = get_manager(state)
    return manager.list_clients()


app: Final = Litestar(
    route_handlers=[
        create_client_handler,
        delete_client_handler,
        list_clients_handler,
    ],
    dependencies={"manager": Provide(get_manager, sync_to_thread=False)},
    lifespan=[manager_lifespan],
    debug=settings.debug,
)
