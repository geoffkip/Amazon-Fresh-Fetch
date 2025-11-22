# Contributing to Amazon Fresh Fetch

Thank you for your interest in contributing!

## Development Setup

1. Clone the repository
2. Create virtual environment: `python -m venv .venv`
3. Activate: `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Install Playwright: `playwright install chromium`

## Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to functions and classes

## Testing

Run tests with:
```bash
pytest tests/
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Building Installers

See [DISTRIBUTION_GUIDE.md](DISTRIBUTION_GUIDE.md) for instructions on building installers.

