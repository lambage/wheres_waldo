from ctypes import windll

import pygame

from game.title_screen import TitleScreen
from game.adhawk_control import AdHawkControl


def generate_cursor() -> pygame.surface.Surface:
    cursor = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(cursor, pygame.Color("black"), (25, 25), 25, 1)
    pygame.draw.circle(cursor, pygame.Color("white"), (25, 25), 24, 1)
    pygame.draw.circle(cursor, pygame.Color("black"), (25, 25), 23, 1)
    pygame.draw.circle(cursor, pygame.Color("white"), (25, 25), 6, 1)
    pygame.draw.circle(cursor, pygame.Color("black"), (25, 25), 5, 1)
    return cursor


def get_dpi():
    LOGPIXELSX = 88
    LOGPIXELSY = 90
    user32 = windll.user32
    user32.SetProcessDPIAware()
    dc = user32.GetDC(0)
    dots_per_inch = (
        windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX),
        windll.gdi32.GetDeviceCaps(dc, LOGPIXELSY),
    )
    return dots_per_inch


def main():
    pygame.init()
    pygame.font.init()
    pygame.mouse.set_visible(False)

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    draw_surface = pygame.surface.Surface([1280, 720])

    adhawk_control = AdHawkControl(screen, draw_surface, get_dpi())

    try:
        title_screen = TitleScreen(
            screen, draw_surface, generate_cursor(), adhawk_control
        )
        title_screen.run()
    finally:
        adhawk_control.shutdown()


if __name__ == "__main__":
    main()
