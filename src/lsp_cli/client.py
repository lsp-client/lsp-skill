from pathlib import Path
from typing import NamedTuple

from lsp_client.client import Client
from lsp_client.clients.lang import lang_clients


class ClientTarget(NamedTuple):
    client_cls: type[Client]
    project_path: Path


def find_target(path: Path) -> ClientTarget | None:
    """Identify the appropriate client and project root for a given path.

    Args:
        path: The file or directory path to find a client for.
    """
    candidates = lang_clients.values()

    for client_cls in candidates:
        lang_config = client_cls.get_language_config()
        if root := lang_config.find_project_root(path):
            return ClientTarget(client_cls=client_cls, project_path=root)
    return None


def match_target(project_path: Path) -> ClientTarget | None:
    """Identify the appropriate client for a given project root.

    Args:
        project_path: The directory path that is expected to be a project root.
    """
    candidates = lang_clients.values()

    for client_cls in candidates:
        lang_config = client_cls.get_language_config()
        if lang_config.is_project_root(project_path):
            return ClientTarget(client_cls=client_cls, project_path=project_path)

    return None
