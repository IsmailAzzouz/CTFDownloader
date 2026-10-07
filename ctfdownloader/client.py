"""Client interface for CTFd API and session authentication."""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

from .utils import RateLimitedSession

_NONCE_PATTERNS = (
    re.compile(r'["\']?csrfNonce["\']?\s*[:=]\s*["\']([^"\']+)["\']'),
    re.compile(r'name=["\']nonce["\'][^>]*?value=["\']([^"\']+)["\']'),
    re.compile(r'value=["\']([^"\']+)["\'][^>]*?name=["\']nonce["\']'),
    re.compile(r'<meta[^>]*name=["\']csrf-token["\'][^>]*content=["\']([^"\']+)["\']'),
)


class CTFdClient:
    """Interacts with the CTFd platform via API token or session login."""

    def __init__(
        self,
        base_url: str,
        session: Optional[requests.Session] = None,
        min_delay: float = 1.0,
        max_delay: float = 3.0,
        request_timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip('/')
        self.timeout = request_timeout
        self.session = session or RateLimitedSession(min_delay=min_delay, max_delay=max_delay)

    def authenticate_with_token(self, token: str) -> None:
        """Configure requests session headers with a CTFd personal access token.

        # Complexity: O(1)
        """
        clean_token = token.strip()
        self.session.headers.update({
            'Authorization': f'Token {clean_token}',
            'Content-Type': 'application/json',
        })

    def extract_csrf_nonce(self) -> Optional[str]:
        """Fetch login page and locate the CSRF nonce token.

        # Complexity: O(P * M) where P is patterns count and M is HTML length
        """
        login_url = f'{self.base_url}/login'
        resp = self.session.get(login_url, timeout=self.timeout)
        resp.raise_for_status()

        for pattern in _NONCE_PATTERNS:
            match = pattern.search(resp.text)
            if match:
                return match.group(1)
        return None

    def authenticate_with_credentials(self, username: str, password: str) -> bool:
        """Authenticate against CTFd using credentials and CSRF nonce.

        # Complexity: O(1) + network request time
        """
        login_url = f'{self.base_url}/login'
        nonce = self.extract_csrf_nonce()
        if not nonce:
            raise RuntimeError("Could not find CSRF nonce on CTFd login page")

        payload = {'name': username, 'password': password, 'nonce': nonce}
        resp = self.session.post(login_url, data=payload, timeout=self.timeout)

        # Check response content for typical CTFd auth failures
        lower_body = resp.text.lower()
        if 'incorrect' in lower_body or 'authentication failed' in lower_body:
            return False

        # In CTFd, a successful login usually sets session cookies and redirects to /challenges
        return resp.status_code in (200, 302)

    def get_challenges(self) -> List[Dict[str, Any]]:
        """Fetch list of all visible challenges.

        # Complexity: O(K) where K is the number of challenges in JSON
        """
        api_url = f'{self.base_url}/api/v1/challenges'
        resp = self.session.get(api_url, timeout=self.timeout)

        if resp.status_code == 401 or resp.status_code == 403:
            raise PermissionError("Authentication failed or unauthorized to view challenges.")

        resp.raise_for_status()
        data = resp.json()
        return data.get('data', [])

    def get_challenge_detail(self, challenge_id: int) -> Dict[str, Any]:
        """Fetch full details and file attachments for a specific challenge.

        # Complexity: O(1) + network request time
        """
        detail_url = f'{self.base_url}/api/v1/challenges/{challenge_id}'
        resp = self.session.get(detail_url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json().get('data', {})

    def resolve_url(self, relative_or_absolute_url: str) -> str:
        """Resolve a CTFd file path or URL to an absolute URL.

        # Complexity: O(1)
        """
        return urljoin(f'{self.base_url}/', relative_or_absolute_url.lstrip('/'))
