"""
Experiment Tracker.

Tracks ML experiments including parameters, metrics, and artifacts.
Follows MLflow tracking pattern.
"""

from typing import Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum


class RunStatus(str, Enum):
    """Status of an experiment run."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RunInfo:
    """Information about an experiment run."""

    run_id: str
    experiment_name: str
    status: RunStatus
    start_time: float
    end_time: float | None = None
    params: dict[str, Any] | None = None
    metrics: dict[str, float] | None = None
    artifacts: list[str] | None = None


class ExperimentTracker:
    """
    Experiment tracking for ML training runs.

    Provides:
    - Experiment and run management
    - Parameter logging
    - Metric logging (per step and final)
    - Artifact logging (models, plots, data)

    Can be backed by:
    - Local filesystem (default)
    - MLflow
    - Weights & Biases
    - Custom backend
    """

    def __init__(
        self,
        tracking_uri: str | None = None,
        artifact_location: str | Path | None = None,
    ) -> None:
        """
        Initialize tracker.

        Args:
            tracking_uri: URI for tracking backend (file:// or http://)
            artifact_location: Base path for artifact storage
        """
        self.tracking_uri = tracking_uri
        self.artifact_location = Path(artifact_location) if artifact_location else None
        self._current_run: RunInfo | None = None

    def start_run(
        self,
        experiment_name: str,
        run_name: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> str:
        """
        Start a new experiment run.

        Args:
            experiment_name: Name of the experiment
            run_name: Optional name for this run
            tags: Optional tags for the run

        Returns:
            Run ID
        """
        # Here your code for:
        # 1. Create or get experiment by name
        # 2. Generate run ID
        # 3. Initialize RunInfo
        # 4. Create run directory for artifacts
        # 5. Return run ID
        pass

    def end_run(self, status: RunStatus = RunStatus.COMPLETED) -> None:
        """
        End the current run.

        Args:
            status: Final status of the run
        """
        # Here your code for ending run
        pass

    def log_params(self, params: dict[str, Any]) -> None:
        """
        Log parameters for current run.

        Args:
            params: Dictionary of parameter names and values
        """
        # Here your code for logging parameters
        pass

    def log_param(self, key: str, value: Any) -> None:
        """
        Log a single parameter.

        Args:
            key: Parameter name
            value: Parameter value
        """
        # Here your code for logging single parameter
        pass

    def log_metrics(self, metrics: dict[str, float], step: int | None = None) -> None:
        """
        Log metrics for current run.

        Args:
            metrics: Dictionary of metric names and values
            step: Optional step number (epoch, iteration)
        """
        # Here your code for logging metrics
        pass

    def log_metric(self, key: str, value: float, step: int | None = None) -> None:
        """
        Log a single metric.

        Args:
            key: Metric name
            value: Metric value
            step: Optional step number
        """
        # Here your code for logging single metric
        pass

    def log_artifact(self, local_path: str | Path, artifact_path: str | None = None) -> None:
        """
        Log an artifact (file) for current run.

        Args:
            local_path: Path to local file
            artifact_path: Optional path within artifact directory
        """
        # Here your code for logging artifact
        pass

    def log_model(
        self,
        model: Any,
        artifact_path: str,
        registered_model_name: str | None = None,
    ) -> None:
        """
        Log a model artifact.

        Args:
            model: Model object to save
            artifact_path: Path within artifact directory
            registered_model_name: Optional name to register model
        """
        # Here your code for logging model
        pass

    def get_run(self, run_id: str) -> RunInfo | None:
        """
        Get information about a run.

        Args:
            run_id: Run identifier

        Returns:
            RunInfo or None if not found
        """
        # Here your code for getting run info
        pass

    def list_runs(
        self,
        experiment_name: str,
        status: RunStatus | None = None,
    ) -> list[RunInfo]:
        """
        List runs for an experiment.

        Args:
            experiment_name: Experiment name
            status: Optional filter by status

        Returns:
            List of RunInfo
        """
        # Here your code for listing runs
        pass

    def get_best_run(
        self,
        experiment_name: str,
        metric: str,
        maximize: bool = True,
    ) -> RunInfo | None:
        """
        Get the best run based on a metric.

        Args:
            experiment_name: Experiment name
            metric: Metric to compare
            maximize: Whether higher is better

        Returns:
            RunInfo of best run or None
        """
        # Here your code for getting best run
        pass
