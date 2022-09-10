from typing import Optional, Tuple

import pygame

from game.screen_tools import point_screen_to_surface

from .button import Button


class UI:
    def __init__(self, screen: pygame.surface.Surface, surface: pygame.surface.Surface, clock: pygame.time.Clock):
        self._screen = screen
        self._draw_surface = surface
        self._buttons = []
        self._mouse_position = (0, 0)
        self._tracker_position = (0, 0)
        self._cursor = None
        self._clock = clock
        self._use_tracker = True

    def create_button(
        self,
        text: Optional[str],
        position: Tuple,
        size: Tuple,
        image: Optional[pygame.surface.Surface] = None,
        visible: bool = True,
        font_size: int = 48,
    ):
        new_button = Button(
            self._screen,
            self._draw_surface,
            self._clock,
            text,
            position,
            size,
            image,
            visible,
            font_size,
        )
        self._buttons.append(new_button)
        return new_button

    def set_cursor(self, cursor: pygame.surface.Surface):
        self._cursor = cursor
        self._mouse_position = point_screen_to_surface(
            pygame.mouse.get_pos(), self._screen, self._draw_surface
        )

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self._mouse_position = point_screen_to_surface(
                event.pos, self._screen, self._draw_surface
            )
        for button in self._buttons:
            button.handle_event(event)

    def update_screen_tracker(self, position):
        self._tracker_position = position
        for button in self._buttons:
            button.update_screen_tracker(position)


    def render(self):
        for button in self._buttons:
            button.draw()

        if self._cursor:
            if self._use_tracker:
                tracker_rect = self._cursor.get_rect(center=self._tracker_position)
                self._draw_surface.blit(self._cursor, tracker_rect)
            else:
                cursor_rect = self._cursor.get_rect(center=self._mouse_position)
                self._draw_surface.blit(self._cursor, cursor_rect)

