from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

logger = logging.getLogger("api_client")
logging.getLogger("faker").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

TokenCallback = Callable[[], str | Awaitable[str]]


class APIClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        headers: dict[str, str] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        auth_token_getter: TokenCallback | None = None,
        auth_token_refresher: TokenCallback | None = None,
        retries: int = 2,
        retry_backoff: float = 0.2,
        retry_statuses: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers=headers,
            transport=transport,
        )
        self._auth_token_getter = auth_token_getter
        self._auth_token_refresher = auth_token_refresher
        self._retries = retries
        self._retry_backoff = retry_backoff
        self._retry_statuses = retry_statuses

    async def __aenter__(self) -> APIClient:
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    async def _resolve_token(self, callback: TokenCallback | None) -> str | None:
        if callback is None:
            return None
        token_or_awaitable = callback()
        if asyncio.iscoroutine(token_or_awaitable):
            return await token_or_awaitable
        return token_or_awaitable

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        expected_status: int | None = None,
    ) -> httpx.Response:
        last_error: Exception | None = None
        token_refreshed = False

        for attempt in range(self._retries + 1):
            merged_headers: dict[str, str] = dict(headers or {})
            token = await self._resolve_token(self._auth_token_getter)
            if token:
                merged_headers["Authorization"] = f"Bearer {token}"

            logger.debug("→ %s %s | body: %s", method, endpoint, json)

            try:
                response = await self._client.request(
                    method=method,
                    url=endpoint,
                    params=params,
                    json=json,
                    headers=merged_headers or None,
                )
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc
                if attempt < self._retries:
                    await asyncio.sleep(self._retry_backoff * (2**attempt))
                    continue
                raise

            logger.debug("← %s %s | status: %s | body: %s", method, endpoint, response.status_code, response.text)

            if response.status_code == 401 and self._auth_token_refresher and not token_refreshed:
                await self._resolve_token(self._auth_token_refresher)
                token_refreshed = True
                continue

            if response.status_code in self._retry_statuses and attempt < self._retries:
                await asyncio.sleep(self._retry_backoff * (2**attempt))
                continue

            if expected_status is not None and response.status_code != expected_status:
                raise httpx.HTTPStatusError(
                    f"Expected status {expected_status}, got {response.status_code}",
                    request=response.request,
                    response=response,
                )

            return response

        if last_error is not None:
            raise last_error
        raise RuntimeError("Request retries exhausted without response")

    async def get(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        expected_status: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return await self.request(
            "GET",
            endpoint,
            params=params,
            expected_status=expected_status,
            headers=headers,
        )

    async def post(
        self,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
        expected_status: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return await self.request(
            "POST",
            endpoint,
            json=json,
            expected_status=expected_status,
            headers=headers,
        )

    async def put(
        self,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
        expected_status: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return await self.request(
            "PUT",
            endpoint,
            json=json,
            expected_status=expected_status,
            headers=headers,
        )

    async def patch(
        self,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
        expected_status: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return await self.request(
            "PATCH",
            endpoint,
            json=json,
            expected_status=expected_status,
            headers=headers,
        )

    async def delete(
        self,
        endpoint: str,
        *,
        expected_status: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return await self.request(
            "DELETE",
            endpoint,
            expected_status=expected_status,
            headers=headers,
        )
