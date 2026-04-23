"""Tests for interface validation."""


def test_valid_fueltypes():
    """Test VALID_FUELTYPES constant."""
    from osm_powerplants.interface import VALID_FUELTYPES

    assert "Solar" in VALID_FUELTYPES
    assert "Wind" in VALID_FUELTYPES
    assert "Hydro" in VALID_FUELTYPES
    assert "Nuclear" in VALID_FUELTYPES
    assert "Natural Gas" in VALID_FUELTYPES


def test_valid_technologies():
    """Test VALID_TECHNOLOGIES constant."""
    from osm_powerplants.interface import VALID_TECHNOLOGIES

    assert "PV" in VALID_TECHNOLOGIES
    assert "Onshore" in VALID_TECHNOLOGIES
    assert "Offshore" in VALID_TECHNOLOGIES
    assert "Run-Of-River" in VALID_TECHNOLOGIES
    assert "Pumped Storage" in VALID_TECHNOLOGIES


def test_valid_sets():
    """Test VALID_SETS constant."""
    from osm_powerplants.interface import VALID_SETS

    assert "PP" in VALID_SETS
    assert "Store" in VALID_SETS
    assert "CHP" in VALID_SETS


def test_validate_and_standardize_df():
    """Test DataFrame validation and standardization."""
    import pandas as pd

    from osm_powerplants.interface import validate_and_standardize_df

    df = pd.DataFrame(
        {
            "projectID": ["1", "2"],
            "Country": ["Germany", "France"],
            "Fueltype": ["Solar", "Wind"],
            "Technology": ["PV", "Onshore"],
            "Capacity": [10.0, 20.0],
            "config_hash": ["abc", "def"],  # metadata to remove
        }
    )

    result = validate_and_standardize_df(df)

    assert "config_hash" not in result.columns
    assert "projectID" in result.columns
    assert len(result) == 2


def test_validate_countries_mixed_formats():
    """Test validation with mixed country formats."""
    from osm_powerplants import validate_countries

    valid, codes = validate_countries(["Germany", "FR", "ESP"])

    assert len(valid) == 3
    assert codes["Germany"] == "DE"
    assert codes["FR"] == "FR"
    assert codes["ESP"] == "ES"


def test_validate_countries_common_names():
    """Test validation with common country name variants."""
    from osm_powerplants import validate_countries

    # USA variant
    valid, codes = validate_countries(["USA"])
    assert codes["USA"] == "US"


def test_validate_countries_empty():
    """Test validation with empty list returns empty."""
    from osm_powerplants import validate_countries

    valid, codes = validate_countries([])
    assert len(valid) == 0
    assert len(codes) == 0


# ─── rejected_output_path plumbing (issue #5 follow-up) ─────────────────────


def test_process_units_writes_rejection_report(tmp_path, monkeypatch):
    """When rejected_output_path is set, process_units must create a
    RejectionTracker, thread it into process_countries, and persist the
    report as CSV + GeoJSON so users can diagnose why plants were dropped."""
    import pandas as pd

    import osm_powerplants.interface as iface
    from osm_powerplants.models import ElementType, RejectionReason

    accepted = pd.DataFrame(
        {
            "projectID": ["1"],
            "Country": ["Kenya"],
            "Fueltype": ["Hydro"],
            "Capacity": [5.0],
        }
    )

    observed: dict = {}

    def fake_process_countries(*, rejection_tracker, **kwargs):
        observed["tracker"] = rejection_tracker
        # Simulate the pipeline finding and discarding one plant.
        rejection_tracker.add_rejection(
            element_id="123",
            element_type=ElementType.WAY,
            reason=RejectionReason.MISSING_OUTPUT_TAG,
            details="tags: {'power': 'plant', 'plant:source': 'solar'}",
            country="Kenya",
            unit_type="plant",
            coordinates=(-1.0, 36.0),
        )
        return accepted

    monkeypatch.setattr(iface, "process_countries", fake_process_countries)

    out_csv = tmp_path / "plants.csv"
    rej_csv = tmp_path / "rejected.csv"
    rej_geojson = tmp_path / "rejected.geojson"

    df = iface.process_units(
        countries=["Kenya"],
        config={"force_refresh": True},
        cache_dir=str(tmp_path / "cache"),
        output_path=str(out_csv),
        rejected_output_path=str(rej_csv),
    )

    assert len(df) == 1
    assert observed["tracker"] is not None
    assert out_csv.exists()
    assert rej_csv.exists()
    assert rej_geojson.exists()

    rej = pd.read_csv(rej_csv)
    assert len(rej) == 1
    assert rej.iloc[0]["reason"] == RejectionReason.MISSING_OUTPUT_TAG.value


def test_process_units_without_rejected_output_path_skips_tracker(
    tmp_path, monkeypatch
):
    """Default behaviour: no tracker created, no rejection artefacts written —
    preserves the pre-existing API for callers that don't need diagnostics."""
    import pandas as pd

    import osm_powerplants.interface as iface

    observed: dict = {}

    def fake_process_countries(*, rejection_tracker, **kwargs):
        observed["tracker"] = rejection_tracker
        return pd.DataFrame()

    monkeypatch.setattr(iface, "process_countries", fake_process_countries)

    iface.process_units(
        countries=["Kenya"],
        config={"force_refresh": True},
        cache_dir=str(tmp_path / "cache"),
    )

    assert observed["tracker"] is None
    assert not any(tmp_path.glob("*rejected*"))
