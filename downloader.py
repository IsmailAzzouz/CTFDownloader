"""Challenge content storage and atomic file download logic."""

import os
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

from .client import CTFdClient
from .utils import extract_urls, sanitize_name


class CTFDownloader:
    """Manages directory organization and atomic file downloads for challenges."""

    def __init__(
        self,
        client: CTFdClient,
        output_dir: str = "challenges",
        force_overwrite: bool = False,
        logger: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.client = client
        self.output_dir = os.path.abspath(output_dir)
        self.force_overwrite = force_overwrite
        self.log = logger or print

    def _build_description_content(self, detail: Dict[str, Any], urls: List[str]) -> str:
        """Format challenge metadata into readable plain text.

        # Complexity: O(U + D) where U is URL count and D is description length
        """
        lines = [
            f"Title: {detail.get('name', 'Unknown')}",
            f"Category: {detail.get('category', 'Unknown')}",
            f"Points: {detail.get('value', 'N/A')}",
        ]
        if detail.get('tags'):
            lines.append(f"Tags: {', '.join(detail['tags'])}")
        if detail.get('connection_info'):
            lines.append(f"Connection Info: {detail['connection_info']}")

        lines.extend(["", "Description:", detail.get('description', '').strip()])

        if urls:
            lines.extend(["", "Extracted URLs:"])
            for url in urls:
                lines.append(f"- {url}")

        hints = detail.get('hints', [])
        if hints:
            lines.extend(["", "Hints:"])
            for h in hints:
                content = h.get('content') if isinstance(h, dict) else str(h)
                if content:
                    lines.append(f"- {content}")

        lines.append("")
        return "\n".join(lines)

    def _save_description(self, challenge_dir: str, detail: Dict[str, Any]) -> None:
        """Write challenge description and metadata file.

        # Complexity: O(D) where D is description size
        """
        desc_text = detail.get('description', '')
        urls = extract_urls(desc_text)
        content = self._build_description_content(detail, urls)

        desc_file = os.path.join(challenge_dir, "description.txt")
        with open(desc_file, "w", encoding="utf-8") as handle:
            handle.write(content)

    def _extract_filename_from_url(self, file_url: str) -> str:
        """Derive safe filename from URL path component.

        # Complexity: O(L) where L is url string length
        """
        path = urlparse(file_url).path
        raw_name = path.rstrip('/').split('/')[-1] if '/' in path else "attachment"
        return sanitize_name(raw_name, fallback="attachment")

    def _download_file_atomic(self, file_url: str, dest_path: str) -> bool:
        """Download remote file atomically into temporary file before replacing.

        # Complexity: O(S) where S is file size (streamed in 8KB chunks)
        """
        abs_url = self.client.resolve_url(file_url)
        temp_path = f"{dest_path}.part"

        try:
            with self.client.session.get(abs_url, stream=True, timeout=self.client.timeout) as resp:
                resp.raise_for_status()
                content_length = resp.headers.get('Content-Length')

                if not self.force_overwrite and os.path.isfile(dest_path) and content_length:
                    if os.path.getsize(dest_path) == int(content_length):
                        self.log(f"    [*] Already up-to-date: {os.path.basename(dest_path)}")
                        return True

                with open(temp_path, "wb") as handle:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            handle.write(chunk)

            os.replace(temp_path, dest_path)
            self.log(f"    [+] Saved: {os.path.basename(dest_path)}")
            return True
        except Exception as exc:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            self.log(f"    [!] Failed to download {os.path.basename(dest_path)}: {exc}")
            return False

    def download_challenge(self, challenge_id: int) -> bool:
        """Download all content and attachments for a single challenge.

        # Complexity: O(F * S) where F is file count and S is average file size
        """
        try:
            detail = self.client.get_challenge_detail(challenge_id)
        except Exception as exc:
            self.log(f"[!] Could not fetch details for challenge ID {challenge_id}: {exc}")
            return False

        name = detail.get('name', f"Challenge_{challenge_id}")
        category = detail.get('category', 'Uncategorized')

        safe_cat = sanitize_name(category, fallback="Misc")
        safe_name = sanitize_name(name, fallback=f"challenge_{challenge_id}")

        challenge_dir = os.path.join(self.output_dir, safe_cat, safe_name)
        os.makedirs(challenge_dir, exist_ok=True)

        self.log(f"[*] Processing: {name} [{category}]")
        self._save_description(challenge_dir, detail)

        files = detail.get('files', [])
        for file_ref in files:
            file_url = file_ref if isinstance(file_ref, str) else file_ref.get('location', '')
            if not file_url:
                continue
            filename = self._extract_filename_from_url(file_url)
            dest_file = os.path.join(challenge_dir, filename)
            self._download_file_atomic(file_url, dest_file)

        return True

    def download_all(
        self,
        category_filter: Optional[str] = None,
        challenge_filter: Optional[str] = None,
    ) -> int:
        """Download all visible challenges matching optional criteria.

        # Complexity: O(C * D) where C is challenge count and D is average download work
        """
        challenges = self.client.get_challenges()
        self.log(f"[*] Found {len(challenges)} total challenges")

        cat_f = category_filter.strip().lower() if category_filter else None
        chall_f = challenge_filter.strip().lower() if challenge_filter else None

        processed = 0
        for chall in challenges:
            c_cat = str(chall.get('category', '')).strip().lower()
            c_name = str(chall.get('name', '')).strip().lower()
            c_id = str(chall.get('id', ''))

            if cat_f and cat_f != c_cat:
                continue
            if chall_f and chall_f not in (c_name, c_id):
                continue

            self.download_challenge(chall['id'])
            processed += 1

        self.log(f"[+] Download complete: {processed} challenges saved to {self.output_dir}")
        return processed
