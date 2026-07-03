"""Tests for parsing utilities."""


def test_capacity_extractor_init():
    """Test CapacityExtractor initialization."""
    from osm_powerplants import get_config
    from osm_powerplants.parsing.capacity import CapacityExtractor
    from osm_powerplants.quality.rejection import RejectionTracker

    tracker = RejectionTracker()
    config = get_config()
    extractor = CapacityExtractor(tracker, config)
    assert extractor is not None


def test_capacity_extractor_basic():
    """Test basic capacity extraction."""
    from osm_powerplants import get_config
    from osm_powerplants.parsing.capacity import CapacityExtractor
    from osm_powerplants.quality.rejection import RejectionTracker

    tracker = RejectionTracker()
    config = get_config()
    extractor = CapacityExtractor(tracker, config)

    element = {"id": 1, "type": "node", "tags": {"plant:output:electricity": "100 MW"}}
    success, value, source = extractor.basic_extraction(
        element, "plant:output:electricity"
    )
    assert success
    assert value == 100.0


def test_capacity_extractor_units():
    """Test capacity extraction with MW units."""
    from osm_powerplants import get_config
    from osm_powerplants.parsing.capacity import CapacityExtractor
    from osm_powerplants.quality.rejection import RejectionTracker

    tracker = RejectionTracker()
    config = get_config()
    extractor = CapacityExtractor(tracker, config)

    # MW - basic extraction handles MW
    element = {"id": 1, "type": "node", "tags": {"plant:output:electricity": "50 MW"}}
    success, value, _ = extractor.basic_extraction(element, "plant:output:electricity")
    assert success
    assert value == 50.0


def test_capacity_extractor_placeholder():
    """Test capacity extraction rejects placeholders."""
    from osm_powerplants import get_config
    from osm_powerplants.parsing.capacity import CapacityExtractor
    from osm_powerplants.quality.rejection import RejectionTracker

    tracker = RejectionTracker()
    config = get_config()
    extractor = CapacityExtractor(tracker, config)

    element = {"id": 1, "type": "node", "tags": {"plant:output:electricity": "yes"}}
    success, value, _ = extractor.basic_extraction(element, "plant:output:electricity")
    assert not success


def _make_plant_parser():
    from pathlib import Path

    import osm_powerplants
    from osm_powerplants import get_config
    from osm_powerplants.parsing.plants import PlantParser
    from osm_powerplants.quality.rejection import RejectionTracker

    # Load the bundled config explicitly so the test is independent of any
    # (possibly stale) user-level config in the platformdirs config dir.
    bundled_config = Path(osm_powerplants.__file__).parent / "config.yaml"
    return PlantParser(None, RejectionTracker(), get_config(str(bundled_config)))


def test_technology_combustion_waste_is_steam_turbine():
    """plant:method=combustion on a waste plant maps to Steam Turbine.

    'combustion' describes the heat-generating method, not the prime mover;
    waste incinerators are boiler + steam turbine plants.
    """
    parser = _make_plant_parser()
    element = {
        "id": 47962126,
        "type": "way",
        "tags": {"plant:source": "waste", "plant:method": "combustion"},
    }
    assert parser.extract_technology_from_tags(element, "plant", "Waste") == (
        "Steam Turbine"
    )


def test_technology_combustion_biomass_is_steam_turbine():
    """plant:method=combustion on a solid-biomass plant maps to Steam Turbine."""
    parser = _make_plant_parser()
    element = {
        "id": 1,
        "type": "way",
        "tags": {"plant:source": "biomass", "plant:method": "combustion"},
    }
    assert parser.extract_technology_from_tags(element, "plant", "Solid Biomass") == (
        "Steam Turbine"
    )


def test_technology_combustion_biogas_stays_combustion_engine():
    """plant:method=combustion on a biogas plant still maps to Combustion Engine."""
    parser = _make_plant_parser()
    element = {
        "id": 1,
        "type": "node",
        "tags": {"plant:source": "biogas", "plant:method": "combustion"},
    }
    assert parser.extract_technology_from_tags(element, "plant", "Biogas") == (
        "Combustion Engine"
    )


def test_technology_specific_tag_beats_source_preference():
    """An unambiguous prime-mover tag is not overridden by the source order."""
    parser = _make_plant_parser()
    element = {
        "id": 1,
        "type": "way",
        "tags": {"plant:source": "waste", "plant:method": "reciprocating_engine"},
    }
    assert parser.extract_technology_from_tags(element, "plant", "Waste") == (
        "Combustion Engine"
    )
