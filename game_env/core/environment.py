
from abc import ABC, abstractmethod

import numpy as np

from game_env.controllers.action import Action


class Environment(ABC):
    @abstractmethod
    def reset(
        self,
        seed: int | None = None,
    ) -> tuple[np.ndarray, dict]:
        """Почати новий епізод."""
        pass

    @abstractmethod
    def step(
        self,
        action: Action,
    ) -> tuple[np.ndarray, float, bool, bool, dict]:
        """Виконати одну дію та оновити середовище."""
        pass
