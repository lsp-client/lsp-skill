from pathlib import Path

import anyio
from tenacity import AsyncRetrying, stop_after_delay, wait_fixed


async def is_socket_alive(path: Path) -> bool:
    try:
        await anyio.connect_unix(path)
    except (OSError, ConnectionRefusedError, FileNotFoundError):
        return False

    return True


async def wait_socket(path: Path, timeout: float = 10.0) -> None:
    async for attempt in AsyncRetrying(
        stop=stop_after_delay(timeout),
        wait=wait_fixed(0.1),
        reraise=True,
    ):
        with attempt:
            await anyio.connect_unix(path)
