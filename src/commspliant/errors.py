from __future__ import annotations

from typing import Any, Optional


class APIError(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.code = code
        self.details = details
        self.request_id = request_id
