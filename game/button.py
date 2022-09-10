from typing import Optional, Tuple

import pygame
import pygame.freetype

from game.screen_tools import point_screen_to_surface

from .notification import Notification


class ButtonClicked(Notification):
    def Notify(self, location: Tuple):
        self._notify_callbacks(location)


class Button:

    button_clicked: ButtonClicked
    TIME_TO_REGISTER_TRACKER_CLICK = 1000
    GRACE_PERIOD = 250

    def __init__(
        self,
        screen: pygame.surface.Surface,
        draw_surface: pygame.surface.Surface,
        clock: pygame.time.Clock,
        text: Optional[str],
        position: Tuple,
        size: Tuple,
        image: Optional[pygame.surface.Surface] = None,
        visible: bool = True,
        font_size: int = 48,
    ):
        self._screen = screen
        self._draw_surface = draw_surface
        self._text = text
        self._size = size
        self._clock = clock

        self._visible = visible

        self._mouse_position = (0, 0)

        self._button_image = pygame.surface.Surface(size, pygame.SRCALPHA)
        if image:
            self._button_image.blit(
                pygame.transform.scale(image, self._button_image.get_size()), (0, 0)
            )
        pygame.draw.rect(
            self._button_image,
            color=pygame.Color("black"),
            rect=pygame.rect.Rect(0, 0, size[0], size[1]),
            width=2,
            border_radius=3,
        )

        self._button_hover_image = pygame.surface.Surface(size, pygame.SRCALPHA)
        if image:
            self._button_hover_image.blit(
                pygame.transform.scale(image, self._button_hover_image.get_size()),
                (0, 0),
            )
        pygame.draw.rect(
            self._button_hover_image,
            color=pygame.Color("black"),
            rect=pygame.rect.Rect(0, 0, size[0], size[1]),
            width=2,
            border_radius=3,
        )
        pygame.draw.rect(
            self._button_hover_image,
            color=pygame.Color("blue"),
            rect=pygame.rect.Rect(2, 2, size[0] - 4, size[1] - 4),
            width=2,
            border_radius=3,
        )

        self._position = position

        if text:
            font = pygame.freetype.SysFont("Comic Sans MS", font_size)

            text_image, _ = font.render(text, (255, 0, 0), None)
            text_rect = text_image.get_rect(
                center=(
                    (self._button_image.get_width() / 2),
                    (self._button_image.get_height() / 2),
                )
            )

            self._button_image.blit(text_image, text_rect)
            self._button_hover_image.blit(text_image, text_rect)

        self._mouse_click_in = False

        self._rect = self._button_image.get_rect(center=position)
        self.button_clicked = ButtonClicked()

        self._use_tracker = True
        self._tracker_inside = False
        self._tracker_time_inside = 0
        self._grace_period = 0

    @staticmethod
    def _interpolate_color(colors, percent) -> Tuple:
        delta = (
            colors[1][0] - colors[0][0],
            colors[1][1] - colors[0][1],
            colors[1][2] - colors[0][2],
        )
        result = (
            colors[0][0] + (delta[0] * percent),
            colors[0][1] + (delta[1] * percent),
            colors[0][2] + (delta[2] * percent),
        )
        return result

    def draw(self):
        if not self._visible:
            return

        if self._use_tracker:
            if self._tracker_inside:
                colors = [(0, 0, 0), (128, 75, 222)]

                button_image = pygame.surface.Surface(self._size, pygame.SRCALPHA)
                color = self._interpolate_color(
                    colors, self._tracker_time_inside / self.TIME_TO_REGISTER_TRACKER_CLICK
                )
                pygame.draw.rect(
                    button_image,
                    color=color,
                    rect=self._rect,
                    width=2,
                    border_radius=3,
                )
                button_image.fill(
                    color, (2, 2, self._rect.width - 2, self._rect.height - 2)
                )
                button_image.blit(self._button_hover_image, (0, 0))
                self._draw_surface.blit(button_image, self._rect)
            else:
                self._draw_surface.blit(self._button_image, self._rect)
        else:
            if self._rect.collidepoint(self._mouse_position):
                self._draw_surface.blit(self._button_hover_image, self._rect)
            else:
                self._draw_surface.blit(self._button_image, self._rect)

    def handle_event(self, event: pygame.event.Event):
        if not self._visible:
            return

        if self._use_tracker:
            return

        if event.type == pygame.MOUSEMOTION:
            self._mouse_position = point_screen_to_surface(
                event.pos, self._screen, self._draw_surface
            )
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self._rect.collidepoint(self._mouse_position):
                    self._mouse_click_in = True
                else:
                    self._mouse_click_in = False

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self._mouse_click_in and self._rect.collidepoint(
                    self._mouse_position
                ):
                    self.button_clicked.Notify(self._mouse_position)
                self._mouse_click_in = False

    def update_screen_tracker(self, position):
        if not self._use_tracker or not self._visible:
            return

        self._tracker_position = position
        if self._rect.collidepoint(self._tracker_position):
            if not self._tracker_inside:
                self._tracker_inside = True
                self._tracker_time_inside = 0
                self._grace_period = 0
            else:
                self._tracker_time_inside += self._clock.get_time()
                self._grace_period = 0
                if self._tracker_time_inside > self.TIME_TO_REGISTER_TRACKER_CLICK:
                    self.button_clicked.Notify(self._tracker_position)
        else:
            if self._tracker_inside:
                self._tracker_time_inside += self._clock.get_time()
                self._grace_period += self._clock.get_time()
                if self._grace_period > self.GRACE_PERIOD:
                    self._tracker_time_inside = 0
                    self._tracker_inside = False

    def get_visible(self):
        return self._visible

    def set_visible(self, value: bool):
        self._visible = value

    def set_use_tracker(self, value: bool):
        self._use_tracker = value
