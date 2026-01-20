from __future__ import annotations

from pathlib import Path

from lsp_client.jsonrpc.types import RawNotification, RawRequest, RawResponsePackage
from pydantic import BaseModel, RootModel


class ManagedClientInfo(BaseModel):
    project_path: Path
    language: str
    remaining_time: float

    @classmethod
    def format(cls, infos: list[ManagedClientInfo]) -> str:
        lines = [
            f"{info.language:<10} {info.project_path} ({info.remaining_time:.1f}s)"
            for info in infos
        ]
        return "\n".join(lines)


class ManagedClientInfoList(RootModel[list[ManagedClientInfo]]):
    root: list[ManagedClientInfo]


class CreateClientRequest(BaseModel):
    path: Path
    project_path: Path | None = None


class CreateClientResponse(BaseModel):
    uds_path: Path
    info: ManagedClientInfo


class DeleteClientRequest(BaseModel):
    path: Path
    project_path: Path | None = None


class DeleteClientResponse(BaseModel):
    info: ManagedClientInfo


class LspRequest(BaseModel):
    payload: RawRequest


class LspResponse(BaseModel):
    payload: RawResponsePackage


class LspNotification(BaseModel):
    payload: RawNotification
