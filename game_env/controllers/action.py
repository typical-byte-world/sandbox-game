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


# @dataclass(frozen=True)
# class Action:
#     move_x: int = 0
#     move_y: int = 0
#     shoot: bool = False

#     @classmethod
#     def all_actions(cls):
#         actions = []

#         for move_x in [-1, 0, 1]:
#             for move_y in [-1, 0, 1]:
#                 for shoot in [False, True]:
#                     actions.append(
#                         cls(move_x, move_y, shoot)
#                     )

#         return actions