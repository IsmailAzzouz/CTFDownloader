"""Environment variable management and minimal .env file parser."""

import os
import re
from typing import Dict, Optional

_LINE_RE = re.compile(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$')


def _unquote(value: str) -> str:
    """Strip quotes or trailing inline comments from an env value.

    # Complexity: O(m) where m is the length of value
    """
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    if '#' in value:
        value = value.split('#', 1)[0].strip()
    return value


def load_env(filepath: Optional[str] = None) -> Dict[str, str]:
    """Parse KEY=VALUE lines from a .env file into os.environ.

    Pre-existing environment variables have precedence over file entries.

    # Complexity: O(n * m) where n is line count and m is average line length
    """
    target_path = filepath or os.path.join(os.getcwd(), '.env')
    loaded: Dict[str, str] = {}

    if not os.path.isfile(target_path):
        return loaded

    with open(target_path, 'r', encoding='utf-8') as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            match = _LINE_RE.match(line)
            if not match:
                continue
            key, raw_val = match.group(1), match.group(2)
            parsed_val = _unquote(raw_val)
            loaded[key] = parsed_val
            os.environ.setdefault(key, parsed_val)

    return loaded


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Fetch an environment variable with an optional default.

    # Complexity: O(1)
    """
    return os.environ.get(key, default)


def get_env_float(key: str, default: float) -> float:
    """Fetch an environment variable as a float, falling back to default.

    # Complexity: O(1)
    """
    raw_val = os.environ.get(key)
    if raw_val is None:
        return default
    try:
        return float(raw_val)
    except ValueError:
        return default
