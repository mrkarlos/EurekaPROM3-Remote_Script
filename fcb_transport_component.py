
from __future__ import absolute_import, print_function, unicode_literals
from builtins import zip
import Live
from ableton.v2.control_surface.components import TransportComponent
from ableton.v2.control_surface.control import ButtonControl, ToggleButtonControl

from .fcb_clip_slot_component import FcbClipSlotComponent
from .fcb_switch_control import FcbSwitchControl

import logging
logger = logging.getLogger(__name__)

class FcbTransportComponent(TransportComponent):
    stop_all_clips_button = FcbSwitchControl()
    # play_button = FcbBlinkingButtonControl()


    def __init__(self, *args, **keywords):
        logger.info('in __init__()')
        super().__init__(*args, **keywords)


    @stop_all_clips_button.pressed
    def stop_all_clips_button(self, value):
        logger.info('in stop_all_clips_button().pressed')
        self._on_stop_all_clips_button_pressed()

    # @play_button.toggled
    # def _on_play_button_toggled(self, is_toggled, button):
    #     self.song.is_playing = is_toggled
    #     # self.play_button.start_blinking()

    # @stop_all_clips_button.released
    # def stop_all_clips_button(self, value):
    #     logger.info('in stop_all_clips_button().released')
    #     self._on_stop_all_clips_button_released()

    def _on_stop_all_clips_button_pressed(self):
        logger.info('in _on_stop_all_clips_button_pressed()')
        self.song.stop_all_clips()
