"""Tests for OverpassAPIClient failure-handling correctness.

Covers two bugs:

1. After all retries fail, ``query_overpass`` silently returned a fake empty
   response (``{"elements": [], "error": ...}``) instead of raising.  Callers
   had no way to distinguish "API failed" from "country has no plants".
2. ``get_plants_data`` / ``get_generators_data`` unconditionally wrote the
   query response to the per-country JSON cache — including empty-on-error
   responses — which poisoned subsequent retries against mirror endpoints.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from osm_powerplants.retrieval.client import OverpassAPIClient, OverpassAPIError


@pytest.fixture
def client(tmp_path):
    """Fresh OverpassAPIClient with an isolated cache dir."""
    return OverpassAPIClient(
        cache_dir=str(tmp_path / "cache"),
        timeout=1,
        max_retries=2,
        retry_delay=0,
        show_progress=False,
    )


# ─── Bug 1: silent failure on exhausted retries ─────────────────────────────


def test_query_overpass_raises_when_all_retries_fail(client):
    """After max_retries consecutive RequestExceptions, query_overpass must
    raise OverpassAPIError so callers can distinguish failure from empty data."""
    with patch("osm_powerplants.retrieval.client.requests.post") as post:
        post.side_effect = requests.exceptions.Timeout("fake timeout")

        with pytest.raises(OverpassAPIError) as exc:
            client.query_overpass("[out:json];node;out;")

        assert "fake timeout" in str(exc.value) or "timeout" in str(exc.value).lower()
        assert post.call_count == client.max_retries


def test_query_overpass_returns_data_on_success(client):
    """Success path still returns the parsed JSON dict unchanged."""
    payload = {"elements": [{"type": "node", "id": 1}]}
    with patch("osm_powerplants.retrieval.client.requests.post") as post:
        mock_resp = MagicMock()
        mock_resp.json.return_value = payload
        mock_resp.raise_for_status.return_value = None
        post.return_value = mock_resp

        result = client.query_overpass("[out:json];node;out;")
        assert result == payload


def test_query_overpass_recovers_after_transient_failure(client):
    """A single failure followed by success returns the success payload."""
    payload = {"elements": [{"type": "node", "id": 42}]}
    ok = MagicMock()
    ok.json.return_value = payload
    ok.raise_for_status.return_value = None

    with patch("osm_powerplants.retrieval.client.requests.post") as post:
        post.side_effect = [requests.exceptions.Timeout("first fails"), ok]

        result = client.query_overpass("[out:json];node;out;")
        assert result == payload
        assert post.call_count == 2


# ─── Bug 2: cache poisoning on failure ──────────────────────────────────────


def test_get_plants_data_does_not_cache_on_failure(client):
    """When the underlying query fails, no entry should be written to the
    plants cache — otherwise mirror-fallback retries hit a poisoned entry."""
    with patch("osm_powerplants.retrieval.client.requests.post") as post:
        post.side_effect = requests.exceptions.Timeout("unreachable")

        with pytest.raises(OverpassAPIError):
            client.get_plants_data("Luxembourg")

    # Cache must NOT have an entry for LU
    cached = client.cache.get_plants("LU")
    assert cached is None or cached == {} or not cached.get("elements")


def test_get_generators_data_does_not_cache_on_failure(client):
    """Same guarantee for generators."""
    with patch("osm_powerplants.retrieval.client.requests.post") as post:
        post.side_effect = requests.exceptions.Timeout("unreachable")

        with pytest.raises(OverpassAPIError):
            client.get_generators_data("Luxembourg")

    cached = client.cache.get_generators("LU")
    assert cached is None or cached == {} or not cached.get("elements")


def test_failed_call_allows_successful_retry(client):
    """After a failure, a subsequent successful call should actually hit the
    network (not return a stale empty cache entry) and succeed."""
    payload = {
        "elements": [
            {"type": "node", "id": 1, "tags": {"power": "plant"}, "lat": 0, "lon": 0}
        ]
    }
    ok = MagicMock()
    ok.json.return_value = payload
    ok.raise_for_status.return_value = None

    with patch("osm_powerplants.retrieval.client.requests.post") as post:
        # First call: always fails
        post.side_effect = requests.exceptions.Timeout("unreachable")
        with pytest.raises(OverpassAPIError):
            client.get_plants_data("Luxembourg")

        # Second call with the same client must hit the network again
        post.side_effect = None
        post.return_value = ok
        result = client.get_plants_data("Luxembourg")
        assert result.get("elements")
        assert len(result["elements"]) == 1
