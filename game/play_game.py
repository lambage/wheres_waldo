from typing import Tuple

import pygame

from game.adhawk_control import AdHawkControl
from game.screen_tools import point_screen_to_surface
from game.ui import UI


class PlayGame:
    def __init__(
        self,
        screen: pygame.surface.Surface,
        draw_surface: pygame.surface.Surface,
        cursor: pygame.surface.Surface,
        adhawk_control: AdHawkControl,        
        scene,
    ):
        self._running = True
        self._screen = screen
        self._draw_surface = draw_surface
        self._bg = pygame.transform.scale(
            pygame.image.load(scene["filename"]), draw_surface.get_size()
        )
        self._cursor = cursor

        self._clock = pygame.time.Clock()
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        
        self._ui = UI(self._screen, self._draw_surface, self._clock)
        self._ui.set_cursor(cursor)

        self._mouse_position = (0, 0)
        self._counter = 120
        self._in_waldo = False
        self._looking_at_waldo_time = 0
        self._total_looking_at_waldo_time = 0
        self._number_times_looked_at_waldo = 0
        self._grace_period = 0
        self._font = pygame.freetype.SysFont("Comic Sans MS", 36)
        self._stats_font = pygame.freetype.SysFont("Comic Sans MS", 24)
        waldo_location = scene["waldo_location"]
        self._waldo_rect = pygame.rect.Rect(
            waldo_location["x"],
            waldo_location["y"],
            waldo_location["width"],
            waldo_location["height"],
        )
        self._circle_cache = {}
        self._use_tracker = True
        self._adhawk_control = adhawk_control

    def _circlepoints(self, r):
        r = int(round(r))
        if r in self._circle_cache:
            return self._circle_cache[r]
        x, y, e = r, 0, 1 - r
        self._circle_cache[r] = points = []
        while x >= y:
            points.append((x, y))
            y += 1
            if e < 0:
                e += 2 * y - 1
            else:
                x -= 1
                e += 2 * (y - x) - 1
        points += [(y, x) for x, y in points if x > y]
        points += [(-x, y) for x, y in points if x]
        points += [(x, -y) for x, y in points if y]
        points.sort()
        return points

    def _render_outline_text(
        self,
        font: pygame.freetype.SysFont,
        text: str,
        gfcolor: Tuple,
        ocolor: Tuple,
        outline_size=2,
    ):
        textsurface, _ = font.render(text, gfcolor, None)
        w = textsurface.get_width() + 2 * outline_size
        h = textsurface.get_height() + 2 * outline_size

        osurf = pygame.surface.Surface((w, h + 2 * outline_size), pygame.SRCALPHA)
        osurf.fill((0, 0, 0, 0))

        surf = osurf.copy()

        osurf.blit(font.render(text, ocolor, None)[0], (0, 0))

        for dx, dy in self._circlepoints(outline_size):
            surf.blit(osurf, (dx + outline_size, dy + outline_size))

        surf.blit(textsurface, (outline_size, outline_size))
        return surf

    def run(self):
        self._running = True

        text = str(self._counter).rjust(2)
        game_won = False

        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    self._running = False
                    break
                elif event.type == pygame.USEREVENT:
                    self._counter = self._counter - 1
                    text = (
                        str(self._counter).rjust(2)
                        if self._counter > 0
                        else "Game over!"
                    )
                else:
                    self._ui.handle_event(event)
                if event.type == pygame.MOUSEMOTION:
                    self._mouse_position = point_screen_to_surface(
                        event.pos, self._screen, self._draw_surface
                    )

            self._draw_surface.blit(self._bg, (0, 0))

            text_image = self._render_outline_text(
                self._font,
                text,
                (255, 0, 0),
                (0, 0, 0),
                2,
            )

            self._draw_surface.blit(text_image, (640, 30))

            self._adhawk_control.draw()
            self._ui.update_screen_tracker(self._adhawk_control.get_coords())

            self._ui.render()

            self.waldo_logic()

            if self._looking_at_waldo_time > 3000:
                self._running = False
                game_won = True

            if self._counter == 0:
                self._running = False
                game_won = False

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

        back_button = self._ui.create_button("Back", (640, 640), (200, 100))
        back_button.button_clicked.add_callback(self._back)

        self._bg = pygame.transform.scale(
            pygame.image.load("data/level_selector/bg.png"),
            self._draw_surface.get_size(),
        )
        if game_won:
            self._game_won()
        else:
            self._game_lost()

    def _game_won(self):
        win_text = self._render_outline_text(
            self._font, "You Win!", (128, 128, 255), (0, 0, 0), 5
        )
        self._bg.blit(win_text, (550, 100))
        self._run_post_game_screen()

    def _game_lost(self):
        lost_text = self._render_outline_text(
            self._font, "You Lost!", (255, 128, 128), (0, 0, 0), 5
        )
        self._bg.blit(lost_text, (550, 100))
        self._run_post_game_screen()

    def _run_post_game_screen(self):
        self._render_stats()
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

    def _back(self, _):
        self._running = False

    def _render_stats(self):
        total_time = self._render_outline_text(
            self._stats_font, f"Total time looking at Waldo: {self._total_looking_at_waldo_time / 1000}s", (255, 255, 255), (0, 0, 0), 3
        )
        self._bg.blit(total_time, (450, 250))
        times_looked = self._render_outline_text(
            self._stats_font, f"Number of times looked at Waldo: {self._number_times_looked_at_waldo}", (255, 255, 255), (0, 0, 0), 3
        )
        self._bg.blit(times_looked, (450, 300))


    def waldo_logic(self):
        if self._use_tracker:
            pos = self._adhawk_control.get_coords()
        else:
            pos = self._mouse_position

        if self._waldo_rect.collidepoint(pos):
            if self._in_waldo:
                delta = self._clock.get_time()
                self._looking_at_waldo_time += delta
                self._total_looking_at_waldo_time += delta
            else:
                self._in_waldo = True
                self._looking_at_waldo_time = 0
                self._number_times_looked_at_waldo += 1
            self._grace_period = 0
        else:
            if self._in_waldo:
                delta = self._clock.get_time()
                self._looking_at_waldo_time += delta
                self._total_looking_at_waldo_time += delta
                self._grace_period += delta
                if self._grace_period > 250:
                    self._in_waldo = False
                    self._grace_period = 0
