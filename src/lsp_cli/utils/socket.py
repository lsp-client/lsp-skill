import socket
from pathlib import Path

import anyio
from tenacity import AsyncRetrying, stop_after_delay, wait_fixed


def is_socket_alive(path: Path) -> bool:
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(str(path))
            return True
    except OSError:
        return False


async def wait_socket(path: Path, timeout: float = 10.0) -> None:
    async for attempt in AsyncRetrying(
        stop=stop_after_delay(timeout),
        wait=wait_fixed(0.1),
        reraise=True,
    ):
        with attempt:
            try:
                _ = await anyio.connect_unix(path)
            except (OSError, RuntimeError) as e:
                raise OSError(f"Socket {path} not ready") from e
