"""CTFDownloader - Download challenges and attachments from CTFd platforms."""

__version__ = "1.0.0"
__author__ = "CTFDownloader Contributors"
__all__ = ["CTFdClient", "CTFDownloader", "load_env", "RateLimitedSession"]

from .client import CTFdClient
from .downloader import CTFDownloader
from .env import load_env
from .utils import RateLimitedSession
