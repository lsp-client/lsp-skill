from __future__ import annotations

import httpx
from attrs import define, field
from pydantic import BaseModel


@define
class HttpClient:
    client: httpx.Client = field(factory=httpx.Client)

    def request[T: BaseModel](
        self,
        method: str,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T | None:
        resp = self.client.request(
            method,
            url,
            params=params.model_dump(exclude_none=True, mode="json")
            if params
            else None,
            json=json.model_dump(exclude_none=True, mode="json") if json else None,
        )
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content:
            return None
        json_data = resp.json()
        if json_data is None:
            return None
        return resp_schema.model_validate(json_data)

    def get[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
    ) -> T | None:
        return self.request("GET", url, resp_schema, params=params)

    def post[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T | None:
        return self.request("POST", url, resp_schema, params=params, json=json)

    def put[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T | None:
        return self.request("PUT", url, resp_schema, params=params, json=json)

    def patch[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T | None:
        return self.request("PATCH", url, resp_schema, params=params, json=json)

    def delete[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T | None:
        return self.request("DELETE", url, resp_schema, params=params, json=json)

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


@define
class AsyncHttpClient:
    client: httpx.AsyncClient = field(factory=httpx.AsyncClient)

    async def request[T: BaseModel](
        self,
        method: str,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T | None:
        resp = await self.client.request(
            method,
            url,
            params=params.model_dump(exclude_none=True, mode="json")
            if params
            else None,
            json=json.model_dump(exclude_none=True, mode="json") if json else None,
        )
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content:
            return None
        json_data = resp.json()
        if json_data is None:
            return None
        return resp_schema.model_validate(json_data)

    async def get[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
    ) -> T | None:
        return await self.request("GET", url, resp_schema, params=params)

    async def post[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T | None:
        return await self.request("POST", url, resp_schema, params=params, json=json)

    async def put[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T | None:
        return await self.request("PUT", url, resp_schema, params=params, json=json)

    async def patch[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T | None:
        return await self.request("PATCH", url, resp_schema, params=params, json=json)

    async def delete[T: BaseModel](
        self,
        url: str,
        resp_schema: type[T],
        *,
        params: BaseModel | None = None,
        json: BaseModel | None = None,
    ) -> T | None:
        return await self.request("DELETE", url, resp_schema, params=params, json=json)

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self) -> AsyncHttpClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
