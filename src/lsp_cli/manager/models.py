from __future__ import annotations

from pathlib import Path

from lsp_client.jsonrpc.types import RawNotification, RawRequest, RawResponsePackage
from pydantic import BaseModel, RootModel


class ManagedClientInfo(BaseModel):
    project_path: Path
    language: str
    remaining_time: float
    is_warming_up: bool = False

    @classmethod
    def format(cls, infos: list[ManagedClientInfo]) -> str:
        lines = []
        for info in infos:
            status = " (warming up)" if info.is_warming_up else ""
            lines.append(
                f"{info.language:<10} {info.project_path} ({info.remaining_time:.1f}s){status}"
            )
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
    path: Path | None = None
    project_path: Path | None = None
    all: bool = False


class DeleteClientResponse(BaseModel):
    info: ManagedClientInfo


class LspRequest(BaseModel):
    payload: RawRequest


class LspResponse(BaseModel):
    payload: RawResponsePackage


class LspNotification(BaseModel):
    payload: RawNotification


class GetIDResponse(BaseModel):
    id: str
