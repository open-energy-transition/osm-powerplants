# Contributing

## Setup

```bash
git clone https://github.com/open-energy-transition/osm-powerplants.git
cd osm-powerplants
pip install -e ".[dev]"
pre-commit install
```

## Workflow

Single long-lived branch: `main`. Features, fixes and docs go in via
pull request from a topic branch.

```bash
git checkout -b feat/my-thing    # or fix/, docs/, chore/
# edit, commit, push
gh pr create
```

## Code style & tests

```bash
ruff check .
ruff format .
pytest
```

CI runs lint (`ruff check` + `ruff format --check`), docs build, and
the test suite on Python 3.10 / 3.11 / 3.12. All must pass before
merge.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/) — used as
hints for the changelog, not enforced by automation:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation only
- `test:` tests only
- `refactor:` internal restructuring
- `chore:` maintenance / tooling
- `feat!:` or `fix!:` breaking change

## Bug reports

Please include:

- Package version (`osm-powerplants --version`), Python version, OS
- Steps to reproduce
- Expected vs actual behaviour
- Full error traceback

## Releasing (maintainers)

Release is driven by pushing a `vX.Y.Z` tag:

1. Open a `chore: release X.Y.Z` PR that bumps `__version__`
   (`src/osm_powerplants/__init__.py`) and `version` in
   `pyproject.toml`, and moves `CHANGELOG.md`'s `Unreleased` block
   into a dated `## [X.Y.Z]` section.
2. Merge the PR.
3. Tag the merge commit and push:
   ```bash
   git checkout main && git pull --ff-only
   git tag -a vX.Y.Z -m "Release X.Y.Z"
   git push origin vX.Y.Z
   ```
4. Approve the `pypi` environment deployment in the Actions UI when
   prompted.

The `publish.yml` workflow verifies that the tag matches both version
strings, builds the sdist + wheel, publishes to PyPI via Trusted
Publishing, and creates a GitHub Release with the matching CHANGELOG
section as the body.

### PyPI Trusted Publishing (one-time)

[Trusted Publishing](https://docs.pypi.org/trusted-publishers/) is
already configured:

- Project: `osm-powerplants`
- Repository: `open-energy-transition/osm-powerplants`
- Workflow: `publish.yml`
- Environment: `pypi` (GitHub environment, approval-gated)
