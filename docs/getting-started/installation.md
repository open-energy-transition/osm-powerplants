# Installation

## Requirements

- Python 3.10+

## Install

```bash
pip install osm-powerplants
```

## From Source

```bash
git clone https://github.com/open-energy-transition/osm-powerplants.git
cd osm-powerplants
pip install -e .
```

## Verify

```bash
osm-powerplants info
```

## Development

```bash
pip install -e ".[dev]"
pre-commit install
pytest
```
