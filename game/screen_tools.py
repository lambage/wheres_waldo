import pygame
from typing import Tuple

def point_screen_to_surface(
    point: Tuple,
    screen: pygame.surface.Surface,
    draw_surface: pygame.surface.Surface,
)-> Tuple:
    return (point[0] * draw_surface.get_width() / screen.get_width(), point[1] * draw_surface.get_height() / screen.get_height())


def point_surface_to_screen(
    point: Tuple,
    screen: pygame.surface.Surface,
    draw_surface: pygame.surface.Surface,
) -> Tuple:
    return (point[0] * screen.get_width() / draw_surface.get_width(), point[1] * screen.get_height() / draw_surface.get_height())
