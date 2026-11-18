from __future__ import annotations

import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.data.synth import BLOCKS
from app.main import app, get_geo_tree, geo_tree

client = TestClient(app)


def test_geo_tree_shape():
    r = client.get("/api/geo/tree")
    assert r.status_code == 200
    data = r.json()

    assert data["state"] == "Uttar Pradesh"
    assert "source_url" in data and isinstance(data["source_url"], str) and data["source_url"].startswith("http")

    districts = data["districts"]
    assert len(districts) == 20

    for d in districts:
        assert isinstance(d["name"], str) and d["name"]
        assert isinstance(d["lat"], (int, float)) and 23.5 <= d["lat"] <= 30.5
        assert isinstance(d["lon"], (int, float)) and 77.0 <= d["lon"] <= 84.5
        assert isinstance(d["source_record_id"], str) and d["source_record_id"].startswith("IN19")
        assert isinstance(d["blocks"], list)
        for b in d["blocks"]:
            assert isinstance(b, str) and b

    # Check known districts match BLOCKS dict
    districts_by_name = {d["name"]: d for d in districts}
    for name, expected_blocks in BLOCKS.items():
        assert name in districts_by_name
        assert districts_by_name[name]["blocks"] == expected_blocks

    # Districts without block entries in synth.py should have empty list
    non_blocks_districts = [d for d in districts if d["name"] not in BLOCKS]
    assert len(non_blocks_districts) == 20 - len(BLOCKS)
    for d in non_blocks_districts:
        assert d["blocks"] == []


def test_geo_tree_source_url_carried_through_unchanged():
    districts_json_path = Path(__file__).resolve().parents[2] / "docs" / "research" / "up_districts.json"
    raw_data = json.loads(districts_json_path.read_text(encoding="utf-8"))

    tree = get_geo_tree()
    expected_url = raw_data.get("coordinate_source_url")
    assert tree["source_url"] == expected_url


def test_geo_tree_cache_returns_same_object():
    obj1 = get_geo_tree()
    obj2 = get_geo_tree()
    assert obj1 is obj2
    assert hasattr(get_geo_tree, "cache_info")
    assert get_geo_tree.cache_info().hits >= 1

    # Calling geo_tree directly without request also delegates to cached object
    assert geo_tree() is obj1


def test_geo_tree_etag_present_and_quoted():
    r = client.get("/api/geo/tree")
    assert r.status_code == 200
    assert "etag" in r.headers

    etag = r.headers["etag"]
    assert etag.startswith('"') and etag.endswith('"')

    digest = hashlib.sha256(r.content).hexdigest()
    assert etag == f'"{digest}"'


def test_geo_tree_304_on_matching_if_none_match():
    r1 = client.get("/api/geo/tree")
    assert r1.status_code == 200
    etag = r1.headers["etag"]

    # Matching quoted ETag -> 304 with no body
    r2 = client.get("/api/geo/tree", headers={"If-None-Match": etag})
    assert r2.status_code == 304
    assert r2.text == ""
    assert len(r2.content) == 0

    # Matching unquoted ETag -> 304 with no body
    r3 = client.get("/api/geo/tree", headers={"If-None-Match": etag.strip('"')})
    assert r3.status_code == 304
    assert len(r3.content) == 0

    # Non-matching ETag -> 200 with full body
    r4 = client.get("/api/geo/tree", headers={"If-None-Match": '"different_etag"'})
    assert r4.status_code == 200
    assert len(r4.content) > 0
    assert r4.json()["state"] == "Uttar Pradesh"
