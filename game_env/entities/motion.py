"""Shared boundary rules for moving entities."""


def constrain_to_screen(position, velocity, rect, width, height, *, bounce):
    half_width = rect.width / 2
    half_height = rect.height / 2
    if position.x < half_width:
        position.x = half_width
        velocity.x = -velocity.x if bounce else 0
    if position.x > width - half_width:
        position.x = width - half_width
        velocity.x = -velocity.x if bounce else 0
    if position.y < half_height:
        position.y = half_height
        velocity.y = -velocity.y if bounce else 0
    if position.y > height - half_height:
        position.y = height - half_height
        velocity.y = -velocity.y if bounce else 0
