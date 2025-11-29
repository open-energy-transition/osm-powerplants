"""Tests for models module."""


def test_rejection_reason_enum():
    """Test RejectionReason enumeration."""
    from osm_powerplants.models import RejectionReason

    assert RejectionReason.MISSING_SOURCE_TAG.value == "Missing source tag"
    assert RejectionReason.CAPACITY_ZERO.value == "Capacity zero"


def test_unit_config_hash():
    """Test configuration hash generation."""
    from osm_powerplants.models import Unit

    config1 = {"plants_only": True, "source_mapping": {"Solar": ["solar"]}}
    config2 = {"plants_only": False, "source_mapping": {"Solar": ["solar"]}}

    hash1 = Unit._generate_config_hash(config1)
    hash2 = Unit._generate_config_hash(config2)

    assert hash1 != hash2
    assert len(hash1) == 32  # MD5 hash length


def test_units_statistics():
    """Test Units statistics calculation."""
    from osm_powerplants import Unit, Units

    units = Units(
        [
            Unit(
                projectID="1",
                Country="Germany",
                Fueltype="Solar",
                lat=52.0,
                lon=13.0,
                Capacity=10.0,
            ),
            Unit(
                projectID="2",
                Country="Germany",
                Fueltype="Wind",
                lat=52.1,
                lon=13.1,
                Capacity=20.0,
            ),
            Unit(
                projectID="3",
                Country="France",
                Fueltype="Solar",
                lat=48.0,
                lon=2.0,
                Capacity=15.0,
            ),
        ]
    )

    stats = units.get_statistics()

    assert stats["total_units"] == 3
    assert stats["units_with_coordinates"] == 3
    assert stats["coverage_percentage"] == 100.0
    assert "Germany" in stats["countries"]
    assert "France" in stats["countries"]
    assert "Solar" in stats["fuel_types"]
    assert "Wind" in stats["fuel_types"]
    assert stats["total_capacity_mw"] == 45.0


def test_units_empty_statistics():
    """Test statistics for empty Units collection."""
    from osm_powerplants import Units

    units = Units()
    stats = units.get_statistics()

    assert stats["total_units"] == 0


def test_plant_geometry_point():
    """Test PlantGeometry with point."""
    from shapely.geometry import Point

    from osm_powerplants.models import PlantGeometry

    geom = PlantGeometry(
        id="node/123",
        type="node",
        geometry=Point(13.0, 52.0),
    )

    centroid = geom.get_centroid()
    assert centroid == (52.0, 13.0)


def test_plant_geometry_contains():
    """Test PlantGeometry point containment."""
    from shapely.geometry import Polygon

    from osm_powerplants.models import PlantGeometry

    # Create a simple square polygon
    polygon = Polygon(
        [
            (13.0, 52.0),
            (13.1, 52.0),
            (13.1, 52.1),
            (13.0, 52.1),
            (13.0, 52.0),
        ]
    )

    geom = PlantGeometry(
        id="way/456",
        type="way",
        geometry=polygon,
    )

    # Point inside
    assert geom.contains_point(52.05, 13.05)

    # Point outside
    assert not geom.contains_point(53.0, 14.0)
