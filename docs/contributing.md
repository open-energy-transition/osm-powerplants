# Contributing

## Setup

```bash
git clone https://github.com/open-energy-transition/osm-powerplants.git
cd osm-powerplants
pip install -e ".[dev]"
pre-commit install
```

## Code Style

```bash
ruff check .
ruff format .
pytest
```

## Pull Request Process

1. Create branch: `git checkout -b feature/name`
2. Make changes with tests
3. Run: `pre-commit run --all-files`
4. Commit: `git commit -m "feat: add feature"`
5. Push and create PR

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Refactoring

## Bug Reports

Include:
- Version, Python version, OS
- Steps to reproduce
- Expected vs actual behavior
- Error traceback
