"""Tests for region_download config plumbing."""

from unittest.mock import MagicMock, patch

from osm_powerplants.retrieval import regional


def test_region_download_uses_overpass_api_url_from_config():
    """The user's `overpass_api.api_url` config override must reach the
    OverpassAPIClient (issue #5: previously read the wrong key `url` and
    silently fell back to the public instance)."""
    sentinel_url = "https://overpass.private.coffee/api/interpreter"
    config = {
        "OSM": {
            "overpass_api": {"api_url": sentinel_url},
        }
    }
    region = {
        "type": "bbox",
        "name": "Tiny",
        "bounds": [0.0, 0.0, 0.1, 0.1],
    }

    with (
        patch.object(regional, "OverpassAPIClient") as ClientCls,
        patch.object(
            regional, "get_osm_cache_paths", return_value=("/tmp/c", "/tmp/u")
        ),
        patch.object(
            regional,
            "_region_download_with_client",
            return_value={
                "success": True,
                "regions_processed": 1,
                "regions_failed": 0,
                "results": {},
                "total_elements_updated": 0,
                "total_elements_added": 0,
            },
        ),
    ):
        ClientCls.return_value.__enter__.return_value = MagicMock()
        regional.region_download(regions=region, config=config)

        assert ClientCls.call_args.kwargs["api_url"] == sentinel_url
