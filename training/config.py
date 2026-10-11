"""Experiment options and their validation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExperimentConfig:
    mode: str = "train"
    environment: str = "space-invaders"
    episodes: int = 20
    max_steps: int = 3600
    seed: int = 42
    experiment_name: str = "baseline"
    render: bool = False
    reward_shaping: bool = False
    shaping_scale: float = 1.0
    agent_type: str = "neural"
    n_steps: int = 5
    max_stagnation_steps: int | None = 300
    debug_last_steps: int = 30

    def __post_init__(self):
        if self.mode not in {"train", "evaluate", "random"}:
            raise ValueError(f"Unknown mode: {self.mode}")
        if self.environment not in {"space-invaders", "simple-target"}:
            raise ValueError(f"Unknown environment: {self.environment}")
        if self.agent_type not in {"neural", "dqn"}:
            raise ValueError(f"Unknown agent type: {self.agent_type}")
        if self.episodes < 1:
            raise ValueError("episodes must be >= 1")
        if self.max_steps < 1:
            raise ValueError("max_steps must be >= 1")
        if self.n_steps < 1:
            raise ValueError("n_steps must be >= 1")
        if self.max_stagnation_steps is not None and self.max_stagnation_steps < 1:
            raise ValueError("max_stagnation_steps must be >= 1")
        if self.debug_last_steps < 1:
            raise ValueError("debug_last_steps must be >= 1")
