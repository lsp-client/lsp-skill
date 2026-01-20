from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from lsap.schema.locate import LineScope, Locate
from lsap.utils.locate import parse_locate_string

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
            json=CreateClientRequest(path=path.absolute(), project_path=project_path),
        )

    uds_path = resp.uds_path
    await wait_socket(uds_path, timeout=10.0)

    transport = httpx.AsyncHTTPTransport(uds=uds_path.as_posix())
    async with AsyncHttpClient(
        httpx.AsyncClient(transport=transport, base_url="http://localhost")
    ) as client:
        yield client


def create_locate(locate_str: str) -> Locate:
    locate = parse_locate_string(locate_str)

    match locate.scope:
        case LineScope(line=(start, end)):
            if start <= 0 or end <= 0:
                raise ValueError("Line numbers must be positive integers")
            if start > end:
                raise ValueError(
                    f"Start line ({start}) cannot be greater than end line ({end})"
                )
        case LineScope(line=int(line)) if line <= 0:
            raise ValueError("Line number must be a positive integer")

    if not locate.file_path.is_absolute():
        locate.file_path = locate.file_path.absolute()

    if not locate.file_path.is_file():
        raise FileNotFoundError(f"File not found: {locate.file_path}")

    return locate
