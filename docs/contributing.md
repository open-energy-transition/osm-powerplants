# Contributing

## Setup

```bash
git clone https://github.com/open-energy-transition/osm-powerplants.git
cd osm-powerplants
git checkout dev
pip install -e ".[dev]"
pre-commit install
```

## Branching Strategy

```
main    ← stable releases only, tagged (v0.1.0, v0.2.0)
  └── dev    ← integration branch, PRs target here
       ├── feature/xyz
       ├── fix/abc
       └── docs/...
```

- **Daily work**: Branch from `dev`, create PR back to `dev`
- **Releases**: Managed automatically by Release Please

## Code Style

```bash
ruff check .
ruff format .
pytest
```

## Pull Request Process

1. Create branch from `dev`: `git checkout dev && git checkout -b feature/name`
2. Make changes with tests
3. Run: `pre-commit run --all-files`
4. Commit: `git commit -m "feat: add feature"`
5. Push and create PR targeting `dev`

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature (bumps minor version)
- `fix:` Bug fix (bumps patch version)
- `feat!:` or `fix!:` Breaking change (bumps major version)
- `docs:` Documentation
- `test:` Tests
- `refactor:` Refactoring
- `chore:` Maintenance

## Bug Reports

Include:
- Version, Python version, OS
- Steps to reproduce
- Expected vs actual behavior
- Error traceback

## Releasing

Releases are automated via [Release Please](https://github.com/googleapis/release-please-action).

### How it works

1. Conventional commits on `main` trigger Release Please
2. Release Please creates/updates a "Release PR" with changelog
3. Merging the Release PR creates a GitHub release and publishes to PyPI

### PyPI Setup (one-time, maintainers only)

The package uses [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC).

1. On PyPI, go to [project publishing settings](https://pypi.org/manage/project/osm-powerplants/settings/publishing/)
2. Add trusted publisher:
   - Owner: `open-energy-transition`
   - Repository: `osm-powerplants`
   - Workflow: `release-please.yml`
   - Environment: `pypi`
3. On GitHub, create environment named `pypi` (Settings → Environments)
