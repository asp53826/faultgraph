from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from faultgraph.api import create_app
from faultgraph.settings import Settings


def client_for(tmp_path: Path, static_directory: Path | None = None) -> AsyncClient:
    app = create_app(
        Settings(
            database_path=tmp_path / "faultgraph.db",
            static_directory=static_directory or tmp_path / "missing-static",
            environment="production" if static_directory else "test",
        )
    )
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://faultgraph.test")


@pytest.mark.anyio
async def test_health_and_security_headers(tmp_path) -> None:
    async with client_for(tmp_path) as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["environment"] == "test"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "object-src 'none'" in response.headers["content-security-policy"]
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.anyio
async def test_incident_and_analysis_contracts(tmp_path) -> None:
    async with client_for(tmp_path) as client:
        incidents = await client.get("/api/incidents")
        analysis = await client.get("/api/incidents/INC-2026-0813-17/analysis")
        missing = await client.get("/api/incidents/does-not-exist")

    assert incidents.status_code == 200
    assert len(incidents.json()) == 3
    assert analysis.status_code == 200
    assert analysis.json()["top_hypothesis_id"] == "h-stream"
    assert missing.status_code == 404


@pytest.mark.anyio
async def test_replay_persists_a_checksum_addressed_experiment(tmp_path) -> None:
    payload = {
        "hypothesis_id": "h-stream",
        "intervention": "Remove the injected broker throttle and replay the captured workload.",
        "seed": 17,
    }
    async with client_for(tmp_path) as client:
        created = await client.post("/api/incidents/INC-2026-0813-17/experiments", json=payload)
        retained = await client.get("/api/incidents/INC-2026-0813-17/experiments")

    assert created.status_code == 201
    assert created.json()["state"] == "completed"
    assert len(created.json()["manifest_sha256"]) == 64
    assert retained.json()[0]["manifest_sha256"] == created.json()["manifest_sha256"]


@pytest.mark.anyio
async def test_replay_rejects_unknown_hypothesis_and_short_manifest(tmp_path) -> None:
    async with client_for(tmp_path) as client:
        unknown = await client.post(
            "/api/incidents/INC-2026-0813-17/experiments",
            json={"hypothesis_id": "unknown", "intervention": "long enough", "seed": 1},
        )
        invalid = await client.post(
            "/api/incidents/INC-2026-0813-17/experiments",
            json={"hypothesis_id": "h-stream", "intervention": "short", "seed": 1},
        )

    assert unknown.status_code == 422
    assert invalid.status_code == 422


@pytest.mark.anyio
async def test_incident_event_stream_is_finite_and_typed(tmp_path) -> None:
    async with client_for(tmp_path) as client:
        response = await client.get("/api/incidents/INC-2026-0813-17/events")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: analysis" in response.text
    assert '"top_hypothesis_id": "h-stream"' in response.text


@pytest.mark.anyio
async def test_production_static_server_supports_client_routes_and_hsts(tmp_path) -> None:
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<main>FaultGraph production shell</main>", encoding="utf-8")

    async with client_for(tmp_path, static_directory=static) as client:
        response = await client.get("/benchmark")

    assert response.status_code == 200
    assert "FaultGraph production shell" in response.text
    assert response.headers["strict-transport-security"].startswith("max-age=31536000")
