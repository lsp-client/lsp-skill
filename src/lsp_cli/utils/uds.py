from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import anyio


@asynccontextmanager
async def open_uds(uds_path: Path) -> AsyncGenerator[Path]:
    path = anyio.Path(uds_path)
    await path.unlink(missing_ok=True)
    await path.parent.mkdir(parents=True, exist_ok=True)
    try:
        yield uds_path
    finally:
        with anyio.CancelScope(shield=True):
            await path.unlink(missing_ok=True)
