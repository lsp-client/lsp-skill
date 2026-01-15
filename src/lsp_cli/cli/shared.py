import re
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from lsap.schema.locate import LineScope, Locate
from lsap.utils.locate import parse_locate_string
from pydantic import ValidationError

from lsp_cli.manager import CreateClientRequest, CreateClientResponse
from lsp_cli.server import get_manager_client
from lsp_cli.utils.http import AsyncHttpClient
from lsp_cli.utils.socket import wait_socket


def clean_error_msg(msg: str) -> str:
    return re.sub(r"\[Errno \d+\] ", "", msg)


@asynccontextmanager
async def managed_client(path: Path) -> AsyncGenerator[AsyncHttpClient]:
    path = path.absolute()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with get_manager_client() as client:
        info = client.post(
            "/create",
            CreateClientResponse,
            json=CreateClientRequest(path=path, cwd=Path.cwd()),
        )
        assert info is not None

    uds_path = info.uds_path
    await wait_socket(uds_path, timeout=10.0)

    transport = httpx.AsyncHTTPTransport(uds=uds_path.as_posix())
    async with AsyncHttpClient(
        httpx.AsyncClient(transport=transport, base_url="http://localhost")
    ) as client:
        yield client


def create_locate(locate_str: str) -> Locate:
    locate = parse_locate_string(locate_str)
    if isinstance(locate.scope, LineScope):
        if isinstance(locate.scope.line, tuple):
            start, end = locate.scope.line
            if start <= 0 or end <= 0:
                raise ValueError("Line numbers must be positive integers")
            if start > end:
                raise ValueError(
                    f"Start line ({start}) cannot be greater than end line ({end})"
                )
        elif locate.scope.line <= 0:
            raise ValueError("Line number must be a positive integer")

    if not locate.file_path.is_absolute():
        locate.file_path = locate.file_path.absolute()

    return locate


def get_msg(err: Exception | ExceptionGroup) -> str:
    match err:
        case ExceptionGroup():
            return "\n".join(get_msg(se) for se in err.exceptions)
        case ValidationError():
            msgs = []
            for e in err.errors():
                m = str(e["msg"])
                if m.startswith("Value error, "):
                    m = m[len("Value error, ") :]
                msgs.append(m)
            return "\n".join(msgs)
        case httpx.HTTPStatusError():
            data = err.response.json()
            if isinstance(data, dict) and "detail" in data:
                return clean_error_msg(str(data["detail"]))
            return clean_error_msg(str(err))
        case ValueError():
            msg = str(err)
            if "invalid literal for int()" in msg:
                return f"Invalid line number or range in locate string: {msg.split(': ')[-1]}"
            return msg
        case OSError() as e:
            if e.strerror and e.filename:
                return f"{e.strerror}: {e.filename}"
            return clean_error_msg(str(e))
        case _:
            return str(err)
