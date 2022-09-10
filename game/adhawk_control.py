from collections import deque
import math
from typing import Tuple

import adhawkapi
import adhawkapi.frontend
import cv2
import numpy as np
import pygame
from adhawkapi.publicapi import Events, MarkerSequenceMode, PacketType

class AdHawkControl:

    MARKER_DIC = cv2.aruco.DICT_4X4_50  # pylint: disable=no-member
    EDGE_OFFSETS_MM = np.array(
        [[10, 10], [10, 10]]
    )  # Marker offsets: [[left, right], [top, bottom]]

    NUM_POINTS = 10

    GAZE_MARKER_SIZE = 20

    def __init__(
        self,
        screen: pygame.surface.Surface,
        draw_surface: pygame.surface.Surface,
        dpi: Tuple,
    ):
        self._api = adhawkapi.frontend.FrontendApi()
        self._api.register_stream_handler(
            PacketType.GAZE_IN_SCREEN, self._handle_gaze_in_screen_stream
        )
        self._api.register_stream_handler(PacketType.EVENTS, self._handle_event_stream)
        self._api.start(connect_cb=self._handle_connect_response)
        self._size_mm = self._pix_to_mm(screen.get_size(), dpi)
        self._marker_ids = [0, 1, 2, 3]
        self._marker_positions = self._create_custom_board()
        self._screen = screen
        self._draw_surface = draw_surface
        self._aruco_image = pygame.transform.scale(
            pygame.image.load("data/screen_tracking/aruco_markers.png"),
            self._draw_surface.get_size(),
        )
        self._point_deque = deque()
        self._running_xcoord = 0
        self._running_ycoord = 0
        self._xcoord = 0
        self._ycoord = 0

    def shutdown(self):
        self._enable_screen_tracking(False)
        self._api.stop_camera_capture(lambda *_args: None)
        self._api.shutdown()

    def quickstart(self):
        self._api.quick_start_gui(
            mode=MarkerSequenceMode.FIXED_GAZE,
            marker_size_mm=35,
            callback=(lambda *_args: None),
        )

    def calibrate(self):
        self._api.start_calibration_gui(
            mode=MarkerSequenceMode.FIXED_HEAD,
            n_points=9,
            marker_size_mm=35,
            randomize=False,
            callback=(lambda *_args: None),
        )

    def _register_screen(
        self, screen_width, screen_height, aruco_dic, marker_ids, markers
    ):
        self._api.register_screen_board(
            screen_width,
            screen_height,
            aruco_dic,
            marker_ids,
            markers,
            self._handle_screen_registered_response,
        )

    def _enable_screen_tracking(self, enable):
        if enable:
            self._api.start_screen_tracking(lambda *_args: None)
        else:
            self._api.stop_screen_tracking(lambda *_args: None)

    def _handle_event_stream(self, event_type, _timestamp, *_args):
        if event_type == Events.PROCEDURE_ENDED:
            self._enable_screen_tracking(True)

    def _handle_connect_response(self, error):
        if not error:
            self._api.set_stream_control(
                adhawkapi.PacketType.GAZE_IN_SCREEN, 125, callback=(lambda *args: None)
            )
            self._api.set_event_control(
                adhawkapi.EventControlBit.PRODECURE_START_END,
                1,
                callback=(lambda *args: None),
            )
            self._api.start_camera_capture(
                camera_index=0,
                resolution_index=adhawkapi.CameraResolution.MEDIUM,
                correct_distortion=False,
                callback=self._handle_camera_start_response,
            )

    def _handle_screen_registered_response(self, error):
        if not error:
            self._enable_screen_tracking(True)

    def _handle_camera_start_response(self, error):
        if not error:
            self._register_screen(
                self._size_mm[0] * 1e-3,
                self._size_mm[1] * 1e-3,
                self.MARKER_DIC,
                self._marker_ids,
                self._marker_positions,
            )

    @staticmethod
    def _pix_to_mm(length_pix, dpi):
        """Converts an array of pixel lengths to an array of values in mm"""
        mm2inch = 25.4
        return (length_pix[0] * mm2inch / dpi[0], length_pix[1] * mm2inch / dpi[1])

    def _create_custom_board(self):
        """Calculates up the positions of the ArUco markers on the screen"""
        margin_size = self.EDGE_OFFSETS_MM * 1e-3
        board_size = (self._size_mm[0] * 1e-3, self._size_mm[1] * 1e-3)
        marker_size = self.GAZE_MARKER_SIZE * 1e-3
        positions = np.array(
            [
                [margin_size[0, 0], -margin_size[1, 0] - marker_size],
                [
                    board_size[0] - margin_size[0, 1] - marker_size,
                    -margin_size[1, 0] - marker_size,
                ],
                [margin_size[0, 0], -board_size[1] + margin_size[1, 1]],
                [
                    board_size[0] - margin_size[0, 1] - marker_size,
                    -board_size[1] + margin_size[1, 1],
                ],
            ]
        )
        markers = []
        for marker_pos in positions:
            markers.append([*marker_pos, marker_size])
        return markers

    def _handle_gaze_in_screen_stream(self, _timestamp, xpos, ypos):
        """Handler for the gaze in screen stream"""
        if math.isnan(xpos) or math.isnan(ypos):
            return

        # Translates the passed coordinates to positions on the screen
        new_xcoord = round(self._screen.get_width() * xpos)
        new_ycoord = round(self._screen.get_height() * ypos)

        # Adds the new point to the point deque, and pops the least recent entry if the size of the deque exceeds
        # its maximum allowed size
        old_xcoord = 0
        old_ycoord = 0
        self._point_deque.append((new_xcoord, new_ycoord))
        if len(self._point_deque) > self.NUM_POINTS:
            (old_xcoord, old_ycoord) = self._point_deque.popleft()

        # Calculates display coordinates as an average of all points in the deque (reduces jitter)
        self._running_xcoord += new_xcoord - old_xcoord
        self._running_ycoord += new_ycoord - old_ycoord

        self._xcoord = self._running_xcoord / len(self._point_deque)
        self._ycoord = self._running_ycoord / len(self._point_deque)

    def get_coords(self):
        return (self._xcoord, self._ycoord)

    def draw(self):
        self._draw_surface.blit(self._aruco_image, (0, 0))
