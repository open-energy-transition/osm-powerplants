"""Tests for core module."""

from pathlib import Path

import pytest


def test_import():
    """Test that the package can be imported."""
    import osm_powerplants

    assert hasattr(osm_powerplants, "__version__")
    assert isinstance(osm_powerplants.__version__, str)


def test_public_api():
    """Test that public API is accessible."""
    from osm_powerplants import (
        get_cache_dir,
        get_config,
        process_countries,
        process_units,
        validate_countries,
    )

    assert callable(process_countries)
    assert callable(process_units)
    assert callable(validate_countries)
    assert callable(get_config)
    assert callable(get_cache_dir)


def test_get_config():
    """Test configuration loading."""
    from osm_powerplants import get_config

    config = get_config()
    assert isinstance(config, dict)
    # Check some expected keys
    assert "source_mapping" in config
    assert "technology_mapping" in config


def test_get_cache_dir():
    """Test cache directory creation."""
    from osm_powerplants import get_cache_dir, get_config

    config = get_config()
    cache_dir = get_cache_dir(config)

    assert isinstance(cache_dir, Path)
    assert cache_dir.exists()


def test_validate_countries_valid():
    """Test country validation with valid inputs."""
    from osm_powerplants import validate_countries

    valid, codes = validate_countries(["Germany", "France"])

    assert len(valid) == 2
    assert "Germany" in valid
    assert "France" in valid
    assert codes["Germany"] == "DE"
    assert codes["France"] == "FR"


def test_validate_countries_iso_codes():
    """Test country validation with ISO codes."""
    from osm_powerplants import validate_countries

    valid, codes = validate_countries(["DE", "FR", "ES"])

    assert len(valid) == 3
    assert codes["DE"] == "DE"
    assert codes["FR"] == "FR"
    assert codes["ES"] == "ES"


def test_validate_countries_invalid():
    """Test country validation with invalid inputs."""
    from osm_powerplants import validate_countries

    with pytest.raises(ValueError, match="Invalid country"):
        validate_countries(["InvalidCountryName"])


def test_unit_creation():
    """Test Unit dataclass creation."""
    from osm_powerplants import Unit

    unit = Unit(
        projectID="test_123",
        Country="Germany",
        lat=52.52,
        lon=13.405,
        Fueltype="Solar",
        Technology="PV",
        Capacity=10.5,
    )

    assert unit.projectID == "test_123"
    assert unit.Country == "Germany"
    assert unit.Capacity == 10.5


def test_unit_to_dict():
    """Test Unit to dictionary conversion."""
    from osm_powerplants import Unit

    unit = Unit(
        projectID="test_123",
        Country="Germany",
        Capacity=10.5,
    )

    data = unit.to_dict()

    assert isinstance(data, dict)
    assert data["projectID"] == "test_123"
    assert data["Country"] == "Germany"
    assert data["Capacity"] == 10.5
    # None values should be excluded
    assert "Name" not in data


def test_units_collection():
    """Test Units collection."""
    from osm_powerplants import Unit, Units

    units = Units()
    assert len(units) == 0

    unit1 = Unit(projectID="1", Country="Germany", Fueltype="Solar")
    unit2 = Unit(projectID="2", Country="France", Fueltype="Wind")

    units.add_unit(unit1)
    units.add_unit(unit2)

    assert len(units) == 2


def test_units_filter_by_country():
    """Test Units filtering by country."""
    from osm_powerplants import Unit, Units

    units = Units(
        [
            Unit(projectID="1", Country="Germany"),
            Unit(projectID="2", Country="France"),
            Unit(projectID="3", Country="Germany"),
        ]
    )

    german = units.filter_by_country("Germany")

    assert len(german) == 2


def test_units_to_dataframe():
    """Test Units to DataFrame conversion."""
    from osm_powerplants import Unit, Units

    units = Units(
        [
            Unit(projectID="1", Country="Germany", Capacity=10.0),
            Unit(projectID="2", Country="France", Capacity=20.0),
        ]
    )

    df = units.to_dataframe()

    assert len(df) == 2
    assert "projectID" in df.columns
    assert "Country" in df.columns
    assert df["Capacity"].sum() == 30.0
