from dataclasses import dataclass


from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    move_x: int = 0
    move_y: int = 0
    shoot: bool = False

    @classmethod
    def all_actions(cls):
        return [
            cls(0, 0, False),   # Нічого не робити
            cls(-1, 0, False),  # Рух ліворуч
            cls(1, 0, False),   # Рух праворуч
            cls(0, 0, True),    # Стріляти
        ]


