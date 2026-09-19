from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://api.commspliant.com"


@dataclass
class RenderResult:
    body: bytes
    content_type: str
    request_id: str
    content_disposition: Optional[str] = None


class Client:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        use_bearer_auth: bool = False,
        timeout: float = 60.0,
    ) -> None:
        trimmed_key = api_key.strip()
        if not trimmed_key:
            raise ValueError("api key is required")

        self._api_key = trimmed_key
        self._base_url = base_url.rstrip("/")
        self._use_bearer_auth = use_bearer_auth
        self._timeout = timeout

    def render_html(
        self,
        *,
        template_id: str,
        variables: Mapping[str, Any],
        template_version_id: Optional[str] = None,
    ) -> RenderResult:
        return self._post_render(
            "/api/v1/render/html",
            template_id=template_id,
            variables=variables,
            template_version_id=template_version_id,
        )

    def render_pdf(
        self,
        *,
        template_id: str,
        variables: Mapping[str, Any],
        template_version_id: Optional[str] = None,
    ) -> RenderResult:
        return self._post_render(
            "/api/v1/render/pdf",
            template_id=template_id,
            variables=variables,
            template_version_id=template_version_id,
        )

    def _post_render(
        self,
        path: str,
        *,
        template_id: str,
        variables: Mapping[str, Any],
        template_version_id: Optional[str],
    ) -> RenderResult:
        if not template_id or not template_id.strip():
            raise ValueError("template_id is required")
        if variables is None:
            raise ValueError("variables is required")

        payload: dict[str, Any] = {
            "templateId": template_id,
            "variables": dict(variables),
        }
        if template_version_id:
            payload["templateVersionId"] = template_version_id

        headers = {"Content-Type": "application/json"}
        if self._use_bearer_auth:
            headers["Authorization"] = f"Bearer {self._api_key}"
        else:
            headers["X-Api-Key"] = self._api_key

        request = Request(
            f"{self._base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urlopen(request, timeout=self._timeout) as response:
                body = response.read()
                return RenderResult(
                    body=body,
                    content_type=response.headers.get("Content-Type", ""),
                    request_id=response.headers.get("X-Request-ID", ""),
                    content_disposition=response.headers.get("Content-Disposition"),
                )
        except HTTPError as error:
            request_id = error.headers.get("X-Request-ID", "") if error.headers else ""
            raw = error.read()
            message = error.reason or "request failed"
            code = None
            details = None

            if raw:
                try:
                    parsed = json.loads(raw.decode("utf-8"))
                    message = parsed.get("error", message)
                    code = parsed.get("code")
                    details = parsed.get("details")
                except json.JSONDecodeError:
                    message = raw.decode("utf-8", errors="replace")

            from commspliant.errors import APIError

            raise APIError(
                error.code or 0,
                message,
                code=code,
                details=details,
                request_id=request_id,
            ) from error
