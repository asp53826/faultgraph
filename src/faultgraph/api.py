"""FaultGraph HTTP and event-stream API."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import Scope

from faultgraph import __version__
from faultgraph.engine import analyze, benchmark
from faultgraph.models import (
    Analysis,
    BenchmarkReport,
    ExperimentRecord,
    ExperimentRequest,
    Incident,
    IncidentSummary,
)
from faultgraph.repository import ExperimentRepository, IncidentRepository
from faultgraph.scenarios import bundled_incidents
from faultgraph.service import run_experiment
from faultgraph.settings import Settings


class SPAStaticFiles(StaticFiles):
    """Serve the workbench entrypoint for client-side routes."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            response = await super().get_response(path, scope)
        except StarletteHTTPException as error:
            if error.status_code == status.HTTP_404_NOT_FOUND:
                return await super().get_response("index.html", scope)
            raise
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return await super().get_response("index.html", scope)
        return response


def create_app(settings: Settings | None = None) -> FastAPI:
    runtime = settings or Settings()
    incidents = IncidentRepository(bundled_incidents())
    experiments = ExperimentRepository(runtime.database_path)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield

    app = FastAPI(
        title="FaultGraph API",
        version=__version__,
        description="Evidence-first causal incident analysis and deterministic replay.",
        lifespan=lifespan,
    )
    app.state.incidents = incidents
    app.state.experiments = experiments
    app.add_middleware(
        CORSMiddleware,
        allow_origins=runtime.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Accept"],
    )

    @app.middleware("http")
    async def security_headers(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        if runtime.environment == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Cache-Control"] = (
            "no-store" if request.url.path.startswith("/api") else "public, max-age=300"
        )
        return response

    def get_incident(incident_id: str) -> Incident:
        incident = incidents.get(incident_id)
        if incident is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="incident not found")
        return incident

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__, "environment": runtime.environment}

    @app.get("/api/incidents", response_model=list[IncidentSummary])
    def list_incidents() -> list[IncidentSummary]:
        summaries: list[IncidentSummary] = []
        for incident in incidents.list():
            result = analyze(incident, now=incident.detected_at)
            top = result.ranked_hypotheses[0]
            affected = sum(
                node.observed_latency_ms > node.baseline_latency_ms * 1.25
                for node in incident.nodes
            )
            summaries.append(
                IncidentSummary(
                    id=incident.id,
                    title=incident.title,
                    severity=incident.severity,
                    status=incident.status,
                    started_at=incident.started_at,
                    top_hypothesis=top.title,
                    confidence=top.probability,
                    affected_nodes=affected,
                )
            )
        return summaries

    @app.get("/api/incidents/{incident_id}", response_model=Incident)
    def incident_detail(incident_id: str) -> Incident:
        return get_incident(incident_id)

    @app.get("/api/incidents/{incident_id}/analysis", response_model=Analysis)
    def incident_analysis(incident_id: str) -> Analysis:
        return analyze(get_incident(incident_id))

    @app.get("/api/incidents/{incident_id}/experiments", response_model=list[ExperimentRecord])
    def list_experiments(incident_id: str) -> list[ExperimentRecord]:
        get_incident(incident_id)
        return experiments.list_for_incident(incident_id)

    @app.post(
        "/api/incidents/{incident_id}/experiments",
        response_model=ExperimentRecord,
        status_code=status.HTTP_201_CREATED,
    )
    def create_experiment(incident_id: str, payload: ExperimentRequest) -> ExperimentRecord:
        try:
            return run_experiment(get_incident(incident_id), payload, experiments)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
            ) from error

    @app.get("/api/benchmark", response_model=BenchmarkReport)
    def benchmark_report() -> BenchmarkReport:
        return benchmark(incidents.list())

    @app.get("/api/incidents/{incident_id}/events")
    async def incident_events(incident_id: str) -> StreamingResponse:
        incident = get_incident(incident_id)

        async def stream() -> AsyncIterator[str]:
            payload = {
                "type": "analysis.ready",
                "incident_id": incident.id,
                "top_hypothesis_id": analyze(incident).top_hypothesis_id,
            }
            yield f"event: analysis\ndata: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0)
            yield ": stream-complete\n\n"

        return StreamingResponse(stream(), media_type="text/event-stream")

    if runtime.static_directory.is_dir():
        app.mount(
            "/", SPAStaticFiles(directory=runtime.static_directory, html=True), name="workbench"
        )

    return app


app = create_app()
