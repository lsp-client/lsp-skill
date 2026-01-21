from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import anyio
import asyncer
import loguru
import uvicorn
import xxhash
from attrs import define, field
from litestar import Controller, Litestar, Request, Response, get
from litestar.datastructures import State
from loguru import logger

from lsp_cli.client import ClientTarget
from lsp_cli.manager.capability import Capabilities, CapabilityController
from lsp_cli.settings import RUNTIME_DIR, get_client_log_path, settings
from lsp_cli.utils.logging import extra_filter
from lsp_cli.utils.uds import open_uds

from .models import GetIDResponse, ManagedClientInfo


def get_client_id(target: ClientTarget) -> str:
    kind = target.client_cls.get_language_config().kind
    path_hash = xxhash.xxh32_hexdigest(target.project_path.as_posix())
    return f"{kind.value}-{path_hash}-default"


class ClientController(Controller):
    path = "/client"

    @get("/id")
    async def get_id(self, state: State) -> GetIDResponse:
        managed_client: ManagedClient = state.managed_client
        return GetIDResponse(id=managed_client.id)


@define
class ManagedClient:
    target: ClientTarget

    _server: uvicorn.Server = field(init=False)
    _timeout_scope: anyio.CancelScope = field(init=False)
    _server_scope: anyio.CancelScope = field(init=False)

    _deadline: float = field(init=False)
    _should_exit: bool = False

    _logger: loguru.Logger = field(init=False)
    _sink_id: int = field(init=False)

    def _setup_logger(self) -> None:
        log_file = get_client_log_path(self.id)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        self._sink_id = logger.add(
            log_file,
            filter=extra_filter("client_id", self.id),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
        )
        self._logger = logger.bind(client_id=self.id)

    def __attrs_post_init__(self) -> None:
        self._deadline = anyio.current_time() + settings.idle_timeout

        self._setup_logger()
        self._logger.info("Client initialized")

    @property
    def id(self) -> str:
        return get_client_id(self.target)

    @property
    def uds_path(self) -> Path:
        return RUNTIME_DIR / f"{self.id}.sock"

    @property
    def info(self) -> ManagedClientInfo:
        return ManagedClientInfo(
            project_path=self.target.project_path,
            language=self.target.client_cls.get_language_config().kind.value,
            remaining_time=max(0.0, self._deadline - anyio.current_time()),
        )

    def stop(self) -> None:
        self._logger.info("Stopping managed client")
        self._should_exit = True
        self._server.should_exit = True
        self._server_scope.cancel()
        self._timeout_scope.cancel()

    def _reset_timeout(self) -> None:
        self._deadline = anyio.current_time() + settings.idle_timeout
        self._timeout_scope.cancel()

    async def _timeout_loop(self) -> None:
        while not self._should_exit:
            if self._server.should_exit:
                break
            remaining = self._deadline - anyio.current_time()
            if remaining <= 0:
                break
            with anyio.CancelScope() as scope:
                self._timeout_scope = scope
                await anyio.sleep(remaining)

        self._server.should_exit = True
        self._server_scope.cancel()

    async def _serve(self) -> None:
        @asynccontextmanager
        async def lifespan(app: Litestar) -> AsyncGenerator[None]:
            app.state.managed_client = self
            async with self.target.client_cls(
                workspace=self.target.project_path,
                request_timeout=120,
            ) as client:
                app.state.capabilities = Capabilities.build(client)
                yield

        def exception_handler(request: Request, exc: Exception) -> Response:
            self._logger.exception("Unhandled exception in Litestar: {}", exc)
            return Response(
                content={"detail": str(exc)},
                status_code=500,
            )

        app = Litestar(
            route_handlers=[CapabilityController, ClientController],
            lifespan=[lifespan],
            exception_handlers={Exception: exception_handler},
        )

        config = uvicorn.Config(app, uds=str(self.uds_path), loop="asyncio")
        self._server = uvicorn.Server(config)

        async with asyncer.create_task_group() as tg:
            with anyio.CancelScope() as scope:
                self._server_scope = scope
                tg.soonify(self._timeout_loop)()
                await self._server.serve()

    async def run(self) -> None:
        self._logger.info(
            "Starting managed client for project {} at {}",
            self.target.project_path,
            self.uds_path,
        )

        async with open_uds(self.uds_path):
            try:
                await self._serve()
            finally:
                self._logger.info("Cleaning up client")
                logger.remove(self._sink_id)
                self._timeout_scope.cancel()
                self._server_scope.cancel()
