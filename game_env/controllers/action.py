from dataclasses import dataclass


@dataclass
class Action:
    move_x: int = 0
    move_y: int = 0
    shoot: bool = False