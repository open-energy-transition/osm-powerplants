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

## Releasing

### PyPI Setup (one-time)

The package uses [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC) for secure, tokenless releases.

1. On PyPI, go to [project publishing settings](https://pypi.org/manage/project/osm-powerplants/settings/publishing/)
2. Add trusted publisher:
   - Owner: `open-energy-transition`
   - Repository: `osm-powerplants`
   - Workflow: `publish.yml`
   - Environment: `pypi`
3. On GitHub, create environment named `pypi` (Settings → Environments)

### Publishing

1. Update version in `pyproject.toml`
2. Commit: `git commit -m "chore: bump version to X.Y.Z"`
3. Create GitHub release with tag `vX.Y.Z`
4. The `publish.yml` workflow triggers automatically
