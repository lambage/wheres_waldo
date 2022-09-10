import pygame
from game.adhawk_control import AdHawkControl
from game.level_selector import LevelSelector
from game.ui import UI


class TitleScreen:
    def __init__(
        self,
        screen: pygame.surface.Surface,
        draw_surface: pygame.surface.Surface,
        cursor: pygame.surface.Surface,
        adhawk_control: AdHawkControl,
    ):
        self._running = True
        self._screen = screen
        self._draw_surface = draw_surface
        self._bg = pygame.transform.scale(
            pygame.image.load("data/title_screen/bg.png"), draw_surface.get_size()
        )
        self._cursor = cursor
        self._clock = pygame.time.Clock()
        self._ui = UI(self._screen, self._draw_surface, self._clock)
        play_button = self._ui.create_button("Play", (750, 400), (300, 100))
        quit_button = self._ui.create_button("Quit", (750, 525), (300, 100))

        play_button.button_clicked.add_callback(self._start_game)
        quit_button.button_clicked.add_callback(self._quit_game)

        self._adhawk_control = adhawk_control
        self._ui.set_cursor(cursor)

    def run(self):
        self._running = True

        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    self._running = False
                    break
                else:
                    self._ui.handle_event(event)

            self._draw_surface.blit(self._bg, (0, 0))

            self._adhawk_control.draw()
            self._ui.update_screen_tracker(self._adhawk_control.get_coords())
            self._ui.render()

            self._screen.blit(
                pygame.transform.scale(
                    self._draw_surface,
                    (
                        (
                            self._screen.get_width(),
                            self._screen.get_height(),
                        )
                    ),
                ),
                (0, 0),
            )

            pygame.display.flip()
            self._clock.tick(30)

    def _start_game(self, _):
        level_selector = LevelSelector(self._screen, self._draw_surface, self._cursor, self._adhawk_control)
        level_selector.run()
        self._ui.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {"pos": pygame.mouse.get_pos()}))


    def _quit_game(self, _):
        self._running = False
