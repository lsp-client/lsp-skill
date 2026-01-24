from typing import Self

from attrs import frozen
from litestar import Controller, post
from litestar.datastructures.state import State
from lsap.capability.definition import (
    DefinitionCapability,
    DefinitionRequest,
    DefinitionResponse,
)
from lsap.capability.locate import LocateCapability, LocateRequest, LocateResponse
from lsap.capability.outline import OutlineCapability, OutlineRequest, OutlineResponse
from lsap.capability.reference import (
    ReferenceCapability,
    ReferenceRequest,
    ReferenceResponse,
)
from lsap.capability.relation import (
    RelationCapability,
    RelationRequest,
    RelationResponse,
)
from lsap.capability.rename import (
    RenameExecuteCapability,
    RenameExecuteRequest,
    RenameExecuteResponse,
    RenamePreviewCapability,
    RenamePreviewRequest,
    RenamePreviewResponse,
)
from lsap.capability.search import SearchCapability, SearchRequest, SearchResponse
from lsap.capability.symbol import SymbolCapability, SymbolRequest, SymbolResponse
from lsp_client import Client


@frozen
class Capabilities:
    definition: DefinitionCapability
    locate: LocateCapability
    outline: OutlineCapability
    reference: ReferenceCapability
    relation: RelationCapability
    rename_preview: RenamePreviewCapability
    rename_execute: RenameExecuteCapability
    search: SearchCapability
    symbol: SymbolCapability

    @classmethod
    def build(cls, client: Client) -> Self:
        return cls(
            definition=DefinitionCapability(client),
            locate=LocateCapability(client),
            outline=OutlineCapability(client),
            reference=ReferenceCapability(client),
            relation=RelationCapability(client),
            rename_preview=RenamePreviewCapability(client),
            rename_execute=RenameExecuteCapability(client),
            search=SearchCapability(client),
            symbol=SymbolCapability(client),
        )


class CapabilityController(Controller):
    path = "/capability"

    @post("/definition")
    async def definition(
        self, data: DefinitionRequest, state: State
    ) -> DefinitionResponse | None:
        return await state.capabilities.definition(data)

    @post("/locate")
    async def locate(self, data: LocateRequest, state: State) -> LocateResponse | None:
        return await state.capabilities.locate(data)

    @post("/outline")
    async def outline(
        self, data: OutlineRequest, state: State
    ) -> OutlineResponse | None:
        return await state.capabilities.outline(data)

    @post("/reference")
    async def reference(
        self, data: ReferenceRequest, state: State
    ) -> ReferenceResponse | None:
        return await state.capabilities.reference(data)

    @post("/relation")
    async def relation(
        self, data: RelationRequest, state: State
    ) -> RelationResponse | None:
        return await state.capabilities.relation(data)

    @post("/rename/preview")
    async def rename_preview(
        self, data: RenamePreviewRequest, state: State
    ) -> RenamePreviewResponse | None:
        return await state.capabilities.rename_preview(data)

    @post("/rename/execute")
    async def rename_execute(
        self, data: RenameExecuteRequest, state: State
    ) -> RenameExecuteResponse | None:
        return await state.capabilities.rename_execute(data)

    @post("/search")
    async def search(self, data: SearchRequest, state: State) -> SearchResponse | None:
        return await state.capabilities.search(data)

    @post("/symbol")
    async def symbol(self, data: SymbolRequest, state: State) -> SymbolResponse | None:
        return await state.capabilities.symbol(data)
