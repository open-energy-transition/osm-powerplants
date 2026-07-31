"""Tests for parsing utilities."""


def _make_processor():
    """Minimal concrete ElementProcessor for testing tag-extraction helpers."""
    from osm_powerplants import get_config
    from osm_powerplants.parsing.base import ElementProcessor
    from osm_powerplants.quality.rejection import RejectionTracker

    class _Processor(ElementProcessor):
        def process_element(self, element, country=None):
            return None

    return _Processor(
        client=None,
        geometry_handler=None,
        rejection_tracker=RejectionTracker(),
        config=get_config(),
    )


def test_extract_eic_from_tags():
    """ref:EU:EIC is read verbatim; blank/missing yields None."""
    proc = _make_processor()

    assert (
        proc.extract_eic_from_tags({"tags": {"ref:EU:EIC": "49W000000000070Z"}})
        == "49W000000000070Z"
    )
    # multiple codes kept as the raw semicolon-separated string
    assert (
        proc.extract_eic_from_tags(
            {"tags": {"ref:EU:EIC": "49W000000000092P;49W000000000094L"}}
        )
        == "49W000000000092P;49W000000000094L"
    )
    assert proc.extract_eic_from_tags({"tags": {"ref:EU:EIC": "   "}}) is None
    assert proc.extract_eic_from_tags({"tags": {"name": "no eic"}}) is None
    assert proc.extract_eic_from_tags({}) is None


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
