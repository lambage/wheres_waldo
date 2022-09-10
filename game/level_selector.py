import json

import pygame

from game.adhawk_control import AdHawkControl
from game.play_game import PlayGame
from game.ui import UI


class LevelSelector:
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
            pygame.image.load("data/level_selector/bg.png"), draw_surface.get_size()
        )

        font = pygame.freetype.SysFont("Comic Sans MS", 72)

        text_image, _ = font.render("Select a level", (255, 0, 0), None)
        self._bg.blit(text_image, (400, 50))

        self._clock = pygame.time.Clock()

        self._adhawk_control = adhawk_control
        self._cursor = cursor
        self._ui = UI(self._screen, self._draw_surface, self._clock)

        with open("data/scenes/scenes.json", "r", encoding="utf8") as reader:
            scenes_data = json.load(reader)

        self._level_index = 0
        self._levels = []
        for scene in scenes_data:
            level = self._ui.create_button(
                None,
                (640, 350),
                (350, 350),
                image=pygame.image.load(scene["filename"]),
                visible=False,
            )
            self._levels.append(level)
            level.button_clicked.add_callback(
                lambda _, scene=scene: self._play_level(scene)
            )

        self._levels[self._level_index].set_visible(True)

        previous_button = self._ui.create_button(
            "Previous", (350, 360), (150, 150), font_size=36
        )
        next_button = self._ui.create_button(
            "Next", (950, 360), (150, 150), font_size=36
        )
        back_button = self._ui.create_button(
            "Back To Main", (640, 640), (500, 100), font_size=36
        )

        previous_button.button_clicked.add_callback(self._previous)
        next_button.button_clicked.add_callback(self._next)
        back_button.button_clicked.add_callback(self._back_to_main)

        self._ui.set_cursor(cursor)
        self._cursor = cursor

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

    def _previous(self, _):
        self._levels[self._level_index].set_visible(False)
        self._level_index = self._level_index - 1
        if self._level_index < 0:
            self._level_index = len(self._levels) - 1
        self._levels[self._level_index].set_visible(True)

    def _next(self, _):
        self._levels[self._level_index].set_visible(False)
        self._level_index = self._level_index + 1
        if self._level_index == len(self._levels):
            self._level_index = 0
        self._levels[self._level_index].set_visible(True)

    def _back_to_main(self, _):
        self._running = False

    def _play_level(self, scene):
        play = PlayGame(self._screen, self._draw_surface, self._cursor, self._adhawk_control, scene)
        play.run()

        # little hack to make sure cursor goes back to actual pointer position on returning here
        self._ui.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {"pos": pygame.mouse.get_pos()}))
