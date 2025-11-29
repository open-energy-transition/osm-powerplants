# Contributing

Thank you for your interest in contributing to OSM Power Plants!

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/open-energy-transition/osm-powerplants.git
cd osm-powerplants
```

### 2. Create Virtual Environment

```bash
# Using uv (recommended)
uv venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Using pip
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Set up Pre-commit Hooks

```bash
pre-commit install
```

### 5. Verify Installation

```bash
osm-powerplants info
pytest
```

## Code Style

We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting, and [pre-commit](https://pre-commit.com/) to enforce code quality:

```bash
# Run pre-commit on all files
pre-commit run --all-files

# Check code manually
ruff check .

# Format code
ruff format .
```

### Style Guidelines

- Follow PEP 8
- Use type hints for function signatures
- Write docstrings in NumPy format
- Keep lines under 88 characters

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=osm_powerplants

# Specific test file
pytest tests/test_interface.py

# Verbose output
pytest -v
```

### Writing Tests

```python
# tests/test_example.py
import pytest
from osm_powerplants import validate_countries

def test_validate_countries_valid():
    valid, codes = validate_countries(["Germany", "France"])
    assert len(valid) == 2
    assert codes["Germany"] == "DE"

def test_validate_countries_invalid():
    with pytest.raises(ValueError, match="Invalid country"):
        validate_countries(["InvalidCountry"])
```

## Documentation

### Building Docs Locally

```bash
pip install mkdocs-material mkdocstrings[python]
mkdocs serve
```

Then visit http://localhost:8000

### Documentation Style

- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Keep API docs in sync with code

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code
- Add tests
- Update documentation

### 3. Run Checks

```bash
# Pre-commit runs all checks automatically
pre-commit run --all-files

# Or run individually
ruff check .
ruff format .
pytest
```

### 4. Commit

```bash
git add .
git commit -m "feat: add new feature"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `test:` Adding tests
- `refactor:` Code refactoring

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Issue Reporting

### Bug Reports

Include:

1. OSM Power Plants version
2. Python version
3. Operating system
4. Steps to reproduce
5. Expected vs actual behavior
6. Error messages/traceback

### Feature Requests

Include:

1. Clear description of the feature
2. Use case / motivation
3. Proposed implementation (optional)

## Architecture Overview

Before contributing, familiarize yourself with the [Architecture](advanced/architecture.md) documentation.

Key areas:

| Module | Purpose |
|--------|---------|
| `interface.py` | High-level API |
| `workflow.py` | Processing pipeline |
| `retrieval/` | API and caching |
| `parsing/` | OSM element parsing |
| `enhancement/` | Data improvement |
| `quality/` | Rejection tracking |

## Release Process

Releases are managed by maintainers:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create GitHub release
4. CI publishes to PyPI

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Questions?

- Open a GitHub issue
- Join discussions on GitHub
- Contact maintainers

Thank you for contributing! 🎉
