"""Tests for utility functions."""


def test_parse_capacity_basic():
    """Test basic capacity parsing."""
    from osm_powerplants.utils import parse_capacity_value

    success, capacity, _ = parse_capacity_value("50 MW", advanced_extraction=False)
    assert success
    assert capacity == 50.0


def test_parse_capacity_advanced():
    """Test advanced capacity parsing with units."""
    from osm_powerplants.utils import parse_capacity_value

    # Megawatts
    success, capacity, _ = parse_capacity_value("100MW", advanced_extraction=True)
    assert success
    assert capacity == 100.0

    # Kilowatts
    success, capacity, _ = parse_capacity_value("500 kW", advanced_extraction=True)
    assert success
    assert capacity == 0.5

    # Gigawatts
    success, capacity, _ = parse_capacity_value("1.5GW", advanced_extraction=True)
    assert success
    assert capacity == 1500.0


def test_parse_capacity_peak():
    """Test capacity parsing with peak suffix."""
    from osm_powerplants.utils import parse_capacity_value

    success, capacity, _ = parse_capacity_value("100 MWp", advanced_extraction=True)
    assert success
    assert capacity == 100.0

    success, capacity, _ = parse_capacity_value("50kWp", advanced_extraction=True)
    assert success
    assert capacity == 0.05


def test_parse_capacity_invalid():
    """Test capacity parsing with invalid input."""
    from osm_powerplants.utils import parse_capacity_value

    success, capacity, _ = parse_capacity_value("invalid", advanced_extraction=True)
    assert not success
    assert capacity is None


def test_get_country_code():
    """Test country code lookup."""
    from osm_powerplants.utils import get_country_code

    assert get_country_code("Germany") == "DE"
    assert get_country_code("France") == "FR"
    assert get_country_code("DE") == "DE"
    assert get_country_code("DEU") == "DE"
    assert get_country_code("InvalidCountry") is None


def test_standardize_country_name():
    """Test country name standardization."""
    from osm_powerplants.utils import standardize_country_name

    assert standardize_country_name("DE") == "Germany"
    assert standardize_country_name("Germany") == "Germany"
    assert standardize_country_name("FR") == "France"


def test_determine_set_type():
    """Test set type determination from technology."""
    from osm_powerplants import get_config
    from osm_powerplants.utils import determine_set_type

    config = get_config()

    # PP technologies
    assert determine_set_type("PV", config) == "PP"
    assert determine_set_type("Onshore", config) == "PP"
    assert determine_set_type("Run-Of-River", config) == "PP"

    # Store technologies
    assert determine_set_type("Pumped Storage", config) == "Store"
    assert determine_set_type("Reservoir", config) == "Store"

    # Unknown
    assert determine_set_type("Unknown", config) is None
    assert determine_set_type(None, config) is None
