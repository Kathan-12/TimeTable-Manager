"""HTTP API client for the desktop app."""

from __future__ import annotations

import os
from typing import Any, Dict

import requests


class ApiClient:
    """Thin wrapper around requests for the FastAPI backend."""

    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = (base_url or os.getenv("API_BASE_URL", "http://127.0.0.1:8000")).rstrip("/")

    def get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        response = requests.get(f"{self._base_url}{path}", params=params, timeout=10)
        self._raise_for_status(response)
        return response.json()

    def post(self, path: str, json_body: Dict[str, Any] | None = None, files=None, data=None) -> Dict[str, Any]:
        response = requests.post(
            f"{self._base_url}{path}",
            json=json_body,
            files=files,
            data=data,
            timeout=20,
        )
        self._raise_for_status(response)
        return response.json()

    def put(self, path: str, json_body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        response = requests.put(f"{self._base_url}{path}", json=json_body, timeout=20)
        self._raise_for_status(response)
        return response.json()

    def delete(self, path: str) -> Dict[str, Any]:
        response = requests.delete(f"{self._base_url}{path}", timeout=20)
        self._raise_for_status(response)
        return response.json()

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        if response.ok:
            return
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise RuntimeError(f"API error {response.status_code}: {detail}")
