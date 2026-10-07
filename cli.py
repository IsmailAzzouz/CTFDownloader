"""Command-line interface for CTFDownloader."""

import argparse
import sys
from typing import Any, Dict, List, Optional

from .client import CTFdClient
from .downloader import CTFDownloader
from .env import get_env, get_env_float, load_env


def _build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    # Complexity: O(1)
    """
    parser = argparse.ArgumentParser(
        prog="ctfdownloader",
        description="Download challenges and files from CTFd platforms.",
    )
    parser.add_argument(
        "--env-file",
        metavar="PATH",
        help="Path to .env configuration file (default: .env)",
    )
    parser.add_argument(
        "-u", "--url",
        help="CTFd base URL (overrides CTF_BASE_URL)",
    )
    parser.add_argument(
        "-t", "--token",
        help="CTFd API access token (overrides CTF_TOKEN)",
    )
    parser.add_argument(
        "-U", "--username",
        help="CTFd username (overrides CTF_USERNAME)",
    )
    parser.add_argument(
        "-P", "--password",
        help="CTFd password (overrides CTF_PASSWORD)",
    )
    parser.add_argument(
        "--min-delay",
        type=float,
        help="Minimum delay between HTTP requests in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--max-delay",
        type=float,
        help="Maximum delay between HTTP requests in seconds (default: 3.0)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Action to execute")

    # Command: list
    subparsers.add_parser("list", help="List all challenges from the CTFd platform")

    # Command: download
    dl_parser = subparsers.add_parser("download", help="Download challenges and attachments")
    dl_parser.add_argument(
        "-o", "--output",
        default="challenges",
        help="Target folder layout destination (default: challenges)",
    )
    dl_parser.add_argument(
        "-c", "--category",
        help="Filter downloads by challenge category",
    )
    dl_parser.add_argument(
        "--challenge",
        help="Filter downloads by challenge name or ID",
    )
    dl_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite files even if they already exist locally",
    )

    return parser


def _resolve_configuration(args: argparse.Namespace) -> Dict[str, Any]:
    """Merge CLI arguments with environment variables.

    # Complexity: O(1)
    """
    load_env(args.env_file)

    base_url = args.url or get_env("CTF_BASE_URL")
    if not base_url:
        print("[!] Error: CTFd base URL is missing. Provide --url or define CTF_BASE_URL.")
        sys.exit(1)

    if not base_url.startswith(("http://", "https://")):
        print("[!] Error: Base URL must start with http:// or https://")
        sys.exit(1)

    token = args.token or get_env("CTF_TOKEN") or get_env("CTFD_TOKEN")
    username = args.username or get_env("CTF_USERNAME")
    password = args.password or get_env("CTF_PASSWORD")

    min_delay = args.min_delay if args.min_delay is not None else get_env_float("RATE_MIN_DELAY", 1.0)
    max_delay = args.max_delay if args.max_delay is not None else get_env_float("RATE_MAX_DELAY", 3.0)

    return {
        "base_url": base_url,
        "token": token,
        "username": username,
        "password": password,
        "min_delay": min_delay,
        "max_delay": max_delay,
    }


def _setup_client(config: Dict[str, Any]) -> CTFdClient:
    """Instantiate and authenticate CTFdClient based on resolved configuration.

    # Complexity: O(1) + network auth time
    """
    client = CTFdClient(
        base_url=config["base_url"],
        min_delay=config["min_delay"],
        max_delay=config["max_delay"],
    )

    if config.get("token"):
        print("[*] Authenticating using API token...")
        client.authenticate_with_token(config["token"])
        return client

    if config.get("username") and config.get("password"):
        print("[*] Authenticating with username and password...")
        success = client.authenticate_with_credentials(config["username"], config["password"])
        if not success:
            print("[!] Authentication failed: invalid credentials.")
            sys.exit(1)
        print("[+] Login successful.")
        return client

    print("[*] No credentials or token provided. Proceeding as unauthenticated user...")
    return client


def _cmd_list(client: CTFdClient) -> None:
    """Execute list command.

    # Complexity: O(N) where N is challenge count
    """
    challenges = client.get_challenges()
    if not challenges:
        print("[*] No challenges found or platform is not public.")
        return

    print(f"[*] Found {len(challenges)} challenges:")
    for ch in challenges:
        cid = ch.get("id", "?")
        name = ch.get("name", "Unnamed")
        category = ch.get("category", "General")
        pts = ch.get("value", 0)
        print(f"  [{cid}] {name} ({category}) - {pts} pts")


def _cmd_download(client: CTFdClient, args: argparse.Namespace) -> None:
    """Execute download command.

    # Complexity: O(N * D) where N is challenge count and D is download work
    """
    downloader = CTFDownloader(
        client=client,
        output_dir=args.output,
        force_overwrite=args.force,
    )
    downloader.download_all(
        category_filter=args.category,
        challenge_filter=args.challenge,
    )


def main(argv: Optional[List[str]] = None) -> None:
    """CLI entrypoint function.

    # Complexity: O(1) + command execution
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        config = _resolve_configuration(args)
        client = _setup_client(config)

        if args.command == "list":
            _cmd_list(client)
        elif args.command == "download":
            _cmd_download(client, args)
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled by user.")
        sys.exit(130)
    except Exception as exc:
        print(f"[!] Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
