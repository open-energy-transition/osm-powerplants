"""Tests for OverpassAPIClient failure-handling correctness."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from osm_powerplants.retrieval.client import (
    USER_AGENT,
    OverpassAPIClient,
    OverpassAPIError,
)


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


# ─── Bug 3: Overpass "200 OK but resource-limited" empty responses ──────────


@pytest.mark.parametrize(
    "remark",
    [
        'runtime error: Query run out of memory in "query" at line 5',
        'runtime error: Query timed out in "query" at line 1 after 30 seconds',
        "Query run out of memory using about 2048 MB of RAM",
        "timed out",
    ],
)
def test_query_overpass_raises_on_error_remark(client, remark):
    """Overpass sometimes returns HTTP 200 with an ``elements: []`` body and
    an error in the ``remark`` field (resource-limited / server overload).
    The client must detect this and raise instead of propagating a
    falsely-successful empty response."""
    payload = {"version": 0.6, "elements": [], "remark": remark}
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status.return_value = None

    with patch("osm_powerplants.retrieval.client.requests.post") as post:
        post.return_value = mock_resp

        with pytest.raises(OverpassAPIError) as exc:
            client.query_overpass("[out:json];node;out;")

        assert "remark" in str(exc.value).lower() or remark.split(":")[0] in str(
            exc.value
        )


def test_query_overpass_tolerates_harmless_remark(client):
    """A ``remark`` field WITHOUT error keywords (e.g. informational notice)
    on an otherwise valid response must NOT trigger a raise."""
    payload = {
        "version": 0.6,
        "elements": [{"type": "node", "id": 1}],
        "remark": "attic query: this is an informational note",
    }
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status.return_value = None

    with patch("osm_powerplants.retrieval.client.requests.post") as post:
        post.return_value = mock_resp
        result = client.query_overpass("[out:json];node;out;")
        assert result == payload


def test_query_overpass_allows_legitimate_empty_result(client):
    """An empty ``elements`` list with NO remark is a legitimate "no data"
    response (e.g. tiny area with no plants).  Must return normally."""
    payload = {"version": 0.6, "elements": []}
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status.return_value = None

    with patch("osm_powerplants.retrieval.client.requests.post") as post:
        post.return_value = mock_resp
        result = client.query_overpass("[out:json];node;out;")
        assert result == payload


# ─── Bug 2: Overpass rejects default requests UA with 406 ───────────────────


def test_query_overpass_sends_explicit_user_agent(client):
    """Public Overpass instances reject `python-requests/X` with HTTP 406, so
    every request must carry our explicit User-Agent header (issue #5)."""
    payload = {"elements": []}
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status.return_value = None

    with patch("osm_powerplants.retrieval.client.requests.post") as post:
        post.return_value = mock_resp
        client.query_overpass("[out:json];node;out;")

        headers = post.call_args.kwargs.get("headers", {})
        assert headers.get("User-Agent") == USER_AGENT
        assert "osm-powerplants" in headers["User-Agent"]
