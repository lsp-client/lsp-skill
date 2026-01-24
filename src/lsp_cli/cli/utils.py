from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress
from pathlib import Path

import httpx
from lsap.schema.locate import Locate

from lsp_cli.exceptions import CapabilityCommandException
from lsp_cli.manager.manager import connect_manager
from lsp_cli.manager.models import (
    CreateClientRequest,
    CreateClientResponse,
    GetIDResponse,
)
from lsp_cli.settings import settings
from lsp_cli.utils.http import AsyncHttpClient
from lsp_cli.utils.locate import parse_scope
from lsp_cli.utils.socket import wait_socket


@asynccontextmanager
async def connect_server(
    path: Path, project_path: Path | None = None
) -> AsyncGenerator[AsyncHttpClient]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        async with connect_manager() as client:
            resp = await client.post(
                "/create",
                CreateClientResponse,
                json=CreateClientRequest(
                    path=path.resolve(), project_path=project_path
                ),
            )
            uds_path = resp.uds_path

        await wait_socket(uds_path, timeout=10.0)

        transport = httpx.AsyncHTTPTransport(uds=uds_path.as_posix())
        async with AsyncHttpClient(
            httpx.AsyncClient(
                transport=transport,
                base_url="http://localhost",
                timeout=settings.warmup_time + 60.0,
            )
        ) as client:
            resp = await client.get("/client/id", GetIDResponse)
            client_id = resp.id

            try:
                yield client
            except httpx.HTTPStatusError as e:
                detail = str(e)
                with suppress(Exception):
                    detail = e.response.json().get("detail", detail)
                raise CapabilityCommandException(
                    client_id=client_id, message=detail
                ) from e
            except Exception as e:
                raise CapabilityCommandException(client_id=client_id) from e
    except httpx.HTTPStatusError as e:
        detail = str(e)
        with suppress(Exception):
            detail = e.response.json().get("detail", detail)
        raise RuntimeError(detail) from e


def create_locate(
    file_path: Path, scope: str | None = None, find: str | None = None
) -> Locate:
    return Locate(file_path=file_path, scope=parse_scope(scope), find=find)
