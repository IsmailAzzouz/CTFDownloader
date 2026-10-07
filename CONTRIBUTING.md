# Contributing to CTFDownloader

Thank you for your interest in improving **CTFDownloader**! We welcome contributions, bug reports, feature suggestions, and documentation improvements.

---

## Code of Conduct

Please be respectful, constructive, and mindful of other participants. Keep discussions focused on improving the tool for legitimate and authorized CTF training and archiving.

---

## Getting Started

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/ctfdownloader.git
   cd ctfdownloader
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

---

## Development Standards

- **Minimal Dependencies**: CTFDownloader adheres strictly to a zero-bloat philosophy. Avoid adding third-party dependencies unless strictly necessary.
- **Single Responsibility**: Keep modules and functions concise and dedicated to a single intent.
- **Complexity Documentation**: If a function exhibits algorithmic complexity greater than $O(1)$ or $O(\log n)$, document its Big-O performance in comments.
- **Input Validation**: Always sanitize and validate external inputs, URLs, and server responses. Prevent directory traversal and path injections.
- **Testing**: Every bugfix or new feature should be accompanied by deterministic unit tests under `tests/`.

---

## Running Tests

Before submitting a Pull Request, ensure all tests pass:

```bash
python -m unittest discover -s tests -v
# or
pytest
```

---

## Submitting a Pull Request

1. Create a feature branch:
   ```bash
   git checkout -b feature/my-enhancement
   ```
2. Commit your changes with clear, descriptive commit messages.
3. Push your branch:
   ```bash
   git push origin feature/my-enhancement
   ```
4. Open a Pull Request on GitHub detailing what changed and why.
