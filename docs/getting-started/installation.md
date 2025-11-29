# Installation

## Requirements

- Python 3.10 or higher
- pip or uv package manager

## Install from PyPI

```bash
pip install osm-powerplants
```

Or using [uv](https://github.com/astral-sh/uv):

```bash
uv pip install osm-powerplants
```

## Install from Source

For development or to get the latest features:

```bash
git clone https://github.com/open-energy-transition/osm-powerplants.git
cd osm-powerplants
pip install -e .
```

## Dependencies

The package automatically installs the following dependencies:

| Package | Purpose |
|---------|---------|
| `pandas` | Data manipulation |
| `numpy` | Numerical operations |
| `requests` | HTTP requests to Overpass API |
| `pycountry` | Country name validation |
| `shapely` | Geometric operations |
| `diskcache` | Persistent caching |
| `tqdm` | Progress bars |
| `scikit-learn` | Clustering algorithms |
| `platformdirs` | Cross-platform cache directories |
| `pyyaml` | Configuration file parsing |

## Verify Installation

After installation, verify everything works:

```bash
osm-powerplants info
```

Expected output:

```txt
Cache directory: /home/user/.cache/osm-powerplants
Config loaded: True
  - force_refresh: False
  - plants_only: True
```

## Optional: Development Dependencies

For contributing or running tests:

```bash
pip install -e ".[dev]"
```

This installs additional packages:

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `ruff` - Linting and formatting
- `pre-commit` - Git hooks for code quality

### Setting up Pre-commit

After installing dev dependencies, set up pre-commit hooks:

```bash
pre-commit install
```

This will automatically run linting and formatting checks before each commit.
