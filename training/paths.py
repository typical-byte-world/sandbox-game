"""Stable artifact locations shared by experiment runs."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExperimentPaths:
    model: Path
    results: Path

    @classmethod
    def for_experiment(cls, environment, agent_type, experiment_name, mode):
        suffix = Path(environment)
        if agent_type == "dqn":
            suffix /= "dqn"
        return cls(
            model=Path("models") / suffix / f"{experiment_name}.pt",
            results=Path("results") / suffix / f"{experiment_name}_{mode}.csv",
        )

    def create_directories(self):
        self.model.parent.mkdir(parents=True, exist_ok=True)
        self.results.parent.mkdir(parents=True, exist_ok=True)
