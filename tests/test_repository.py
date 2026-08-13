from datetime import UTC, datetime

from faultgraph.models import ExperimentRecord, ExperimentState
from faultgraph.repository import ExperimentRepository


def test_experiment_repository_round_trips_records(tmp_path) -> None:
    repository = ExperimentRepository(tmp_path / "nested" / "experiments.db")
    timestamp = datetime(2026, 8, 13, 14, 20, tzinfo=UTC)
    record = ExperimentRecord(
        id="EXP-TEST",
        incident_id="INC-TEST",
        hypothesis_id="H-TEST",
        intervention="Remove the injected throttle and replay.",
        seed=17,
        state=ExperimentState.COMPLETED,
        created_at=timestamp,
        completed_at=timestamp,
        predicted_reduction=0.75,
        observed_reduction=0.78,
        manifest_sha256="a" * 64,
        conclusion="Supported in replay.",
    )

    repository.save(record)

    assert repository.list_for_incident("INC-TEST") == [record]
    assert repository.list_for_incident("INC-OTHER") == []
