"""Incident and experiment persistence boundaries."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path

from faultgraph.models import ExperimentRecord, Incident


class IncidentRepository:
    def __init__(self, incidents: Iterable[Incident]) -> None:
        self._incidents = {incident.id: incident for incident in incidents}

    def list(self) -> list[Incident]:
        return sorted(self._incidents.values(), key=lambda item: item.started_at, reverse=True)

    def get(self, incident_id: str) -> Incident | None:
        return self._incidents.get(incident_id)


class ExperimentRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS experiments (
                    id TEXT PRIMARY KEY,
                    incident_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save(self, record: ExperimentRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO experiments (id, incident_id, payload, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.incident_id,
                    record.model_dump_json(),
                    record.created_at.isoformat(),
                ),
            )

    def list_for_incident(self, incident_id: str) -> list[ExperimentRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM experiments WHERE incident_id = ? ORDER BY created_at DESC",
                (incident_id,),
            ).fetchall()
        return [ExperimentRecord.model_validate_json(row["payload"]) for row in rows]
