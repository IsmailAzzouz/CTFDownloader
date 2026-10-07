"""Utility helpers for filename sanitization, URL extraction, and throttling."""

import random
import re
import time
from urllib.parse import unquote
from typing import List, Optional

import requests

_FORBIDDEN_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_URL_RE = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')


def sanitize_name(name: str, fallback: str = "item") -> str:
    """Sanitize directory or file names across Windows and POSIX systems.

    Prevents directory traversal, removes forbidden characters, and trims dots.

    # Complexity: O(L) where L is the length of name
    """
    if not name:
        return fallback

    decoded = unquote(str(name)).strip()
    cleaned = _FORBIDDEN_CHARS_RE.sub('_', decoded)
    # Remove relative traversal sequences
    cleaned = re.sub(r'\.{2,}', '_', cleaned)
    # Collapse consecutive underscores and strip edge artifacts
    cleaned = re.sub(r'_+', '_', cleaned).strip(' ._')

    if not cleaned or cleaned in ('.', '..'):
        return fallback

    # Truncate to safe length to avoid MAX_PATH issues
    return cleaned[:120]


def extract_urls(content: str) -> List[str]:
    """Extract http/https and www URLs from arbitrary text descriptions.

    # Complexity: O(N) where N is the length of content
    """
    if not content:
        return []
    return _URL_RE.findall(content)


class RateLimitedSession(requests.Session):
    """Requests Session that pauses between requests to prevent rate limiting."""

    def __init__(
        self,
        min_delay: float = 1.0,
        max_delay: float = 3.0,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.min_delay = max(0.0, float(min_delay))
        self.max_delay = max(self.min_delay, float(max_delay))
        self._last_request_time: Optional[float] = None

    def _throttle(self) -> None:
        """Enforce delay measured from previous request completion.

        # Complexity: O(1)
        """
        if self.max_delay <= 0.0:
            return

        delay = random.uniform(self.min_delay, self.max_delay)
        if self._last_request_time is not None:
            elapsed = time.monotonic() - self._last_request_time
            remaining = delay - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self._last_request_time = time.monotonic()

    def request(self, *args, **kwargs) -> requests.Response:
        """Throttle before delegating to superclass request.

        # Complexity: O(1) + network time
        """
        self._throttle()
        return super().request(*args, **kwargs)
