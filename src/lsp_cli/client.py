from pathlib import Path
from typing import NamedTuple

from lsp_client.client import Client
from lsp_client.clients.lang import lang_clients


class ClientTarget(NamedTuple):
    client_cls: type[Client]
    project_path: Path


def find_client(path: Path, cwd: Path | None = None) -> ClientTarget | None:
    """Identify the appropriate client and project root for a given path.

    Args:
        path: The file or directory path to find a client for.
        cwd: Optional working directory to constrain the search. If provided,
             only search for project roots within this directory and its subdirectories.
    """
    candidates = lang_clients.values()

    for client_cls in candidates:
        lang_config = client_cls.get_language_config()
        if root := lang_config.find_project_root(path, cwd):
            return ClientTarget(client_cls=client_cls, project_path=root)
    return None
