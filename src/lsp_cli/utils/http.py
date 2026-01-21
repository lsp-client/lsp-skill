from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self

import httpx
from anyio import AsyncContextManagerMixin
from attrs import define
from pydantic import BaseModel


@define
class AsyncHttpClient(AsyncContextManagerMixin):
    client: httpx.AsyncClient

    async def request[T: BaseModel](
        self,
        method: str,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T:
        resp = await self.client.request(
            method,
            url,
            params=params.model_dump(exclude_none=True, mode="json")
            if params
            else None,
            json=json.model_dump(exclude_none=True, mode="json") if json else None,
        )
        resp.raise_for_status()
        json = resp.json()
        return resp_schema.model_validate(json)

    async def get[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
    ) -> T:
        return await self.request("GET", url, resp_schema, params=params)

    async def post[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T:
        return await self.request("POST", url, resp_schema, params=params, json=json)

    async def put[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T:
        return await self.request("PUT", url, resp_schema, params=params, json=json)

    async def patch[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T:
        return await self.request("PATCH", url, resp_schema, params=params, json=json)

    async def delete[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T:
        return await self.request("DELETE", url, resp_schema, params=params, json=json)

    @asynccontextmanager
    async def __asynccontextmanager__(self) -> AsyncGenerator[Self]:
        async with self.client:
            yield self
