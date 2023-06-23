
from __future__ import absolute_import, print_function, unicode_literals
import Live
from ableton.v2.base import listens, liveobj_valid, lazy_attribute, task
from ableton.v2.control_surface.components.clip_slot import ClipSlotComponent, find_nearest_color, is_button_pressed
from ableton.v2.control_surface.control import ButtonControl

from .fcb_switch_control import FcbSwitchControl

import logging
logger = logging.getLogger(__name__)


class FcbClipSlotComponent(ClipSlotComponent):
    launch_button = FcbSwitchControl()

    def __init__(self, *a, **k):
        logger.info('in __init__()')
        super().__init__(*a, **k)

        
    @launch_button.released
    def launch_button(self, button):
        logger.info('in launch_button().released')
        # self._on_launch_button_released()


    @launch_button.released_immediately
    def launch_button(self, button):
        logger.info('in launch_button().released_immediately')
        if button._double_click_context.click_count > 0:
            return
        self._on_launch_button_pressed()


    @launch_button.released_delayed
    def launch_button(self, button):
        logger.info('in launch_button().released_delayed')
        # self._on_launch_button_released()
        self._do_delete_clip()


    @launch_button.pressed
    def launch_button(self, button):
        logger.info('in launch_button().pressed')
        # self._on_launch_button_pressed()
        pass

    @launch_button.double_clicked
    def launch_button(self, button):
        logger.info('in launch_button().double_clicked')
        self._track_stop_button_pressed()
        pass


    @launch_button.pressed_delayed
    def launch_button(self, button):
        logger.info('in launch_button().pressed_delayed')
        # self._on_launch_button_pressed()
        pass


    def _on_launch_button_pressed(self):
        logger.info('in _on_launch_button_pressed()')
        if is_button_pressed(self._select_button):
            self._do_select_clip(self._clip_slot)
        elif liveobj_valid(self._clip_slot):
            if is_button_pressed(self._duplicate_button):
                self._do_duplicate_clip()
            elif is_button_pressed(self._delete_button):
                self._do_delete_clip()
            else:
                self._do_launch_clip(True)
                self._show_launched_clip_as_highlighted_clip()


    def _on_launch_button_released(self):
        logger.info('in _on_launch_button_released()')
        if self.launch_button.is_momentary:
            if not is_button_pressed(self._select_button) or liveobj_valid(self._clip_slot):
                if not is_button_pressed(self._duplicate_button):
                    if not is_button_pressed(self._delete_button):
                        self._do_launch_clip(False)


    def _track_stop_button_pressed(self):
        logger.info('in _track_stop_button_pressed()')
        track = self._clip_slot.canonical_parent
        if track == self.song.master_track:
            self.song.stop_all_clips()
        elif track in self.song.tracks:
            track.stop_all_clips()
