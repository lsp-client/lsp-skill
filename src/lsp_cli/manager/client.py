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
from litestar import Litestar, Request, Response
from loguru import logger as global_logger

from lsp_cli.client import ClientTarget
from lsp_cli.manager.capability import Capabilities, CapabilityController
from lsp_cli.settings import CLIENT_LOG_DIR, RUNTIME_DIR, settings

from .models import ManagedClientInfo


def get_client_id(target: ClientTarget) -> str:
    kind = target.client_cls.get_language_config().kind
    path_hash = xxhash.xxh32_hexdigest(target.project_path.as_posix())
    return f"{kind.value}-{path_hash}-default"


@define
class ManagedClient:
    target: ClientTarget

    _server: uvicorn.Server = field(init=False)
    _timeout_scope: anyio.CancelScope = field(init=False)
    _server_scope: anyio.CancelScope = field(init=False)

    _deadline: float = field(init=False)
    _should_exit: bool = False

    _logger: loguru.Logger = field(init=False)
    _logger_sink_id: int = field(init=False)

    def __attrs_post_init__(self) -> None:
        self._deadline = anyio.current_time() + settings.idle_timeout

        client_log_dir = CLIENT_LOG_DIR
        client_log_dir.mkdir(parents=True, exist_ok=True)

        log_path = client_log_dir / f"{self.id}.log"
        log_level = settings.effective_log_level
        self._logger_sink_id = global_logger.add(
            log_path,
            rotation="10 MB",
            retention="1 day",
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
            enqueue=True,
        )
        self._logger = global_logger.bind(client_id=self.id)
        self._logger.info("Client log initialized at {}", log_path)

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
            async with self.target.client_cls(
                workspace=self.target.project_path,
                request_timeout=120,
            ) as client:
                app.state.client = client
                app.state.capabilities = Capabilities.build(client)
                yield

        def exception_handler(request: Request, exc: Exception) -> Response:
            self._logger.exception("Unhandled exception in Litestar: {}", exc)
            return Response(
                content={"detail": str(exc)},
                status_code=500,
            )

        app = Litestar(
            route_handlers=[CapabilityController],
            lifespan=[lifespan],
            debug=settings.debug,
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

        uds_path = anyio.Path(self.uds_path)
        await uds_path.unlink(missing_ok=True)
        await uds_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            await self._serve()
        finally:
            self._logger.info("Cleaning up client")
            await uds_path.unlink(missing_ok=True)
            self._logger.remove(self._logger_sink_id)
            self._timeout_scope.cancel()
            self._server_scope.cancel()
