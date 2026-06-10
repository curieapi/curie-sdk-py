# curie/_http.py
import time
import httpx
from typing import Any
from .exceptions import (
    AuthenticationError, ModelNotFoundError, InferenceError,
    RateLimitError, ValidationError, CurieError
)


class HttpClient:
    """Internal HTTP client with retry logic."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int,
        max_retries: int,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.Client(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "curie-python/0.1.0",
            },
            timeout=timeout,
        )
        self._async_client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "curie-python/0.1.0",
            },
            timeout=timeout,
        )

    def post(self, path: str, body: dict) -> dict:
        """Synchronous POST with retry logic."""
        url = f"{self.base_url}{path}"
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.post(url, json=body)
                return self._handle_response(response)
            except httpx.TimeoutException:
                last_error = CurieError(f"Request timed out after {self.timeout}s")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
            except httpx.NetworkError as e:
                last_error = CurieError(f"Network error: {e}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue

        raise last_error

    async def apost(self, path: str, body: dict) -> dict:
        """Async POST with retry logic."""
        import asyncio
        url = f"{self.base_url}{path}"
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await self._async_client.post(url, json=body)
                return self._handle_response(response)
            except httpx.TimeoutException:
                last_error = CurieError(f"Request timed out after {self.timeout}s")
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
            except httpx.NetworkError as e:
                last_error = CurieError(f"Network error: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue

        raise last_error

    def _handle_response(self, response: httpx.Response) -> dict:
        """Parse response and raise appropriate exceptions."""
        if response.status_code == 200 or response.status_code == 201:
            return response.json()

        try:
            data = response.json()
            error_msg = data.get('error', 'Unknown error')
            error_code = data.get('code', '')
            job_id = data.get('job_id')
        except Exception:
            error_msg = response.text
            error_code = ''
            job_id = None

        if response.status_code == 401:
            raise AuthenticationError(error_msg)
        elif response.status_code == 404 and error_code == 'MODEL_NOT_FOUND':
            available = data.get('available_models', [])
            model = error_msg.split("'")[1] if "'" in error_msg else 'unknown'
            raise ModelNotFoundError(model, available)
        elif response.status_code == 429:
            raise RateLimitError(error_msg)
        elif response.status_code == 422:
            raise ValidationError(error_msg)
        elif response.status_code == 500:
            raise InferenceError(error_msg, job_id=job_id)
        else:
            raise CurieError(f"HTTP {response.status_code}: {error_msg}")

    def close(self):
        self._client.close()

    async def aclose(self):
        await self._async_client.aclose()
