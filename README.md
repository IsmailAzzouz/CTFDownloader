# CTFDownloader

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CTFd API v1](https://img.shields.io/badge/CTFd-API%20v1%20Compatible-green.svg)](https://ctfd.io/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**CTFDownloader** is a lightweight, zero-bloat CLI utility designed to scrape, download, and organize challenges, attachments, and metadata from any [CTFd](https://ctfd.io/)-based competition platform.

---

## Key Features

- **Dual Authentication Modes**:
  - **API Token (Recommended)**: Seamless and reliable access using CTFd personal access tokens.
  - **Session Login**: Automatic scraping of CSRF nonces across modern and legacy CTFd themes.
- **Atomic & Resilient Downloads**: Files are downloaded to `.part` buffers and committed atomically, preventing corrupted or truncated files if your connection drops.
- **Smart Resumability**: Existing files matching the server's `Content-Length` are automatically skipped unless `--force` is specified.
- **Rate-Limiting & Anti-Ban**: Configurable randomized delays between requests to respect server policies and avoid Cloudflare or WAF rate-limiting.
- **Automatic Organization**: Saves challenges in neat `<Category>/<Challenge>/` directory trees with full metadata (`description.txt`, connection info, tags, extracted URLs).
- **Targeted Scraping**: Download the entire competition or filter by specific category or challenge name/ID.
- **Directory Traversal Protection**: Comprehensive sanitization of file and folder names across Windows, macOS, and Linux.
- **Zero Bloat**: Only one external dependency (`requests`).

---

## Installation

### From Source

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/ctfdownloader.git
cd ctfdownloader
pip install -r requirements.txt
```

### Install as a CLI Tool

You can also install CTFDownloader globally or in your virtual environment:

```bash
pip install .
```

This registers the `ctfdownloader` command directly in your shell.

---

## Configuration

CTFDownloader can be configured through command-line arguments, environment variables, or a `.env` file.

Copy the example file to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your CTFd instance details:

```env
# Required: Base URL of your CTFd instance
CTF_BASE_URL=https://ctf.example.com

# Option 1: CTFd Personal Access Token (Recommended)
# Found under: Profile -> Settings -> Access Tokens -> Generate
CTF_TOKEN=ctfd_abcdef123456...

# Option 2: Traditional Username & Password
CTF_USERNAME=your_username
CTF_PASSWORD=your_password

# Optional: Delay range between requests (in seconds)
RATE_MIN_DELAY=1.0
RATE_MAX_DELAY=3.0
```

> **Note**: Shell environment variables always take precedence over values defined in `.env`.

---

## Quick Start

### 1. List Available Challenges

Display all challenges with their category, ID, and point value:

```bash
ctfdownloader list
```

Or using python module syntax:

```bash
python -m ctfdownloader list
```

### 2. Download All Challenges

Download all challenges and attachments to the default `./challenges` directory:

```bash
ctfdownloader download
```

### 3. Filter by Category

Download only Web challenges:

```bash
ctfdownloader download --category Web
```

### 4. Download a Specific Challenge

Target a single challenge by name or ID:

```bash
ctfdownloader download --challenge "Buffer Overflow 101"
# or by ID:
ctfdownloader download --challenge 42
```

### 5. Custom Output Directory & Overwrite

Save to a custom folder and force re-download of existing files:

```bash
ctfdownloader download --output ./my_ctf_archive --force
```

---

## Generated Folder Layout

Downloaded challenges are structured cleanly:

```
challenges/
├── Cryptography/
│   └── RSA_Warmup/
│       ├── description.txt
│       └── cipher.txt
├── Forensics/
│   └── Memory_Dump/
│       ├── description.txt
│       └── memory.raw
└── Web/
    └── SQLi_Lab/
        └── description.txt
```

### Challenge Metadata Format

Each `description.txt` aggregates all challenge details for offline analysis:

```text
Title: SQLi Lab
Category: Web
Points: 200
Tags: sqli, web, easy
Connection Info: nc 10.10.10.10 1337

Description:
Can you bypass the authentication gate?

Extracted URLs:
- http://challenge.ctf.example.com:8080

Hints:
- Check how quotes are escaped in the login form.
```

---

## CLI Reference

```text
usage: ctfdownloader [-h] [--env-file PATH] [-u URL] [-t TOKEN] [-U USERNAME]
                     [-P PASSWORD] [--min-delay MIN_DELAY]
                     [--max-delay MAX_DELAY]
                     {list,download} ...

Options:
  -h, --help            Show this help message and exit
  --env-file PATH       Path to .env configuration file (default: .env)
  -u, --url URL         CTFd base URL (overrides CTF_BASE_URL)
  -t, --token TOKEN     CTFd API access token (overrides CTF_TOKEN)
  -U, --username USER   CTFd username (overrides CTF_USERNAME)
  -P, --password PASS   CTFd password (overrides CTF_PASSWORD)
  --min-delay FLOAT     Minimum delay between HTTP requests (default: 1.0s)
  --max-delay FLOAT     Maximum delay between HTTP requests (default: 3.0s)

Commands:
  list                  List all challenges from the CTFd platform
  download              Download challenges and attachments

Download Options:
  -o, --output DIR      Destination directory (default: challenges)
  -c, --category CAT    Filter downloads by challenge category
  --challenge NAME/ID   Filter downloads by challenge name or numeric ID
  --force               Force re-download even if files already exist locally
```

---

## Backward Compatibility

If you are using scripts from earlier versions of this scraper, compatibility entry points are preserved:

```bash
python list_challenges.py        # Equivalent to: ctfdownloader list
python scrape_and_organize.py    # Equivalent to: ctfdownloader download
```

---

## Development & Testing

Unit tests are implemented with standard `unittest` and can also be run with `pytest`:

```bash
# Run tests with unittest
python -m unittest discover -s tests -v

# Or run tests with pytest
pytest
```

---

## Contributing

Contributions, bug reports, and pull requests are welcome! Please check out [CONTRIBUTING.md](CONTRIBUTING.md) for details on code style, testing, and pull request guidelines.

---

## Ethics & Disclaimer

CTFDownloader is built solely for educational purposes, personal archiving, and offline CTF preparation. Only use this tool against CTFd instances where you have explicit permission to participate and download challenge assets. Always adhere to competition rules regarding automated scraping and rate limits.

---

## License

This project is licensed under the [MIT License](LICENSE).
