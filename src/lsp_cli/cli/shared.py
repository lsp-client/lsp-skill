from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from lsap.schema.locate import LineScope, Locate, SymbolScope

from lsp_cli.manager.manager import connect_manager
from lsp_cli.manager.models import CreateClientRequest, CreateClientResponse
from lsp_cli.utils.http import AsyncHttpClient
from lsp_cli.utils.socket import wait_socket


@asynccontextmanager
async def managed_client(
    path: Path, project_path: Path | None = None
) -> AsyncGenerator[AsyncHttpClient]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    async with connect_manager() as client:
        resp = await client.post(
            "/create",
            CreateClientResponse,
            json=CreateClientRequest(path=path.resolve(), project_path=project_path),
        )

    uds_path = resp.uds_path
    await wait_socket(uds_path, timeout=10.0)

    transport = httpx.AsyncHTTPTransport(uds=uds_path.as_posix())
    async with AsyncHttpClient(
        httpx.AsyncClient(transport=transport, base_url="http://localhost")
    ) as client:
        yield client


def parse_scope(scope_str: str | None) -> LineScope | SymbolScope | None:
    if not scope_str:
        return None

    if "," in scope_str:
        start, end = scope_str.split(",", 1)
        start_val = int(start)
        end_val = int(end)
        actual_end = 0 if end_val == 0 else end_val + 1
        return LineScope(start_line=start_val, end_line=actual_end)
    if scope_str.isdigit():
        return LineScope(start_line=int(scope_str), end_line=int(scope_str) + 1)
    symbol_path = scope_str.split(".")
    return SymbolScope(symbol_path=symbol_path)


def create_locate(
    file_path: Path,
    scope: str | None = None,
    find: str | None = None,
) -> Locate:
    return Locate(file_path=file_path, scope=parse_scope(scope), find=find)
