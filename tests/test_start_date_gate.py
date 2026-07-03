"""Tests for the missing_start_date_allowed gate on way/node plants and generators.

Regression tests for https://github.com/open-energy-transition/osm-powerplants/issues/15:
way- and node-type plants without a start_date tag were silently dropped even
when the config said missing_start_date_allowed: true, appearing in neither the
accepted output nor the rejection tracker.
"""

import copy
from pathlib import Path

import pytest

import osm_powerplants
from osm_powerplants import get_config
from osm_powerplants.models import RejectionReason
from osm_powerplants.parsing.generators import GeneratorParser
from osm_powerplants.parsing.plants import PlantParser
from osm_powerplants.quality.rejection import RejectionTracker
from osm_powerplants.retrieval.client import OverpassAPIClient


@pytest.fixture
def client(tmp_path):
    """Client with an isolated cache seeded with nodes for a closed way."""
    client = OverpassAPIClient(cache_dir=str(tmp_path / "cache"), show_progress=False)
    client.cache.store_nodes_bulk(
        [
            {"type": "node", "id": 101, "lat": 51.803, "lon": 4.640},
            {"type": "node", "id": 102, "lat": 51.804, "lon": 4.642},
            {"type": "node", "id": 103, "lat": 51.802, "lon": 4.643},
        ]
    )
    return client


def make_config(missing_start_date_allowed: bool) -> dict:
    # Load the bundled config explicitly so the test is independent of any
    # (possibly stale) user-level config in the platformdirs config dir.
    bundled_config = Path(osm_powerplants.__file__).parent / "config.yaml"
    config = copy.deepcopy(get_config(str(bundled_config)))
    config["missing_start_date_allowed"] = missing_start_date_allowed
    return config


def make_way_plant(tags: dict | None = None) -> dict:
    """Closed way modeled on way/1431035765 (AEC Dordrecht): complete except start_date."""
    base_tags = {
        "power": "plant",
        "name": "Afvalenergiecentrale Dordrecht",
        "plant:source": "waste",
        "plant:method": "combustion",
        "plant:output:electricity": "32 MW",
    }
    if tags:
        base_tags.update(tags)
    return {
        "type": "way",
        "id": 1431035765,
        "nodes": [101, 102, 103, 101],
        "tags": base_tags,
    }


def make_node_plant() -> dict:
    return {
        "type": "node",
        "id": 4242,
        "lat": 51.9,
        "lon": 4.5,
        "tags": {
            "power": "plant",
            "name": "Test Node Plant",
            "plant:source": "waste",
            "plant:output:electricity": "10 MW",
        },
    }


def test_way_plant_without_start_date_emitted_when_allowed(client):
    tracker = RejectionTracker()
    parser = PlantParser(client, tracker, make_config(True))

    unit = parser.process_element(make_way_plant(), "Netherlands")

    assert unit is not None
    assert unit.DateIn is None
    assert unit.Capacity == 32.0
    assert unit.Name == "Afvalenergiecentrale Dordrecht"


def test_node_plant_without_start_date_emitted_when_allowed(client):
    tracker = RejectionTracker()
    parser = PlantParser(client, tracker, make_config(True))

    unit = parser.process_element(make_node_plant(), "Netherlands")

    assert unit is not None
    assert unit.DateIn is None


def test_way_plant_without_start_date_rejected_and_tracked_when_not_allowed(client):
    tracker = RejectionTracker()
    parser = PlantParser(client, tracker, make_config(False))

    unit = parser.process_element(make_way_plant(), "Netherlands")

    assert unit is None
    reasons = [
        rejection.reason
        for rejections in tracker.rejected_elements.values()
        for rejection in rejections
    ]
    assert RejectionReason.MISSING_START_DATE_TAG in reasons


def test_way_plant_with_start_date_keeps_date(client):
    tracker = RejectionTracker()
    parser = PlantParser(client, tracker, make_config(True))

    unit = parser.process_element(make_way_plant({"start_date": "2009"}), "Netherlands")

    assert unit is not None
    assert unit.DateIn == 2009


def test_generator_without_start_date_emitted_when_allowed(client):
    tracker = RejectionTracker()
    parser = GeneratorParser(client, tracker, make_config(True))

    element = {
        "type": "node",
        "id": 5151,
        "lat": 52.0,
        "lon": 4.3,
        "_country": "Netherlands",
        "tags": {
            "power": "generator",
            "name": "Test Generator",
            "generator:source": "wind",
            "generator:output:electricity": "3 MW",
        },
    }
    unit = parser.process_element(element, "Netherlands")

    assert unit is not None
    assert unit.DateIn is None


def test_generator_without_start_date_rejected_and_tracked_when_not_allowed(client):
    tracker = RejectionTracker()
    parser = GeneratorParser(client, tracker, make_config(False))

    element = {
        "type": "node",
        "id": 5151,
        "lat": 52.0,
        "lon": 4.3,
        "_country": "Netherlands",
        "tags": {
            "power": "generator",
            "name": "Test Generator",
            "generator:source": "wind",
            "generator:output:electricity": "3 MW",
        },
    }
    unit = parser.process_element(element, "Netherlands")

    assert unit is None
    reasons = [
        rejection.reason
        for rejections in tracker.rejected_elements.values()
        for rejection in rejections
    ]
    assert RejectionReason.MISSING_START_DATE_TAG in reasons
