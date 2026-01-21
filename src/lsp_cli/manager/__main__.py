from contextlib import suppress

import httpx
import uvicorn

from lsp_cli.manager.models import RootModel
from lsp_cli.settings import MANAGER_UDS_PATH
from lsp_cli.utils.uds import open_uds

from .manager import anyio, app, connect_manager


async def main() -> None:
    # shutdown previous manager if exists
    with suppress(httpx.ConnectError):
        async with connect_manager(start=False) as client:
            await client.post("/shutdown", RootModel[None])

    async with open_uds(MANAGER_UDS_PATH):
        config = uvicorn.Config(app, uds=str(MANAGER_UDS_PATH), loop="asyncio")
        server = uvicorn.Server(config)
        await server.serve()


if __name__ == "__main__":
    anyio.run(main)
